"""Atomic local metadata publication under concurrent Windows readers.

These helpers do not grant authority or replace a caller's path/receipt checks.
Retries repeat only the same rename, never the operation described by the file.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import time


def atomic_replace(source, destination):
    delays=(0,.01,.025,.05,.1,.2)
    for index,delay in enumerate(delays):
        if delay:time.sleep(delay)
        try:
            _replace_once(source,destination)
            return
        except OSError as error:
            if getattr(error,'winerror',None) not in {5,32,33} or index==len(delays)-1:
                raise


@lru_cache(maxsize=1)
def _windows_files():
    import ctypes
    from ctypes import wintypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    create=kernel.CreateFileW
    create.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,
                     wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    create.restype=wintypes.HANDLE
    close=kernel.CloseHandle;close.argtypes=[wintypes.HANDLE]
    rename=kernel.SetFileInformationByHandle
    rename.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
    rename.restype=wintypes.BOOL
    return create,close,wintypes.HANDLE(-1).value,rename


def _windows_path(path):
    value=os.path.abspath(os.fspath(path))
    if value.startswith('\\\\?\\'):return value
    return '\\\\?\\UNC\\'+value[2:] if value.startswith('\\\\') else '\\\\?\\'+value


def _replace_once(source,destination):
    if os.name!='nt':
        os.replace(source,destination)
        return
    import ctypes
    from ctypes import wintypes
    create,close,invalid,rename=_windows_files()
    # FileRenameInfoEx (22), REPLACE_IF_EXISTS | POSIX_SEMANTICS (3).
    # Sharing DELETE alone does not make MoveFileEx replace an open target.
    # https://learn.microsoft.com/windows/win32/api/winbase/ns-winbase-file_rename_info
    class RenameInfo(ctypes.Structure):
        _fields_=[('Flags',wintypes.DWORD),('RootDirectory',wintypes.HANDLE),
                  ('FileNameLength',wintypes.DWORD),('FileName',wintypes.WCHAR*1)]
    name=_windows_path(destination).encode('utf-16-le')
    size=max(ctypes.sizeof(RenameInfo),RenameInfo.FileName.offset+len(name)+ctypes.sizeof(wintypes.WCHAR))
    buffer=ctypes.create_string_buffer(size)
    info=ctypes.cast(buffer,ctypes.POINTER(RenameInfo)).contents
    info.Flags=3;info.RootDirectory=None;info.FileNameLength=len(name)
    ctypes.memmove(ctypes.addressof(buffer)+RenameInfo.FileName.offset,name,len(name))
    handle=create(_windows_path(source),0x10000,7,None,3,0x00200000,None)
    if handle==invalid:raise ctypes.WinError(ctypes.get_last_error())
    try:
        if not rename(handle,22,buffer,size):raise ctypes.WinError(ctypes.get_last_error())
    finally:
        close(handle)


@contextmanager
def shared_reader(path):
    """Read one open version while allowing its pathname to be replaced."""
    if os.name!='nt':
        with open(path,'rb') as stream:yield stream
        return
    import ctypes
    import msvcrt
    create,close,invalid,_=_windows_files()
    handle=create(_windows_path(path),0x80000000,7,None,3,0x80,None)
    if handle==invalid:raise ctypes.WinError(ctypes.get_last_error())
    try:
        descriptor=msvcrt.open_osfhandle(handle,os.O_RDONLY|os.O_BINARY)
    except BaseException:
        close(handle)
        raise
    with os.fdopen(descriptor,'rb') as stream:
        yield stream


def read_bytes_shared(path):
    with shared_reader(path) as stream:
        return stream.read()


def write_bytes_atomic(path, raw, *, fsync=False):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('wb',delete=False,dir=path.parent,
                                     prefix=path.name+'.',suffix='.tmp') as stream:
        stream.write(raw)
        if fsync:
            stream.flush()
            os.fsync(stream.fileno())
        temporary=Path(stream.name)
    # On a permanent publication failure, retain the temporary as evidence.
    atomic_replace(temporary,path)


@contextmanager
def os_lock(path, *, blocking):
    """Hold an advisory OS lock on byte 0 of ``path``, creating the file if absent.

    ``blocking=False`` raises ``OSError`` at once when another holder has it.
    ``blocking=True`` waits: on POSIX without bound, on Windows ``LK_LOCK``
    retries ten times at one-second intervals and then raises ``OSError``.
    """
    descriptor=os.open(path,os.O_RDWR|os.O_CREAT,0o600)
    try:
        if os.fstat(descriptor).st_size==0:
            os.write(descriptor,b'\0')
        os.lseek(descriptor,0,os.SEEK_SET)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(descriptor,msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(descriptor,fcntl.LOCK_EX if blocking else fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:
            yield
        finally:
            os.lseek(descriptor,0,os.SEEK_SET)
            if os.name=='nt':
                msvcrt.locking(descriptor,msvcrt.LK_UNLCK,1)
            else:
                fcntl.flock(descriptor,fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def stat_fingerprint(st):
    """Metadata fingerprint (지문) of one file: size, modification and birth time.

    Accepts ``os.stat`` results and ``os.DirEntry.stat(follow_symlinks=False)``.
    A rewrite that preserves all three values is not detected; only an explicit
    full-byte check catches it (accidental-change threat model). NTFS tunneling
    keeps the birth time when a name is deleted and recreated within ~15 s, so a
    same-size replacement that also restores the modification time is missed.
    """
    return (st.st_size, st.st_mtime_ns, getattr(st, 'st_birthtime_ns', st.st_ctime_ns))


def fingerprint_json(fingerprint):
    """Stored form: nanosecond times exceed canonical_json's safe integer range."""
    size, modified, born = fingerprint
    return [size, str(modified), str(born)]


def file_fingerprint(path):
    return stat_fingerprint(os.stat(path))


# Windows file times advance in ~15.6 ms ticks, so a same-size rewrite shortly
# after a read can keep the fingerprint (the racy-git case). Only fingerprints
# older than this may stand in for the bytes. Tunable, not a proven bound.
RACY_NS=2_000_000_000


def fingerprint_settled(fingerprint):
    """True when a fingerprint may justify skipping a content read."""
    return time.time_ns()-max(fingerprint[1],fingerprint[2])>RACY_NS


def json_copy(value):
    """A copy of a JSON value in which no container is shared with ``value`` or within itself.

    ``copy.deepcopy`` keeps a node that occurs twice in ``value`` as one shared
    node of the copy. Schema builders return this copy, so a caller may change
    any node in place without changing another field or a module global.
    """
    return json.loads(json.dumps(value))


def compact_json_bytes(value):
    """Compact sorted UTF-8 JSON, for values outside the state tree.

    Provider responses and transport files may hold fractional numbers, which
    ``repository.canonical_json`` rejects. NaN and infinities are refused.
    """
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def json_digest(value):
    """SHA-256 of ``compact_json_bytes(value)``."""
    return hashlib.sha256(compact_json_bytes(value)).hexdigest()


def bytes_evidence(raw):
    """Bytes recorded in JSON evidence: their SHA-256, a lossy UTF-8 reading and the exact base64."""
    import base64
    return {"sha256": hashlib.sha256(raw).hexdigest(), "text": raw.decode("utf-8", "replace"),
            "base64": base64.b64encode(raw).decode("ascii")}


def unique_pairs(pairs):
    """``object_pairs_hook`` that refuses a repeated key."""
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: "+key)
        result[key]=value
    return result


def reject_constant(value):
    """``parse_constant`` hook that refuses NaN and the infinities."""
    raise ValueError("non-finite JSON constant: "+value)


def strict_json_loads(raw):
    """Parse JSON refusing duplicate keys, named non-finite constants and
    exponents that overflow to infinity (such as ``1e999``)."""
    value=json.loads(raw,object_pairs_hook=unique_pairs,parse_constant=reject_constant)
    compact_json_bytes(value)
    return value


# The shape of a SHA-256 digest. Stored, wire and toolchain record schemas embed this node.
SHA256_SCHEMA={"type":"string","pattern":"^[0-9a-f]{64}$"}
_SHA256=re.compile(SHA256_SCHEMA["pattern"])


def is_sha256(value):
    """Lowercase 64-digit hexadecimal: the shape of a SHA-256 digest."""
    return isinstance(value,str) and _SHA256.fullmatch(value) is not None


def require_text(value, label):
    """``value`` when it is a string with a non-whitespace character; otherwise ``ValueError``."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def distinct_texts(value, label, *, nonempty=False):
    """``value`` as a new list when it is a list of distinct nonempty texts (and, with ``nonempty``, not empty)."""
    if (not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value)
            or len(set(value)) != len(value) or (nonempty and not value)):
        raise ValueError(f"{label} requires {'a nonempty list of ' if nonempty else ''}distinct nonempty strings")
    return list(value)


def now() -> str:
    """The current UTC time as an ISO string, the form ``parse_utc`` reads."""
    return datetime.now(timezone.utc).isoformat()


def parse_utc(value):
    """Parse an ISO time that states its offset, as an aware UTC datetime.

    A trailing ``Z`` means UTC. A missing offset, a non-string or a malformed
    time raises ``ValueError``.
    """
    if not isinstance(value,str) or not value:
        raise ValueError("time must be a nonempty ISO timestamp string")
    parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp requires a timezone: "+value)
    return parsed.astimezone(timezone.utc)


def sha256_file(path):
    digest=hashlib.sha256()
    with shared_reader(path) as stream:
        for block in iter(lambda: stream.read(1<<20), b''):
            digest.update(block)
    return digest.hexdigest()


_hashed={}


def cached_sha256(path):
    """Full-byte SHA-256, recomputed only when the file's fingerprint changes."""
    key=os.path.normcase(os.path.abspath(path))
    before=file_fingerprint(key)
    hit=_hashed.get(key)
    if hit and hit[0]==before:
        return hit[1]
    value=sha256_file(key)
    # A file that changed while being read is hashed again on the next call.
    if file_fingerprint(key)==before and fingerprint_settled(before):
        _hashed[key]=(before,value)
    return value


def no_reparse(path, *, below=None):
    """Reject a symlink or reparse point at ``path`` or an ancestor, stopping at ``below`` when given.

    Absent components are skipped. Here, not in git_store, because the frozen
    operator bootstrap may import only this module before its snapshot is verified.
    """
    candidate = Path(path).absolute()
    for part in (candidate, *candidate.parents):
        if part == below:
            return
        try:
            value = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(value.st_mode) or getattr(value, "st_file_attributes", 0) & 0x400:
            raise ValueError("physical path crosses a reparse point or symlink: " + str(part))


def installation_files(root):
    """Files that make up an installed skill, keyed by POSIX relative path.

    One definition for the repair identity and the frozen supervisor copy.
    Tests, bytecode caches and VCS/build outputs are not part of the skill.
    """
    root=Path(root)
    files={}
    for path in sorted(root.rglob('*')):
        relative=path.relative_to(root)
        if ({'__pycache__','.git','.lake'} & set(relative.parts) or relative.parts[:2]==('scripts','tests')
                or path.suffix=='.pyc' or not path.is_file()):
            continue
        files[relative.as_posix()]=path
    return files

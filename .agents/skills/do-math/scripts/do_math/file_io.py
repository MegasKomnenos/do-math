"""Atomic local metadata publication under concurrent Windows readers.

These helpers do not grant authority or replace a caller's path/receipt checks.
Retries repeat only the same rename, never the operation described by the file.
"""
from contextlib import contextmanager
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
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


def write_bytes_atomic(path, raw):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('wb',delete=False,dir=path.parent,
                                     prefix=path.name+'.',suffix='.tmp') as stream:
        stream.write(raw)
        temporary=Path(stream.name)
    # On a permanent publication failure, retain the temporary as evidence.
    atomic_replace(temporary,path)


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


def json_digest(value):
    """SHA-256 of compact sorted JSON, for values outside the state tree.

    Provider responses and transport files may hold fractional numbers, which
    ``repository.exact_content_hash`` rejects. NaN and infinities are refused.
    """
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


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

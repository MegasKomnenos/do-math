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
import re
import stat
import sys
import tempfile
import time


def atomic_replace(source, destination):
    delays=(0,.01,.025,.05,.1,.2)
    for index,delay in enumerate(delays):
        if delay:time.sleep(delay)  # layer: retry after a Windows sharing violation; the file system is not a port (설계 2.2)
        try:
            _replace_once(source,destination)
            return
        except OSError as error:
            if getattr(error,'winerror',None) not in {5,32,33} or index==len(delays)-1:
                raise


@lru_cache(maxsize=1)
def _windows_files():
    import ctypes  # layer: Windows file API; the file system is not a port (설계 2.2)
    from ctypes import wintypes  # layer: Windows file API; the file system is not a port (설계 2.2)
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
    import ctypes  # layer: Windows file API; the file system is not a port (설계 2.2)
    from ctypes import wintypes  # layer: Windows file API; the file system is not a port (설계 2.2)
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
    import ctypes  # layer: Windows file API; the file system is not a port (설계 2.2)
    import msvcrt  # layer: Windows file API; the file system is not a port (설계 2.2)
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
            import msvcrt  # layer: Windows file API; the file system is not a port (설계 2.2)
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


def fingerprint_settled(fingerprint, *, now_ns=None, racy_ns=None):
    """True when a fingerprint may justify skipping a content read."""
    if now_ns is None:
        now_ns = time.time_ns()  # layer: file metadata defaults to the OS wall clock
    return now_ns-max(fingerprint[1],fingerprint[2])>(RACY_NS if racy_ns is None else racy_ns)




def console_python():
    """The interpreter for commands a worker or person runs from a shell.

    A scheduled engine runs under ``pythonw.exe``, a GUI-subsystem program:
    PowerShell neither waits for it nor shows its output. Its sibling
    ``python.exe`` is the same installation with a console. Processes the
    engine starts itself with piped output keep ``sys.executable``.
    """
    current=Path(sys.executable)
    console=current.with_name('python.exe')
    return str(console) if current.name.lower()=='pythonw.exe' and console.is_file() else sys.executable


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


def _windows_handle_facts(handle):
    import ctypes  # layer: Windows file API; the file system is not a port (설계 2.2)
    from ctypes import wintypes  # layer: Windows file API; the file system is not a port (설계 2.2)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    final = kernel.GetFinalPathNameByHandleW
    final.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    final.restype = wintypes.DWORD
    buffer = ctypes.create_unicode_buffer(32768)
    count = final(handle, buffer, len(buffer), 0)
    if not count or count >= len(buffer):
        raise ctypes.WinError(ctypes.get_last_error())
    path = buffer.value
    if path.startswith("\\\\?\\UNC\\"):
        raise ValueError("storage requires a local fixed NTFS volume")
    path = path.removeprefix("\\\\?\\")
    volume = ctypes.create_unicode_buffer(32768)
    volume_path = kernel.GetVolumePathNameW
    volume_path.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    if not volume_path(path, volume, len(volume)):
        raise ctypes.WinError(ctypes.get_last_error())
    drive_type = kernel.GetDriveTypeW
    drive_type.argtypes = [wintypes.LPCWSTR]
    if drive_type(volume.value) != 3:
        raise ValueError("storage requires a local fixed volume")
    serial = wintypes.DWORD()
    fs = ctypes.create_unicode_buffer(256)
    info = kernel.GetVolumeInformationW
    info.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                     ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD), wintypes.LPWSTR, wintypes.DWORD]
    if not info(volume.value, None, 0, ctypes.byref(serial), None, None, fs, len(fs)):
        raise ctypes.WinError(ctypes.get_last_error())
    if fs.value.upper() != "NTFS":
        raise ValueError("storage requires NTFS")
    return Path(path), (volume.value.casefold(), serial.value)


class PhysicalBoundary:
    """A root proved physical once, when the boundary is opened.

    ``check`` proves the root: no reparse ancestor, the same local fixed NTFS
    volume, and a directory handle whose final path is the lexical root.
    Opening a file below the root only rejects reparse points between the root
    and the file. Handles are not re-verified after opening: swapping a path
    between check and use is deliberate tampering, not an accidental change.
    Does not assert an unspecified ACL policy.
    """
    def __init__(self, root):
        self.root = Path(os.path.abspath(root))
        no_reparse(self.root)
        if not self.root.is_dir():
            raise ValueError("physical boundary root must be an existing directory")
        self.device = self.root.stat().st_dev
        self.check()

    def check(self):
        no_reparse(self.root)
        if self.root.stat().st_dev != self.device:
            raise ValueError("physical root volume changed")
        if os.name == "nt":
            import ctypes  # layer: Windows file API; the file system is not a port (설계 2.2)
            from ctypes import wintypes  # layer: Windows file API; the file system is not a port (설계 2.2)
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            create = kernel.CreateFileW
            create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                               wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
            create.restype = wintypes.HANDLE
            close = kernel.CloseHandle
            close.argtypes = [wintypes.HANDLE]
            handle = create(str(self.root), 0, 3, None, 3, 0x02000000 | 0x00200000, None)
            if handle == wintypes.HANDLE(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                final, volume = _windows_handle_facts(handle)
                if os.path.normcase(str(final)) != os.path.normcase(str(self.root)):
                    raise ValueError("physical directory handle resolves elsewhere")
                if hasattr(self, "volume") and volume != self.volume:
                    raise ValueError("physical volume identity changed")
                self.volume = volume
            finally:
                close(handle)

    @contextmanager
    def open(self, path, mode):
        if mode not in {"rb", "xb"}:
            raise ValueError("physical boundary supports read or exclusive creation")
        path = Path(os.path.abspath(path))
        if not path.is_relative_to(self.root):
            raise ValueError("file path is outside the physical boundary")
        # The root and its ancestors were proved when this boundary opened.
        no_reparse(path, below=self.root)
        with path.open(mode) as stream:
            yield stream

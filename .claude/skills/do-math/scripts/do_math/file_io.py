"""Atomic local metadata publication under concurrent Windows readers.

These helpers do not grant authority or replace a caller's path/receipt checks.
Retries repeat only the same rename, never the operation described by the file.
"""
from contextlib import contextmanager
from functools import lru_cache
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

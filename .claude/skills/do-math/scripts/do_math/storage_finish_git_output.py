"""Pure decoding of Git cat-file batch responses, preserving order and exact bytes."""
from .ports.git_backend import GitBackendError
from pathlib import Path


def parse_project_root(raw: bytes):
    root = raw.decode().strip()
    return Path(root) if root else None


def parse_project_tree(returncode, raw: bytes):
    return raw.decode().strip() if returncode == 0 else None


def parse_project_paths(returncode, raw: bytes):
    if returncode:
        raise RuntimeError('cannot read tracked paths for the configured project')
    return frozenset(name.decode('utf-8') for name in raw.split(b'\0') if name)


def parse_object_info(specs, raw: bytes):
    rows = raw.decode("utf-8").splitlines()
    if len(rows) != len(specs):
        raise GitBackendError("batch object check response count differs")
    result = []
    for spec, row in zip(specs, rows):
        if row == f"{spec} missing":
            result.append(None)
            continue
        fields = row.split()
        if len(fields) != 3 or not fields[2].isdigit():
            raise GitBackendError("invalid batch object check row for " + spec)
        result.append((fields[0], fields[1], int(fields[2])))
    return result


def parse_read_objects(specs, raw: bytes):
    result, offset = [], 0
    for spec in specs:
        end = raw.find(b"\n", offset)
        if end >= 0 and raw[offset:end] == f"{spec} missing".encode("utf-8"):
            result.append(None)
            offset = end + 1
            continue
        header = raw[offset:end].split() if end >= 0 else []
        if len(header) != 3 or not header[2].isdigit():
            raise GitBackendError("batch read returned no object header for " + spec)
        size = int(header[2])
        start, offset = end + 1, end + 1 + size
        if raw[offset:offset + 1] != b"\n":
            raise GitBackendError("truncated batch object: " + spec)
        result.append((header[1].decode("ascii"), raw[start:offset]))
        offset += 1
    if offset != len(raw):
        raise GitBackendError("unexpected trailing batch output")
    return result

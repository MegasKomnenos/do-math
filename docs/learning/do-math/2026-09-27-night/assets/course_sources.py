"""Read this edition's exact source bytes from its pinned Git commit."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[5]


@lru_cache(maxsize=1)
def source_manifest():
    return json.loads((BASE / 'reference/sources/manifest.json').read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def source_bytes():
    """Batch-read and verify every blob; never substitute the current worktree."""
    manifest = source_manifest()
    commit = manifest['head']
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', commit):
        raise ValueError('Invalid source commit in the edition manifest')
    requests = []
    for row in manifest['files']:
        path = row['path']
        if (PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts
                or any(char in path for char in ('\n', '\r', '\0', '\\'))):
            raise ValueError('Invalid source path: ' + repr(path))
        requests.append(f'{commit}:.claude/skills/do-math/{path}\n')
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=''.join(requests).encode('utf-8'), capture_output=True, check=True)
    blobs = {}
    offset = 0
    for row in manifest['files']:
        end = result.stdout.index(b'\n', offset)
        header = result.stdout[offset:end].split()
        if len(header) != 3 or header[1] != b'blob':
            raise ValueError('Pinned source unavailable: ' + row['path'])
        size = int(header[2])
        offset = end + 1
        raw = result.stdout[offset:offset + size]
        offset += size + 1
        if len(raw) != row['bytes'] or sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Pinned source differs from the edition manifest: ' + row['path'])
        blobs[row['path']] = raw
    return blobs


def source_text(path):
    return source_bytes()[path].decode('utf-8-sig')

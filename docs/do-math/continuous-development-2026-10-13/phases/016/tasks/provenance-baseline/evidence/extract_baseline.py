"""Extract exactly the selected Git scripts subtree, without a checkout or product import."""
import ast
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import stat
import subprocess
import sys
from datetime import datetime, timezone
from investigate import REPO, OUT, PREFIX, sha, write, git


def no_reparse(path):
    for part in [path, *path.parents]:
        if part.exists():
            info = part.lstat()
            assert not part.is_symlink(), str(part)
            assert not getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT, str(part)


def safe_relative(name):
    posix, windows = PurePosixPath(name), PureWindowsPath(name)
    assert not posix.is_absolute() and not windows.is_absolute() and not windows.drive, name
    assert '\\' not in name and not any(p in ('', '.', '..') for p in name.split('/')), name
    assert all(not any(c in p for c in ':<>"|?*') and p.rstrip(' .') == p for p in posix.parts), name
    assert all(not PureWindowsPath(p).is_reserved() for p in posix.parts), name
    return posix


selection = json.loads((OUT/'history-selection.json').read_text(encoding='utf-8'))
commit, fix = selection['baseline_commit'], selection['introduction_commit']
root = OUT/'pre-provenance/scripts'
assert root.resolve() != (REPO/PREFIX).resolve()
assert root.resolve().is_relative_to(OUT.resolve())
assert not root.exists(), 'Extraction must be new and cannot overwrite an old run.'
no_reparse(OUT)
tree = git('extraction-tree', 'ls-tree', '-r', '-z', commit, '--', PREFIX+'/')
entries=[]
for record in tree.split(b'\0'):
    if not record:
        continue
    meta, path = record.split(b'\t', 1)
    mode, kind, blob = meta.decode('ascii').split()
    original=path.decode('utf-8')
    assert original.startswith(PREFIX+'/')
    relative=original[len(PREFIX)+1:]
    safe_relative(relative)
    assert mode in ('100644', '100755') and kind=='blob', (mode, kind, original)
    entries.append(dict(repository_path=original, path=relative, mode=mode, git_blob=blob))
assert len({row['path'].casefold() for row in entries}) == len(entries), 'Windows path collision'
ids=list(dict.fromkeys(row['git_blob'] for row in entries))
request=('\n'.join(ids)+'\n').encode('ascii')
(OUT/'extraction-objects.stdin').write_bytes(request)
argv=['git','cat-file','--batch']
started=datetime.now(timezone.utc).isoformat()
p=subprocess.run(argv,input=request,cwd=REPO,capture_output=True)
(OUT/'extraction-objects.stdout.bin').write_bytes(p.stdout)
(OUT/'extraction-objects.stderr').write_bytes(p.stderr)
write('extraction-objects.command.json', dict(argv=argv,cwd=str(REPO),started=started,
      ended=datetime.now(timezone.utc).isoformat(),exit_code=p.returncode,
      stdin='extraction-objects.stdin',stdin_sha256=sha(request),
      stdout='extraction-objects.stdout.bin',stdout_sha256=sha(p.stdout),
      stderr='extraction-objects.stderr',object_count=len(ids)))
assert p.returncode==0
objects={}
stream=io.BytesIO(p.stdout)
for blob in ids:
    actual, kind, size=stream.readline().decode('ascii').strip().split()
    assert actual==blob and kind=='blob'
    data=stream.read(int(size))
    assert len(data)==int(size) and stream.read(1)==b'\n'
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blob
    objects[blob]=data
assert stream.read()==b''
root.mkdir(parents=True)
for row in entries:
    path=root.joinpath(*safe_relative(row['path']).parts)
    assert path.resolve().is_relative_to(root.resolve())
    path.parent.mkdir(parents=True,exist_ok=True)
    no_reparse(path.parent)
    data=objects[row['git_blob']]
    with path.open('xb') as target:
        target.write(data)
    readback=path.read_bytes()
    assert readback==data
    row.update(bytes=len(data),sha256=sha(readback))
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
assert actual=={row['path'] for row in entries}
required=['run_tests.py','test_categories.py','tests/support/branch_gate.py','tests/support/t3_store.py',
          'tests/support/selection.py','do_math/file_io.py','do_math/layers.py']
assert all((root/name).is_file() for name in required)
manifest=dict(format='git-scripts-baseline/1',baseline_commit=commit,introduction_commit=fix,
              scripts_git_tree=git('scripts-tree-id','rev-parse',commit+':'+PREFIX).decode().strip(),
              repository_prefix=PREFIX,extracted_scripts=str(root.resolve()),
              current_scripts=str((REPO/PREFIX).resolve()),
              extraction='git ls-tree -r -z -> git cat-file --batch; binary exclusive writes, no filters or newline conversion',
              command_receipts=['extraction-tree.command.json','extraction-objects.command.json','scripts-tree-id.command.json'],
              all_paths_validated=True,symlinks_or_gitlinks=0,reparse_points=0,
              file_count=len(entries),total_bytes=sum(r['bytes'] for r in entries),
              required_files=required,files=entries)
write('baseline-manifest.json',manifest)
print(json.dumps({k:manifest[k] for k in ('baseline_commit','extracted_scripts','file_count','total_bytes')},ensure_ascii=False))

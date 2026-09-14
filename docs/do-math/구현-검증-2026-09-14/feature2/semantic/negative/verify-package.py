"""Verify packaged evidence and frozen skill bytes; never invokes models or Lean."""
from pathlib import Path, PurePosixPath
import hashlib,json,zipfile

def verify(root):
    package=json.loads((root/'package-manifest.json').read_text(encoding='utf-8'))
    for entry in package['files']:
        path=root/entry['path']
        raw=path.read_bytes()
        assert len(raw)==entry['bytes'], entry['path']
        assert hashlib.sha256(raw).hexdigest()==entry['sha256'], entry['path']
    original=json.loads((root/'skill-source-manifest.json').read_text(encoding='utf-8'))
    expected={entry['path']:entry for entry in original['files']}
    with zipfile.ZipFile(root/'tested-skill.zip') as archive:
        assert set(archive.namelist())==set(expected), 'archive entry set differs'
        assert archive.testzip() is None, 'archive CRC failed'
        for name,entry in expected.items():
            assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
            raw=archive.read(name)
            assert len(raw)==entry['bytes'], name
            assert hashlib.sha256(raw).hexdigest()==entry['sha256'], name
    raw_logs=json.loads((root/'jsonl-manifest.json').read_text(encoding='utf-8'))
    copied={entry.get('source_relative'):entry for entry in package['files'] if entry.get('source_relative')}
    for entry in raw_logs:
        packaged=copied[entry['path']]
        assert packaged['sha256']==entry['sha256'] and packaged['bytes']==entry['bytes'], entry['path']
    return {'passed':True,'packaged_files_verified':len(package['files']),
            'frozen_source_files_verified':len(expected),'raw_jsonl_files_verified':len(raw_logs)}

if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parent),ensure_ascii=False,indent=2))

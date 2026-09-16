from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(r'C:\math')
HERE = Path(__file__).resolve().parent
SKILL = ROOT / '.claude/skills/do-math'
docs = [SKILL / 'SKILL.md', SKILL / 'GLOSSARY.md', SKILL / 'README.md']
docs += sorted((SKILL / 'references').glob('*.md'))
docs += sorted((SKILL / '계약').glob('*.md'))
assert len(docs) == 19, len(docs)
text = '\n\n'.join('# 파일: ' + path.relative_to(SKILL).as_posix() + '\n\n'
    + path.read_text(encoding='utf-8').rstrip() for path in docs) + '\n'
(HERE / '문서-독해본.md').write_text(text, encoding='utf-8', newline='\n')
target = HERE / 'full-v2'
shutil.copytree(SKILL, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
manifest = [{'path': path.relative_to(target).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(target.rglob('*')) if path.is_file()]
(HERE / 'full-v2-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'snapshot_files': len(manifest), 'document_files': len(docs), 'draft_bytes': len(text.encode('utf-8'))}))

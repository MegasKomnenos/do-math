"""Deliver bounded, complete source ranges; retain coordinates for this repair."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / '.claude/skills/do-math'
LEDGER = Path(__file__).with_name('reading-manifest.json')

if not LEDGER.exists():
    preferred = ['SKILL.md', 'GLOSSARY.md', 'references/공통-실행.md',
                 'references/모델과-실행예산.md', 'references/지식-저작과-재사용.md',
                 'references/학술자료-활용.md', 'README.md', 'references/CLI-실행-계약.md']
    paths = sorted(p.relative_to(SKILL).as_posix() for p in SKILL.rglob('*')
                   if p.is_file() and '__pycache__' not in p.parts)
    ordered = preferred + [p for p in paths if p not in preferred]
    files = []
    for name in ordered:
        raw = (SKILL / name).read_bytes()
        lines = raw.decode('utf-8-sig').splitlines(keepends=True)
        files.append(dict(path=name, sha256=hashlib.sha256(raw).hexdigest(),
                          bytes=len(raw), lines=len(lines), read_to=len(lines) if name == 'SKILL.md' else 0))
    state = {'files': files, 'deliveries': [{'path': 'SKILL.md', 'start': 1, 'end': files[0]['lines'],
                                          'note': 'Read in full before creating this ledger.'}]}
else:
    state = json.loads(LEDGER.read_text(encoding='utf-8'))

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 22000
size = 0
for item in state['files']:
    if item['read_to'] == item['lines']:
        continue
    lines = (SKILL / item['path']).read_text(encoding='utf-8-sig').splitlines(keepends=True)
    start = item['read_to']
    end = start
    while end < len(lines) and (size + len(lines[end]) <= limit or size == 0):
        size += len(lines[end])
        end += 1
    if end == start:
        break
    print(f"\nFILE {item['path']} LINES {start + 1}-{end}/{len(lines)}\n")
    print(''.join(lines[start:end]), end='')
    item['read_to'] = end
    state['deliveries'].append({'path': item['path'], 'start': start + 1, 'end': end})
    if end != len(lines):
        break
LEDGER.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
done = sum(x['read_to'] == x['lines'] for x in state['files'])
print(f"\nDELIVERY TOTAL: {done}/{len(state['files'])} complete files; "
      f"{sum(x['read_to'] for x in state['files'])}/{sum(x['lines'] for x in state['files'])} lines.")

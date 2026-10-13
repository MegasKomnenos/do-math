import hashlib
import json
from pathlib import Path
import subprocess
import sys

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).parent
previous = json.loads((RUN / 'phases/013/manager-evidence/source-inspected.json').read_bytes())
current = {name: hashlib.sha256((REPO / name).read_bytes()).hexdigest()
           for name in previous if (REPO / name).is_file()}
extra = list((REPO / 'services/scholarly-mcp').glob('*.py'))
current.update({p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in extra})
(OUT / 'source-start.json').write_text(json.dumps(current, indent=2), encoding='utf-8')
comparison = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO).decode().strip(),
              'changed_from_013': [p for p, h in previous.items() if current.get(p) != h],
              'missing_from_013': [p for p in previous if not (REPO / p).is_file()]}
(OUT / 'start-comparison.json').write_text(json.dumps(comparison, indent=2), encoding='utf-8')
sys.path.insert(0, str(REPO / '.claude/skills/do-math/scripts'))
from do_math.scholarly_config import resolve_scholarly_server
import os
home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
server = resolve_scholarly_server(None, start=REPO, codex_home=home)
(OUT / 'server-selection.json').write_text(json.dumps({'server': server, 'start': str(REPO), 'codex_home': str(home)}, indent=2), encoding='utf-8')
print(json.dumps(comparison))
print(json.dumps(server))

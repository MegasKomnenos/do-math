import collections
import json
from pathlib import Path
import sys

S = Path('C:/math/.claude/skills/do-math/scripts')
sys.path.insert(0, str(S))
from do_math.file_io import read_bytes_shared
E = Path(__file__).resolve().parent
root = E / sys.argv[1]
for directory in [root, root/'boundary', *sorted(root.glob('*isolated*'))]:
    path = directory / 'result.json'
    if path.exists():
        try:
            d = json.loads(read_bytes_shared(path))
            rows = d.get('rows', [])
            print(directory.name, d.get('complete'), dict(collections.Counter(r['outcome'] for r in rows)),
                  rows[-1]['id'] if rows else '')
        except (OSError, ValueError) as exc:
            print(directory.name, type(exc).__name__)

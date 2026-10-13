"""Read-only minimal reproduction of the external fixture's actual record rejection.

Reuses a preserved verified Lean identity; does not compile, adopt trust, or
change the installation. Only a fresh evidence workspace is requested.
"""
import json
import hashlib
from pathlib import Path
import sys
from task_tools import ROOT, HERE, dump

sys.path[:0] = [str(ROOT/'.claude/skills/do-math/scripts'),str(ROOT/'.claude/skills/do-math/scripts/tests')]
from support.knowledge_roundtrip import installed_request
from do_math.trust_inventory import observe_fingerprint

original = ROOT/'docs/do-math/continuous-development-2026-10-13/phases/012/tasks/lean-smoke/evidence/live-final/smoke-isolated-000/scratch/lean-smoke-x55z1ajz/normal.json'
observed = json.loads(original.read_text(encoding='utf-8-sig'))
identity = observed['toolchain']
fingerprint = observe_fingerprint(identity)
workspace = HERE/'fixture-reproduction-workspace'
workspace.mkdir()
record = {'identity_source':str(original), 'identity_source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
          'identity':identity,'fingerprint_files':sorted(fingerprint['files']),
          'fixture_content_files':[], 'source_files':{path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in (
              '.claude/skills/do-math/scripts/tests/support/knowledge_roundtrip.py',
              '.claude/skills/do-math/scripts/do_math/trust_inventory.py')}}
try:
    installed_request(workspace,identity)
except ValueError as error:
    record.update(result='rejected', error_type=type(error).__name__, error=str(error),
                  created_record_files=[str(p) for p in workspace.rglob('*.json')])
else:
    record['result']='unexpected_success'
dump(HERE/'fixture-reproduction.json',record)
print(json.dumps({key:record[key] for key in ('result','error_type','error')},ensure_ascii=False))
assert record['result']=='rejected' and record['error']=='toolchain baseline 0 fingerprint and content file populations differ'

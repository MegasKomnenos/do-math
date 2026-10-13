"""Read assigned inputs and bind this task to the inspected source version."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from run_command import ROOT, EVIDENCE, snapshot, write_json, changed

RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OLD = RUN / 'phases/008/tasks/document-recovery/evidence'
MANAGER = RUN / 'phases/008/manager-evidence'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True).stdout

current = snapshot()
write_json(EVIDENCE / 'source-start.json', current)
previous = read(OLD / 'source-final.json')
manager = read(MANAGER / 'verification.json')
preservation = read(MANAGER / 'preservation.json')
assert sha(OLD / 'source-final.json') == manager['source_final_sha256']
assert not changed(previous, current), changed(previous, current)
pending = preservation['pending_product']['files']
assert all(current[p] == h for p, h in pending.items())
state = {'head': git('rev-parse', 'HEAD').decode().strip(),
         'prior_inspected_head': manager['head'],
         'difference_from_008_source_final': changed(previous, current),
         'source_count': len(current), 'pending_product_preserved': list(pending),
         'head_changes_since_inspection': git('diff', '--name-only', manager['head'], 'HEAD').decode('utf-8'),
         'status': git('-c', 'core.quotepath=false', 'status', '--porcelain=v1').decode('utf-8')}
write_json(EVIDENCE / 'start-state.json', state)
inputs = read(RUN / 'phases/009/phase.json')['tasks'][0]['inputs']
hashes = {}
for ref in inputs:
    scope, rel = ref.split(':', 1)
    path = (ROOT if scope == 'repo' else RUN) / rel
    raw = path.read_bytes()
    hashes[ref] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
write_json(EVIDENCE / 'input-hashes.json', hashes)
scripts = ROOT / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(scripts), str(scripts / 'tests')]
from support import doc_code
from do_math import provider_final
doc = ROOT / '.claude/skills/do-math/references/CLI-실행-계약.md'
raw = doc.read_bytes()
(EVIDENCE / 'cli-before.txt').write_bytes(raw)
text = raw.decode('utf-8')
schemas = doc_code.field_schemas()
unowned = doc_code.unowned_field_references(text, schemas)
assert unowned == ['provider_final.output_contract'], unowned
assert text.count('`provider_final.output_contract`') == 1
assert callable(provider_final.output_contract)
old_rows = {}
for label in ('canonical-joined-final', 'mirror-final'):
    report = read(OLD / label / 'results/report.json')
    rows = [row for group in report['reports'] for row in group['rows']]
    failures = [row for row in rows if row['outcome'] != 'passed']
    assert len(failures) == 4
    assert all(r['outcome'] == 'failed' and 'provider_final.output_contract' in str(r) for r in failures)
    old_rows[label] = {'selected': len(report['selected']), 'counts': report['counts'],
                       'report_sha256': sha(OLD / label / 'results/report.json'),
                       'failures': failures}
write_json(EVIDENCE / 'baseline-reference.json', {'callable': True, 'unowned_before': unowned,
           'document_sha256': sha(doc), 'helper_sha256': sha(scripts / 'tests/support/doc_code.py'),
           'prior_suites': old_rows, 'manager_callable_issue': manager['callable_issue']})
print(json.dumps({'head': state['head'], 'source_count': len(current),
                  'difference_from_008': [], 'pending_preserved': len(pending),
                  'unowned': unowned}, ensure_ascii=False))

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from run_command import ROOT, EVIDENCE, write_json

run = ROOT / 'docs/do-math/continuous-development-2026-10-13'
phase = json.loads((run / 'phases/008/phase.json').read_text(encoding='utf-8-sig'))
inputs = {}
for ref in phase['tasks'][0]['inputs']:
    kind, relative = ref.split(':', 1)
    path = (ROOT if kind == 'repo' else run) / relative
    raw = path.read_bytes()
    inputs[ref] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
write_json(EVIDENCE / 'input-hashes.json', inputs)
prior = json.loads((run / 'phases/007/manager-evidence/verification.json').read_bytes())
write_json(EVIDENCE / 'prior-verification-summary.json', {
    key: value for key, value in prior.items() if key not in ('sources', 'changes', 'changes_from_start')})
packets = json.loads((run / 'phases/001/tasks/document-closeout/evidence/followup-packets.json').read_bytes())
selected = []
def walk(value):
    if isinstance(value, dict):
        if value.get('id') == 'P01':
            selected.append(value)
        elif value.get('id') == 'N03-003':
            selected.append(value)
        elif value.get('token') == 'LIVE_INSTALLATION_ROOT':
            selected.append(value)
        else:
            for child in value.values(): walk(child)
    elif isinstance(value, list):
        for child in value: walk(child)
walk(packets)
write_json(EVIDENCE / 'selected-input-packets.json', selected)
inventory = json.loads((run / 'phases/001/tasks/document-closeout/evidence/binding-inventory.json').read_bytes())
relevant = []
def inventory_walk(value):
    if isinstance(value, dict):
        if value.get('owner') in ('checkpoint_source', 'recovery_source', 'checkpoint_files',
                                'recovered_output_files', 'recovery_materials', 'operational_evidence'):
            relevant.append(value)
        else:
            for child in value.values(): inventory_walk(child)
    elif isinstance(value, list):
        for child in value: inventory_walk(child)
inventory_walk(inventory)
write_json(EVIDENCE / 'prior-binding-selection.json', relevant)
sys.path[:0] = [str(ROOT / '.claude/skills/do-math/scripts'), str(ROOT / '.claude/skills/do-math/scripts/tests')]
paths = ['.claude/skills/do-math/scripts/tests/support/doc_code.py',
         '.claude/skills/do-math/references/CLI-실행-계약.md']
baseline = {}
for path in paths:
    result = subprocess.run(['git', 'cat-file', '--filters', 'HEAD:' + path], cwd=ROOT, capture_output=True)
    assert result.returncode == 0
    baseline[path] = result.stdout
    (EVIDENCE / ('baseline-doc-code.txt' if path.endswith('.py') else 'baseline-cli-contract.md')).write_bytes(result.stdout)
start = json.loads((EVIDENCE / 'source-start.json').read_bytes())
for path in baseline:
    assert path in start
namespace = {'__name__': 'baseline_doc_code'}
exec(compile(baseline[paths[0]], paths[0], 'exec'), namespace)
text = baseline[paths[1]].decode('utf-8')
unowned = namespace['unowned_field_references'](text, namespace['field_schemas']())
write_json(EVIDENCE / 'preexisting-field-failure.json', {
    'basis': 'HEAD normalized text; start working files have mixed line endings, so raw hashes are recorded separately.',
    'start_raw_sha256': {path: start[path] for path in baseline}, 'unowned_fields': unowned,
    'callable_exists': callable(__import__('do_math.provider_final', fromlist=['output_contract']).output_contract),
    'baseline_sha256': {path: hashlib.sha256(raw).hexdigest() for path, raw in baseline.items()}})
assert unowned == ['provider_final.output_contract']
consumers = []
for path in (ROOT / '.claude/skills/do-math/scripts/tests').rglob('*.py'):
    if path.name == 'doc_code.py': continue
    tree = ast.parse(path.read_text(encoding='utf-8'))
    if any(isinstance(node, ast.ImportFrom) and node.module == 'support.doc_code' for node in ast.walk(tree)):
        consumers.append(path.relative_to(ROOT).as_posix())
write_json(EVIDENCE / 'doc-code-consumers.json', consumers)
print(json.dumps({'inputs': len(inputs), 'consumers': consumers, 'preexisting_unowned': unowned}, ensure_ascii=False))

"""Read-only manager comparison; does not import or execute do-math code."""
from collections import Counter
from datetime import datetime, timezone
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[6]
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
SCRIPTS = ROOT / '.claude/skills/do-math/scripts'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True)
    return p.stdout.decode('utf-8').strip()


baseline = read(RUN / 'sources/baseline.json')
baseline_rows = baseline['product_files'] + baseline['source_files'] + baseline['engine_files']
differences = [row['path'] for row in baseline_rows
               if not (ROOT / row['path']).is_file() or sha(ROOT / row['path']) != row['sha256']]
assert not differences, differences
index = read(RUN / 'sources/requirements-index.json')['rows']
mapping = read(RUN / 'phases/001/tasks/closure-map/evidence/requirement-state.json')['rows']
key = lambda row: (row['group'], row['id'])
assert len({key(row) for row in mapping}) == len(mapping) == 103
assert {key(row) for row in index} == {key(row) for row in mapping}
assert {key(row): row['original'] for row in index if row['group'] != 'p2'} == {
    key(row): row['original'] for row in mapping if row['group'] != 'p2'}
assert {key(row): row['historical_expectation'] for row in index if row['group'] == 'p2'} == {
    key(row): row['original'] for row in mapping if row['group'] == 'p2'}

historical = read(RUN / 'phases/001/tasks/gate-readiness/evidence/historical-reports.json')
report_comparisons = []
for expected in historical:
    path = ROOT / expected['path']
    assert sha(path) == expected['sha256'], path
    report = read(path)
    rows = [row for group in report['reports'] for row in group['rows'] if not row.get('fixture')]
    selected = report['selected']
    ids = [row['id'] for row in rows]
    assert Counter(ids) == Counter(selected), path
    report_comparisons.append({
        'path': expected['path'], 'sha256': sha(path), 'selected': len(selected),
        'counts': dict(Counter(row['outcome'] for row in rows)),
        'complete': report['complete'], 'successful': report['successful'],
        'current_python_differences': [name for name, digest in report['source_sha256'].items()
                                       if sha(SCRIPTS / name) != digest],
    })

source_ranges = {
    '.claude/skills/do-math/scripts/tests/support/mutation.py': [(248, 267), (312, 356), (366, 371), (416, 448)],
    '.claude/skills/do-math/scripts/tests/boundary/test_mutation_baseline.py': [(1, 38)],
    '.claude/skills/do-math/scripts/run_tests.py': [(58, 70), (525, 533), (552, 562), (798, 815)],
    '.claude/skills/do-math/scripts/tests/support/doc_code.py': [(30, 40), (277, 289)],
    '.claude/skills/do-math/계약/운영-점검.md': [(15, 21)],
    '.claude/skills/do-math/scripts/do_math/core_engine.py': [(1807, 1865)],
    '.claude/skills/do-math/계약/독립-운영.md': [(21, 21)],
    '.claude/skills/do-math/scripts/operator_bootstrap.py': [(159, 170)],
    'docs/do-math/시험-재편-2026-09-29/설계.md': [(271, 275), (299, 307)],
}
excerpts = []
for name, ranges in source_ranges.items():
    lines = (ROOT / name).read_text(encoding='utf-8-sig').splitlines()
    excerpts.append({'path': name, 'sha256': sha(ROOT / name), 'ranges': [
        {'start': start, 'end': end, 'text': '\n'.join(lines[start - 1:end])} for start, end in ranges]})
(OUT / 'source-excerpts.json').write_text(json.dumps(excerpts, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

tree = ast.parse((SCRIPTS / 'do_math/layers.py').read_text(encoding='utf-8-sig'))
layers = next(ast.literal_eval(node.value) for node in tree.body
              if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'LAYERS' for t in node.targets))
population = read(RUN / 'phases/001/tasks/gate-readiness/evidence/population-and-corpus.json')
assert sorted(name for name, layer in layers.items() if layer in ('1', '2', '3')) == sorted(population['eligible_modules'])
smoke = list((SCRIPTS / 'tests/smoke').glob('test_*.py'))
assert not smoke
assert 'LIVE_INSTALLATION_ROOT' not in (SCRIPTS / 'operator_bootstrap.py').read_text(encoding='utf-8')

task_files = [p for p in (RUN / 'phases/001/tasks').rglob('*') if p.is_file()]
verification = {
    'observed_at': datetime.now(timezone.utc).isoformat(), 'head': git('rev-parse', 'HEAD'),
    'branch': git('branch', '--show-current'), 'baseline_files_checked': len(baseline_rows),
    'baseline_differences': differences, 'requirement_populations': dict(Counter(row['group'] for row in mapping)),
    'historical_reports': report_comparisons, 'layer_counts': dict(Counter(layers.values())),
    'smoke_test_modules': len(smoke), 'excluded_from_layer123_mutation': population['shard_ineligible_files'],
    'method': 'Current bytes, original report rows and source branches only. No product tests, mutation or live calls executed.',
    'task_input_hashes': {p.relative_to(RUN).as_posix(): sha(p) for p in sorted(task_files)},
}
(OUT / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: verification[k] for k in ['head', 'branch', 'baseline_files_checked', 'baseline_differences',
                 'requirement_populations', 'layer_counts', 'smoke_test_modules']}, ensure_ascii=False))
print(f'Original report comparisons: {len(report_comparisons)}; immutable task files recorded: {len(task_files)}')

"""Read-only manager checks of phase 002's preserved evidence and current edition."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[6]
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).parent
E = RUN / 'phases/002/tasks/mutation-baseline/evidence'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

check = subprocess.run([sys.executable, '-B', str(REPO / 'services/continuous-development/check.py'),
                        'report', str(REPO), str(RUN), '002', 'mutation-baseline'],
                       cwd=REPO, capture_output=True)
(OUT / 'report-check.stdout.txt').write_bytes(check.stdout)
(OUT / 'report-check.stderr.txt').write_bytes(check.stderr)
assert check.returncode == 0

before, after = (read(E / name) for name in ('source-before.json', 'source-after.json'))
changed = sorted(k for k in before['files'].keys() | after['files'].keys()
                 if before['files'].get(k) != after['files'].get(k))
task = read(RUN / 'phases/002/phase.json')['tasks'][0]
task_report = read(RUN / 'phases/002/tasks/mutation-baseline/report.json')
assert set(changed) == {c['path'] for c in task_report['changes']}
assert set(changed) <= set(task['writes'])
current_drift = [p for p, h in after['files'].items()
                 if not (REPO / p).is_file() or digest(REPO / p) != h]
assert not current_drift, current_drift

report = read(E / 'related-final/report.json')
process = read(E / 'related-final-run/process.json')
rows = [row for worker in report['reports'] for row in worker['rows']
        if not row.get('fixture', False)]
assert Counter(report['selected']) == Counter(row['id'] for row in rows)
assert len(rows) == 58 and Counter(row['outcome'] for row in rows) == {'passed': 58}
assert report['complete'] and report['successful'] and report['changed_during_run'] == []
assert process['exit_code'] == 0
edition_drift = [p for p, h in report['source_sha256'].items()
                 if digest(REPO / '.claude/skills/do-math/scripts' / p) != h]
assert not edition_drift, edition_drift

old_source = E / 'mutation-before.py'
assert digest(old_source) == before['files']['.claude/skills/do-math/scripts/tests/support/mutation.py']
function = next(n for n in ast.parse(old_source.read_text(encoding='utf-8')).body
                if isinstance(n, ast.FunctionDef) and n.name == 'passed')
namespace = {}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(old_source), 'exec'), namespace)
observations = read(E / 'boundary-observations.json')
observed = []
preserve = set()
for item in observations:
    path = E / item['report']
    assert digest(path) == item['report_sha256']
    actual = read(path)
    assert actual['counts'] == item['counts']
    assert actual['baseline_failing'] == item['baseline_failing']
    root = path.parent
    assert (root / 'scripts/mutation_fixture_tests.py').read_text(encoding='utf-8') == item['test_source']
    attempts = []
    if item['edition'] == 'red2':
        assert namespace['passed'](actual) == item['original_passed']
        assert [p.exists() for p in sorted(root.glob('mutation/unmutated-*'))
                for p in [p / 'result.json']] == item['normal_result_exists']
    else:
        records = [a['execution'] for o in actual['outcomes'] for a in o.get('attempts', [])]
        records += [b['attempt'] for b in actual['baselines']]
        for attempt in records:
            directory = Path(attempt['directory'])
            assert directory.is_relative_to(E.resolve())
            assert read(directory / 'attempt.json') == attempt
            assert (directory / 'spec.json').is_file() and (directory / 'output.txt').is_file()
            if attempt['result'] is not None:
                assert read(directory / 'result.json') == attempt['result']
            attempts.append({'directory': directory.relative_to(E).as_posix(),
                             'exit_code': attempt['exit_code'], 'error': attempt['error']})
        ids = {b['id'] for b in actual['baselines']}
        assert all(set(a['baselines']) <= ids for o in actual['outcomes'] for a in o.get('attempts', []))
    if item['consumer'] is not None:
        assert read(root / 'consumer.json') == item['consumer']
    for p in root.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            preserve.add(p.relative_to(REPO).as_posix())
    observed.append({'report': item['report'], 'sha256': digest(path), 'counts': actual['counts'],
                     'consumer': item['consumer'], 'attempts': attempts})
assert Counter(item['edition'] for item in observations) == {'red2': 2, 'related-final': 17}

prior = read(E / 'prior-review.json')
missing_paths = []
def walk(value):
    if isinstance(value, dict):
        if 'declaration' in value and 'exists' in value:
            path = value['declaration']['path']
            assert not Path(path).exists() and value['exists'] is False
            missing_paths.append(path)
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)
walk(prior)
assert len(missing_paths) == 4
for short in ('bbe64043', 'f56a2772'):
    patch = E / (short + '.patch')
    assert patch.is_file()

result = {
    'observed_at': datetime.now(timezone.utc).isoformat(),
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
    'report_check_exit_code': check.returncode,
    'task_report_sha256': digest(RUN / 'phases/002/tasks/mutation-baseline/report.json'),
    'snapshot_file_count': len(after['files']), 'current_snapshot_drift': current_drift,
    'changed_paths': changed, 'writes_match': True,
    'related_final': {'sha256': digest(E / 'related-final/report.json'),
                      'selected': len(report['selected']), 'rows': len(rows), 'counts': report['counts'],
                      'complete': report['complete'], 'successful': report['successful'],
                      'changed_during_run': report['changed_during_run'], 'exit_code': process['exit_code'],
                      'current_python_drift': edition_drift, 'python_file_count': len(report['source_sha256']),
                      'total_seconds': report['total_seconds']},
    'boundary_observations': observed,
    'prior_missing_paths': missing_paths,
    'limits': ['No product tests rerun by manager; verifies preserved raw output and present source bytes.',
               'G4/G5/G6/G7 full gates and final G8 review remain outstanding.'],
}
(OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(OUT / 'preserve-fixtures.json').write_text(json.dumps(sorted(preserve), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k not in ('boundary_observations', 'changed_paths', 'prior_missing_paths')},
                 ensure_ascii=False, indent=2))
print('Preserve raw fixture files:', len(preserve), 'bytes:', sum((REPO / p).stat().st_size for p in preserve))

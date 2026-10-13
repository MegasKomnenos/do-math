"""Cross-check original reports, immutable editions, child artifacts and authorized changes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from record import ROOT, EVIDENCE, snapshot, write


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def changed(before, after):
    return sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))


before = read(EVIDENCE / 'source-before.json')
after = snapshot()
write(EVIDENCE / 'source-after.json', after)
phase = read(EVIDENCE.parents[2] / 'phase.json')
allowed = set(phase['tasks'][0]['writes'])
delta = changed(before['files'], after['files'])
assert set(delta) <= allowed, delta
assert before['head'] == after['head']
report = read(EVIDENCE / 'related-final/report.json')
rows = [row for part in report['reports'] for row in part['rows'] if not row.get('fixture')]
assert len(report['selected']) == len(set(report['selected'])) == len(rows) == 58
assert sorted(report['selected']) == sorted(row['id'] for row in rows)
assert all(row['outcome'] == 'passed' for row in rows)
assert report['complete'] and report['successful'] and not report['changed_during_run']
scripts = ROOT / '.claude/skills/do-math/scripts'
edition_changes = [p for p, sha in report['source_sha256'].items()
                   if hashlib.sha256((scripts / p).read_bytes()).hexdigest() != sha]
assert not edition_changes, edition_changes
run_before = read(EVIDENCE / 'related-final-run/source-before.json')
run_after = read(EVIDENCE / 'related-final-run/source-after.json')
during = changed(run_before['files'], run_after['files'])
assert during == ['.claude/skills/do-math/scripts/tests/.timings.json'], during
mirror_before = read(EVIDENCE / 'mirror-build/source-before.json')
mirror_after = read(EVIDENCE / 'mirror-build/source-after.json')
mirror_delta = changed(mirror_before['files'], mirror_after['files'])
assert len(mirror_delta) == 6 and all(p.startswith('.agents/') and p in allowed for p in mirror_delta)
for p in delta:
    if p.startswith('.claude/'):
        mirror = p.replace('.claude/', '.agents/', 1)
        assert after['files'][p] == after['files'][mirror], p

# Execute the original shared predicate on the real, pre-fix parent reports.
# The failing red assertion stopped before its later passed() assertion; this
# makes that separate verdict observation explicit without rerunning the child.
relative = '.claude/skills/do-math/scripts/tests/support/mutation.py'
original = subprocess.check_output(['git', 'show', before['head'] + ':' + relative], cwd=ROOT)
assert hashlib.sha256(original).hexdigest() == before['files'][relative]
original_path = EVIDENCE / 'mutation-before.py'
original_path.write_bytes(original)
namespace = {'__name__': 'mutation_before', '__file__': str(original_path)}
exec(compile(original, str(original_path), 'exec'), namespace)
observations = []
for edition in ('red2', 'related-final'):
    for path in sorted((EVIDENCE / edition).rglob('report.json')):
        if not path.parent.name.startswith('mutation-baseline-'):
            continue
        data = read(path)
        root = path.parent
        item = {'edition': edition, 'report': path.relative_to(EVIDENCE).as_posix(),
                'report_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'test_source': (root / 'scripts/mutation_fixture_tests.py').read_text(encoding='utf-8'),
                'counts': data['counts'], 'baseline_failing': data['baseline_failing'],
                'consumer': read(root / 'consumer.json') if (root / 'consumer.json').exists() else None}
        if edition == 'red2':
            item['original_passed'] = namespace['passed'](data)
            item['normal_result_exists'] = [(p / 'result.json').exists()
                                            for p in sorted((root / 'mutation').glob('unmutated-*'))]
        else:
            attempts = [a['execution'] for outcome in data['outcomes'] for a in outcome['attempts']]
            attempts += [baseline['attempt'] for baseline in data['baselines']]
            for attempt in attempts:
                directory = Path(attempt['directory'])
                assert read(directory / 'attempt.json') == attempt
                assert (directory / 'spec.json').is_file() and (directory / 'output.txt').is_file()
                assert attempt['pid'] and type(attempt['exit_code']) is int
                if attempt['result'] is not None:
                    assert read(directory / 'result.json') == attempt['result']
            item['attempts'] = [{'directory': Path(a['directory']).relative_to(EVIDENCE).as_posix(),
                                 'pid': a['pid'], 'exit_code': a['exit_code'], 'error': a['error']}
                                for a in attempts]
            item['baseline_statuses'] = [b['status'] for b in data['baselines']]
        observations.append(item)
red = [o for o in observations if o['edition'] == 'red2' and 'os._exit(17)' in o['test_source']]
assert len(red) == 1 and red[0]['counts'] == {'killed': 1} and red[0]['original_passed']
assert red[0]['normal_result_exists'] == [False]
write(EVIDENCE / 'boundary-observations.json', observations)
verification = {'head': after['head'], 'changed_paths': delta, 'within_writes': True,
    'selected': report['selected'], 'rows': rows, 'selected_row_count': len(rows),
    'final_counts': report['counts'], 'complete': report['complete'], 'successful': report['successful'],
    'report_exit_code': read(EVIDENCE / 'related-final-run/process.json')['exit_code'],
    'report_sha256': hashlib.sha256((EVIDENCE / 'related-final/report.json').read_bytes()).hexdigest(),
    'current_edition_diff': edition_changes, 'during_run_changes': during,
    'mirror_changes': mirror_delta, 'boundary_fixture_count': len(observations),
    'old_report_verdict_source_sha256': hashlib.sha256(original).hexdigest(),
    'budget': report['budget']}
assert verification['report_exit_code'] == 0
write(EVIDENCE / 'verification.json', verification)
print(json.dumps({key: verification[key] for key in ('selected_row_count', 'final_counts',
    'current_edition_diff', 'within_writes', 'changed_paths', 'boundary_fixture_count')}, ensure_ascii=False))

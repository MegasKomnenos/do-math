"""Manager comparison of submitted records with current files; no product writes."""
import collections
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
EV = RUN / 'phases/008/tasks/document-recovery/evidence'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def git(*args):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True)
    return result.stdout

def main():
    phase = read(RUN / 'phases/008/phase.json')['tasks'][0]
    report = read(EV.parent / 'report.json')
    check = subprocess.run([sys.executable, '-B', str(ROOT / 'services/continuous-development/check.py'),
                            'report', str(ROOT), str(RUN), '008', phase['id']], cwd=ROOT, capture_output=True)
    write('report-check.json', {'argv': check.args, 'exit_code': check.returncode,
          'stdout': check.stdout.decode('utf-8'), 'stderr': check.stderr.decode('utf-8')})
    assert check.returncode == 0
    initial, final = read(EV / 'source-start.json'), read(EV / 'source-final.json')
    paths = set()
    for folder in ('.claude/skills', '.agents/skills', '.agents/diff', 'services/continuous-development'):
        paths.update(p for p in (ROOT / folder).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    paths.add(ROOT / '.gitattributes')
    current = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    assert current == final
    prior = read(RUN / 'phases/007/tasks/provider-consumers/evidence/source-final.json')
    prior_changes = sorted(p for p in prior.keys() | initial.keys() if prior.get(p) != initial.get(p))
    changes = sorted(p for p in initial.keys() | final.keys() if initial.get(p) != final.get(p))
    assert set(changes) == {v['path'] for v in report['changes']}
    assert all(any(p == w or w.endswith('/') and p.startswith(w) for w in phase['writes']) for p in changes)
    checks = {}
    final_failures = {}
    for label in ('red', 'focused-01', 'focused-02', 'canonical-final', 'canonical-final-02',
                  'shared-consumers-final', 'canonical-joined-final', 'mirror-final'):
        path = EV / label
        result, command = read(path / 'results/report.json'), read(path / 'command.json')
        rows = [row for group in result['reports'] for row in group['rows']]
        ids = [row['id'] for row in rows]
        assert len(ids) == len(set(ids)) == len(result['selected'])
        assert set(ids) == set(result['selected'])
        assert dict(collections.Counter(row['outcome'] for row in rows)) == result['counts']
        assert result['complete'] and not result['changed_during_run']
        assert command['state'] == 'exited' and command['ended_at'] > command['started_at']
        assert command['exit_code'] == (0 if result['successful'] else 1)
        before, after = read(path / 'source-before.json'), read(path / 'source-after.json')
        delta = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
        assert delta == sorted(command['changed_sources'])
        assert all(p.endswith('/tests/.timings.json') for p in delta)
        tree = '.agents' if label == 'mirror-final' else '.claude'
        base = tree + '/skills/do-math/scripts/'
        assert all(before[base + p] == h == after[base + p] for p, h in result['source_sha256'].items())
        mismatches = [p for p, h in result['source_sha256'].items() if current[base + p] != h]
        failures = [row for row in rows if row['outcome'] != 'passed']
        checks[label] = {'selected': len(ids), 'unique_rows': len(set(ids)), 'counts': result['counts'],
                        'complete': result['complete'], 'successful': result['successful'],
                        'exit_code': command['exit_code'], 'python_source_count': len(result['source_sha256']),
                        'changed_after_run': mismatches, 'failures': failures,
                        'command_sha256': sha(path / 'command.json'), 'report_sha256': sha(path / 'results/report.json')}
        if label in ('canonical-joined-final', 'mirror-final'):
            assert not mismatches and len(failures) == 4
            assert all(row['outcome'] == 'failed' and 'provider_final.output_contract' in str(row) for row in failures)
            final_failures[label] = sorted(row['id'] for row in failures)
    assert final_failures['canonical-joined-final'] == final_failures['mirror-final']
    red_ids = {row['id'] for row in checks['red']['failures']}
    last = read(EV / 'canonical-joined-final/results/report.json')
    assert red_ids <= {row['id'] for group in last['reports'] for row in group['rows'] if row['outcome'] == 'passed'}
    runtime = read(RUN / 'phases/007/manager-evidence/verification.json')['runtime_unchanged_since_live']
    assert len(runtime) == 124 and all(initial[p] == final[p] for p in runtime)
    smoke = ['.claude/skills/do-math/scripts/' + name for name in
             ('tests/support/provider_live.py', 'tests/smoke/test_provider_live.py', 'probe_cli.py')]
    assert all(initial[p] == final[p] for p in smoke)
    corpus = read(EV / 'corpus-final.json')
    git_rows = []
    for tree in corpus['trees'].values():
        for item in tree['files'].values():
            p = item['path']
            assert current[p] == initial[p] == item['sha256']
            assert (ROOT / p).stat().st_size == item['bytes']
            raw = git('hash-object', '--no-filters', '--', p).decode().strip()
            clean = git('hash-object', '--path=' + p, '--', p).decode().strip()
            assert raw == clean
            git_rows.append({'path': p, 'argv_path': p, 'raw': raw, 'clean': clean})
    write('git-clean-observation.json', {'cwd': str(ROOT), 'rows': git_rows})
    for label, plan in (('mirror-build', 'mirror-plan-final'), ('cache-sync', 'cache-plan')):
        command = read(EV / label / 'command.json')
        assert command['exit_code'] == 0
        assert set(command['changed_sources']) == set(read(EV / (plan + '.json'))['changed'])
    gates = {}
    for label in ('mirror-check', 'skill-only'):
        command = read(EV / label / 'command.json')
        assert command['exit_code'] == 0 and command['state'] == 'exited'
        assert read(EV / label / 'source-before.json') == read(EV / label / 'source-after.json') == final
        gates[label] = (EV / label / 'stdout.txt').read_text(encoding='utf-8')
    scripts = ROOT / '.claude/skills/do-math/scripts'
    sys.path[:0] = [str(scripts), str(scripts / 'tests')]
    from support import doc_code
    from do_math import provider_final
    doc_path = '.claude/skills/do-math/references/CLI-실행-계약.md'
    source_path = '.claude/skills/do-math/scripts/tests/support/doc_code.py'
    text = (ROOT / doc_path).read_text(encoding='utf-8')
    schemas = doc_code.field_schemas()
    assert doc_code.unowned_field_references(text, schemas) == ['provider_final.output_contract']
    assert callable(provider_final.output_contract)
    old_text = git('show', 'HEAD:' + doc_path).decode('utf-8').replace('\r\n', '\n')
    old_code = git('show', 'HEAD:' + source_path).decode('utf-8').replace('\r\n', '\n')
    assert old_text == (EV / 'baseline-cli-contract.md').read_text(encoding='utf-8')
    assert old_code == (EV / 'baseline-doc-code.txt').read_text(encoding='utf-8')
    old_module = {'__file__': str(scripts / 'tests/support/doc_code.py'), '__name__': 'manager_baseline_doc_code'}
    exec(compile(old_code, '<HEAD doc_code>', 'exec'), old_module)
    assert old_module['unowned_field_references'](old_text, old_module['field_schemas']()) == ['provider_final.output_contract']
    notation = '`provider_final.output_contract(...)`'
    assert doc_code.function_reference_issues(notation) == []
    assert doc_code.unowned_field_references(notation, schemas) == []
    (OUT / 'product.diff').write_bytes(git('diff', '--', '.claude/skills/do-math', '.agents/skills/do-math'))
    result = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'head': git('rev-parse', 'HEAD').decode().strip(), 'source_count': len(final),
              'source_final_sha256': sha(EV / 'source-final.json'), 'current_mismatches': [],
              'start_changes_since_007': prior_changes, 'changes': changes,
              'suites': checks, 'runtime_unchanged': len(runtime), 'smoke_inputs_unchanged': smoke,
              'corpus_paths_unchanged': len(git_rows), 'gates': gates,
              'callable_issue': {'baseline_reproduced': True, 'current_unowned': ['provider_final.output_contract'],
                                 'existing_explicit_notation_resolves': notation},
              'report_status': report['status'], 'acceptance': {v['id']: v['result'] for v in report['acceptance']}}
    write('verification.json', result)
    print(json.dumps({k: result[k] for k in ('head', 'source_count', 'current_mismatches', 'runtime_unchanged',
          'corpus_paths_unchanged', 'report_status', 'acceptance')}, ensure_ascii=False))
    print(json.dumps({'suites': {k: {a: v[a] for a in ('selected', 'counts', 'exit_code')} for k, v in checks.items()},
                      'final_failed_ids': final_failures['canonical-joined-final']}, ensure_ascii=False))

if __name__ == '__main__':
    main()

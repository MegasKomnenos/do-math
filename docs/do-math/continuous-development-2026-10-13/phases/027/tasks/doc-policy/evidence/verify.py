import ast
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from work import REPO, RUN, HERE, save, snapshot, difference

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

start, end = load(HERE / 'source-start.json'), snapshot()
writes = load(RUN / 'phases/027/phase.json')['tasks'][0]['writes']
changed = difference(start, end)
assert all(path in writes for path in changed)
baseline = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO).decode().strip()
preservation = {}
baseline_sources = {}
diffs = []
for path in changed:
    if not path.startswith('.claude/') or Path(path).name.startswith('.timings'):
        continue
    old = subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=REPO)
    baseline_sources[path] = 'Git HEAD bytes'
    if hashlib.sha256(old).hexdigest() != start[path]:
        # Git's text blob and the Windows working-tree newline bytes can differ.
        # Accept this reconstruction only if the entire recorded start hash matches.
        candidates = [old.replace(b'\r\n', b'\n'), old.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')]
        old = next((value for value in candidates if hashlib.sha256(value).hexdigest() == start[path]), old)
        baseline_sources[path] = 'Git HEAD bytes with start-SHA-verified newline reconstruction'
    if hashlib.sha256(old).hexdigest() != start[path]:
        with zipfile.ZipFile(RUN / 'phases/025/manager-evidence/raw-evidence.zip') as archive:
            if path in archive.namelist():
                old = archive.read(path)
                baseline_sources[path] = '025 manager raw-evidence.zip member verified against complete start SHA'
    assert hashlib.sha256(old).hexdigest() == start[path], path
    new = (REPO / path).read_bytes()
    diffs.extend(difflib.unified_diff(old.decode('utf-8').splitlines(True), new.decode('utf-8').splitlines(True),
                                    fromfile='start/' + path, tofile='end/' + path))
    if path.endswith('.py'):
        old_tree, new_tree = ast.parse(old), ast.parse(new)
        def definitions(tree):
            result = {}
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result[node.name] = node
                if isinstance(node, ast.ClassDef):
                    for method in node.body:
                        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            result[node.name + '.' + method.name] = method
            return result
        before, after = definitions(old_tree), definitions(new_tree)
        removed = sorted(before.keys() - after.keys())
        altered = [name for name in before.keys() & after.keys()
                   if ast.dump(before[name], include_attributes=False) != ast.dump(after[name], include_attributes=False)]
        assert not removed
        allowed = {'command_issues', 'PublicControlBoundaryTests.test_resume_requires_a_live_generation_newer_than_the_lost_generation'}
        assert set(altered) <= allowed, (path, altered)
        if altered and altered[0].startswith('PublicControlBoundaryTests'):
            name = altered[0]
            old_assertions = [ast.dump(n, include_attributes=False) for n in ast.walk(before[name])
                              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr.startswith('assert')]
            new_assertions = [ast.dump(n, include_attributes=False) for n in ast.walk(after[name])
                              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr.startswith('assert')]
            assert all(n in new_assertions for n in old_assertions)
        preservation[path] = {'old_definitions': len(before), 'removed': removed,
                              'altered': sorted(altered), 'added': sorted(after.keys() - before.keys())}
(HERE / 'changes-final.diff').write_text(''.join(diffs), encoding='utf-8')
save('assertion-preservation-final.json', {'baseline': baseline, 'baseline_sources': baseline_sources, 'files': preservation})

reports = {}
selected = None
prior_docs = load(RUN / 'phases/026/tasks/role-contract-names/evidence/reused-rows.json')[0]['rows']
prior_ids = {row['id'] for row in prior_docs}
assert len(prior_ids) == 33
for label, tree in [('c3', '.claude'), ('m2', '.agents')]:
    report = load(HERE / label / 'report.json')
    rows = [row for group in report['reports'] for row in group['rows']]
    ids = [row['id'] for row in rows]
    assert len(ids) == len(set(ids)) == len(report['selected'])
    assert set(ids) == set(report['selected'])
    assert all(row['outcome'] == 'passed' for row in rows)
    assert report['complete'] and report['successful'] and not report['changed_during_run']
    assert prior_ids <= set(ids)
    hashes = report['source_sha256']
    # Runner keys are paths relative to scripts.
    for path, digest in hashes.items():
        actual = REPO / tree / 'skills/do-math/scripts' / path
        assert hashlib.sha256(actual.read_bytes()).hexdigest() == digest, str(actual)
    if selected is None:
        selected = report['selected']
    else:
        assert set(selected) == set(report['selected'])
    process = load(HERE / ('final-' + label + '-process.json'))
    assert process['exit_code'] == 0 and process['state'] == 'finished'
    assert all(Path(p).name.startswith('.timings') for p in process['source_changes'])
    reports[label] = {'selected': len(ids), 'unique_rows': len(set(ids)), 'counts': report['counts'],
                      'exit_code': process['exit_code'], 'python_files': len(hashes),
                      'prior_doc_rows_retained': len(prior_ids), 'seconds': report['total_seconds']}

    raw = [json.loads(line) for line in (HERE / (label + '-returns.jsonl')).read_text(encoding='utf-8').splitlines()]
    default = {'id': 'review-policy-v5-default', 'minimum_initial_slots': 3, 'round_limit': 2,
               'activity_execution_limit': 17, 'judge_slots': ['judge-0', 'judge-1', 'judge-2'],
               'required_perspectives': [], 'overflow_disposition': 'unresolved'}
    from hashlib import sha256
    # Independently reproduce the contract's canonical object digest without
    # calling the policy builder or borrowing the stored hash as expectation.
    expected_hash = sha256((json.dumps(default, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()).hexdigest()
    default_rows = [r['value'] for r in raw if r['kind'] == 'load' and
                    r['test'].endswith('.test_default_review_policy_is_generated_from_current_config_and_saved')]
    observed_defaults = [v for v in default_rows if (v['review_policy'] or {}).get('id') == default['id']]
    assert observed_defaults
    for value in observed_defaults:
        assert value['config'] == {'reviewers': 3, 'review_rounds': 2}
        assert value['review_policy'] == default
        assert value['adoption']['review_policy_sha256'] == expected_hash
    assert any((r['review_policy'] or {}).get('id') == 'other-policy' for r in default_rows)
    explicit_rows = [r['value'] for r in raw if r['kind'] == 'load' and
                     r['test'].endswith('.test_explicit_review_policy_takes_precedence_over_default_adoption')
                     and (r['value']['review_policy'] or {}).get('id') == 'explicit-policy']
    assert explicit_rows
    for value in explicit_rows:
        policy = value['review_policy']
        assert policy == {'id': 'explicit-policy', 'minimum_initial_slots': 1, 'round_limit': 1,
                          'activity_execution_limit': 9, 'judge_slots': ['judge-a', 'judge-b', 'judge-c'],
                          'required_perspectives': ['domain'], 'overflow_disposition': 'defer'}
        assert value['adoption']['review_policy_sha256'] == sha256((json.dumps(policy, ensure_ascii=False,
               sort_keys=True, indent=2) + '\n').encode()).hexdigest()
    generations = {}
    for row in raw:
        if row['kind'] != 'load' or not row['test'].endswith('.test_resume_requires_a_live_generation_newer_than_the_lost_generation'):
            continue
        value = row['value']
        connection = value['conversations'].get('lease')
        if connection:
            generation = connection['generation']
            policy = 'pause' if generation in (1, 2) else 'continue_authorized'
            assert value['conversation_loss_policy'] == connection['disconnect_policy'] == policy
            generations.setdefault(generation, set()).add(connection['source_ref'])
    assert set(generations) == {1, 2, 3, 4}
    assert all(len(refs) == 1 for refs in generations.values())
    assert len(set().union(*generations.values())) == 4
    probes = [r for r in raw if r['kind'] == 'probe']
    outcomes = {}
    for row in probes:
        value = row['value']
        outcomes[value['outcome']] = outcomes.get(value['outcome'], 0) + 1
        if value['outcome'] == 'held':
            assert value == {'outcome': 'held'}
        elif value['outcome'] == 'observed':
            assert value['model_called'] is False
        elif value['outcome'] == 'recovery_required':
            assert 'model_called' not in value and value['error_type'] == 'SyntaxError' and value['error'] == 'engine broken'
        else:
            raise AssertionError(value)
    assert set(outcomes) == {'held', 'observed', 'recovery_required'}
    reports[label]['raw'] = {'returns': len(raw), 'default_stored_rows': len(observed_defaults),
                              'explicit_stored_rows': len(explicit_rows), 'generations': {k: sorted(v) for k,v in generations.items()},
                              'probe_outcomes': outcomes}

verification = {'source_files': len(end), 'changes': changed, 'outside_writes': [],
                'runtime_and_unlisted_sources_unchanged': True, 'reports': reports,
                'meaning_limit': 'Specified task checks only; G4/G5/G6/G7 final edition/G8 and L01 remain open.'}
save('verification-final.json', verification)
print(json.dumps(verification, ensure_ascii=False, indent=2))

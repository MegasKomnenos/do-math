"""Manager's read-only source/report/raw checks; output stays in manager evidence."""
import ast
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
T = RUN / 'phases/027/tasks/doc-policy'
E = T / 'evidence'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (O / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def snapshot():
    return {p.relative_to(R).as_posix(): sha(p)
            for base in ('.claude/skills', '.agents/skills', '.agents/diff')
            for p in sorted((R / base).rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def diff(a, b):
    return sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))

def definitions(data):
    result = {}
    for node in ast.parse(data).body:
        if isinstance(node, ast.FunctionDef): result[node.name] = node
        elif isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, ast.FunctionDef): result[node.name + '.' + method.name] = method
    return result

def main():
    check_args = [sys.executable, str(R / 'services/continuous-development/check.py'), 'report', str(R), str(RUN), '027', 'doc-policy']
    p = subprocess.run(check_args, capture_output=True, text=True, encoding='utf-8', cwd=R)
    save('report-check.json', dict(command=check_args, exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr))
    assert p.returncode == 0
    task_files = {p.relative_to(RUN).as_posix(): sha(p) for p in sorted(T.rglob('*')) if p.is_file()}
    save('task-files.json', task_files)
    for name in ('context.md', 'plan.md', 'seams.md'):
        dest = O / (name + '.before')
        if not dest.exists(): dest.write_bytes((RUN / name).read_bytes())
    current = snapshot()
    start, end = read(E / 'source-start.json'), read(E / 'source-end.json')
    assert start == read(RUN / 'phases/026/manager-evidence/source-inspected.json')
    assert current == end, diff(current, end)
    save('source-inspected.json', current)
    report = read(T / 'report.json')
    changes = diff(start, end)
    assert set(changes) == {r['path'] for r in report['changes']}
    writes = read(RUN / 'phases/027/phase.json')['tasks'][0]['writes']
    assert set(changes) <= set(writes)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R).decode().strip()
    preservation, all_diff = {}, []
    for path in changes:
        if not path.startswith('.claude/') or Path(path).name.startswith('.timings'): continue
        raw = subprocess.check_output(['git', 'show', head + ':' + path], cwd=R)
        candidates = [raw, raw.replace(b'\r\n', b'\n'), raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')]
        old = next((b for b in candidates if hashlib.sha256(b).hexdigest() == start[path]), None)
        source = 'Git HEAD, full start SHA checked'
        if old is None:
            with zipfile.ZipFile(RUN / 'phases/025/manager-evidence/raw-evidence.zip') as archive:
                old = archive.read(path)
            source = '025 raw-evidence archive, full start SHA checked'
        assert hashlib.sha256(old).hexdigest() == start[path], path
        new = (R / path).read_bytes()
        all_diff.extend(difflib.unified_diff(old.decode().splitlines(True), new.decode().splitlines(True), fromfile='start/' + path, tofile='end/' + path))
        if not path.endswith('.py'): continue
        a, b = definitions(old), definitions(new)
        assert not (a.keys() - b.keys())
        changed = sorted(k for k in a if ast.dump(a[k]) != ast.dump(b[k]))
        assert set(changed) <= {'command_issues', 'PublicControlBoundaryTests.test_resume_requires_a_live_generation_newer_than_the_lost_generation'}
        for k in changed:
            if not k.startswith('PublicControl'): continue
            assertions = lambda node: Counter(ast.dump(n) for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr.startswith('assert'))
            assert not (assertions(a[k]) - assertions(b[k]))
        preservation[path] = dict(source=source, old_definitions=len(a), changed=changed, added=sorted(b.keys() - a.keys()), removed=[])
    (O / 'verified-changes.diff').write_text(''.join(all_diff), encoding='utf-8')
    save('assertion-preservation.json', preservation)
    prior = read(RUN / 'phases/026/tasks/role-contract-names/evidence/reused-rows.json')[0]['rows']
    prior_ids = {row['id'] for row in prior}
    runs = {}
    for label, process_name, tree in [('f', 'focus', '.claude'), ('f2', 'corrected', '.claude'), ('c', 'final-c', '.claude'), ('c2', 'final-c2', '.claude'), ('m', 'final-m', '.agents'), ('c3', 'final-c3', '.claude'), ('m2', 'final-m2', '.agents')]:
        d = read(E / label / 'report.json')
        proc = read(E / (process_name + '-process.json'))
        before, after = read(E / (process_name + '-source-before.json')), read(E / (process_name + '-source-after.json'))
        rows = [row for group in d['reports'] for row in group['rows']]
        ids = [row['id'] for row in rows]
        assert len(ids) == len(set(ids)) == len(d['selected']) and set(ids) == set(d['selected'])
        assert d['complete'] and not d['changed_during_run']
        assert diff(before, after) == proc['source_changes']
        assert all(Path(k).name.startswith('.timings') for k in proc['source_changes'])
        for path, digest in d['source_sha256'].items():
            key = tree + '/skills/do-math/scripts/' + path
            assert before[key] == after[key] == digest
            if label in ('c3', 'm2'): assert current[key] == digest
        counts = dict(Counter(row['outcome'] for row in rows))
        assert counts == d['counts']
        assert proc['state'] == 'finished' and proc['exit_code'] == (0 if d['successful'] else 1)
        runs[label] = dict(selected=len(ids), counts=counts, exit_code=proc['exit_code'], source_files=len(d['source_sha256']), source_changes=proc['source_changes'], failed_ids=[row['id'] for row in rows if row['outcome'] != 'passed'])
        if label in ('c3', 'm2'):
            assert len(ids) == 134 and counts == {'passed': 134} and prior_ids <= set(ids)
    assert read(E / 'c3/report.json')['selected'] == read(E / 'm2/report.json')['selected']
    final_ids = set(read(E / 'c3/report.json')['selected'])
    assert set(runs['f']['failed_ids']) | set(runs['c']['failed_ids']) <= final_ids
    raw_checks = {}
    expected = dict(id='review-policy-v5-default', minimum_initial_slots=3, round_limit=2, activity_execution_limit=17, judge_slots=['judge-0', 'judge-1', 'judge-2'], required_perspectives=[], overflow_disposition='unresolved')
    explicit = dict(id='explicit-policy', minimum_initial_slots=1, round_limit=1, activity_execution_limit=9, judge_slots=['judge-a', 'judge-b', 'judge-c'], required_perspectives=['domain'], overflow_disposition='defer')
    digest = lambda x: hashlib.sha256((json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()).hexdigest()
    for label in ('c3', 'm2'):
        rows = [json.loads(line) for line in (E / (label + '-returns.jsonl')).read_text(encoding='utf-8').splitlines()]
        policies, generations, probes = Counter(), {}, Counter()
        for row in rows:
            v = row['value']
            if row['kind'] == 'load':
                if row['test'].endswith('.test_default_review_policy_is_generated_from_current_config_and_saved') and v['review_policy'] == expected:
                    assert v['config'] == {'reviewers': 3, 'review_rounds': 2}
                    assert v['adoption']['review_policy_sha256'] == digest(expected)
                    policies['default'] += 1
                if row['test'].endswith('.test_explicit_review_policy_takes_precedence_over_default_adoption') and v['review_policy']:
                    assert v['review_policy'] == explicit and v['adoption']['review_policy_sha256'] == digest(explicit)
                    policies['explicit'] += 1
                if row['test'].endswith('.test_resume_requires_a_live_generation_newer_than_the_lost_generation') and 'lease' in v['conversations']:
                    c = v['conversations']['lease']; gen = c['generation']
                    assert v['conversation_loss_policy'] == c['disconnect_policy'] == ('pause' if gen <= 2 else 'continue_authorized')
                    generations.setdefault(gen, set()).add(c['source_ref'])
            if row['kind'] == 'probe':
                probes[v['outcome']] += 1
                if v['outcome'] == 'held': assert v == {'outcome': 'held'}
                elif v['outcome'] == 'observed': assert v['model_called'] is False
                else: assert v['outcome'] == 'recovery_required' and 'model_called' not in v and (v['error_type'], v['error']) == ('SyntaxError', 'engine broken')
        assert policies == {'default': 7, 'explicit': 2}
        assert set(generations) == {1, 2, 3, 4} and all(len(v) == 1 for v in generations.values())
        assert len(set().union(*generations.values())) == 4
        assert probes == {'held': 2, 'observed': 1, 'recovery_required': 1}
        raw_checks[label] = dict(rows=len(rows), policies=dict(policies), generation_refs={k:sorted(v) for k,v in generations.items()}, probes=dict(probes))
    save('return-check.json', raw_checks)
    # Preserve and inspect the actual gate outputs instead of rerunning successful suites.
    gates = {}
    for label in ('mirror-check-final', 'skill-c', 'skill-m'):
        p = read(E / (label + '-process.json'))
        assert p['exit_code'] == 0 and not p['source_changes']
        gates[label] = dict(exit_code=p['exit_code'], stdout=(E / (label + '.stdout')).read_text(encoding='utf-8'))
    assert all(sha(RUN / path) == value for path,value in task_files.items())
    assert snapshot() == current
    save('verification.json', dict(head=head, source_files=len(current), source_mismatches=[], task_files=len(task_files), task_files_unchanged=True, changes=changes, noncache_changes=[p for p in changes if not Path(p).name.startswith('.timings')], outside_writes=[], runs=runs, prior_doc_rows=len(prior_ids), gates=gates, acceptance='A1-A5 accepted for the specified scope; final G gates and N01/L01 remain open.'))
    print(json.dumps(dict(source_files=len(current), task_files=len(task_files), changes=len(changes), runs=runs, raw=raw_checks), ensure_ascii=False, indent=2))

if __name__ == '__main__': main()

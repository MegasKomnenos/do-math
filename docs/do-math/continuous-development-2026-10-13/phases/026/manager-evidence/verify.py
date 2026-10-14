"""Read-only manager checks; writes only this manager's evidence."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
TASKS = ('policy-semantics', 'reference-names', 'role-contract-names')

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (O / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def ref(s):
    root, path = s.split(':', 1)
    return (R if root == 'repo' else RUN) / path.split('#')[0]

def task(id, name):
    return read(RUN / 'phases/026/tasks' / id / 'evidence' / name)

def snapshot():
    return {p.relative_to(R).as_posix(): sha(p)
            for base in ('.claude/skills', '.agents/skills', '.agents/diff')
            for p in sorted((R / base).rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def main():
    O.mkdir(exist_ok=True)
    checks = []
    for id in TASKS:
        args = [sys.executable, str(R / 'services/continuous-development/check.py'),
                'report', str(R), str(RUN), '026', id]
        p = subprocess.run(args, cwd=R, capture_output=True, text=True, encoding='utf-8')
        checks.append(dict(task=id, command=args, exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr))
        assert p.returncode == 0, checks[-1]
    save('report-check.json', checks)
    current = snapshot()
    baseline = read(RUN / 'phases/025/manager-evidence/source-inspected.json')
    assert current == baseline, [k for k in current.keys() | baseline.keys() if current.get(k) != baseline.get(k)]
    for id in TASKS:
        for name in ('source-start.json', 'source-end.json'):
            s = task(id, name)
            if id == 'policy-semantics': s = s['sources']
            if id == 'reference-names': s = s['sha256']
            assert s == current, (id, name)
    save('source-inspected.json', current)
    files = {p.relative_to(RUN).as_posix(): sha(p) for id in TASKS
             for p in sorted((RUN / 'phases/026/tasks' / id).rglob('*')) if p.is_file()}
    save('task-files.json', files)
    for name in ('context.md', 'plan.md', 'seams.md'):
        dest = O / (name + '.before')
        if not dest.exists(): dest.write_bytes((RUN / name).read_bytes())
    excerpts = task('policy-semantics', 'source-excerpts.json')
    for row in excerpts:
        p = ref(row['reference'])
        assert sha(p) == row['sha256']
        lines = p.read_text(encoding='utf-8-sig').splitlines()
        lo, hi = row['lines']
        assert row['text'] == '\n'.join(f'{i}: {lines[i-1]}' for i in range(lo, hi+1))
    profiles = task('role-contract-names', 'source-profiles.json')
    checked_profiles = 0
    def verify_objects(x):
        nonlocal checked_profiles
        if isinstance(x, dict):
            if 'path' in x and 'sha256' in x:
                p = ref(x['path'])
                assert sha(p) == x['sha256'], x['path']
                checked_profiles += 1
                if 'excerpt' in x:
                    lines = p.read_text(encoding='utf-8-sig').splitlines()
                    lo, hi = x['line'], x['end_line']
                    assert x['excerpt'] == '\n'.join(f'{i}: {lines[i-1]}' for i in range(lo, hi+1)), x['path']
            for v in x.values(): verify_objects(v)
        elif isinstance(x, list):
            for v in x: verify_objects(v)
    verify_objects(profiles)
    refs = task('reference-names', 'decisions.json')
    verify_objects(refs)
    for row in task('reference-names', 'occurrences.json'):
        lines = (R / row['path']).read_text(encoding='utf-8-sig').splitlines()
        if row['kind'] == 'fence':
            assert row['text'] in '\n'.join(lines[row['line']-1:row['end']]), row
        else:
            assert row['text'] in lines[row['line']-1], row
    roles = task('role-contract-names', 'decisions.json')
    for row in roles:
        lines = ref(row['document']).read_text(encoding='utf-8-sig').splitlines()
        for b in row['bindings']:
            for line in b['lines']:
                assert b['name'] in lines[line-1], (row['id'], b)
    packets = read(RUN / 'phases/001/tasks/document-closeout/evidence/followup-packets.json')['packets']
    for packet_id, decisions in [('N02', refs), ('N03', roles)]:
        packet = next(x for x in packets if x['id'] == packet_id)
        expected = {x['id'] if isinstance(x, dict) else x for x in packet['required_slices']}
        assert {x['id'] for x in decisions} == expected, packet_id
    raw_cache = {}
    def verify_rows(path, expected_sha, rows):
        p = ref(path)
        assert sha(p) == expected_sha, path
        raw = raw_cache.setdefault(path, read(p))
        for row in rows:
            actual = [v for group in raw['reports'] for v in group['rows'] if v['id'] == row['id']]
            assert actual == [row], (path, row['id'])
            assert row['id'] in raw['selected'] and row['outcome'] == 'passed'
        return raw
    historical = task('policy-semantics', 'historical-execution.json')
    for row in historical['rows']:
        verify_rows(row['report'], row['report_sha256'], [row['row']])
    for row in task('role-contract-names', 'reused-rows.json'):
        verify_rows(row['report'], row['sha256'], row['rows'])
    reused = task('reference-names', 'reused-rows.json')
    raw = verify_rows(reused['original'], reused['original_sha256'], reused['rows'])
    for path, digest in raw['source_sha256'].items():
        assert sha(R / '.claude/skills/do-math/scripts' / path) == digest, path
    assert not raw['changed_during_run']
    save('verification.json', dict(
        head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip(),
        source_count=len(current), source_changes=0, task_file_count=len(files),
        reports_checked=3, findings=10, policy_excerpts=len(excerpts), verified_source_records=checked_profiles,
        n02_slices=len(refs), n03_slices=len(roles), historical_policy_rows=len(historical['rows']),
        reused_doc_rows=len(reused['rows']), current_python_files=len(raw['source_sha256']),
        product_tests_rerun=False,
        scope='SHA/coordinates/original rows checked independently. Semantic dispositions are in review.md; no fresh product execution.'))
    assert files == {p.relative_to(RUN).as_posix(): sha(p) for id in TASKS
                     for p in sorted((RUN / 'phases/026/tasks' / id).rglob('*')) if p.is_file()}
    print(json.dumps(read(O / 'verification.json'), ensure_ascii=False))

if __name__ == '__main__':
    main()

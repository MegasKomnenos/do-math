"""Independent read-only source/evidence audit; no product imports or tests."""
import ast
import collections
import hashlib
import json
import subprocess
from pathlib import Path

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
TASKS = ('operator-names', 'cli-control-names', 'role-glossary-names')

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (O / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def ref(s):
    base, rel = s.split(':', 1)
    assert base in ('repo', 'run')
    return (R if base == 'repo' else RUN) / rel.split('#')[0]

def task(t, n):
    return read(RUN / 'phases/028/tasks' / t / 'evidence' / n)

def snapshot():
    return {p.relative_to(R).as_posix(): sha(p)
            for base in ('.claude/skills', '.agents/skills', '.agents/diff')
            for p in sorted((R / base).rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def main():
    current = snapshot()
    baseline = read(RUN / 'phases/027/manager-evidence/source-inspected.json')
    assert current == baseline, [k for k in current.keys() | baseline.keys() if current.get(k) != baseline.get(k)]
    save('source-inspected.json', current)
    artifacts = {p.relative_to(RUN).as_posix(): sha(p) for t in TASKS
                 for p in sorted((RUN / 'phases/028/tasks' / t).rglob('*')) if p.is_file()}
    if (O / 'task-files.json').exists():
        assert artifacts == read(O / 'task-files.json'), 'Task artifacts changed during manager review'
    else:
        save('task-files.json', artifacts)
    for n in ('context.md', 'plan.md', 'seams.md'):
        if not (O / (n + '.before')).exists():
            (O / (n + '.before')).write_bytes((RUN / n).read_bytes())
    assignments = read(RUN / 'phases/028/assignments.json')['tasks']
    sections = []
    occurrences = collections.Counter()
    summary = {}
    for t in TASKS:
        assert task(t, 'source-start.json') == current == task(t, 'source-end.json'), t
        decisions = task(t, 'section-decisions.json')
        expected = next(x for x in assignments if x['task'] == t)['slices']
        assert {x['id'] for x in decisions} == {x['id'] for x in expected}
        assert len(decisions) == len(expected)
        for x in decisions:
            p = ref(x['document'])
            lines = p.read_text(encoding='utf-8-sig').splitlines()
            lo, hi = x.get('current_lines', [x.get('current_start'), x.get('current_end')])
            assert 1 <= lo <= hi <= len(lines), x['id']
            if x['heading'] != '도입':
                assert lines[lo - 1].strip() == x['heading'], (x['id'], lines[lo - 1])
            if 'document_sha256' in x:
                assert sha(p) == x['document_sha256'], x['id']
            assert x['conclusion'] in ('유지', '기존 근거 재사용', '문구 수정', '검사 보강', '정확 미결')
            entries = x.get('inline_occurrences', x.get('occurrences', x.get('names', [])))
            for item in entries:
                value = item.get('text', item.get('surface', item.get('name')))
                for line in item.get('lines', [item.get('line')]):
                    assert lo <= line <= hi and value in lines[line - 1], (x['id'], item)
                    occurrences[t] += 1
            sections.append({'task': t, 'id': x['id'], 'document': x['document'], 'lines': [lo, hi],
                             'conclusion': x['conclusion'], 'reason': x.get('detail', x.get('reason'))})
        summary[t] = dict(sections=len(decisions), conclusions=dict(collections.Counter(x['conclusion'] for x in decisions)))
    assert len(sections) == 288 == len({x['id'] for x in sections})
    assert {x['id'] for x in sections} == {f'N01-{i:03d}' for i in range(1, 289)}
    for x in task('role-glossary-names', 'slice-map.json'):
        p = ref(x['document']); lines = p.read_text(encoding='utf-8-sig').splitlines()
        assert sha(p) == x['sha256']
        assert x['text'].rstrip('\n') == '\n'.join(lines[x['current_start']-1:x['current_end']]).rstrip('\n')
    verified = set()
    def profiles(x):
        if isinstance(x, dict):
            path = x.get('path', x.get('ref'))
            digest = x.get('file_sha256', x.get('sha256'))
            if isinstance(path, str) and path.startswith(('repo:', 'run:')) and digest:
                assert sha(ref(path)) == digest, path
                verified.add((path, digest))
            for key, value in x.items():
                if key.startswith(('repo:', 'run:')) and isinstance(value, dict) and 'sha256' in value:
                    assert sha(ref(key)) == value['sha256'], key
                    verified.add((key, value['sha256']))
                profiles(value)
        elif isinstance(x, list):
            for item in x: profiles(item)
    for t, names in {
        'operator-names': ['source-anchors.json', 'test-bindings.json', 'section-decisions.json'],
        'cli-control-names': ['owner-profiles.json'],
        'role-glossary-names': ['source-profiles.json', 'test-bindings.json']
    }.items():
        for n in names: profiles(task(t, n))
    report_path = RUN / 'phases/027/tasks/doc-policy/evidence/c3/report.json'
    raw = read(report_path)
    all_rows = [row for group in raw['reports'] for row in group['rows']]
    assert raw['complete'] and raw['successful'] and not raw['changed_during_run']
    assert set(raw['selected']) == {x['id'] for x in all_rows}
    assert len(all_rows) == len(raw['selected']) == len({x['id'] for x in all_rows}) == 134
    doc_rows = [x for x in all_rows if x['id'].startswith('structure.test_doc_code.')]
    assert len(doc_rows) == 38 and all(x['outcome'] == 'passed' for x in doc_rows)
    for path, digest in raw['source_sha256'].items():
        assert sha(R / '.claude/skills/do-math/scripts' / path) == digest, path
    assert len(raw['source_sha256']) == 875
    save('reused-report.json', {'ref': 'run:phases/027/tasks/doc-policy/evidence/c3/report.json',
                              'sha256': sha(report_path), 'selected': len(all_rows), 'document_rows': doc_rows,
                              'current_python_files': 875, 'new_execution': False})
    operator = task('operator-names', 'minimal-counterexamples.json')
    assert len(operator) == 4
    for row in operator: assert all(not x for x in row['counterexample_helper'].values())
    cli = task('cli-control-names', 'pure-observations.json')
    gaps = [x for x in cli['cases'] if 'replacement' in x]
    assert len(gaps) == 5
    for row in gaps: assert all(not x for x in row['observation'].values())
    role = task('role-glossary-names', 'schema-observations.json')
    assert len(role['counterexamples']) == 5
    assert 'enum' not in role['knowledge_kind']['actual_shape']
    save('sections-verified.json', sections)
    # Preserve decisive current source excerpts; these are static grounds, not new execution evidence.
    ranges = {
        '.claude/skills/do-math/references/초기화-운전.md': [(180, 180)],
        '.claude/skills/do-math/references/CLI-실행-계약.md': [(487, 487), (512, 514), (546, 546), (573, 573), (609, 609), (748, 748)],
        '.claude/skills/do-math/scripts/do_math/codex_adapter.py': [(92, 103), (235, 237)],
        '.claude/skills/do-math/scripts/do_math/claude_adapter.py': [(31, 31)],
        '.claude/skills/do-math/scripts/do_math/knowledge_io.py': [(136, 148), (249, 277)],
        '.claude/skills/do-math/scripts/do_math/knowledge.py': [(513, 565)],
        '.claude/skills/do-math/scripts/do_math/external.py': [(81, 115)],
        '.claude/skills/do-math/scripts/do_math/contracts.py': [(253, 259)],
        '.claude/skills/do-math/scripts/do_math/submission.py': [(816, 838)],
        '.claude/skills/do-math/scripts/setup_lean.py': [(208, 232)],
        '.claude/skills/do-math/scripts/probe_cli.py': [(114, 135)],
    }
    excerpts = []
    for path, spans in ranges.items():
        p = R / path; lines = p.read_text(encoding='utf-8-sig').splitlines()
        for lo, hi in spans:
            excerpts.append(dict(path='repo:' + path, sha256=sha(p), lines=[lo, hi],
                                 text='\n'.join(f'{i}: {lines[i-1]}' for i in range(lo, hi+1))))
    save('decisive-sources.json', excerpts)
    assert snapshot() == current
    assert artifacts == {p.relative_to(RUN).as_posix(): sha(p) for t in TASKS
                         for p in sorted((RUN / 'phases/028/tasks' / t).rglob('*')) if p.is_file()}
    result = dict(source_files=len(current), source_changed=0, task_files=len(artifacts), task_files_changed=0,
                  tasks=summary, sections=288, occurrence_coordinates=dict(occurrences),
                  verified_current_source_profiles=len(verified), prior_document_rows=38,
                  prior_python_sources=875, retained_helper_counterexamples=14, new_product_executions=0,
                  decisive_source_excerpts=len(excerpts), findings=9, followup_issues=8,
                  head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip())
    save('verification.json', result)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()

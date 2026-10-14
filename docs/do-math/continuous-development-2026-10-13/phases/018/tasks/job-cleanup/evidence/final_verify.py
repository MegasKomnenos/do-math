import collections
import hashlib
import sys
from pathlib import Path
from task_driver import E, REPO, RUN, read, sha, write
from verify_task import scripts, suite_verify, preservation

suite_verify('canonical','related','canonical-related')
suite_verify('mirror','related','mirror-related')
suite_verify('canonical','exact-job','canonical-exact-job')
suite_verify('canonical','full','canonical-t4-short')
suite_verify('mirror','full','mirror-t4-short')

summaries = {}
for label in ['canonical-related','mirror-related','canonical-exact-job','canonical-t4-short','mirror-t4-short']:
    result = read(E/(label+'-verification.json'))
    assert result['complete'] and result['successful'] and result['exit_code'] == 0
    assert result['counts'] == {'passed':result['selected']}
    assert not result['fixture_counts'] and not result['nonpassed']
    if 'adapter' in result:
        assert result['adapter']['complete'] and result['adapter']['tests_complete']
        assert not result['adapter']['problems']
    summaries[label] = result

old = RUN/'phases/017/tasks/t4-baseline-integration/evidence'
expected = read(E/'previous-evidence-start.json')
actual = {p.relative_to(old).as_posix():sha(p) for p in old.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert actual == expected
start = read(E/'source-start.json')
for p,h in read(E/'raw-reuse-basis.json')['unchanged_current_definitions'].items():
    assert sha(REPO/p) == h == start[p]

ids = {}
for output in ['canonical-t4-full','canonical-t4-full-final','c4']:
    d = read(old/output/'report.json')
    for group in d['reports']:
        for row in group['rows']:
            if not row.get('fixture') and row['outcome'] != 'passed':
                ids.setdefault(row['id'],[]).append({'prior_output':output,'outcome':row['outcome']})
maps = {}
for tree, output in [('canonical','c4'),('mirror','m4')]:
    d = read(E/output/'report.json')
    rows = {r['id']:r for g in d['reports'] for r in g['rows'] if not r.get('fixture')}
    maps[tree] = [{'id':key,'history':history,'current':rows[key]['outcome']} for key,history in sorted(ids.items())]
    assert all(r['current'] == 'passed' for r in maps[tree])
    exact = [r for key,r in rows.items() if 'test_exact_baseline_' in key]
    assert len(exact) == 2 and all(r['outcome'] == 'passed' for r in exact)
    worker = E/output/'boundary-isolated-021'
    request = read(worker/'worker-report.json')
    assert any('test_empty_installed_document_reports_incomplete_with_nonzero_exit' in s for s in request['requested'])

preservation()
write(E/'verification.json',{'suites':summaries,'017_nonpassed_to_current':maps,
    'previous_evidence_unchanged':{'files':len(actual),'excluded_components':['__pycache__']},
    'raw_companion_reuse':'Same current TestCase/WORKER/SNAPSHOT and measurement definitions; prior canonical raw only.',
    'path_preflight':read(E/'path-preflight.json'),
    'scope':'018 acceptance only; G4-G6/G8, remaining semantic/document/L01 and manager Git closeout stay open.'})
print('Final suites all passed; 017 previous nonpassed mappings',len(ids),'per tree; previous raw unchanged',len(actual))

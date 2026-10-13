"""Select historical JSON records and validate stable source hashes; no product import."""
import json
from pathlib import Path
from investigate import REPO, RUN, OUT, PREFIX, sha, write, git


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def walk(value, path=''):
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, path+'/'+key)
    elif isinstance(value, list):
        for n, item in enumerate(value):
            yield from walk(item, path+'/'+str(n))


prior = load(RUN/'phases/001/tasks/closure-map/evidence/prior-review-state.json')
pr01 = [(p,v) for p,v in walk(prior) if isinstance(v,dict) and v.get('id')=='PR01']
write('pr01-slice.json', pr01)
requirements = load(RUN/'phases/001/tasks/closure-map/evidence/requirement-state.json')
print('requirement top keys', list(requirements))
matches = [(p,v) for p,v in walk(requirements) if isinstance(v,dict) and
           any(str(v.get(k,'')) in {'P10','P11','P-10','P-11','10','11'} for k in ('id','obligation'))]
write('requirement-candidate-slices.json', matches)
print('requirement candidate selectors', [p for p,_ in matches])
board = load(REPO/'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json')
integration = board['current_work']['measurement_integration']
write('b56-original-record.json', integration)
print('B56 keys', list(integration))
for p,v in walk(integration):
    if isinstance(v,str) and any(s in v.lower() for s in ('p10','p11','provenance','baseline','report.json')):
        print(p, v)
stable = load(RUN/'phases/015/manager-evidence/source-inspected.json')
comparison = []
for rel in ['tests/boundary/test_shared_input_provenance.py','tests/support/branch_gate.py','tests/support/t3_store.py']:
    path = PREFIX+'/'+rel
    old = stable[path]
    current = sha((REPO/path).read_bytes())
    expected = old if isinstance(old,str) else old['sha256']
    comparison.append(dict(path=path, phase015=old, current_sha256=current, equal=current==expected))
    assert current==expected, path
write('stable-source-comparison.json', comparison)
v = load(RUN/'phases/015/manager-evidence/verification.json')
write('manager-verification-top-keys.json', list(v))
print('manager verification keys', list(v))
print('stable source comparisons', comparison)
fix='bbe64043f49d46fb7c3b6e768b99a8acbaa125cf'
for rel in ['docs/do-math/시험-재편-2026-09-29/진행.md',
            'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json']:
    git('fix-history-'+Path(rel).stem, 'show', fix, '--', rel)

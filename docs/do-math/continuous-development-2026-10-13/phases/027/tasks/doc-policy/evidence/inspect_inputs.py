import hashlib
import json
from work import REPO, RUN, HERE, save

assignment = json.loads((RUN / 'phases/027/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]
start = json.loads((HERE / 'source-start.json').read_text())
inputs = {}
for ref in assignment['inputs']:
    root, rel = ref.split(':', 1)
    path = (REPO if root == 'repo' else RUN) / rel
    raw = path.read_bytes()
    inputs[ref] = {'bytes': len(raw), 'sha256_current': hashlib.sha256(raw).hexdigest(),
                   'sha256_start': start.get(rel) if root == 'repo' else hashlib.sha256(raw).hexdigest()}
save('input-hashes.json', inputs)
profiles = json.loads((RUN / 'phases/026/tasks/role-contract-names/evidence/source-profiles.json').read_text(encoding='utf-8-sig'))
summaries = {}
for name, profile in profiles.items():
    summaries[name] = {'meaning': profile['meaning']}
    for kind in ('definitions', 'consumers', 'tests'):
        summaries[name][kind] = []
        for row in profile.get(kind, []):
            rel = row['path'].removeprefix('repo:')
            assert start[rel] == row['sha256'], row['path']
            summaries[name][kind].append({key: value for key, value in row.items() if key != 'excerpt'})
save('profile-source-verification.json', summaries)
bindings = json.loads((RUN / 'phases/026/tasks/policy-semantics/evidence/test-bindings.json').read_text(encoding='utf-8-sig'))
save('policy-test-bindings-read.json', bindings)
print(json.dumps({'input_files': len(inputs), 'profiles': {name: value['meaning'] for name, value in summaries.items()},
                  'policy_test_ids': {name: [r['id'] for r in values] for name, values in bindings.items()}},
                 ensure_ascii=False, indent=2))

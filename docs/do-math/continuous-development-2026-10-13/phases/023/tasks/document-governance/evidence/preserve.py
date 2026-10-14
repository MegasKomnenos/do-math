from work import *
start=json.loads((E/'start.json').read_text(encoding='utf-8-sig'))
current=snapshot('preservation-current')
previous=json.loads((RUN/'phases/022/tasks/review-delivery/evidence/preservation.json').read_text(encoding='utf-8-sig'))
inputs=previous['runtime_and_live_inputs']
assert all(start[p]==current[p] for p in inputs)
boundary=previous['fixed_runtime_and_t4_paths']
assert all(start[p]==current[p] for p in boundary)
tools={path:digest(Path(path))['sha256'] for path in previous['tools']}
assert tools==previous['tools']
host=previous['host_recordings']
for row in host: assert digest(RUN/row['path'])['sha256']==row['sha256']
baseline=json.loads((RUN/'phases/018/tasks/job-cleanup/evidence/final-baseline.json').read_text(encoding='utf-8-sig'))
base=Path(baseline['baseline'])
for row in baseline['files']:
    raw=(base/row['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==row['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
corpus=[]
for row in previous['corpus']:
    path=REPO/row['path']; raw=path.read_bytes()
    assert start[row['path']]==current[row['path']]
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    argv=['git','hash-object','--path='+row['path'],'--stdin']
    p=subprocess.run(argv,input=raw,cwd=REPO,capture_output=True)
    assert p.returncode==0 and p.stdout.decode().strip()==blob
    corpus.append({**row,'raw_git_blob':blob,'clean_git_blob':p.stdout.decode().strip(),'argv':argv,'exit_code':p.returncode})
for row in previous['explicit_sha']:
    assert digest(REPO/row['tree']/'skills/do-math/scripts/tests/corpus'/row['path'])['sha256']==row['sha256']
for row in corpus:
    if row['path'].startswith('.claude/'):
        assert current[row['path']]==current[row['path'].replace('.claude/','.agents/',1)]
assert (len(inputs),len(boundary),len(corpus),len(previous['explicit_sha']),len(host),len(tools),len(baseline['files']))==(139,258,144,150,8,5,910)
save('preservation.json',{**previous,'corpus':corpus,'runtime_changes':[],
    'fixed_runtime_and_t4_changes':[],'baseline_revision':'022 manager source-inspected and 023 start; review_cycle repair from 022 is the retained current baseline.',
    'runtime_sha256':{p:current[p]['sha256'] for p in inputs},'fixed_runtime_and_t4_sha256':{p:current[p]['sha256'] for p in boundary},
    'derived_artifact_impact':'Runtime and product documents remain byte-identical to 022. This task modifies only test/helper code and generated mirrors/cost caches. The 022 review_cycle change and its historical installation/prompt limitations still apply; this phase does not restore pre-022 whole-installation equivalence.',
    'reuse_scope':'Only the previously approved unchanged lower-boundary provider/worker/host/Lean/held-scheduler/scholarly properties are reused, with their recorded tools and inputs. No new paid/scheduled/scholarly calls, model document-reading certification, whole ordinary/fresh T3/mutation/final review or final-revision whole T4 claim.'})
print('Unchanged current runtime/live139 and fixed boundary258; corpus144/SHA150; host8/tools5; baseline910')

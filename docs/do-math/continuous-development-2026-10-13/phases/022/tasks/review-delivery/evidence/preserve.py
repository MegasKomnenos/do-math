from work import *
start=json.loads((E/'start.json').read_text(encoding='utf-8'))
current=snapshot('preservation-current')
previous=json.loads((RUN/'phases/021/tasks/document-review/evidence/preservation.json').read_text(encoding='utf-8-sig'))
inputs=previous['runtime_and_live_inputs']
runtime_changes=[p for p in inputs if start[p]!=current[p]]
allowed_runtime={'.claude/skills/do-math/scripts/do_math/review_cycle.py'}
assert set(runtime_changes)==allowed_runtime, runtime_changes
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
    path=REPO/row['path']
    assert start[row['path']]==current[row['path']]
    raw=path.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    argv=['git','hash-object','--path='+row['path'],'--stdin']
    p=subprocess.run(argv,input=raw,cwd=REPO,capture_output=True)
    assert p.returncode==0 and p.stdout.decode().strip()==blob
    corpus.append({**row,'raw_git_blob':blob,'clean_git_blob':p.stdout.decode().strip(),
                   'argv':argv,'exit_code':p.returncode})
for row in previous['explicit_sha']:
    assert digest(REPO/row['tree']/'skills/do-math/scripts/tests/corpus'/row['path'])['sha256']==row['sha256']
boundary=previous['fixed_runtime_and_t4_paths']
boundary_changes=[p for p in boundary if start[p]!=current[p]]
assert set(boundary_changes)=={p for p in current if p.endswith('/scripts/do_math/review_cycle.py')}
for row in corpus:
    if row['path'].startswith('.claude/'):
        assert current[row['path']]==current[row['path'].replace('.claude/','.agents/',1)]
assert len(inputs)==139 and len(boundary)==258 and len(corpus)==144 and len(previous['explicit_sha'])==150 and len(host)==8 and len(tools)==5 and len(baseline['files'])==910
save('preservation.json', {**previous,'tools':tools,'corpus':corpus,
    'runtime_changes':runtime_changes,'fixed_runtime_and_t4_changes':boundary_changes,
    'derived_artifact_impact': 'submission.install_tools includes review_cycle.py in submission-support.zip, so a newly installed archive/tool_sha256 changes. Historical archive byte equality and whole frozen scheduler installation equality are not claimed. The changed function is context_for: maintenance record reading, provider maintenance request construction, formal verification, held scheduling and scholarly list_sources do not invoke that identity-review rendering path. Current installed archive member/hash/command contracts are verified by the selected P03 packaging/preview/CLI tests; historical live claims are limited to the unchanged lower boundary behavior.',
    'reuse_scope':'review_cycle.context_for changed only the rendering of sealed proposal messages in identity-review history. ModelRunner/provider_final/worker/collector/real_ports, Windows Job, Lean, scheduler and scholarly paths and historical fixed smoke inputs/tools remain unchanged. Approved minimal live-boundary properties are reused only for those paths. Historical T4 results are not final-revision whole-product proof; the new exact review/packaging/restoration regressions replace the affected identity-review slice. Full general/fresh T3/extreme mutation/final review remain required. Product documents unchanged; future identity-review context/prompt bytes change through the runtime repair.'})
print('Preserved',len(inputs)-len(runtime_changes),'of',len(inputs),'live inputs; changed',runtime_changes)
print('Corpus',len(corpus),'explicit SHA',len(previous['explicit_sha']),'host',len(host),'tools',len(tools),'baseline',len(baseline['files']),'fixed boundary changes',boundary_changes)

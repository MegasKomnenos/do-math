from work import *
start=json.loads((E/'start.json').read_text(encoding='utf-8'))
current=snapshot('preservation-current')
previous=json.loads((RUN/'phases/018/tasks/job-cleanup/evidence/preservation.json').read_text(encoding='utf-8-sig'))
inputs=previous['runtime_and_live_inputs']
assert len(inputs)==139
assert all(start[p]==current[p] for p in inputs)
tools={path:digest(Path(path))['sha256'] for path in previous['tools']}
assert tools==previous['tools']
host=previous['host_recordings']
assert len(host)==8
for row in host:assert digest(RUN/row['path'])['sha256']==row['sha256']
baseline=json.loads((RUN/'phases/018/tasks/job-cleanup/evidence/final-baseline.json').read_text(encoding='utf-8-sig'))
base=Path(baseline['baseline'])
assert len(baseline['files'])==910
for row in baseline['files']:
    raw=(base/row['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==row['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
corpus=[]
explicit=[]
for tree in ('.claude','.agents'):
    root=REPO/tree/'skills/do-math/scripts/tests/corpus'
    for p in sorted(root.rglob('*')):
        if p.is_file():
            rel=p.relative_to(REPO).as_posix()
            assert start[rel]==current[rel]
            raw=p.read_bytes()
            blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            argv=['git','hash-object','--path='+rel,'--stdin']
            got=subprocess.run(argv,input=raw,cwd=REPO,capture_output=True)
            assert got.returncode==0 and got.stdout.decode().strip()==blob
            corpus.append({'path':rel,'sha256':hashlib.sha256(raw).hexdigest(),'raw_git_blob':blob,
                           'clean_git_blob':got.stdout.decode().strip(),'argv':argv,'exit_code':got.returncode})
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8-sig'))
    for entry in manifest['entries']:
        refs=[]
        for digest_key,path_key in [('source_sha256','path'),('schema_sha256','schema_path'),('transport_schema_sha256','transport_schema_path')]:
            if digest_key in entry: refs.append((digest_key,entry[path_key],entry[digest_key]))
        refs += [('recordings/'+str(i),row['path'],row['sha256']) for i,row in enumerate(entry.get('recordings',[]))]
        for selector,path,sha in refs:
            assert digest(root/path)['sha256']==sha
            explicit.append({'tree':tree,'entry':entry['id'],'selector':selector,'path':path,'sha256':sha})
assert len(corpus)==144 and len(explicit)==150
for row in corpus:
    if row['path'].startswith('.claude/'):
        peer=row['path'].replace('.claude/','.agents/',1)
        assert current[row['path']]==current[peer]
boundary_paths=[p for p in start if '/scripts/do_math/' in p or p.endswith(('/scripts/run_tests.py','/scripts/test_categories.py','/scripts/tests/support/adapter_coverage.py','/scripts/tests/support/port_contracts/jobs.py','/scripts/tests/boundary/test_port_jobs.py'))]
assert all(start[p]==current[p] for p in boundary_paths)
save('preservation.json',{'runtime_and_live_inputs':inputs,'host_recordings':host,'tools':tools,
    'baseline_files':910,'baseline_commit':baseline['commit'],'baseline_source':str(base),
    'corpus':corpus,'explicit_sha':explicit,'fixed_runtime_and_t4_paths':boundary_paths,
    'reuse_scope':'Previously approved live properties only, same input/tool bytes. Document wording changes future role prompts, not historical smoke inputs or corpus. No new live calls, final general/T3/mutation/review remain required.'})
print('Preserved runtime/live',len(inputs),'host',len(host),'tools',len(tools),'baseline',len(baseline['files']),'corpus',len(corpus),'explicit SHA',len(explicit),'runtime/T4 paths',len(boundary_paths))

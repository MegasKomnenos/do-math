from work import *
v=json.loads((E/'verification.json').read_text())
final=json.loads((E/'final.json').read_text())
preserved=json.loads((E/'preservation-current.json').read_text())
diff=[p for p in set(final)|set(preserved) if final.get(p)!=preserved.get(p)]
assert all(Path(p).name in ('.timings.json','.timings-t3.json') for p in diff),diff
actual=json.loads((E/'proposal-return-14.json').read_text())['context']['role_review']
a,b=actual['proposal'],actual['self_messages'][0]['content']
assert a==b
raw=json.dumps(a,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')
assert raw==json.dumps(b,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')
argv=['git','diff','--check','--',*v['changes']]
proc=subprocess.run(argv,cwd=REPO,capture_output=True)
(E/'diff-whitespace.stdout').write_bytes(proc.stdout)
(E/'diff-whitespace.stderr').write_bytes(proc.stderr)
assert proc.returncode==0,proc.stdout.decode('utf-8',errors='replace')
save('final-inspection.json',{'preservation_noncache_equal_final':True,'cache_differences':diff,
 'duplicate_complete_map_equal':True,'duplicate_canonical_bytes':len(raw),
 'duplicate_canonical_sha256':hashlib.sha256(raw).hexdigest(),'expected_copies':1,'observed_copies':2,
 'duplicate_paths':['context.role_review.proposal','context.role_review.self_messages[0].content'],
 'exact_diff_whitespace_argv':argv,'exact_diff_whitespace_exit':proc.returncode,
 'final_counts':{k:v['suites'][k]['counts'] for k in ('c','m')},'changes':len(v['changes'])})
print('Final immutable paths match preservation; exact diff clean; duplicated maps equal; changes',len(v['changes']))

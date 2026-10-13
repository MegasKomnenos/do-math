"""Preserve exact evidence, validate and publish handoff, then commit only this unit."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import zipfile

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; T=RUN/'phases/014/tasks/scholarly-smoke'; E=T/'evidence'
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v): (O/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def cmd(name,args,allowed=(0,)):
    p=subprocess.run(args,cwd=R,capture_output=True)
    result={'argv':args,'cwd':str(R),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')}
    save(name,result)
    assert p.returncode in allowed,(name,p.returncode,result['stderr'])
    return result
head=git('rev-parse','HEAD').decode().strip()
assert head==read(O/'verification.json')['head'] and not git('diff','--cached','--name-only','-z')
source=read(O/'source-inspected.json'); assert all(sha(R/p)==h for p,h in source.items())
products={r['path'] for r in read(T/'report.json')['changes'] if not r['path'].endswith('/.timings.json')}
assert len(products)==32
# The unchanged G section stays the same as the previous manager's committed input.
old=git('show','HEAD:docs/do-math/continuous-development-2026-10-13/context.md').decode('utf-8-sig').replace('\r\n','\n')
current=(RUN/'context.md').read_text(encoding='utf-8')
assert old.split('## C2 ')[0]==current.split('## C2 ')[0]
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0564.md'
archived={p for p in T.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
archived.update(R/p for p in products)
entries={}; archive=O/'raw-evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(archived):
        raw=p.read_bytes(); rel=p.relative_to(R).as_posix()
        z.writestr(rel,raw); entries[rel]=hashlib.sha256(raw).hexdigest()
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(entries)
    assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in entries.items())
paths={R/p for p in products}
paths.update(RUN/p for p in ('context.md','plan.md','seams.md','phases/014/manager.json','phases/015/phase.json','phases/015/tasks/t4-adapter-report/objective.md'))
paths.update({R/'기억/layer1/M-0564.md',R/'기억/색인.md',T/'report.json'})
for name in ('verify.py','prepare.py','finalize.py','verification.json','source-inspected.json','corpus-final.json','history-check.json','report-check.json','mirror-check.json','review.md','common-docs.diff','preservation.json','raw-evidence.zip'):
    paths.add(O/name)
# Root task outputs and official suite reports are direct tracked entry points.
# Repeated scratch/bootstrap files are preserved once inside the archive.
paths.update(p for p in E.iterdir() if p.is_file() and not p.name.endswith('.started.json') and p.name not in ('write_report.py',))
for name in ('live-01','live-02','live-final','canonical-related','mirror-related','canonical-final','mirror-final'):
    paths.add(E/name/'report.json')
relative=sorted(p.relative_to(R).as_posix() for p in paths)
save('preservation.json',{'archive':archive.relative_to(R).as_posix(),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'entries':entries,'products':sorted(products),'product_count':len(products),'tracked_paths':relative,'raw_bytes':'All task originals are untouched and archived with SHA256. Selected evidence, report, manager and corpus index blobs must equal raw working bytes. Product source text retains existing LF attributes; its raw bytes are also archived.','local_only':'Unselected scratch/bootstrap and repeated raw command files remain local at original paths; their bytes are tracked in raw-evidence.zip. Stage/commit receipts and process/session logs remain local and may be removed by later cleanup. Archive is not a restoration instruction.','whitespace_policy':'Run ordinary staged diff --check. If only preserved raw corpus CRLF/JSON indentation is flagged, verify every warned line has no spaces/tabs before CRLF and run the unmodified check for all other paths; keep audit receipts locally. Do not rewrite corpus or attributes to silence warnings.','scope':'No timing caches, old untracked files, engine, other operator changes or unrelated memories are staged.'})
pending=RUN/'phases/014/manager.pending.json'; published=RUN/'phases/014/manager.json'
assert pending.exists() and not published.exists()
hashes={p:sha(R/p) for p in relative if not p.endswith('/manager.json')}
save('commit-plan.json',{'head':head,'paths':relative,'sha256':hashes,'products':len(products)})
(O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
cmd('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
cmd('handoff-check.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'014'])
assert all(sha(R/p)==h for p,h in hashes.items())
pending_hash=sha(pending); pending.rename(published); assert sha(published)==pending_hash
print('PASS memory/handoff 014; manager.json published. Staging exact reviewed paths.',flush=True)
assert git('rev-parse','HEAD').decode().strip()==head and not git('diff','--cached','--name-only','-z')
cmd('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
staged_paths=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
assert staged_paths==set(relative),(staged_paths-set(relative),set(relative)-staged_paths)
whitespace=cmd('staged-diff-check.json',['git','-c','core.quotePath=false','diff','--cached','--check'],allowed=(0,2))
if whitespace['exit_code']:
    headers=[]
    for line in whitespace['stdout'].splitlines():
        m=re.fullmatch(r'(.+):(\d+): (trailing whitespace(?:, indent with spaces)?\.|indent with spaces\.)',line)
        if m: headers.append(m.groups())
    assert headers and all('/scripts/tests/corpus/' in p and p in products for p,_,_ in headers)
    warned={p for p,_,_ in headers}
    for p,n,kind in headers:
        raw=git('show',':'+p); assert raw==(R/p).read_bytes()
        line=raw.splitlines(keepends=True)[int(n)-1]
        assert line.endswith(b'\r\n') and line[:-2]==line[:-2].rstrip(b' \t'),(p,n,kind)
        if 'indent' in kind:
            indent=line[:-2][:len(line[:-2])-len(line[:-2].lstrip(b' '))]
            assert len(indent)%2==0 and b'\t' not in indent
    cmd('noncorpus-diff-check.json',['git','diff','--cached','--check','--','.']+[':(exclude)'+p for p in sorted(warned)])
    save('stage-whitespace-audit.json',{'result':'accepted_raw_format','warning_count':len(headers),'paths':sorted(warned),'reason':'All warned lines are preserved raw corpus CRLF / even-space JSON indentation, with no trailing spaces or tabs before CRLF. Index bytes equal verified raw files. Every other staged path passes ordinary diff --check. No file or attribute changed.'})
staged={}
for p in relative:
    raw=(R/p).read_bytes(); received=git('show',':'+p); blob=git('rev-parse',':'+p).decode().strip()
    clean=subprocess.check_output(['git','hash-object','--path='+p,'--stdin'],cwd=R,input=raw).decode().strip()
    assert clean==blob,p
    if '/evidence/' in p or '/manager-evidence/' in p or '/tests/corpus/' in p or p.endswith(('/report.json','/manager.json')): assert received==raw,p
    if p in products: assert received.replace(b'\r\n',b'\n')==raw.replace(b'\r\n',b'\n'),p
    staged[p]={'sha256':hashlib.sha256(raw).hexdigest(),'blob':blob,'raw_equals_blob':received==raw}
save('stage.json',{'head':head,'exact_count':len(relative),'product_count':len(products),'paths':staged})
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
assert all(sha(R/p)==v['sha256'] for p,v in staged.items())
assert all(sha(R/p)==h for p,h in source.items())
assert [p for p in relative if p.startswith('기억/layer1/')]==['기억/layer1/M-0564.md']
cmd('pre-commit-status.json',['git','status','--short','--untracked-files=no'])
(O/'commit-message.txt').write_text('학술 완료 응답을 검수하고 T4 분기 보고를 배정함\n',encoding='utf-8')
cmd('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
assert committed==set(relative)
assert all(git('rev-parse',newhead+':'+p).decode().strip()==v['blob'] for p,v in staged.items())
assert all(sha(R/p)==v['sha256'] for p,v in staged.items()) and all(sha(R/p)==h for p,h in source.items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(relative),'products':len(products),'source_raw_bytes_unchanged':True,'index_empty':True,'manager_sha256':pending_hash,'next':'015','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(relative),'products':len(products),'handoff':'PASS 014','next':'015'},ensure_ascii=False))

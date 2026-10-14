"""Preserve originals, validate the handoff, then publish and commit exact paths."""
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; P=RUN/'phases/022'; T=P/'tasks/review-delivery'; E=T/'evidence'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def command(n,args):
    p=subprocess.run(args,cwd=R,capture_output=True)
    v=dict(argv=args,cwd=str(R),exit_code=p.returncode,stdout=p.stdout.decode('utf-8',errors='replace'),stderr=p.stderr.decode('utf-8',errors='replace'))
    save(n,v); assert p.returncode==0,v
    return v

head=read(O/'verification.json')['head']
sources=read(O/'source-inspected.json'); task_hashes=read(O/'task-files.json'); products=read(O/'product-paths.json')
assert len(products)==36
def unchanged():
    assert git('rev-parse','HEAD').decode().strip()==head
    assert all(sha(R/p)==h for p,h in sources.items())
    assert task_hashes=={p.relative_to(T).as_posix():sha(p) for p in T.rglob('*') if p.is_file()}
    assert all(sha(RUN/n)==h for n,h in read(O/'common-after-sha.json').items())
    assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0572.md'
    assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')

mode=sys.argv[1]
if mode=='prepare':
    unchanged()
    assert not git('diff','--cached','--name-only','-z')
    dirty=set(filter(None,git('diff','--name-only','-z','--','.claude/skills/do-math','.agents/skills/do-math').decode().split('\0')))
    assert dirty==set(products)
    sections=read(E/'current-sections.json'); decisions=read(E/'section-name-decisions.json')
    assert len(decisions)==247
    for section in sections:
        assert section['body'] in (R/section['path']).read_text(encoding='utf-8')
        expected=set(section['tokens'])
        actual=[row['token'] for row in decisions if row['section']==section['id']]
        assert len(actual)==len(set(actual)) and set(actual)==expected
        for row in (r for r in decisions if r['section']==section['id']):
            assert all(sentence in section['body'] for sentence in row['sentences'])
    save('section-check.json',dict(counts=dict(Counter(r['section'] for r in decisions)),current_text_equal=True,
        interpretation='Name ownership and recorded exclusions only; F5 semantics remain assigned to 023 and later work.'))
    archive=O/'raw-evidence.zip'; assert not archive.exists()
    archived={p for p in T.rglob('*') if p.is_file()} | {R/p for p in products}
    entries={}
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in sorted(archived):
            raw=path.read_bytes(); rel=path.relative_to(R).as_posix()
            z.writestr(rel,raw); entries[rel]=hashlib.sha256(raw).hexdigest()
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())==set(entries)
        assert all(hashlib.sha256(z.read(path)).hexdigest()==digest for path,digest in entries.items())
    paths={R/p for p in products}
    paths.update(RUN/n for n in ('context.md','plan.md','seams.md','phases/022/manager.json',
        'phases/023/phase.json','phases/023/tasks/document-governance/objective.md'))
    paths.update({R/'기억/layer1/M-0572.md',R/'기억/색인.md',T/'report.json'})
    paths.update(O/n for n in ('verify.py','prepare.py','finalize.py','verification.json','source-inspected.json',
        'report-check.json','review.md','common-docs.diff','common-before-sha.json','common-after-sha.json',
        'task-files.json','history-check.json','proposal-check.json','failure-mapping.json','product-paths.json',
        'section-check.json','preservation.json','raw-evidence.zip'))
    paths.update(path for path in E.iterdir() if path.is_file()
        and not path.name.endswith(('-before.json','-after.json'))
        and not path.name.startswith(('c-return-','m-return-'))
        and path.name not in ('preservation-current.json','diff-current.json'))
    paths.update(E/n/'report.json' for n in ('red','red-doc','focus','corrected','c','m'))
    relative=sorted(p.relative_to(R).as_posix() for p in paths)
    save('preservation.json',dict(archive=archive.relative_to(R).as_posix(),archive_sha256=sha(archive),
        archive_bytes=archive.stat().st_size,entries=entries,products_committed=products,product_count=36,
        task_files=len(task_hashes),tracked_paths=relative,
        raw_bytes='Original 355 task files and the final 36 product paths are archived and independently read back with SHA256. All original report/evidence bytes remain unchanged. Historical 021 bytes stay in its existing archive.',
        local_only='Unselected return files, repeated snapshots and scratch stay local at their original paths; their exact bytes are preserved in this tracked archive. Stage/commit receipts and session logs remain local and may disappear during cleanup. Archive is not a restoration instruction.',
        scope='Reviewed 021/022 product union, management handoff, selected originals, 023 assignment and one memory node. Unrelated dirty/untracked files, engine and operator changes are excluded.'))
    pending=P/'manager.pending.json'; published=P/'manager.json'
    assert pending.exists() and not published.exists()
    hashes={p:sha(R/p) for p in relative if p!=published.relative_to(R).as_posix()}
    save('commit-plan.json',dict(head=head,paths=relative,sha256=hashes,products=36,pending_sha256=sha(pending)))
    (O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
    command('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
    command('worktree-diff-check.json',['git','diff','--check','--',*products,
        'docs/do-math/continuous-development-2026-10-13/context.md',
        'docs/do-math/continuous-development-2026-10-13/plan.md',
        'docs/do-math/continuous-development-2026-10-13/seams.md','기억/색인.md'])
    command('handoff-check.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'022'])
    unchanged()
    assert all(sha(R/p)==h for p,h in hashes.items()) and sha(pending)==read(O/'commit-plan.json')['pending_sha256']
    print(json.dumps(dict(archive_entries=len(entries),archive_bytes=archive.stat().st_size,
        planned_paths=len(relative),products=36,memory='PASS',handoff='PASS 022',next='023'),ensure_ascii=False))
elif mode=='publish':
    unchanged()
    plan=read(O/'commit-plan.json'); relative=plan['paths']; hashes=plan['sha256']
    assert not git('diff','--cached','--name-only','-z')
    assert read(O/'memory-check.json')['exit_code']==read(O/'handoff-check.json')['exit_code']==0
    assert all(sha(R/p)==h for p,h in hashes.items())
    pending=P/'manager.pending.json'; published=P/'manager.json'
    assert pending.exists() and not published.exists() and sha(pending)==plan['pending_sha256']
    pending.rename(published)
    assert sha(published)==plan['pending_sha256']
    print('Published checked manager.json; next 023.',flush=True)
    command('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
    staged=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
    assert staged and staged<=set(relative) and set(products)<=staged
    assert [p for p in staged if p.startswith('기억/layer1/')]==['기억/layer1/M-0572.md']
    command('staged-diff-check.json',['git','diff','--cached','--check'])
    data=subprocess.check_output(['git','cat-file','--batch'],cwd=R,input=('\n'.join(':'+p for p in relative)+'\n').encode('utf-8'))
    stream=io.BytesIO(data); received={}
    for path in relative:
        oid,kind,size=stream.readline().decode().split(); assert kind=='blob'
        blob=stream.read(int(size)); assert stream.read(1)==b'\n'
        raw=(R/path).read_bytes()
        if '/evidence/' in path or '/manager-evidence/' in path or path.endswith(('/report.json','/manager.json')):
            assert blob==raw,path
        else:
            assert blob==raw or blob==raw.replace(b'\r\n',b'\n'),path
        received[path]=dict(blob=oid,sha256=sha(R/path),raw_equals_blob=blob==raw)
    assert not stream.read()
    save('stage.json',dict(head=head,planned_count=len(relative),staged_count=len(staged),products=36,paths=received,changed_paths=sorted(staged)))
    unchanged()
    assert all(sha(R/p)==v['sha256'] for p,v in received.items())
    assert staged==set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
    command('pre-commit-status.json',['git','status','--short','--untracked-files=no'])
    (O/'commit-message.txt').write_text('검토 제안 단일 지급과 제출 문서 결속을 검수하고 수입·현재 조회 작업을 묶어 배정함\n',encoding='utf-8')
    command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
    newhead=git('rev-parse','HEAD').decode().strip()
    committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
    assert committed==staged
    blobs={row.split(b'\t',1)[1].decode('utf-8'):row.split(b'\t',1)[0].decode().split()[2]
        for row in git('ls-tree','-r','-z',newhead).split(b'\0') if row}
    assert all(blobs[p]==v['blob'] for p,v in received.items())
    assert all(sha(R/p)==v['sha256'] for p,v in received.items())
    assert all(sha(R/p)==h for p,h in sources.items())
    assert all(sha(T/p)==h for p,h in task_hashes.items())
    assert not git('diff','--cached','--name-only','-z')
    save('post-commit.json',dict(head=newhead,parent=head,committed_count=len(committed),products_committed=36,
        source_raw_bytes_unchanged=True,task_raw_bytes_preserved=True,index_empty=True,
        manager_sha256=plan['pending_sha256'],next='023',push_performed=False))
    print(json.dumps(dict(head=newhead,committed=len(committed),products=36,handoff='PASS 022',next='023'),ensure_ascii=False))
else:
    raise ValueError(mode)

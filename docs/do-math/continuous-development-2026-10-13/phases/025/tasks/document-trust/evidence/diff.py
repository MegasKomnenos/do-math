from work import *
import difflib, zipfile
start=json.loads((E/'start.json').read_text())
now=snapshot('diff-current')
manager=json.loads((RUN/'phases/024/manager-evidence/preservation.json').read_text(encoding='utf-8-sig'))
changes=[p for p in start if start[p]!=now[p] and Path(p).name not in ('.timings.json','.timings-t3.json')]
sources=[]; diffs=[]
with zipfile.ZipFile(REPO/manager['archive']) as z:
    members=set(z.namelist())
    for relative in changes:
        candidates=[]
        if relative in members:
            candidates.append(('024 archive',z.read(relative)))
        p=subprocess.run(['git','show','HEAD:'+relative],cwd=REPO,capture_output=True)
        if p.returncode==0:
            candidates.append(('current HEAD Git blob',p.stdout))
            candidates.append(('current HEAD LF to CRLF',p.stdout.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')))
        match=next(((origin,raw) for origin,raw in candidates if hashlib.sha256(raw).hexdigest()==start[relative]['sha256']),None)
        assert match is not None,relative
        origin,raw=match
        sources.append({'path':relative,'origin':origin,'verified_start_sha256':start[relative]['sha256']})
        diffs.extend(difflib.unified_diff(raw.decode('utf-8').splitlines(keepends=True),
            (REPO/relative).read_bytes().decode('utf-8').splitlines(keepends=True),
            fromfile=relative+' (start)',tofile=relative+' (final)'))
(E/'changes.diff').write_text(''.join(diffs),encoding='utf-8')
save('diff-sources.json',sources)
head=subprocess.run(['git','rev-parse','HEAD'],cwd=REPO,capture_output=True)
index=subprocess.run(['git','diff','--cached','--no-ext-diff'],cwd=REPO,capture_output=True)
status=subprocess.run(['git','status','--porcelain=v1'],cwd=REPO,capture_output=True)
(E/'git-end-head.stdout').write_bytes(head.stdout)
(E/'git-end-index.stdout').write_bytes(index.stdout)
(E/'git-end-status.stdout').write_bytes(status.stdout)
assert head.returncode==index.returncode==status.returncode==0
assert head.stdout==(E/'git-head.stdout').read_bytes()
assert index.stdout==(E/'git-index.stdout').read_bytes()
save('git-preservation.json',{'head_unchanged':True,'index_diff_unchanged':True,
    'scope':'Initial skills/diff SHA comparison and final exact delta preserve prior dirty bytes; HEAD and staged diff remain unchanged. New task evidence/status entries are expected.'})
print('Exact raw start/final diff verified for',len(changes),'noncache files; HEAD/index unchanged')

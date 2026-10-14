from work import *
import difflib,zipfile
start=json.loads((E/'start.json').read_text(encoding='utf-8'))
current=snapshot('final')
changes=sorted(p for p in set(start)|set(current) if start.get(p)!=current.get(p))
meta=json.loads((RUN/'phases/023/manager-evidence/preservation.json').read_text(encoding='utf-8'))
rows=[]; diffs=[]
with zipfile.ZipFile(REPO/meta['archive']) as archive:
    for path in changes:
        if Path(path).name=='.timings.json':continue
        if path in archive.namelist():
            before=archive.read(path); source=meta['archive']+':'+path
        else:
            argv=['git','show','HEAD:'+path]
            p=subprocess.run(argv,cwd=REPO,capture_output=True); assert p.returncode==0
            before=p.stdout; source='HEAD:'+path
        if hashlib.sha256(before).hexdigest()!=start[path]['sha256']:
            # Git stores clean LF bytes; require a reconstructed CRLF working
            # copy to match the actual start SHA before using it as the baseline.
            crlf=before.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
            assert hashlib.sha256(crlf).hexdigest()==start[path]['sha256'],path
            before=crlf; source+=' (CRLF worktree bytes verified against start SHA)'
        after=(REPO/path).read_bytes()
        diffs.extend(difflib.unified_diff(before.decode('utf-8').splitlines(keepends=True),
            after.decode('utf-8').splitlines(keepends=True),fromfile='start/'+path,tofile='final/'+path))
        rows.append({'path':path,'baseline_source':source,'before_sha256':start[path]['sha256'],
                     'after_sha256':current[path]['sha256']})
(E/'changes.diff').write_text(''.join(diffs),encoding='utf-8')
save('diff-coordinates.json',rows)
print('Exact start/final diff',len(rows),'non-cache paths')

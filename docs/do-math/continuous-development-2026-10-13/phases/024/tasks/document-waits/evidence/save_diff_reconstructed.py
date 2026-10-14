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
            if hashlib.sha256(crlf).hexdigest()==start[path]['sha256']:
                before=crlf; source+=' (CRLF worktree bytes verified against start SHA)'
            elif Path(path).suffix=='.md':
                packet=next(p for p in json.loads((E/'followup-packets-input.json').read_text(encoding='utf-8'))['packets']
                    if p['id']==('P09' if path.endswith('과제-착수조건.md') else 'P11'))
                old=packet['original_document_locations'][0]['text']
                text=(REPO/path).read_text(encoding='utf-8')
                prefix='| `decision_value_is` |' if packet['id']=='P09' else '- 계획과 착수:'
                line=next(line for line in text.splitlines() if line.startswith(prefix))
                reconstructed=text.replace(line,old).encode('utf-8')
                candidates=[reconstructed,reconstructed.replace(b'\n',b'\r\n')]
                before=next((raw for raw in candidates if hashlib.sha256(raw).hexdigest()==start[path]['sha256']),None)
                assert before is not None,path
                source='Unchanged historical packet sentence + final surrounding bytes, verified exactly against actual start SHA'
            else:
                candidates=[]
                for phase in range(8,24):
                    zpath=RUN/f'phases/{phase:03d}/manager-evidence/raw-evidence.zip'
                    if not zpath.is_file():continue
                    with zipfile.ZipFile(zpath) as z:
                        if path in z.namelist():
                            raw=z.read(path)
                            if hashlib.sha256(raw).hexdigest()==start[path]['sha256']:
                                candidates.append((raw,str(zpath)+':'+path))
                assert candidates,path
                before,source=candidates[-1]
        after=(REPO/path).read_bytes()
        diffs.extend(difflib.unified_diff(before.decode('utf-8').splitlines(keepends=True),
            after.decode('utf-8').splitlines(keepends=True),fromfile='start/'+path,tofile='final/'+path))
        rows.append({'path':path,'baseline_source':source,'before_sha256':start[path]['sha256'],
                     'after_sha256':current[path]['sha256']})
(E/'changes.diff').write_text(''.join(diffs),encoding='utf-8')
save('diff-coordinates.json',rows)
print('Exact start/final diff',len(rows),'non-cache paths')

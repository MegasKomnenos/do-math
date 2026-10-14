from work import *
import zipfile, difflib
start=json.loads((E/'start.json').read_text(encoding='utf-8'))
current=snapshot('diff-current')
changes=sorted(p for p in set(start)|set(current) if start.get(p)!=current.get(p))
zip_path=RUN/'phases/021/manager-evidence/raw-evidence.zip'
archive=zipfile.ZipFile(zip_path)
blocks=[]
coordinates=[]
for path in changes:
    if Path(path).name in ('.timings.json','.timings-t3.json'):
        continue
    if path in archive.namelist():
        original=archive.read(path)
        origin='021 manager archive member '+path
    else:
        argv=['git','show','HEAD:'+path]
        p=subprocess.run(argv,cwd=REPO,capture_output=True)
        assert p.returncode==0
        original=p.stdout
        origin='git HEAD:'+path
        if hashlib.sha256(original).hexdigest()!=start[path]['sha256']:
            lf=original.replace(b'\r\n',b'\n')
            candidates=[('LF',lf),('CRLF',lf.replace(b'\n',b'\r\n'))]
            matching=[(name,raw) for name,raw in candidates if hashlib.sha256(raw).hexdigest()==start[path]['sha256']]
            assert len(matching)==1,(path,'Git newline realization does not match the start bytes')
            realization,original=matching[0]
            origin+='; '+realization+' newline realization verified against start SHA256'
    assert hashlib.sha256(original).hexdigest()==start[path]['sha256'],path
    raw=(REPO/path).read_bytes()
    blocks.extend(difflib.unified_diff(original.decode('utf-8').splitlines(keepends=True),
        raw.decode('utf-8').splitlines(keepends=True),fromfile='start/'+path,tofile='final/'+path))
    coordinates.append({'path':path,'original_source':origin,'before':start[path],'after':current[path]})
(E/'task-changes.diff').write_bytes(''.join(blocks).encode('utf-8'))
save('change-coordinates.json',coordinates)
print('Exact task byte diff',len(coordinates),'noncache files. Original bytes match start hashes; prior dirty changes are excluded.')

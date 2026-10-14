from work import *
phase=json.loads((RUN/'phases/023/phase.json').read_text(encoding='utf-8-sig'))
rows=[]
for ref in phase['tasks'][0]['inputs']:
    prefix,path=ref.split(':',1)
    source=(REPO if prefix=='repo' else RUN)/path
    raw=source.read_bytes()
    value=json.loads(raw.decode('utf-8-sig')) if source.suffix=='.json' else raw.decode('utf-8-sig')
    rows.append({'ref':ref,**digest(source),'lines':len(raw.splitlines()),'kind':type(value).__name__})
save('input-audit.json',rows)
for filename in ('followup-packets.json','binding-inventory.json'):
    source=RUN/'phases/001/tasks/document-closeout/evidence'/filename
    value=json.loads(source.read_text(encoding='utf-8-sig'))
    print(filename, list(value) if isinstance(value,dict) else type(value).__name__)
    save('input-'+filename,value)
start=json.loads((E/'start.json').read_text(encoding='utf-8-sig'))
for path in phase['tasks'][0]['writes']:
    source=REPO/path
    if source.is_file():
        target=E/'original'/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(source.read_bytes())
        assert digest(target)==start[path]
print('Read',len(rows),'required sources; saved original authorized files')

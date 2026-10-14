from work import *
phase=json.loads((RUN/'phases/025/phase.json').read_text(encoding='utf-8-sig'))
records=[]
for ref in phase['tasks'][0]['inputs']:
    root, relative=ref.split(':',1)
    path=(REPO if root=='repo' else RUN)/relative
    raw=path.read_bytes()
    value=json.loads(raw.decode('utf-8-sig')) if path.suffix=='.json' else raw.decode('utf-8-sig')
    records.append({'reference':ref,**digest(path)})
    if path.name in ('followup-packets.json','binding-inventory.json','section-name-decisions.json','current-sections.json','prior-review-state.json'):
        def relevant(node):
            if isinstance(node,list):
                return [x for x in node if any(s in json.dumps(x,ensure_ascii=False) for s in ('P08','N01-274','N01-279','N01-281','B110','B111','B112','B113','B114','D-06'))]
            if isinstance(node,dict):
                return {k:relevant(v) for k,v in node.items()}
            return node
        selected=relevant(value)
        save(path.stem+'-input.json',selected)
        print(path.name,json.dumps(selected,ensure_ascii=False)[:12000])
save('inputs-read.json',records)
print('Read and hashed',len(records),'required inputs')

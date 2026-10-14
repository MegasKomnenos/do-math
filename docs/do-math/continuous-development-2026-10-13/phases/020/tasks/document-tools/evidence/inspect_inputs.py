from work import *
import re
old=json.loads((RUN/'phases/019/manager-evidence/source-inspected.json').read_text(encoding='utf-8-sig'))
start=json.loads((E/'start.json').read_text())
diff=[p for p in set(old)|set(start) if old.get(p)!=start.get(p,{}).get('sha256')]
save('start-comparison.json',{'previous_count':len(old),'current_count':len(start),'differences':diff})
print('START',len(start),'DIFF',diff)
phase=json.loads((RUN/'phases/020/phase.json').read_text(encoding='utf-8-sig'))
audit=[]
for ref in phase['tasks'][0]['inputs']:
    kind,rel=ref.split(':',1); path=(RUN if kind=='run' else REPO)/rel
    text=path.read_text(encoding='utf-8-sig')
    audit.append({'ref':ref,**digest(path),'lines':len(text.splitlines())})
    if path.suffix=='.json':
        data=json.loads(text)
        if 'followup-packets' in rel: print('P03',json.dumps([x for x in data['packets'] if x['id']=='P03'],ensure_ascii=False,indent=2))
        elif 'binding-inventory' in rel: print('BINDINGS',json.dumps([x for x in data['bindings'] if x.get('owner') in ('execution_window','scholarly','formal_verifier','preview','record_map','submission_contract')],ensure_ascii=False,indent=2))
        elif path.name=='report.json': print(ref, data['narrative'])
    elif path.suffix=='.md' and ('review' in rel or '설계' in rel or '결함-범주' in rel):
        lines=text.splitlines()
        hits=[i for i,line in enumerate(lines) if re.search(r'13-C|P03|B11[0-4]|preview|console|PR24|read_tool',line)]
        print(ref,'\n'.join(f'{i+1}: '+lines[i] for i in hits))
save('input-audit.json',audit)

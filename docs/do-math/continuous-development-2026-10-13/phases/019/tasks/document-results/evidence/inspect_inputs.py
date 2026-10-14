from work import *

def read(rel):
    return json.loads((RUN / rel).read_text(encoding='utf-8-sig'))

start = read('phases/019/tasks/document-results/evidence/start.json')
old = read('phases/018/manager-evidence/source-inspected.json')
diff = [{'path': p, 'before': old.get(p), 'after': start.get(p)} for p in sorted(set(old)|set(start)) if old.get(p) != start.get(p,{}).get('sha256')]
save('start-comparison.json', {'previous_count':len(old), 'current_count':len(start), 'differences':diff})
print('START DIFF', len(diff), json.dumps(diff,ensure_ascii=False)[:1800])
for rel in ('phases/001/tasks/document-closeout/evidence/followup-packets.json', 'phases/001/tasks/document-closeout/evidence/binding-inventory.json','phases/001/tasks/closure-map/evidence/prior-review-state.json','phases/009/manager-evidence/verification.json','phases/018/manager-evidence/verification.json'):
    obj = read(rel)
    print(rel, 'KEYS', list(obj) if isinstance(obj,dict) else len(obj))
    if isinstance(obj,dict):
        for key,value in obj.items():
            if isinstance(value,list):
                print(' ',key,'rows',len(value), 'first keys',list(value[0]) if value and isinstance(value[0],dict) else '')
for rel, key in (('phases/001/tasks/document-closeout/evidence/followup-packets.json','packets'),('phases/001/tasks/document-closeout/evidence/binding-inventory.json','bindings'),('phases/001/tasks/closure-map/evidence/prior-review-state.json','review_units')):
    obj=read(rel)
    rows = [row for row in obj[key] if row.get('id') in ('P02','PR24') or row.get('owner') in ('source_ref','materialized_output_files','research_sources','results')]
    print(rel, json.dumps(rows,ensure_ascii=False,indent=2))

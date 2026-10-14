from work import *
tree,name=sys.argv[1:]
scripts=REPO/tree/'skills/do-math/scripts'
sys.path[:0]=[str(scripts),str(scripts/'tests')]
from do_math.context_store import prepare_role_input
from support.storage_probes import Returns
import run_tests
rows=[]
def record(prepared):
    context=prepared['context']
    seat=context.get('role_review')
    if not isinstance(seat,dict) or 'proposal' not in seat:
        return None
    proposal=seat['proposal']
    def matches(node,path='context'):
        if isinstance(node,dict):
            return ([path] if node==proposal else [])+[p for key,value in node.items() for p in matches(value,path+'.'+key)]
        if isinstance(node,list):
            return [p for i,value in enumerate(node) for p in matches(value,path+f'[{i}]')]
        return []
    paths=matches(context)
    row={'stage':seat['action']['stage'],'slot':seat['action']['slot'],
         'proposal_digest':seat['proposal_digest'],'paths':paths,'count':len(paths),'expected_count':1}
    index=len(rows)
    row['actual_return_file']=f'{name}-return-{index:03d}.json'
    save(row['actual_return_file'],{'context':context,'manifest':prepared['manifest']})
    rows.append(row)
    return row
ids=json.loads((E/'related-selection.json').read_text(encoding='utf-8'))
sys.argv=[str(scripts/'run_tests.py'),*ids,'--jobs','1','--output',str(E/name)]
with Returns(prepare_role_input,snapshot=record):
    code=run_tests.main()
save(name+'-proposal-observation.json',{'official_exit_code':code,'returns':rows,
    'satisfied':bool(rows) and all(row['count']==1 for row in rows)})
print('Observed exact final review returns',len(rows),'single proposal',all(r['count']==1 for r in rows),flush=True)
assert rows and all(row['count']==1 for row in rows)
sys.exit(code)

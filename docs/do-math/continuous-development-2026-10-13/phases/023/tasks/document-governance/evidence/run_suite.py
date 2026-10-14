from work import *
from contextlib import ExitStack
tree,name=sys.argv[1:]
scripts=REPO/tree/'skills/do-math/scripts'
sys.path[:0]=[str(scripts),str(scripts/'tests')]
from do_math.context_store import prepare_role_input
from do_math.governance import check_import
from do_math.academic import academic_status
from support.storage_probes import Returns
import run_tests
rows=[]; query_rows=[]; check_rows=[]
def record(prepared):
    context=prepared['context']
    role=context['execution_profile']['role']
    seat=context.get('role_review')
    count=None
    if isinstance(seat,dict) and 'proposal' in seat:
        proposal=seat['proposal']
        def matches(node):
            if isinstance(node,dict): return int(node==proposal)+sum(matches(v) for v in node.values())
            if isinstance(node,list): return sum(matches(v) for v in node)
            return 0
        count=matches(context)
        assert count==1, count
    if count is None and role not in ('intent_interpretation','research_plan','goal_audit'):
        return None
    index=len(rows)
    file=f'{name}-return-{index:03d}.json'
    save(file,{'context':context,'manifest':prepared['manifest']})
    row={'role':role,'file':file,'proposal_count':count,
         'academic_validation':context.get('academic_validation'),'governance_charter_id':context.get('governance',{}).get('charter',{}).get('id')}
    rows.append(row)
    return row
def record_check(bundle):
    file=f'{name}-check-{len(check_rows):03d}.json'
    save(file,bundle)
    row={'file':file,'id':bundle['id'],'status':bundle['status'],
         'bundle_sha256':bundle['sha256'],'check_sha256':bundle['check']['sha256']}
    check_rows.append(row)
    return row
ids=json.loads((E/'related-selection.json').read_text(encoding='utf-8'))
sys.argv=[str(scripts/'run_tests.py'),*ids,'--jobs','1','--output',str(E/name)]
with ExitStack() as stack:
    stack.enter_context(Returns(prepare_role_input,snapshot=record))
    stack.enter_context(Returns(check_import,snapshot=record_check))
    stack.enter_context(Returns(academic_status,snapshot=lambda value: query_rows.append(dict(value))))
    code=run_tests.main()
save(name+'-observations.json',{'official_exit_code':code,'final_returns':rows,
    'checks':check_rows,'academic_queries':query_rows,
    'single_proposal':bool([r for r in rows if r['proposal_count'] is not None]) and
        all(r['proposal_count']==1 for r in rows if r['proposal_count'] is not None)})
print('Observed final returns',len(rows),'real check returns',len(check_rows),'academic queries',len(query_rows),flush=True)
sys.exit(code)

"""Observe the existing stage test; preserve exact returns, without replacing calls."""
from work import *
sys.path.insert(0,str(REPO/'.claude/skills/do-math/scripts'))
sys.path.insert(0,str(REPO/'.claude/skills/do-math/scripts/tests'))
from do_math.context_store import prepare_role_input
from support.storage_probes import Returns
import run_tests
observations=[]
def record(prepared):
    context=prepared['context']
    if 'role_review' not in context:return None
    seat=context['role_review']
    if 'proposal' not in seat:return None
    proposal=seat['proposal']
    def matches(node,path='context'):
        if isinstance(node,dict):
            found=[path] if node==proposal else []
            return found+[p for key,value in node.items() for p in matches(value,path+'.'+key)]
        if isinstance(node,list):return [p for i,value in enumerate(node) for p in matches(value,path+f'[{i}]')]
        return []
    paths=matches(context)
    row={'stage':seat['action']['stage'],'slot':seat['action']['slot'],
         'proposal_digest':seat['proposal_digest'],'complete_proposal_paths':paths,'count':len(paths),
         'expected_count':1}
    index=len(observations)
    save(f'proposal-return-{index:02d}.json',{'context':context,'manifest':prepared['manifest']})
    row['actual_return_file']=f'proposal-return-{index:02d}.json'
    observations.append(row)
    return row
sys.argv=['run_tests.py','sim.test_submission_review_inputs.ReviewInputTests.test_review_stage_documents_reach_the_final_seat_input',
          '--jobs','1','--output',str(E/'proposal')]
with Returns(prepare_role_input,snapshot=record):
    code=run_tests.main()
save('proposal-observation.json',{'official_exit_code':code,'returns':observations,
                               'satisfied':all(row['count']==1 for row in observations)})
print(json.dumps(observations,ensure_ascii=False,indent=2))
assert code==0
assert observations and all(row['count']==1 for row in observations), 'complete current proposal is duplicated in final role input'

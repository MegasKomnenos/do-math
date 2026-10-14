from work import *
from copy import deepcopy
tree,name=sys.argv[1:]
scripts=REPO/tree/'skills/do-math/scripts'
sys.path[:0]=[str(scripts),str(scripts/'tests')]
from do_math import planning, task_scope
from do_math.dispatch_engine import DispatchEngineMixin
from do_math.context_store import prepare_role_input
from support.monitoring_slots import reserve_tool
import run_tests
codes={f.__code__:key for key,f in [('condition',planning.evaluate_condition),
    ('current',task_scope.decision_is_current),('settle',DispatchEngineMixin._plan_settle_waits),
    ('dispatch',DispatchEngineMixin._dispatchable),('prepared',prepare_role_input)]}
rows=[]; finals=[]
def returned(code,offset,value):
    frame=sys._getframe(1); args=frame.f_locals; kind=codes[code]
    if kind=='condition':
        if args['condition'].get('op')=='decision_value_is':
            rows.append({'kind':kind,'condition':deepcopy(args['condition']),
                'decision':deepcopy(args['instance'].get('decisions',{}).get(args['condition'].get('decision_id'))),
                'result':deepcopy(value)})
    elif kind=='current':
        rows.append({'kind':kind,'decision':deepcopy(args['decision']),'result':value})
    elif kind in ('settle','dispatch'):
        action=args['action']
        if action.get('role')=='research_plan':
            engine=args['self']
            rows.append({'kind':kind,'action':deepcopy(action),'result':value,
                'now':engine.ports.clock.now(),'limit':engine.instance['config']['plan_settle_seconds'],
                'queue':deepcopy(engine.runtime['queue'])})
    else:
        context=value['context']; seat=context.get('role_review')
        if isinstance(seat,dict) and 'proposal' in seat:
            proposal=seat['proposal']
            def count(node):
                if isinstance(node,dict):return int(node==proposal)+sum(count(v) for v in node.values())
                if isinstance(node,list):return sum(count(v) for v in node)
                return 0
            copies=count(context)
            assert copies==1,copies
            filename=f'{name}-proposal-{len(finals):03d}.json'
            save(filename,{'context':context,'manifest':value['manifest']})
            finals.append({'file':filename,'proposal_count':copies})
ids=json.loads((E/'related-selection.json').read_text(encoding='utf-8'))
sys.argv=[str(scripts/'run_tests.py'),*ids,'--jobs','1','--output',str(E/name)]
tool=reserve_tool('024 actual wait returns')
sys.monitoring.register_callback(tool,sys.monitoring.events.PY_RETURN,returned)
try:
    for code in codes:sys.monitoring.set_local_events(tool,code,sys.monitoring.events.PY_RETURN)
    exit_code=run_tests.main()
finally:
    for code in codes:sys.monitoring.set_local_events(tool,code,sys.monitoring.events.NO_EVENTS)
    sys.monitoring.register_callback(tool,sys.monitoring.events.PY_RETURN,None)
    sys.monitoring.free_tool_id(tool)
save(name+'-observations.json',{'exit_code':exit_code,'actual_returns':rows,'final_proposals':finals})
print('Observed actual wait/condition returns',len(rows),'single-proposal final inputs',len(finals),flush=True)
sys.exit(exit_code)

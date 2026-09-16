"""Compare predeclared and newly discovered knowledge use during a revision."""
from pathlib import Path
import sys,json,time
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'.claude/skills/do-math/scripts'),str(ROOT/'.claude/skills/do-math/scripts/tests')]
import test_session_scheduler as fixtures
from test_engine import common
from test_purpose_engine import parse_context
from do_math.engine import control
from do_math.planning import contract_hash
import jsonschema

def scenario(declared):
    h=fixtures.ParallelEngineTests(); h.setUp()
    evidence={}
    try:
        class Runner:
            def run(self,**kw):
                ctx=parse_context(kw['prompt'],kw['workspace'])
                kw['on_started']({'pid':1})
                original=json.loads((kw['workspace']/'input/knowledge'/f'{kid}.json').read_text(encoding='utf-8'))
                evidence['read_statement']=original['statement']
                control(h.repo,engine.instance['id'],'knowledge',config={'operation':'revise','id':kid,
                    'changes':{'statement':'The corrected bounded computation returned two.'},'reason':'Correct a recorded computational result'})
                kw['should_stop']()
                out=common('research_work')
                out.update(outcome='submitted',report='Use the earlier bounded computation as the result basis.',
                    used_sources=[kid], checkpoint='Finished',knowledge=[{'kind':'observation','title':'Derived result',
                    'statement':'The computation basis returns one.','summary':'One is the result basis.',
                    'explanation':'This uses the provided computation record.','lean_code':'','declaration_names':[],
                    'dependencies':[kid]}])
                jsonschema.validate(out,kw['output_schema'])
                return {'status':'completed','output':out,'usage':{}}
        engine=h.engine(Runner(),count=1,max_output_repairs=0)
        control(h.repo,engine.instance['id'],'knowledge',config={'operation':'import','candidate':{
            'kind':'observation','title':'Prior computation','statement':'The bounded computation returned one.',
            'summary':'A bounded computation','explanation':'Input data and finite computation.','lean_code':''}})
        engine.process_controls()
        kid=next(iter(engine.instance['knowledge']))
        task=next(iter(engine.runtime['tasks'].values()))
        if declared:
            task['reuse']=[kid]
            for review in task['reviews']: review['contract_sha256']=contract_hash(task)
        engine.runtime['queue']=[a for a in engine.runtime['queue'] if a['role']=='research_work']
        engine._save()
        engine.run(max_steps=1)
        execution=next(e for e in engine.runtime['executions'].values() if e['role']=='research_work')
        derived=[k for k in engine.instance['knowledge'].values() if k['title']=='Derived result']
        evidence.update(predeclared=declared,outcome=execution['outcome'],error=execution.get('error'),
            current_statement=engine.instance['knowledge'][kid]['statement'],
            validity_basis=execution.get('validity_basis'),derived_count=len(derived),
            derived_suspension=[k.get('use_suspended',False) for k in derived])
        return evidence
    finally:
        h.tearDown()

if __name__=='__main__':
    rows=[scenario(False),scenario(True)]
    Path(__file__).with_name('actual-dependency-results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False,indent=2))

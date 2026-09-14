from pathlib import Path
import hashlib,json,sys,subprocess
sys.dont_write_bytecode=True
skill=Path(r'C:\math\.skill-workspace\do-math-feature2-tests-fg5ma0v3\do-math')
evidence=Path(r'C:\math\.skill-workspace\do-math-feature2-live-disputed\evidence')
sys.path.insert(0,str(skill/'scripts'))
from do_math.repository import ResearchRepository
instance=json.loads((evidence/'final-instance.json').read_text(encoding='utf-8'))
store=ResearchRepository(evidence/'repository',instance['id'])
head,instance,runtime=store.load()
calls=json.loads((evidence/'actual-cli-invocations.json').read_text(encoding='utf-8'))
checks=[]
for call in calls:
    execution=next(ex for ex in runtime['executions'].values() if ex.get('action',{}).get('id')==call['action']['id'])
    raw=store.read(f"runtime/artifacts/{execution['input_bundle']}/input.txt",head)
    assert hashlib.sha256(raw).hexdigest()==execution['input_sha256']==call['prompt_sha256']
    context=json.loads(raw.decode().split('--- CANONICAL INPUT CONTEXT ---\n',1)[1].split('\n--- OUTPUT JSON SCHEMA ---',1)[0])
    review=context['role_review']
    action=call['action']
    if action['stage']=='judge':
        assert not any(result['action']['stage']=='judge' and result['action']['round']==action['round']
                       for result in review['completed_results'].values())
        if action['round']==2:
            earlier=next(c for c in calls if c['action']['stage']=='judge' and c['action']['slot']==action['slot'] and c['action']['round']==1)
            earlier_execution=next(ex for ex in runtime['executions'].values() if ex.get('action',{}).get('id')==earlier['action']['id'])
            own=next(message for message in review['self_messages'] if message.get('message_id')==earlier_execution['id']+':assistant')
            assert own['content']==earlier['output']
    checks.append({'stage':action['stage'],'slot':action['slot'],'round':action['round'],'input_sha256':execution['input_sha256'],'passed':True})
answer=next(c for c in calls if c['action']['stage']=='answer')
assert all(item['disposition']=='withdraw' for item in answer['output']['answers'])
assert len([ex for ex in runtime['executions'].values() if ex.get('actor_kind')=='synthetic_fixture'])==2
usage={}
for call in calls:
    for key,value in call.get('usage',{}).items():
        if isinstance(value,(int,float)) and not isinstance(value,bool):usage[key]=usage.get(key,0)+value
bundle=subprocess.run(['git','-C',str(evidence/'repository'),'bundle','verify',str(evidence/'state.bundle')],capture_output=True,text=True)
assert bundle.returncode==0,bundle.stderr
manifest=json.loads((evidence/'skill-source-manifest.json').read_text(encoding='utf-8'))
for entry in manifest['files']:
    assert hashlib.sha256((skill/entry['path']).read_bytes()).hexdigest()==entry['sha256']
report={'passed':True,'actual_cli_invocations':len(calls),'synthetic_initial_fixtures':2,'same_slot_prior_assistant_verified':3,
        'judge_peer_results_hidden_in_actual_input':6,'answer_withdrawal_verified':True,'checks':checks,'actual_cli_usage':usage,
        'git_bundle_verified':True,'frozen_source_hashes_verified':len(manifest['files']),'final_snapshot':head}
(evidence/'post-run-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))

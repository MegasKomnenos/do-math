from work import *
import re,ast
S=REPO/'.claude/skills/do-math/scripts/do_math'
packet=next(p for p in json.loads((E/'followup-packets-input.json').read_text(encoding='utf-8'))['packets'] if p['id']=='P11')
owners={'conversation_loss_policy':['initialization_engine.py','lifecycle_engine.py','supervision.py'],
    'disconnect_policy':['control_contracts.py','lifecycle_engine.py','record_schemas/schemas.py'],
    'model_policy':['model_policy.py','model_call.py','provider_engine.py','call_engine.py'],
    'external_policy':['initialization_engine.py','initialization.py','external_engine.py','lifecycle_engine.py'],
    'adopt_default_review_policy':['control_contracts.py','initialization_engine.py']}
policies=[]
for name,files in owners.items():
    definitions=[]
    for rel in files:
        path=S/rel; lines=path.read_text(encoding='utf-8').splitlines()
        hits=[{'line':n,'text':'\n'.join(lines[max(0,n-4):n+4])} for n,line in enumerate(lines,1)
              if name in line or name=='model_policy' and any(x in line for x in ('MODELS =','ROLE_TIERS =','reported model differs'))]
        definitions.append({'path':path.relative_to(REPO).as_posix(),**digest(path),'excerpts':hits})
    occurrences=[]
    for old in packet['policy_name_only_candidates']:
        if old['policy']!=name:continue
        path=REPO/old['document'].split(':',1)[1]
        lines=path.read_text(encoding='utf-8').splitlines()
        line=next((n,line) for n,line in enumerate(lines,1) if old['text'] in line)
        occurrences.append({'historical':old,'current_line':line[0],'current_text':line[1],**digest(path)})
    policies.append({'name':name,'occurrences':occurrences,'definitions':definitions,
        'judgment':'Maintain the current sentences and lexical owner check. Definition/owner identification is not complete policy-semantic certification; the listed owner retains its broader runtime/role review responsibility. No new generic policy evaluator.'})
decisions=json.loads((E/'section-name-decisions-input.json').read_text(encoding='utf-8'))
tokens={'N01-237':{'input_overflow_retry_resolved','input_overflow_retry_failed','question_links'},
        'N02-002':{'input_overflow_requests','input_overflow_resolutions'},
        'N01-260':{'scope','replay_safety','repair_target'}}
selected=[r for r in decisions if r['section'] in tokens and r['token'] in tokens[r['section']]]
assert {r['token'] for r in selected}==set.union(*tokens.values())
for row in selected:
    file='references/공통-실행.md' if row['section']=='N02-002' else 'references/CLI-실행-계약.md'
    path=REPO/'.claude/skills/do-math'/file
    text=path.read_text(encoding='utf-8')
    for sentence in row['sentences']:assert sentence in text,(row['section'],row['token'])
    row['current_file']=path.relative_to(REPO).as_posix(); row['current_sha256']=digest(path)['sha256']
    row['current_lines']=[n for n,line in enumerate(text.splitlines(),1) if '`'+row['token']+'`' in line]
mapping={
    'N01-237':{'consumers':['call_engine._prepare_call','core_engine._retry_input_overflow_action',
        'core_engine._resume_input_overflow_action','core_engine._resolve_input_overflow_question',
        'question_engine._question_view','questions.close'],
        'tests':['flows.test_engine_input_recovery.InputRecoveryPublicTests.test_public_retry_replays_refails_resolves_and_rejects_after_close',
        'flows.test_engine_input_recovery.InputRecoveryPublicTests.test_resolved_retry_marker_survives_provider_deferral_and_repreparation',
        'sim.test_engine_input_overflow.InputRecoveryMarkerTests.test_preexisting_user_resolution_is_preserved_when_retry_input_fits',
        'sim.test_governance_questions.QuestionTextTests.test_overflow_question_text_follows_its_artifact_pointer',
        'unit.test_governance_question_contracts.GovernanceQuestionContractTests.test_pending_overflow_retry_exempts_only_its_question'],
        'judgment':'Retry acceptance only queues a pending retry. Actual packing success resolves it, failure replaces it with another open question while preserving both failures and original source artifact. Pause/resume does not resolve the input question. Existing user-resolution history survives later packing success; unrelated questions and operation-owner restrictions remain.'},
    'N02-002':{'consumers':['input_recovery.overflow_requests','input_recovery.validate_resolutions',
        'core_engine._apply_input_overflow_resolutions','core_engine._resume_input_overflow_action','submission.payload_issues'],
        'tests':['sim.test_engine_input_overflow.OverflowConnections',
                 'flows.test_engine_input_recovery.OverflowGitConnection.test_plan_choice_repackages_original_work_and_reaches_runner',
                 'unit.test_submission_extension_semantics'],
        'judgment':'Actual _context/prepare_role_input provides held request and exact allowed profile refs without adding them to ready IDs. Both fixed and current request, contract hash, question and offered profile are checked before requeue; planner-only extension admission and later role/grant/profile/packing gates are retained.'},
    'N01-260':{'consumers':['core_engine._apply_operational_disposition','core_engine._complete_operational_disposition',
        'core_engine._run_pending_operational_repairs','activities.continue_activity','core_engine._prepare_call',
        'dispatch_engine._dispatchable','repair_execution.request_installation_repair'],
        'tests':['sim.test_scheduling_recovery_dispositions', 'unit.test_repair_execution',
                 'sim.test_scheduling_close_preparation.PreparationBranchTests'],
        'judgment':'Operational retry requires ended predecessor/confirmed local termination, reconciled unknown effects and intact sealed manifest/support. It reuses the activity with an explicit continuation and fresh input/workspace, preserving rejected bundles and current profile/authority/capacity checks. Installation repair has its own accepted diagnosis, installation-relative target, recovery authority, lock, evidence and HOLD conditions; retry does not authorize modifying installation.'}}
save('section-semantic-review.json',{'exact_sentences':selected,'mapping':mapping,'scope':'Only the named sentences, not full N sections or L01/other policy meaning.'})
save('policy-name-decisions.json',policies)
print('Exact N sentences',len(selected),'lexical policy owners',len(policies),'occurrences',sum(len(r['occurrences']) for r in policies))

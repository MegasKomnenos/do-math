"""Read-only schema/doc-helper observations. No runner, store, OS or network calls."""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path('C:/math')
SKILL = ROOT / '.claude/skills/do-math'
OUT = ROOT / 'docs/do-math/continuous-development-2026-10-13/phases/028/tasks/role-glossary-names/evidence'
sys.path[:0] = [str(SKILL/'scripts'),str(SKILL/'scripts/tests')]
from do_math import contracts, observations, review_cycle, submission
from support import doc_code

cli=(SKILL/'references/CLI-실행-계약.md').read_text(encoding='utf-8')
glossary=(SKILL/'GLOSSARY.md').read_text(encoding='utf-8')
schemas=doc_code.field_schemas()
defer=dict(defer_status=True,defer_operation_progress=True,defer_query_record=True,defer_query_result=True,
    defer_cli_results=tuple(doc_code.CLI_RESULT_BOUNDARIES),defer_result_inputs=tuple(doc_code.RESULT_INPUT_BOUNDARIES),
    defer_operational_inputs=tuple(doc_code.OPERATIONAL_INPUT_BOUNDARIES),defer_continuations=tuple(doc_code.CONTINUATION_BOUNDARIES),
    defer_role_inputs=tuple(doc_code.ROLE_INPUT_BOUNDARIES),defer_tool_inputs=tuple(doc_code.TOOL_INPUT_BOUNDARIES),
    defer_review_inputs=tuple(doc_code.REVIEW_INPUT_BOUNDARIES),defer_delivery_inputs=tuple(doc_code.DELIVERY_INPUT_BOUNDARIES),
    defer_governance=tuple(doc_code.GOVERNANCE_BOUNDARIES),defer_waits=tuple(doc_code.WAIT_BOUNDARIES),defer_trust=tuple(doc_code.TRUST_BOUNDARIES))
def diagnostics(text):
    return {'scoped':doc_code.scoped_field_issues(text,schemas,**defer),
            'unowned':doc_code.unowned_field_references(text,schemas),
            'function':doc_code.function_reference_issues(text),
            'constant':doc_code.constant_reference_issues(text)}

normal=diagnostics(cli)
assert not any(normal.values()),normal
cases=[]
for name,old,new,section,schema_path in [
    ('initial output typo','`scope_complete`, `findings`를 추가한다','`scope_complete`, `findingz`를 추가한다','N01-250','findings'),
    ('organize borrows decision','`issues`를 추가하며 승인 decision을 내지 않는다','`issues`와 `decision`을 추가하며 승인 decision을 낸다','N01-251','decision'),
    ('answer output typo','`answers`와 `new_findings`를 추가한다','`answerz`와 `new_findings`를 추가한다','N01-252','answers'),
    ('judge item borrows proposal enum','`decision=approved|rejected|unresolved`','`decision=match|mismatch|unresolved`','N01-253','issue_verdicts[].decision'),
    ('checkpoint key typo','"current_claim":"현재 주장과 판단"','"current_cliam":"현재 주장과 판단"','N01-256','current_claim')]:
    assert cli.count(old)==1,(name,cli.count(old))
    changed=cli.replace(old,new)
    result=diagnostics(changed)
    assert result==normal,(name,result)
    cases.append({'name':name,'section':section,'old':old,'changed':new,'existing_applicable_helper_diagnostics':result,
        'comparison':'same diagnostics as normal; selected role-contract helpers read different document coordinates', 'owner_path':schema_path})
for case in cases:
    name=case['name']
    if name=='initial output typo':
        case['actual_owner_observation']={'normal_exists':bool(doc_code._schema_path(review_cycle.stage_schema('initial'),'findings')),
            'typo_exists':bool(doc_code._schema_path(review_cycle.stage_schema('initial'),'findingz'))}
    elif name=='organize borrows decision':
        case['actual_owner_observation']={'issues_exists':bool(doc_code._schema_path(review_cycle.stage_schema('organize'),'issues')),
            'borrowed_decision_exists':bool(doc_code._schema_path(review_cycle.stage_schema('organize'),'decision'))}
    elif name=='answer output typo':
        case['actual_owner_observation']={'normal_exists':bool(doc_code._schema_path(review_cycle.stage_schema('answer'),'answers')),
            'typo_exists':bool(doc_code._schema_path(review_cycle.stage_schema('answer'),'answerz'))}
    elif name=='judge item borrows proposal enum':
        shape=doc_code._schema_path(review_cycle.stage_schema('judge'),'issue_verdicts[].decision')[0]
        case['actual_owner_observation']={'normal_approved_allowed':'approved' in shape['enum'],
            'borrowed_match_allowed':'match' in shape['enum'],'enum':shape['enum']}

# Complete checkpoint object, not a full role response. File existence is deliberately not evaluated.
section=doc_code._document_section(cli,'`checkpoint.json`')
fence=re.search(r'```json\n(.*?)\n```',section,re.S).group(1)
value=json.loads(fence)
normal_checkpoint=observations.checkpoint_value(fence.encode('utf-8'))
bad=copy.deepcopy(value);bad['current_cliam']=bad.pop('current_claim')
try:
    observations.checkpoint_value(json.dumps(bad,ensure_ascii=False).encode('utf-8'))
except Exception as error:
    bad_checkpoint={'error_type':type(error).__name__,'message':str(error)}
else:
    raise AssertionError('checkpoint typo unexpectedly accepted')
assert normal_checkpoint==value

work=contracts.action_schema({'role':'research_work'})
knowledge_kind=work['properties']['knowledge']['items']['properties']['kind']
assert knowledge_kind.get('type')=='string' and 'enum' not in knowledge_kind
path_specs={
    'N01-240':(contracts.action_schema({'role':'research_preparation'}),'candidates[].revises_task_id candidates[].scope.included candidates[].scope.excluded candidates[].expected.outputs candidates[].expected.research_change candidates[].profile_refs[].id candidates[].profile_refs[].revision candidates[].profile_refs[].sha256'),
    'N01-241':(contracts.schema_for('task_contract_review'),'item_reviews[].item_id item_reviews[].decision item_reviews[].evidence_refs item_reviews[].findings item_reviews[].missing_inputs item_reviews[].next_owner'),
    'N01-242':(contracts.schema_for('research_plan'),'dispositions[].kind preparation_requests goal_audit task_assessments[].decision task_assessments[].item_dispositions[].kind task_assessments[].item_dispositions[].evidence_refs task_assessments[].unresolved'),
    'N01-243':(work,'outcome report knowledge[].kind knowledge[].declaration_names knowledge[].dependencies relations[].kind relations[].source relations[].target relations[].evidence remaining_work checkpoint'),
    'N01-244':(review_cycle.stage_schema('scope'),'scope_assessment'),
    'N01-245':(contracts.schema_for('goal_audit'),'decision reason scope_complete'),
    'N01-246':(contracts.schema_for('operational_review'),'disposition.kind disposition.basis_refs disposition.next_owner disposition.reason'),
    'N01-249':(review_cycle.stage_schema('initial'),'proposal_digest summary used_sources questions'),
    'N01-250':(review_cycle.stage_schema('initial'),'decision scope_complete findings[].id findings[].statement findings[].evidence'),
    'N01-251':(review_cycle.stage_schema('organize'),'issues[].id issues[].finding_refs[].stage issues[].finding_refs[].round issues[].finding_refs[].slot issues[].finding_refs[].id issues[].answer_role_slot_id'),
    'N01-252':(review_cycle.stage_schema('answer'),'answers[].issue_id answers[].disposition answers[].statement answers[].evidence new_findings[].id new_findings[].parent_issue_ids'),
    'N01-253':(review_cycle.stage_schema('judge'),'decision scope_complete issue_verdicts[].issue_id issue_verdicts[].decision issue_verdicts[].reason issue_verdicts[].evidence new_findings'),
    'N01-254':(review_cycle.research_schema(),'research_request_id request_digest outcome answer scope_complete evidence_refs'),
    'N01-256':(observations.CHECKPOINT_SCHEMA,'current_claim evidence_paths attempts remaining_work next_step progress_state iteration counters')}
paths=[]
for section,(schema,names) in path_specs.items():
    for name in names.split():
        variants=doc_code._schema_path(schema,name)
        assert variants,(section,name)
        paths.append({'section':section,'owner_path':name,'variants':variants})
facts={
    'knowledge_kind':{'document':'CLI-실행-계약.md:748','claim':'kind enum은 실행 시점의 active knowledge 종류 정의에서 동적으로 만든다.',
        'call':'contracts.action_schema({role: research_work})','actual_shape':knowledge_kind,
        'consumer':'submission._payload_issues:816-838 accepts active or proposed in this bundle, then candidate_shape_errors',
        'runtime_run':False},
    'resolved_schema_paths':paths,
    'stage_properties':{s:{'properties':list(review_cycle.stage_schema(s)['properties']),
                           'required':review_cycle.stage_schema(s)['required']} for s in ('scope','initial','organize','answer','judge')},
    'judge_proposal_decision':review_cycle.stage_schema('judge')['properties']['decision'],
    'judge_issue_decision':review_cycle.stage_schema('judge')['properties']['issue_verdicts']['items']['properties']['decision'],
    'checkpoint':{'fence':fence,'normal_value':normal_checkpoint,'typo_value':bad_checkpoint,
        'schema_required':observations.CHECKPOINT_SCHEMA['required'],'scope':'shape/JSON only; evidence_paths actual file safety not called'},
    'extension_families':{r:list(submission.extension_schema({'role':r})['properties']) for r in ('research_preparation','research_plan','research_work','operational_review')},
    'normal_cli_diagnostics':normal,'normal_glossary_diagnostics':diagnostics(glossary),'counterexamples':cases,
    'limitations':'No unittest/test runner or runtime store/model/OS/Lean call. Helper observations are not new official passing rows. Deferred actual-return checks are historical evidence, not reexecuted here.'}
(OUT/'schema-observations.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'observations':'saved','counterexamples':len(cases),'kind_has_enum':'enum' in knowledge_kind,'checkpoint_normal':normal_checkpoint is not None,'checkpoint_typo_rejected':bad_checkpoint['error_type']},ensure_ascii=False))

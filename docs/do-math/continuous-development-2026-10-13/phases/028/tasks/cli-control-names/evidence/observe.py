"""Only pure parser/schema/document helpers; no test runner or domain effects."""
from bounded_io import REPO, RUN, OUT, read, digest, save
import sys, json, re, copy
SCRIPTS=REPO/'.claude/skills/do-math/scripts'
sys.path[:0]=[str(SCRIPTS),str(SCRIPTS/'tests')]
from do_math import cli_contract, control_contracts, configuration, knowledge_io
from do_math.record_schemas import config_schema
from do_math.record_schemas.schemas import RECORDS, RUNTIME_FIELDS
from support import doc_code
from jsonschema import Draft202012Validator
text=read(REPO/'.claude/skills/do-math/references/CLI-실행-계약.md')
parser=cli_contract.build_parser()
options=doc_code.parser_options(parser)
flags=doc_code.tool_options(SCRIPTS)
schemas=doc_code.field_schemas()
defer=dict(defer_status=True,defer_operation_progress=True,defer_query_record=True,defer_query_result=True,
 defer_cli_results=tuple(doc_code.CLI_RESULT_BOUNDARIES),defer_role_inputs=tuple(doc_code.ROLE_INPUT_BOUNDARIES),
 defer_continuations=tuple(doc_code.CONTINUATION_BOUNDARIES),defer_operational_inputs=tuple(doc_code.OPERATIONAL_INPUT_BOUNDARIES),
 defer_result_inputs=tuple(doc_code.RESULT_INPUT_BOUNDARIES),defer_tool_inputs=tuple(doc_code.TOOL_INPUT_BOUNDARIES),
 defer_review_inputs=tuple(doc_code.REVIEW_INPUT_BOUNDARIES),defer_delivery_inputs=tuple(doc_code.DELIVERY_INPUT_BOUNDARIES),
 defer_governance=tuple(doc_code.GOVERNANCE_BOUNDARIES),defer_waits=tuple(doc_code.WAIT_BOUNDARIES),defer_trust=tuple(doc_code.TRUST_BOUNDARIES))
def old_document_checks(value):
    return {'command_issues':doc_code.command_issues(value,options,flags),
      'scoped_field_issues':doc_code.scoped_field_issues(value,schemas,**defer),
      'unowned_field_references':doc_code.unowned_field_references(value,schemas),
      'policy_issues':doc_code.policy_issues(value,doc_code.declared_policy_names(SCRIPTS)),
      'function_reference_issues':doc_code.function_reference_issues(value)}
results={'called_functions':['cli_contract.build_parser','doc_code.parser_options','doc_code.tool_options','doc_code.field_schemas',
  'doc_code.command_issues','doc_code.scoped_field_issues','doc_code.unowned_field_references','doc_code.policy_issues',
  'doc_code.declared_policy_names','doc_code.function_reference_issues','control_contracts.validate_control_payload',
  'record_schemas.config_schema','Draft202012Validator.iter_errors','cli_contract._json_arguments','knowledge_io.candidate_shape_errors'],
  'execution_kind':'pure schema/parser/document observation, zero product tests',
  'current_document_checks':old_document_checks(text),'cases':[]}
for label,original,replacement,owner in [
 ('knowledge-candidate-key','"summary":"목차 요약"','"summray":"목차 요약"','control_contracts.CANDIDATE -> knowledge_io.import_candidate'),
 ('knowledge-operation','"operation":"import"','"operation":"improt"','control_contracts.PAYLOADS.knowledge.operation'),
 ('runtime-status','| `capacity_waiting` |','| `capacity_waitng` |','record_schemas.schemas.RUNTIME_FIELDS.status'),
 ('config-default','| `reviewers` | 2 |','| `reviewers` | 200 |','configuration.DEFAULT_CONFIG.reviewers'),
 ('query-combination','[--direction incoming|outgoing|both]','[--direction incoming|outgoing|sideways]','cli_contract.build_parser query direction'),
]:
    assert text.count(original)==1,(label,text.count(original))
    changed=text.replace(original,replacement)
    results['cases'].append({'label':label,'original':original,'replacement':replacement,'expected_owner':owner,
      'observation':old_document_checks(changed),'scope':'document helper only; no command dispatch'})
description=cli_contract.describe_commands(parser)
normal_candidate={'kind':'conjecture','title':'candidate','statement':'P','explanation':'scope','summary':'summary',
 'lean_code':'','declaration_names':[],'dependencies':[]}
for label,operation,candidate in [('candidate-normal','import',normal_candidate),
 ('candidate-key-counterexample','import',{k:v for k,v in {**normal_candidate,'summray':'summary'}.items() if k!='summary'}),
 ('operation-counterexample','improt',normal_candidate)]:
    value={'operation':operation,'candidate':candidate}
    try:
        control_contracts.validate_control_payload('knowledge','',value)
        admitted={'shape_accepted':True}
    except ValueError as error: admitted={'shape_accepted':False,'error':str(error)}
    results['cases'].append({'label':label,'value':value,'observation':admitted,
      'candidate_shape_errors':knowledge_io.candidate_shape_errors(candidate),
      'scope':'pure control/candidate shape only; registry/ID/authority/state/currentness not executed'})
for label,payload in [('record-query',{}),('files-query',{'files':True}),('wrong-direction',{'related_to':'KN-example','direction':'sideways'}),
 ('wrong-file-combination',{'files':True,'kind':'grant'}),('wrong-record-prefix',{'prefix':'runtime/'})]:
    request={'schema_version':5,'command':'query','payload':{'repository':'.','instance':'RI-example',**payload}}
    try:
        cli_contract._json_arguments(parser,request)
        outcome={'accepted_by_parser':True}
    except ValueError as e: outcome={'accepted_by_parser':False,'exception':str(e)}
    results['cases'].append({'label':label,'request':request,'observation':outcome,'scope':'_json_arguments only; no cli.execute/main'})
results['config_table']=[]
for m in re.finditer(r'^\| `([a-z][a-z_]+)` \| ([^|]+) \| (.+?) \|$',text,re.M):
    key,default,allowed=m.groups()
    if key not in config_schema()['properties']: continue
    row={'key':key,'document_default':default.strip(),'document_allowed':allowed,'schema':config_schema()['properties'][key],
         'code_default':configuration.DEFAULT_CONFIG.get(key),'code_default_present':key in configuration.DEFAULT_CONFIG}
    if re.fullmatch(r'\d+|true|false|`(?:null|[a-z_]+)`',default.strip()):
        raw=default.strip().strip('`')
        expected=json.loads(raw) if raw in ('true','false','null') or raw.isdigit() else raw
        row['literal_matches']=expected==configuration.DEFAULT_CONFIG.get(key)
        assert row['literal_matches'],row
    results['config_table'].append(row)
results['config_keys_not_in_table']=sorted(set(config_schema()['properties'])-{r['key'] for r in results['config_table']})
# The five lineage limit keys share one table row, so account for each explicitly.
for key in results['config_keys_not_in_table']:
    assert '`'+key+'`' in text
results['state_enums']={'runtime.status':RUNTIME_FIELDS['status'],
  **{name+'.status':RECORDS[name]['properties']['status'] for name in ('tasks','activities','executions','external_operations')}}
results['negative_task_examples']={name:list(Draft202012Validator(RECORDS['tasks']['properties']['status']).iter_errors(name))[0].message
 for name in ('ready','performing','assessing','needs_revision')}
results['knowledge_operations']=control_contracts.PAYLOADS['knowledge']['properties']['operation']['enum']
results['json_examples']=[]
for m in re.finditer(r'```json\n(.*?)```',text[:text.index('## AI 실행 입력')],re.S):
    value=json.loads(m.group(1)); line=text[:m.start()].count('\n')+1
    section=next(r for r in json.loads(read(OUT/'section-inventory.json')) if r['current_start']<=line<=r['current_end'])['id']
    owner=None
    if section=='N01-218': owner='config-schema fragment'; errors=list(Draft202012Validator(config_schema()).iter_errors(value))
    elif section=='N01-225' and isinstance(value,dict):
        owner='decision'; errors=list(Draft202012Validator(control_contracts.DECISION).iter_errors(value))
    elif section in ('N01-227','N01-228','N01-229','N01-230') and 'operation' in value:
        owner={'N01-227':'knowledge','N01-228':'trust','N01-229':'external','N01-230':'conversation'}[section]
        errors=list(Draft202012Validator(control_contracts.PAYLOADS[owner]).iter_errors(value))
    else: errors=[]; owner='partial relation_claim' if section=='N01-227' else 'partial academic_requirements array'
    results['json_examples'].append({'line':line,'section':section,'owner':owner,'value':value,'shape_errors':[e.message for e in errors],
      'limitation':'placeholder identity/currentness/authority not validated; partial objects are not whole controls'})
    assert not errors
save('pure-observations.json',results)
print(json.dumps({'current_document_checks':results['current_document_checks'],
 'cases':[{'label':r['label'],'observation':r['observation']} for r in results['cases']],
 'configuration_rows':len(results['config_table']),'json_examples':len(results['json_examples']),
 'knowledge_operations':results['knowledge_operations'],'negative_task_examples':results['negative_task_examples']},ensure_ascii=False,indent=2))

"""Read-only calls to existing parser/schema/document functions; no test runner."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/028/tasks/operator-names/evidence'
SCRIPTS = REPO / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from support import doc_code as dc
from do_math.cli_contract import build_parser, CliInputError
from do_math import contracts, control_contracts
from do_math.configuration import validate_config
from do_math.codex_adapter import CodexExecAdapter
from do_math.claude_adapter import ClaudePrintAdapter
from jsonschema import Draft202012Validator

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name, value): (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

sections = read(OUT / 'section-profiles.json')
schemas = dc.field_schemas()
parser = build_parser()
options = dc.parser_options(parser)
flags = dc.tool_options(SCRIPTS)
defer = dict(defer_status=True, defer_operation_progress=True, defer_query_record=True,
             defer_query_result=True, defer_cli_results=tuple(dc.CLI_RESULT_BOUNDARIES),
             defer_role_inputs=tuple(dc.ROLE_INPUT_BOUNDARIES), defer_continuations=tuple(dc.CONTINUATION_BOUNDARIES),
             defer_operational_inputs=tuple(dc.OPERATIONAL_INPUT_BOUNDARIES),
             defer_result_inputs=tuple(dc.RESULT_INPUT_BOUNDARIES), defer_tool_inputs=tuple(dc.TOOL_INPUT_BOUNDARIES),
             defer_review_inputs=tuple(dc.REVIEW_INPUT_BOUNDARIES), defer_delivery_inputs=tuple(dc.DELIVERY_INPUT_BOUNDARIES),
             defer_governance=tuple(dc.GOVERNANCE_BOUNDARIES), defer_waits=tuple(dc.WAIT_BOUNDARIES),
             defer_trust=tuple(dc.TRUST_BOUNDARIES))
names = dc.declared_policy_names(SCRIPTS)
diags = dc.diagnostic_names(SCRIPTS)
def document_checks(text):
    return {'command':dc.command_issues(text,options,flags),
            'scoped':dc.scoped_field_issues(text,schemas,**defer),
            'unowned':dc.unowned_field_references(text,schemas),
            'policy':dc.policy_issues(text,names), 'function':dc.function_reference_issues(text),
            'constant':dc.constant_reference_issues(text), 'diagnostic':dc.diagnostic_reference_issues(text,diags)}
observations = [{ 'id':s['id'], 'issues':document_checks(s['text'])} for s in sections]
assert not any(v for x in observations for v in x['issues'].values())
save('document-observations.json', {'kind':'new pure helper observations, not official tests',
      'calls':['field_schemas','build_parser','parser_options','tool_options','declared_policy_names',
               'diagnostic_names','command_issues','scoped_field_issues','unowned_field_references',
               'policy_issues','function_reference_issues','constant_reference_issues','diagnostic_reference_issues'],
      'deferred_boundaries':defer,'sections':observations})

# Template bodies are observed as written; symbolic IDs/dates are not approvals.
json_examples = []
for s in sections:
    for m in re.finditer(r'```json\s*\n(.*?)```',s['text'],re.S):
        value=json.loads(m.group(1))
        schema=None
        if s['id']=='N01-018':
            validate_config(value,host_id='operator-names-read-only')
            owner='configuration.validate_config (partial config merges actual defaults)'
        elif s['id']=='N01-019': owner='cli._emit response envelope with symbolic request/instance/OID placeholders'
        elif s['id'] in {'N01-271','N01-272','N01-275'}:
            schema=control_contracts.DECISION;owner='control_contracts.DECISION; grants additionally use closed GRANT'
        elif s['id']=='N01-274':
            schema=control_contracts.PAYLOADS['trust'];owner="control_contracts.PAYLOADS['trust'] transition input"
        else: raise AssertionError(s['id'])
        errors=[] if schema is None else [e.message for e in Draft202012Validator(schema).iter_errors(value)]
        assert not errors, (s['id'],errors)
        def keys(v,path=''):
            result=[]
            if isinstance(v,dict):
                for k,child in v.items():
                    full=path+'/'+k;result.append(full);result.extend(keys(child,full))
            elif isinstance(v,list):
                for i,child in enumerate(v): result.extend(keys(child,path+'/'+str(i)))
            return result
        json_examples.append({'section':s['id'],'line':s['current_start']+s['text'][:m.start()].count('\n'),
                              'owner':owner,'key_paths':keys(value),'value':value,'schema_errors':errors,
                              'scope':'shape/key observation only; no authority, date, referential or application claim'})
save('json-example-bindings.json', json_examples)

cases=[]
for normal,bad in [('```powershell\npython setup_lean.py --verify-only --trust-file new.json\n```',
                    '```powershell\npython setup_lean.py --verify-only --watch\n```'),
                   ('`probe_cli.py --skill-only`','`probe_cli.py --skill-only --verify-only`')]:
    cases.append({'kind':'tool flag ownership gap', 'normal':normal,'counterexample':bad,
                  'normal_helper':document_checks(normal),'counterexample_helper':document_checks(bad),
                  'actual_refusal':'static: setup_lean.main/probe_cli.main parser declarations do not accept the borrowed flag; tool main was not executed'})
for section,mutation in [('N01-018','session_limitz'),('N01-272','budget_kind')]:
    normal=next(x['value'] for x in json_examples if x['section']==section)
    bad=copy.deepcopy(normal)
    if section=='N01-018':
        bad['session_limitz']=bad.pop('session_limits')
        try: validate_config(bad,host_id='operator-names-read-only')
        except ValueError as e: rejection=str(e)
        else: raise AssertionError('configuration typo accepted')
    else:
        bad['grant']['budget_kind']='work'
        rejection=[e.message for e in Draft202012Validator(control_contracts.DECISION).iter_errors(bad)]
        assert rejection
    body='```json\n'+json.dumps(bad,ensure_ascii=False,indent=2)+'\n```'
    cases.append({'kind':'initialization JSON fence gap','section':section,'mutation':mutation,
                  'normal':normal,'counterexample':bad,'counterexample_helper':document_checks(body),
                  'actual_schema_refusal':rejection,'scope':'existing pure document helpers and actual schema/config checker; no consumer application or grant approval'})
save('minimal-counterexamples.json',cases)

reading=contracts.reading_map()
save('reading-map-observation.json', {'roles':reading,'documents_exist':all((SCRIPTS.parent/p).is_file() for paths in reading.values() for p in paths),
     'scope':'actual reading_map declaration parser only; no render_prompt/model invocation'})

s=next(s for s in sections if s['id']=='N01-273')
paragraph=next(line for line in s['text'].splitlines() if 'Codex 어댑터의 식별 모듈은' in line)
codex_clause=paragraph.split('Codex 어댑터의 식별 모듈은 ',1)[1].split('이고, Claude',1)[0]
claude_clause=paragraph.split('Claude 어댑터는 여기에 ',1)[1].split('을 더한다',1)[0]
documented_codex=re.findall(r'`([^`]+)`',codex_clause)
claude_additions=re.findall(r'`([^`]+)`',claude_clause)
identity_gap={'section':'N01-273','document':s['document'],
   'line':s['current_start']+s['text'].splitlines().index(paragraph),'quote':paragraph,
   'documented_codex':documented_codex,'actual_codex':list(CodexExecAdapter.identity_modules),
   'documented_claude':documented_codex+claude_additions,'actual_claude':list(ClaudePrintAdapter.identity_modules),
   'omitted_codex':sorted(set(CodexExecAdapter.identity_modules)-set(documented_codex)),
   'extra_codex':sorted(set(documented_codex)-set(CodexExecAdapter.identity_modules)),
   'current_helpers':document_checks(paragraph),
   'scope':'actual class attributes and fixed document clause only; capability_identity was not invoked'}
assert len(identity_gap['actual_codex'])==14 and len(identity_gap['actual_claude'])==17
assert len(identity_gap['omitted_codex'])==7 and not identity_gap['extra_codex']
save('identity-module-mismatch.json',identity_gap)

c3=read(RUN/'phases/027/tasks/doc-policy/evidence/c3/report.json')
rows=[row for group in c3['reports'] for row in group['rows']]
docrows=[row for row in rows if row['id'].startswith('structure.test_doc_code.')]
assert len(docrows)==38 and len({x['id'] for x in docrows})==38
assert all(x['outcome']=='passed' for x in docrows)
assert set(c3['selected'])=={r['id'] for r in rows} and len(rows)==134
assert len(c3['source_sha256'])==875 and not c3['changed_during_run']
mismatches=[p for p,h in c3['source_sha256'].items() if sha(SCRIPTS/p)!=h]
assert not mismatches
process=read(RUN/'phases/027/tasks/doc-policy/evidence/final-c3-process.json')
save('reused-c3-verification.json', {'report':'run:phases/027/tasks/doc-policy/evidence/c3/report.json',
      'report_sha256':sha(RUN/'phases/027/tasks/doc-policy/evidence/c3/report.json'),
      'source_files':875,'source_mismatches':mismatches,'document_rows':docrows,
      'all_selected':134,'all_rows':134,'process':process,'reuse':'prior execution only; does not cover all bare names or all JSON fences'})
print(json.dumps({'pure_sections':len(observations),'json_templates':len(json_examples),'counterexamples':len(cases),
                  'prior_doc_rows':len(docrows),'prior_python_sha':875,'mismatches':mismatches,'roles':len(reading)},ensure_ascii=False))

import ast
import hashlib
import json
from pathlib import Path

REPO=Path('C:/math')
RUN=REPO/'docs/do-math/continuous-development-2026-10-13'
OUT=RUN/'phases/028/tasks/operator-names/evidence'
SCRIPTS=REPO/'.claude/skills/do-math/scripts'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def resolve(ref):
    root,p=ref.split(':',1)
    return (REPO if root=='repo' else RUN)/p.split('#')[0]

assigned=next(t for t in read(RUN/'phases/028/assignments.json')['tasks'] if t['task']=='operator-names')
profiles=read(OUT/'section-profiles.json');decisions=read(OUT/'section-decisions.json')
assert len(decisions)==66 and len({x['id'] for x in decisions})==66
assert {x['id'] for x in decisions}=={x['id'] for x in assigned['slices']}
assert len(read(OUT/'json-example-bindings.json'))==7
assert len(read(OUT/'minimal-counterexamples.json'))==4
sources={}
for d in decisions:
    p=resolve(d['document']);assert sha(p)==d['document_sha256']
    lines=p.read_text(encoding='utf-8-sig').splitlines();begin,end=d['current_lines']
    original=next(s for s in profiles if s['id']==d['id'])
    assert '\n'.join(lines[begin-1:end])==original['text']
    assert len(d['inline_occurrences'])==len(original['inline'])
    assert [(o['line'],o['column'],o['text']) for o in d['inline_occurrences']]==[(o['line'],o['column'],o['text']) for o in original['inline']]
    for owner in d['owners']:
        p=resolve(owner['path']);assert sha(p)==owner['sha256']
        if owner['path'] in sources:continue
        lines=p.read_text(encoding='utf-8-sig').splitlines();metadata={'sha256':sha(p),'lines':len(lines),'declarations':[]}
        if p.suffix=='.py':
            t=ast.parse('\n'.join(lines))
            for node in ast.walk(t):
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    metadata['declarations'].append({'name':node.name,'lines':[node.lineno,node.end_lineno]})
                elif isinstance(node,ast.Assign):
                    for target in node.targets:
                        if isinstance(target,ast.Name):metadata['declarations'].append({'name':target.id,'lines':[node.lineno,node.end_lineno]})
        sources[owner['path']]=metadata
for d in decisions:
    for owner in d['owners']:
        if resolve(owner['path']).suffix!='.py' or owner['symbol']=='module declarations and consumers':continue
        assert owner['symbol'].split('.')[-1] in {x['name'] for x in sources[owner['path']]['declarations']},owner
save('source-anchors.json',sources)

gap=read(OUT/'identity-module-mismatch.json')
assert resolve(gap['document']).read_text(encoding='utf-8-sig').splitlines()[gap['line']-1]==gap['quote']
assert len(gap['documented_codex'])==7 and len(gap['documented_claude'])==10
assert set(gap['omitted_codex'])=={'control_protocol','values','codex_stream','provider_final','control_server','worker_request','cli_execution'}
c3=read(OUT/'reused-c3-verification.json')
assert c3['process']['state']=='finished' and c3['process']['exit_code']==0
assert len(c3['document_rows'])==38 and c3['source_files']==875 and not c3['source_mismatches']

# Existing OS rows are reused only with the producer/consumer byte slice below.
os_reuse=[]
for ph,task,report_dir,row_prefix,required in [
 ('013','scheduler-smoke','canonical-related','smoke.test_scheduler_live.',
  ['operator_schedule.ps1','operator_bootstrap.py','do_math/scheduled_operator.py','tests/support/scheduler_live.py']),
 ('018','job-cleanup','c4','boundary.test_storage_atomic_replace.',
  ['do_math/file_io.py','tests/boundary/test_storage_atomic_replace.py'])]:
    root=RUN/f'phases/{ph}/tasks/{task}/evidence';path=root/report_dir/'report.json';data=read(path)
    rows=[r for group in data['reports'] for r in group['rows'] if r['id'].startswith(row_prefix)]
    assert rows and all(r['outcome']=='passed' for r in rows)
    source=read(root/'source-final.json');checks=[]
    for relative in required:
        repo_path='.claude/skills/do-math/scripts/'+relative
        current=sha(REPO/repo_path)
        assert source[repo_path]==current,(ph,relative)
        checks.append({'path':'repo:'+repo_path,'sha256':current})
        if relative.endswith('.py'):assert data['source_sha256'][relative]==current
    os_reuse.append({'phase':ph,'report':'run:'+path.relative_to(RUN).as_posix(),
                     'report_sha256':sha(path),'rows':rows,'matched_source_slice':checks,
                     'original_source':'run:'+ (root/'source-final.json').relative_to(RUN).as_posix(),
                     'original_source_sha256':sha(root/'source-final.json'),
                     'limit':'existing local OS boundary only; no new invocation, whole-edition equivalence, research/model success or universal filesystem support claim'})
save('external-name-reuse.json',os_reuse)

# Read the previous direct consumer reports only for the named stable modules,
# never adding their counts to current execution or reusing their whole edition.
consumer_reuse=[]
for ph,task,dirs,prefixes in [
 ('025','document-trust',['c2','c'],['unit.test_trust_environment.','unit.test_toolchain_records.']),
 ('024','document-waits',['c2','c'],['unit.test_storage_report_projections.','unit.test_engine_trace_report_corruption.'])]:
    root=RUN/f'phases/{ph}/tasks/{task}/evidence'
    existing=[root/d/'report.json' for d in dirs if (root/d/'report.json').is_file()]
    path=existing[0];data=read(path)
    rows=[r for group in data['reports'] for r in group['rows'] if any(r['id'].startswith(prefix) for prefix in prefixes)]
    stable_rows=[]
    for r in rows:
        if r['outcome']!='passed':continue
        parts=r['id'].split('.');test=parts[0]+'/'+parts[1]+'.py'
        if 'tests/'+test in data['source_sha256'] and sha(SCRIPTS/'tests'/test)==data['source_sha256']['tests/'+test]:
            stable_rows.append(r)
    relevant=['do_math/trust_inventory.py','do_math/trust_validation.py','do_math/formal.py'] if ph=='025' else ['do_math/reporting.py','do_math/trace_report.py','do_math/core_engine.py']
    matched=[]
    for key in relevant:
        assert data['source_sha256'][key]==sha(SCRIPTS/key),(ph,key)
        matched.append({'path':'repo:.claude/skills/do-math/scripts/'+key,'sha256':sha(SCRIPTS/key)})
    consumer_reuse.append({'report':'run:'+path.relative_to(RUN).as_posix(),'sha256':sha(path),'matched_production_slice':matched,
                           'same_test_file_rows':stable_rows,'scope':'unchanged exact consumer test file only; current helper and document bindings observed separately; no whole-run reuse'})
save('consumer-report-reuse.json',consumer_reuse)

input_changes=[]
for p in read(OUT/'input-profiles.json'):
    if sha(resolve(p['ref']))!=p['sha256']:input_changes.append(p['ref'])
assert not input_changes
save('verification.json',{'acceptance':'A1-A4 finite audit delivered; product defects remain follow-up findings',
    'sections':66,'inline_occurrences':sum(len(x['inline_occurrences']) for x in decisions),
    'json_templates':7,'pure_counterexamples':4,'identity_omissions':7,
    'source_owner_files':len(sources),'required_inputs_unchanged':len(read(OUT/'input-profiles.json')),
    'input_changes':input_changes,'prior_document_rows':38,'prior_python_sources':875,
    'new_official_test_runs':0,'external_rows':{x['phase']:len(x['rows']) for x in os_reuse}})
print(json.dumps(read(OUT/'verification.json'),ensure_ascii=False))

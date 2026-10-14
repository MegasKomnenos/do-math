import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
from audit import REPO, RUN, OUT, DOCS, write

BASE=REPO/'.claude/skills/do-math/scripts/do_math'
def assigned(path,name):
    for n in ast.parse(path.read_text(encoding='utf-8-sig')).body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets): return n.value
    raise AssertionError((path,name))
def sets(node):
    return {ast.literal_eval(k): set(ast.literal_eval(v)) if isinstance(v,ast.Set) else set() for k,v in zip(node.keys,node.values)}

common=(REPO/'.claude/skills/do-math/references/공통-실행.md').read_text(encoding='utf-8-sig')
operators=ast.literal_eval(assigned(BASE/'observations.py','OPERATORS'))
documented={op:{'subject_kind':kind,'source':source,'unit':unit} for op,kind,source,unit in re.findall(r'^\| `(\w+)` \| `(\w+)` \| `(\w+)`, `(\w+)` \|$',common,re.M)}
assert documented==operators
readiness=(REPO/'.claude/skills/do-math/references/과제-착수조건.md').read_text(encoding='utf-8-sig')
families=ast.literal_eval(assigned(BASE/'planning.py','RECORD_FAMILIES'))
listed=set(re.findall(r'`([^`]+)`',readiness.split('현재 기록 가족은',1)[1].split('이다.',1)[0]))
assert listed==set(families)
pointer_rows={k:set(re.findall(r'`([^`]+)`',rest)) for k,rest in re.findall(r'^\| `([^`]+)` \| (.+) \|$',readiness,re.M) if k in families}
exposed=sets(assigned(BASE/'planning.py','EXPOSED_FIELDS'))
assert pointer_rows==exposed
ops=sets(assigned(BASE/'planning.py','CONDITION_FIELDS'))
op_rows={op:set(re.findall(r'`([^`]+)`',rest)) for col,rest in re.findall(r'^\| (.+?) \| (.+) \|$',readiness,re.M) for op in re.findall(r'`([^`]+)`',col) if op in ops}
assert set(op_rows)==set(ops)
assert all(fields<=op_rows[op] for op,fields in ops.items())
models=ast.literal_eval(assigned(BASE/'model_policy.py','MODELS'))
modeltext=(REPO/'.claude/skills/do-math/references/모델과-실행예산.md').read_text(encoding='utf-8-sig')
modeltable={tier:(model,int(slots)) for tier,model,slots in re.findall(r'^\| [^`]+`(\w+)` \| `([^`]+)` \| (\d+) \|$',modeltext,re.M)}
assert {t:m for t,(m,n) in modeltable.items()}==models
assert all(n==3 for m,n in modeltable.values())
# LIMITS comprehension uses this literal 3; this is a source comparison only.
limits=assigned(BASE/'model_policy.py','LIMITS')
assert any(isinstance(n,ast.Constant) and n.value==3 for n in ast.walk(limits))
fences=json.loads((OUT/'occurrences.json').read_text(encoding='utf-8'))
fence_checks=[]
for o in fences:
    if o['kind']!='fence': continue
    if o['text'].lstrip().startswith('{'):
        value=json.loads(o['text'])
        fence_checks.append({'path':'repo:'+o['path'],'line':o['line'],'kind':'JSON','keys':list(value),'result':'parses',
                             'limit':'JSON decoding only; actual schema/consumption evidence is the assigned current owner/test.'})
    else:
        fence_checks.append({'path':'repo:'+o['path'],'line':o['line'],'kind':'PowerShell',
                             'result':'inspected','owner':'repo:.claude/skills/do-math/scripts/do_math/submission_tool.py',
                             'flags':['--output','--submit','--wait-seconds'],'limit':'No command executed; actual Python comes from submission_contract.command.'})

# Reuse exact published rows, and check each reported Python hash against this
# fixed edition. Selected passes do not certify the other tests/doc semantics.
report_path=RUN/'phases/025/tasks/document-trust/evidence/c2/report.json'
report=json.loads(report_path.read_text(encoding='utf-8-sig'))
sha_diff=[p for p,h in report['source_sha256'].items() if hashlib.sha256((REPO/'.claude/skills/do-math/scripts'/p).read_bytes()).hexdigest()!=h]
assert not sha_diff
rows=[row for group in report['reports'] for row in group.get('rows',[]) if row['id'].startswith('structure.test_doc_code.')]
assert len(rows)==33 and all(row['outcome']=='passed' for row in rows)
assert report['complete'] and report['successful'] and not report['changed_during_run']
write('reused-rows.json', {'original':'run:phases/025/tasks/document-trust/evidence/c2/report.json',
                         'original_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),
                         'python_files':len(report['source_sha256']),'current_hash_mismatches':sha_diff,'rows':rows,
                         'scope':'025 기존 실행을 읽은 근거. 026 신규 통과가 아니며 standalone 이름 전체 의미를 33 green으로 승인하지 않는다.'})

# Preserve actual read-only Git diff for the finite PR24/document-name slice.
baseline=json.loads((RUN/'sources/baseline.json').read_text(encoding='utf-8-sig'))['head']
paths=[f'.claude/skills/do-math/references/{d}.md' for d in DOCS]
diff=subprocess.run(['git','diff',baseline,'--',*paths],cwd=REPO,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(OUT/'document-history.diff').write_bytes(diff.stdout)
(OUT/'document-history.stderr').write_bytes(diff.stderr)
assert diff.returncode==0

phase=json.loads((RUN/'phases/026/phase.json').read_text(encoding='utf-8-sig'))
inputs=next(t for t in phase['tasks'] if t['id']=='reference-names')['inputs']
protected={}
for ref in inputs:
    root=REPO if ref.startswith('repo:') else RUN
    path=root/ref.split(':',1)[1]
    protected[ref]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
for name in ['context.md','plan.md','seams.md','phases/026/phase.json','phases/026/tasks/reference-names/objective.md']:
    p=RUN/name
    protected['run:'+name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
for name in ['phases/001/tasks/document-closeout/evidence/source-census.json',
             'phases/025/tasks/document-trust/evidence/c2/report.json',
             'phases/025/tasks/document-trust/evidence/binding-review.md',
             'phases/025/tasks/document-trust/evidence/history-verification.json',
             *['phases/025/tasks/document-trust/evidence/B'+str(n)+'-doc-code.diff' for n in range(110,115)]]:
    p=RUN/name
    protected['run:'+name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
for row in json.loads((OUT/'decisions.json').read_text(encoding='utf-8')):
    for ref in row['definitions_and_consumers']+row['current_test_sources']:
        p=REPO/ref['path'][5:]
        protected[ref['path']]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
write('inputs-read.json',protected)
write('static-checks.json',{'operators':{'count':len(operators),'equal':True},'condition_ops':{'count':len(ops),'equal':True},
                          'families':{'count':len(families),'equal':True},'exposed_fields':{'families':len(exposed),'equal':True},
                          'model_defaults':{'equal':True,'table':modeltable},'fences':fence_checks,
                          'published_python_hashes_equal':len(report['source_sha256']), 'reused_doc_rows':len(rows),
                          'git_diff':{'exit_code':diff.returncode,'baseline':baseline},
                          'scope':'stdlib AST/literal/text/JSON comparisons only. No product module, official test, mirror generator or external provider was executed.'})
print('PASS: tables 6 operators /',len(ops),'conditions /',len(families),'families;',len(fence_checks),'fences;',len(rows),'existing doc rows;',len(report['source_sha256']),'current Python hashes')

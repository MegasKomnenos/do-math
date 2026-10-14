from work import *
import ast
owners={'import_payload','import_check','governance','academic_validation'}
packets=json.loads((RUN/'phases/001/tasks/document-closeout/evidence/followup-packets.json').read_text(encoding='utf-8-sig'))
save('packets.json',[p for p in packets['packets'] if p['id'] in ('P06','P10')])
inventory=json.loads((RUN/'phases/001/tasks/document-closeout/evidence/binding-inventory.json').read_text(encoding='utf-8-sig'))
save('bindings.json',[p for p in inventory['bindings'] if p.get('owner') in owners])
names=json.loads((RUN/'phases/022/tasks/review-delivery/evidence/section-name-decisions.json').read_text(encoding='utf-8-sig'))
save('previous-revision-names.json',[p for p in names if p['section']=='N02-014' and p['token'] in
    ('impact_set','previous_hashes','revision_requests','revision_resolutions')])
skill=REPO/'.claude/skills/do-math'
sections=[]
for name,titles in {
    '입력-소비자.md':['# 사용자 입력을 받을 소비자','## charter, policy, research_context, additional_audit'],
    '초기화-운전.md':['## 6. 최초 해석·독립 검사·실제 적용을 확인한다'],
    'CLI-실행-계약.md':['### 목표와 학술 후속 상태','### 검사된 수입의 사용자 승인'],
    '공통-실행.md':['## 예정된 개정과 이번 실행의 책임을 확인한다']}.items():
    lines=(skill/'references'/name).read_text(encoding='utf-8').splitlines()
    for title in titles:
        matches=[i for i,line in enumerate(lines) if line==title]
        if not matches:
            matches=[i for i,line in enumerate(lines) if line.startswith('#') and title.lstrip('# ') in line]
        assert len(matches)==1,(name,title,matches)
        begin=matches[0]
        end=next((i for i in range(begin+1,len(lines)) if lines[i].startswith('#')),len(lines))
        sections.append({'document':'repo:.claude/skills/do-math/references/'+name,
            'heading':lines[begin],'start_line':begin+1,'end_line':end,'text':'\n'.join(lines[begin:end]),
            'sha256':digest(skill/'references'/name)['sha256']})
save('current-sections.json',sections)
modules=['unit/test_governance_decision_basis.py','unit/test_knowledge_impact_review.py',
 'unit/test_submission_extension_semantics.py','unit/test_planning_revision_validation.py',
 'sim/test_planning_revision_transitions.py','sim/test_planning_revision_obligations.py']
tests=[]
for module in modules:
    path=skill/'scripts/tests'/module
    text=path.read_text(encoding='utf-8'); lines=text.splitlines()
    for cls in ast.parse(text).body:
        if not isinstance(cls,ast.ClassDef): continue
        for method in cls.body:
            if isinstance(method,ast.FunctionDef) and method.name.startswith('test_'):
                code='\n'.join(lines[method.lineno-1:method.end_lineno])
                tests.append({'id':module[:-3].replace('/','.')+'.'+cls.name+'.'+method.name,
                    'line':method.lineno,'tokens':[t for t in ('impact_set','previous_hashes','revision_requests','revision_resolutions') if t in code],
                    'code':code,'source_sha256':digest(path)['sha256']})
save('revision-tests.json',tests)
print('Packets 2; sections',len(sections),'revision tests',len(tests))
for row in tests:
    if row['tokens']: print(row['id'],','.join(row['tokens']))

from work import *
import ast
tests=REPO/'.claude/skills/do-math/scripts/tests'
selected=[]; consumers=[]
for path in tests.rglob('test_*.py'):
    if path.parent.name not in ('structure','unit','contracts','sim','flows','boundary'): continue
    text=path.read_text(encoding='utf-8')
    tree=ast.parse(text)
    names={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
    if {'field_schemas','scoped_field_issues'} & names:
        name='.'.join(path.relative_to(tests).with_suffix('').parts)
        selected.append(name)
        consumers.append({'id':name,'sha256':digest(path)['sha256'],
                          'reason':'Actual field_schemas/scoped_field_issues document walker; both new deferred owners must retain their exact assigned document checks.'})
selected += ['unit.test_planning_conditions','unit.test_planning_condition_validation',
    'sim.test_scheduling_session_slots.PlanSettleTests',
    'sim.test_scheduling_session_slots.ReadinessResponsibilityTests',
    'sim.test_engine_input_overflow','flows.test_engine_input_recovery',
    'sim.test_scheduling_recovery_dispositions','unit.test_repair_execution',
    'unit.test_submission_extension_semantics','unit.test_governance_question_contracts',
    'unit.test_governance_questions','sim.test_governance_questions','flows.test_governance_question_flow',
    'sim.test_scheduling_close_preparation.PinnedAuthorityTests',
    'unit.test_review_research_owner_contract','sim.test_submission_review_inputs',
    'boundary.test_review_source_restoration']
# Use actual declared class names rather than guessing an authority selector.
authority=ast.parse((tests/'sim/test_scheduling_close_preparation.py').read_text(encoding='utf-8'))
for cls in authority.body:
    if isinstance(cls,ast.ClassDef) and any(isinstance(n,ast.FunctionDef) and n.name=='test_a_new_grant_does_not_replace_a_revoked_pinned_authority' for n in cls.body):
        selected[-4]='sim.test_scheduling_close_preparation.'+cls.name
selected=list(dict.fromkeys(selected))
prior=json.loads((RUN/'phases/023/tasks/document-governance/evidence/related-selection.json').read_text(encoding='utf-8'))
excluded=[]
for name in prior:
    if name in selected: continue
    path=tests/('/'.join(name.split('.')[:2])+'.py')
    text=path.read_text(encoding='utf-8')
    excluded.append({'id':name,'source_sha256':digest(path)['sha256'],
        'direct_document_walk_consumer':any(x in text for x in ('field_schemas','scoped_field_issues')),
        'reason':'No changed field_schemas/scoped_field_issues consumer. Existing helper/producers for P01-P07/P10 remain unchanged except added wait helper; 023 exact property evidence remains valid. Final whole gates remain separate.'})
save('related-selection.json',selected)
save('selection-decisions.json',{'consumers':consumers,'selected':selected,'excluded_023':excluded,
    'reason':'Select current document walkers, both assigned wait owners, direct condition/settling/retry/question scenes and unchanged single-proposal restoration guards. This is not the previous fixed 460-test union.'})
print(json.dumps(selected,ensure_ascii=False,indent=2))

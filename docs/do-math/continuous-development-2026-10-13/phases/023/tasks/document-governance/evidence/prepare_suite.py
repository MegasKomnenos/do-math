from work import *
import ast
old=json.loads((RUN/'phases/022/tasks/review-delivery/evidence/related-selection.json').read_text(encoding='utf-8-sig'))
excluded=['unit.test_review_cycle_stages','unit.test_review_research_slots',
 'sim.test_review_research_replay_evidence','flows.test_review_research_flows',
 'unit.test_review_transcript_contract','unit.test_review_engine_transcripts',
 'unit.test_review_engine_stages','flows.test_review_owner_flows']
added=['unit.test_governance_imports','unit.test_governance_records','unit.test_academic_requirements',
 'sim.test_governance_interpretation','sim.test_governance_context','sim.test_academic_consumers',
 'sim.test_academic_assessment_flow','sim.test_academic_public_currentness','flows.test_academic_requirement_flows',
 'unit.test_governance_decision_basis','unit.test_knowledge_impact_review','unit.test_submission_extension_semantics',
 'unit.test_planning_revision_validation','sim.test_planning_revision_transitions','sim.test_planning_revision_obligations']
ids=list(dict.fromkeys([i for i in old if i not in excluded]+added))
save('related-selection.json',ids)
decisions=[]
for module in excluded:
    path=REPO/'.claude/skills/do-math/scripts/tests'/Path(module.replace('.','/')+'.py')
    original=(E/'start.json')
    source=path.read_text(encoding='utf-8')
    imports=[ast.unparse(n) for n in ast.walk(ast.parse(source)) if isinstance(n,ast.ImportFrom)
        and n.module and n.module.startswith('support.')]
    assert 'scoped_field_issues' not in source and 'field_schemas' not in source
    decisions.append({'module':module,'source_sha256':digest(path)['sha256'],'imports':imports,
        'reason':'No field_schemas/scoped_field_issues consumer. Its review_cycle/review_engine/transcript/replay/overflow behavior and the called review helpers are unchanged. Existing 022 evidence is reused for those exact properties; final-seat single-body and exact-source coverage remain in sim.test_submission_review_inputs and boundary.test_review_source_restoration. P04/P05 document owner methods remain in unit.test_review_research_owner_contract and sim.test_submission_review_inputs.'})
save('selection-decisions.json',{'selected_modules':ids,'excluded_previous_modules':decisions,
    'reason':'Retain every owner document walk and its real assigned check, P01-P05/P07 delivery/packaging/restoration, and add the specified import/governance/academic/revision consumers. The final suite is determined from shared-helper impact, not a fixed accumulation of all historical selections.'})
sys.path.insert(0,str(REPO/'.claude/skills/writing-skills/scripts'))
import build_skill_mirrors as build
rules=build.load_rules(REPO/'.agents/diff')
allowed=json.loads((RUN/'phases/023/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
planned=[]
for rel,path in build.iter_files(REPO/'.claude/skills').items():
    target=REPO/'.agents/skills'/rel; overlay=REPO/'.agents/diff'/rel
    transformed=overlay.read_bytes() if overlay.is_file() else build.transform(rel,path.read_bytes(),rules)
    if not target.exists() or transformed!=target.read_bytes(): planned.append(target.relative_to(REPO).as_posix())
assert set(planned)<=set(allowed),set(planned)-set(allowed)
save('mirror-plan.json',{'changes':planned,'all_within_writes':True})
print('Final modules',len(ids),'excluded unrelated review modules',len(excluded),'authorized mirror changes',len(planned))

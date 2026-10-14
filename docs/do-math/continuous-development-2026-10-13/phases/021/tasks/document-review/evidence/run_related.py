from work import *
ids=['unit.test_review_cycle_stages','unit.test_review_research_owner_contract',
     'unit.test_review_research_slots','sim.test_submission_review_inputs',
     'sim.test_review_research_replay_evidence','flows.test_review_research_flows',
     'boundary.test_review_source_restoration','structure.test_doc_code',
     'sim.test_role_input_context','unit.test_submission_preview_commands',
     'sim.test_knowledge_project_identity','unit.test_role_input_packaging',
     'unit.test_role_input_scoped_packaging','unit.test_preflight','unit.test_context_catalog',
     'sim.test_submission_receiver','flows.test_submission_acceptance',
     'unit.test_storage_report_projections','unit.test_engine_trace_report_corruption',
     'unit.test_storage_record_queries','boundary.test_engine_cli',
     'sim.test_knowledge_currentness.RecoveryMaterialTests',
     'flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests']
save('related-selection.json',ids)
name,tree=sys.argv[1:]
command(name,[PY,'-u','-B',str(REPO/tree/'skills/do-math/scripts/run_tests.py'),*ids,
              '--jobs','1','--output',str(E/name)])

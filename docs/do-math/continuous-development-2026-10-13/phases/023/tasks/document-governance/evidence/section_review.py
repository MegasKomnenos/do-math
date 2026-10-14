from work import *
import ast
skill=REPO/'.claude/skills/do-math'
decisions=[
 {'token':'impact_set','owner':'do_math/integration.py',
  'symbols':['inspect_bundles','bundle_impact_request','protocol_output'],
  'tests':['unit.test_knowledge_impact_review.ImpactBundleTests.test_only_an_impact_beyond_the_computed_closure_needs_independent_review',
           'unit.test_knowledge_impact_review.ImpactBundleTests.test_ordinary_execution_source_dependency_still_propagates',
           'unit.test_knowledge_impact_review.ImpactBundleTests.test_coupled_changes_use_the_single_reviewed_s0_plan',
           'unit.test_knowledge_impact_review.ImpactBundleTests.test_bundle_level_reviewed_effect_is_applied_once'],
  'decision':'Maintain: declarations supplement the computed transitive closure. A missed computed dependent still enters the machine plan; an extra declared dependent requires independent scoped review. The review is sealed by actual central capture and read back from the actual repository. One coupled S0 plan and one bundle-level effect are applied. This is the precise quoted meaning, not mathematical independence of arbitrary bundles.'},
 {'token':'previous_hashes','owner':'do_math/integration.py','symbols':['inspect_bundles','bundle_impact_request'],
  'tests':['unit.test_knowledge_impact_review.ImpactBundleTests.test_previous_hashes_cover_the_exact_current_mutation_targets',
           'unit.test_knowledge_impact_review.ImpactReviewTests.test_request_cannot_relabel_the_original_producer_snapshot',
           'unit.test_knowledge_impact_review.ImpactReviewTests.test_review_resolver_uses_actual_git_bytes_and_scoped_receipt',
           'unit.test_knowledge_impact_review.ImpactReviewTests.test_sealed_review_allows_real_domain_git_retry_and_rejects_wrong_evidence'],
  'decision':'Maintain and supplement: fixed-input hashes are compared by inspect_bundles; the actual impact-request consumer rechecks current semantic hashes and the original producer snapshot. Added narrow direct normal/missing/changed-hash cases for each actual mutation target without changing the source state. Existing actual Git-byte review resolution and domain retry tests preserve exact assignment/currentness. No runtime/hash rule was changed.'},
 {'token':'revision_requests','owner':'do_math/revisions.py','symbols':['submission_errors'],
  'tests':['unit.test_planning_revision_validation.RevisionSubmissionTests.test_duplicate_request_has_exact_issue_and_no_mutation',
           'unit.test_planning_revision_validation.RevisionSubmissionTests.test_unknown_request_has_exact_issue_and_no_mutation',
           'unit.test_planning_revision_validation.RevisionSubmissionTests.test_same_task_cannot_be_selected_and_requested_for_revision',
           'sim.test_planning_revision_transitions.RevisionTransitionTests.test_followup_request_enqueues_captured_targets_without_an_original_declaration'],
  'decision':'Maintain and strengthen the existing transition: a request names supplied tasks/knowledge and asks for future preparation. protocol_output excludes requests from mutation_members and permits one default atomic bundle for a request-only response. The actual followup creates a research_preparation action with exact captured targets and requester execution; an added before/after assertion proves the existing task stays unchanged. Existing shape/ownership/duplicate/selection rejection is retained.'},
 {'token':'revision_resolutions','owner':'do_math/revisions.py','symbols':['submission_errors'],
  'tests':['unit.test_planning_revision_validation.RevisionSubmissionTests.test_missing_resolution_has_exact_issue_and_no_mutation',
           'unit.test_planning_revision_validation.RevisionSubmissionTests.test_required_unchanged_has_exact_issue_and_no_mutation',
           'unit.test_planning_revision_validation.RevisionSubmissionTests.test_revised_without_write_has_exact_issue_and_no_mutation',
           'sim.test_planning_revision_transitions.RevisionTransitionTests.test_optional_unchanged_child_resolves_parent_exactly_once',
           'sim.test_planning_revision_transitions.RevisionTransitionTests.test_partial_resolution_preserves_remaining_target_and_detached_basis',
           'sim.test_planning_revision_obligations.RevisionObligationTests.test_delegated_work_and_review_do_not_block_on_own_obligation'],
  'decision':'Maintain: resolutions are mutation members and require explicit grouping. Exactly one disposition binds each declared target, actual revised output is required, a mandatory/rejected repair cannot be cancelled as unchanged, and partial/delegated work retains its remaining parent obligation and ownership. Existing pure admission and real engine/store transitions are sufficient for these exact sentences; no duplicate rules were implemented.'}]
previous=json.loads((E/'previous-revision-names.json').read_text(encoding='utf-8'))
for row in decisions:
    row['section']='N02-014'
    row['sentences']=next(r['sentences'] for r in previous if r['token']==row['token'])
    path=skill/'scripts'/row['owner']; tree=ast.parse(path.read_text(encoding='utf-8'))
    defined={n.name for n in tree.body if isinstance(n,ast.FunctionDef)}
    assert set(row['symbols'])<=defined
    row['owner_sha256']=digest(path)['sha256']
    for test_id in row['tests']:
        module,cls,method=test_id.rsplit('.',2)
        source=skill/'scripts/tests'/Path(module.replace('.','/')+'.py')
        tree=ast.parse(source.read_text(encoding='utf-8'))
        node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
        assert any(isinstance(n,ast.FunctionDef) and n.name==method for n in node.body),test_id
save('section-name-decisions.json',{'decisions':decisions,
 'fixed_sections':json.loads((E/'current-sections.json').read_text(encoding='utf-8')),
 'limit':'Six related sections and four N02-014 names only. This does not complete the four entire N sections, all N references, P08/P09/P11, input_overflow/question_links, operational scope/replay_safety/repair_target, L01 or final G gates.'})
print('Bounded decisions',len(decisions),'six fixed sections; exact existing methods and current product definitions confirmed')

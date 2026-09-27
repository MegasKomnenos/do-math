"""Shards and isolation labels for do-math tests.

``SHARDS`` is the one list of which test module runs in which shard;
``run_tests.py`` refuses to run while a ``tests/test_*.py`` module is missing
from it or it names a module that does not exist. The time targets (each shard
alone within 120 s, all shards in sequence within 300 s) and when to run what
are in ``tests/시험-지침.md``.

``test_group('lean')`` and ``test_group('resource')`` mark tests that call the
real Lean toolchain or manage real process lifetimes and resources; the runner
runs them per class in an owned Windows Job with a deadline.
``test_group('in_process')`` on a method runs it in process although its class
is marked.
"""
from pathlib import Path

SHARDS = {name: frozenset(modules.split()) for name, modules in {
    'foundation': '''
        test_academic test_boundary_repairs test_budget test_claude_adapter test_claude_stream
        test_codex_adapter test_completion_settlement test_context_store test_contract_checks
        test_contracts test_control_preview test_control_transport_io test_current_contract
        test_decision_basis test_delegation_storage test_digest_characterization
        test_environment_validation test_execution_observation_profile test_execution_window
        test_file_io test_formal_input_manifest test_git_store test_impact_bundle test_knowledge
        test_knowledge_import_engine test_knowledge_io test_machine_scheduling
        test_model_metadata_boundary test_model_runner test_observation_audit1 test_observations
        test_performance_repairs test_performance_save test_planning test_preparation_cache
        test_provider_final_contract test_query_records test_questions test_reading_map
        test_redesign_ACTIVITIES test_redesign_CONTRACTS test_redesign_EVIDENCE
        test_redesign_EVIDENCE_binding test_redesign_EVIDENCE_host test_redesign_EVIDENCE_run
        test_redesign_EVIDENCE_scope test_redesign_EVIDENCE_walkthroughs test_redesign_GOVERNANCE
        test_redesign_KNOWLEDGE test_redesign_LIFECYCLE test_redesign_OBSERVATION
        test_redesign_PROFILES test_redesign_REVIEWS test_redesign_STORAGE test_redesign_SURFACE
        test_redesign_TASKS test_reference_catalog test_relation_dependencies test_repair_execution
        test_repair_plan test_reporting test_repository test_review_cycle test_review_scope_wire
        test_revision_obligations test_scholarly test_standalone test_state_checks
        test_state_contract_registration test_storage_validation test_task_scope test_test_runner
        test_trust_continuation test_unicode_flow test_walkthrough_contract_repairs
        test_walkthrough_repairs''',
    'host': '''
        test_background_processes test_diagnosed_installation_recovery test_external test_formal
        test_formal_runtime test_host_resources test_launch_recovery test_lean_preview
        test_machine_parallel test_operator test_operator_bootstrap test_preflight test_probe_cli
        test_provider_wait test_schedule_lifetime test_schedule_pythonw test_windows_job
        test_worker_temporary_outputs''',
    'lifecycle': '''
        test_checkpoint_persistence test_cli test_cli_advanced test_connection_repairs
        test_control_shapes test_controls test_document_followup test_efficiency test_engine
        test_governance_engine test_initial_intent_connection test_initialization_efficiency
        test_initialization_probe_batch test_initialization_review_repairs test_input_recovery
        test_lifecycle_engine test_observation_admission test_provider_recovery
        test_redesign_ENGINE test_research_reliability test_six_connections
        test_static_review_repairs test_stop_flags''',
    'research': '''
        test_currentness_recovery test_purpose_engine test_research_recovery test_run_feedback
        test_session_scheduler''',
    'review': '''
        test_native_final_submission test_question_flow test_review_engine test_review_research
        test_submission_boundaries test_submission_flow test_submission_tools
        test_walkthrough_followup''',
    'academic': '''
        test_academic_engine test_academic_preparation test_approved_five_repairs
        test_lifecycle_currentness test_model_assessment_flow''',
}.items()}
LABELS = ('lean', 'resource', 'in_process')
_SHARD_OF = {module: name for name, modules in SHARDS.items() for module in modules}


def unregistered_modules(tests_dir):
    """(test modules on disk missing from SHARDS, SHARDS entries with no module on disk)."""
    present = {path.stem for path in Path(tests_dir).glob('test_*.py')}
    return sorted(present - _SHARD_OF.keys()), sorted(_SHARD_OF.keys() - present)


def test_group(label):
    if label not in LABELS:
        raise ValueError('unknown test label: ' + str(label))
    def decorate(target):
        target.do_math_test_group = label
        return target
    return decorate


def isolation_for(test):
    """'lean' or 'resource' when the test must run isolated, else None; a method label overrides its class."""
    method = getattr(test, getattr(test, '_testMethodName', ''), None)
    label = getattr(method, 'do_math_test_group', None) or getattr(type(test), 'do_math_test_group', None)
    return None if label in (None, 'in_process') else label


def shard_for(test):
    return _SHARD_OF[type(test).__module__.split('.')[-1]]

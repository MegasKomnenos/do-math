"""Role-input and source-catalog test helpers: a review state for the real engine, and catalog file opens.

- ``review_candidate_state(root)``: ``(instance, runtime, scope)``, the state
  ``review_fixtures.ReviewFakeEngine`` builds for its engine double (one
  candidate theorem ``K1`` with verified formal evidence and a review policy),
  without the double: the engine that reads it is the product's, on a
  repository that validated it.
- ``catalog_opens(events, workspace)``: which source catalog files a block
  opened and how, from ``support.storage_files.audit_events('open')``.
"""
from copy import deepcopy
import hashlib
import os
from pathlib import Path


def catalog_opens(events, workspace):
    """``[(file name, mode)]`` of the audit ``open`` events for files in ``workspace/input/catalog``.

    The mode is the raw file mode Python reports: ``x`` creates a new file, ``r`` reads one.
    """
    folder = Path(workspace) / 'input' / 'catalog'
    return [(Path(str(arguments[0])).name, arguments[1]) for _, arguments in events
            if isinstance(arguments[0], (str, os.PathLike)) and Path(str(arguments[0])).parent == folder]


def review_candidate_state(root, rounds=2):
    """``(instance, runtime, scope)``: candidate theorem ``K1`` with verified formal evidence and a review policy.

    ``scope`` is the settled scope a review of ``K1`` begins with
    (``research_fixtures.start_scoped_review``). The synthetic trust toolchain
    is written under ``root``.
    """
    from do_math import knowledge_io, knowledge_records as kr
    from do_math.configuration import DEFAULT_CONFIG
    from do_math.execution_profiles import build_profiles
    from research_fixtures import governance_start, trust_environment, trust_fixture
    source = 'theorem sample : 1 = 1 := rfl'
    policy = {'id': 'fixture-review-policy-v5', 'required_perspectives': [],
              'minimum_initial_slots': 2, 'judge_slots': ['judge-0', 'judge-1', 'judge-2'],
              'round_limit': rounds, 'activity_execution_limit': 24, 'overflow_disposition': 'unresolved'}
    scope = {'assessment_id': 'fixture-scope', 'policy_id': policy['id'],
             'required_perspectives': [], 'initial_slots': [
                 {'id': 'initial-0', 'perspective': 'formal', 'required_source_refs': ['proposal']},
                 {'id': 'initial-1', 'perspective': 'semantic', 'required_source_refs': ['proposal']}],
             'selected_profile_ref': None, 'activity_execution_limit': 24, 'overflow_disposition': 'unresolved'}
    instance = governance_start({'config': {'reviewers': 2,
                                            'review_research_limit': DEFAULT_CONFIG['review_research_limit']}})
    runtime = {'queue': [], 'executions': {}, 'questions': []}
    instance = knowledge_io.ensure_ontology(instance)
    profiles = build_profiles(DEFAULT_CONFIG)
    instance.update(execution_profiles=profiles['execution_profiles'], role_profile_refs=profiles['role_profile_refs'])
    instance['review_policy'] = deepcopy(policy)
    trusted = trust_fixture(Path(root), ['fixture-review-lean'])
    environment, binding = trust_environment(trusted, environment_id='TE-review', source_ref='fixture-review-trust')
    instance.update(active_trust_environment='TE-review', trust_environments={'TE-review': environment})
    runtime['trust_bindings'] = {'TE-review': binding}
    definition = next(row for row in instance['kind_definitions'].values() if row['token'] == 'theorem')
    instance, _ = kr.create_candidate(instance, {
        'id': 'K1', 'statement': 'One equals one', 'explanation': 'Reflexivity', 'summary': 'A sample theorem',
        'lean_code': source, 'declaration_names': ['sample'], 'dependencies': [], 'producer_execution': 'author',
        'revision': 1, 'kind': 'theorem', 'kind_definition_id': definition['id']},
        source_ref='test-fixture', actor_ref='author')
    proof = {'status': 'verified', 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
             'declarations': ['sample'], 'axioms': {'sample': []}, 'toolchain': deepcopy(trusted['toolchain']),
             'execution_id': 'formal-1', 'artifact_ref': 'artifacts/formal-1.json',
             'dependency_closure': {'sample': []}, 'dependency_evidence': {},
             'declaration_evidence': {'sample': {'type': 'fixture-type', 'value': 'fixture-proof'}}}
    instance = kr.record_formal_result(instance, 'K1', proof, 'TE-review', runtime=runtime)
    return instance, runtime, scope

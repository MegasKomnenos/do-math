"""Persisted-state inspection (``state_checks``, layer 2) and the load-time state contract, on records made by domain producers.

``inspect_state`` receives loaded states, so a condition the state contract
checks when a state loads is asserted against ``default_state_contract``
(``assertRejectedAtLoad``) and the inspection only reports what a loaded state
can still get wrong. The batch-read rules of the ``record_storage`` area take
their readers as arguments. The engine's entry inspection and its ``check``
(``core_engine``, layer 2) run on the real engine over a real repository on the
in-process Git fake; artifact bytes that differ from their seal are made by
another writer's commit (``rewrite_commit``), since the product never
publishes them.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

import jsonschema

from do_math import external, knowledge_records
from do_math.context_store import prefetch_artifacts
from do_math.engine import ResearchEngine
from do_math.git_store import GitStateStoreError
from do_math.state_checks import inspect_state
from do_math.state_contract import default_state_contract
from support.record_builders import surface_state
from support.state_builders import current_state
from support.fakes.clock import FakeClock
from support.storage_git import ObservedGit, rewrite_commit
from support.storage_records import INSTANCE_ID, fake_ports, record_store


def storage_state(refs):
    return ({"sources": []},
            {"executions": {"EX-1": {"id": "EX-1", "output_files": refs}}})


def artifact(path, raw, **changes):
    return {"artifact_ref": path, "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), **changes}


def archived_role_input(bundle, snapshot, files):
    """The manifest of a maintenance role input archived once below ``runtime/artifacts/<bundle>``.

    Each row names its archived bytes (prompt at ``input.txt``); ``files``
    receives those bytes.
    """
    prefix = 'runtime/artifacts/' + bundle + '/'

    # A document row carries its own ``path`` field, so the archive location has another name.
    def row(archived, raw, **fields):
        files[prefix + archived] = raw
        return {**fields, **artifact(prefix + archived, raw)}
    return {'role': 'maintenance', 'snapshot': snapshot,
            'output_contract': {'id': 'do-math-cli/5'}, 'prompt': row('input.txt', b'exact prompt'),
            'direct': [row('input/catalog/' + key + '.json', b'{}\n', key=key)
                       for key in ('snapshot', 'governance', 'execution_profile', 'action')],
            'documents': [row('input/implementation/' + path, path.encode() + b'\n', path=path)
                          for path in ('SKILL.md', 'GLOSSARY.md')],
            'references': []}


def at_load(instance, runtime):
    """The domain-produced state as the repository validates it: object format and current lifecycle gate."""
    runtime = {key: value for key, value in runtime.items() if key != 'status'}
    return current_state({**instance, 'object_format': 'sha1'}, runtime)


class StateCheckTests(unittest.TestCase):
    """``inspect_state`` receives loaded states; conditions loading checks are asserted at load."""

    def assertRejectedAtLoad(self, instance, runtime, pattern):
        instance, runtime = at_load(instance, runtime)
        with self.assertRaisesRegex(ValueError, pattern):
            default_state_contract().validate(instance, runtime)

    def area(self, instance, runtime, name):
        return inspect_state(instance, runtime, requested_areas=[name])

    def assertError(self, instance, runtime, text, area):
        errors = self.area(instance, runtime, area)['findings']
        self.assertTrue(any(text in row['message'] for row in errors), errors)

    def test_active_environment_uniqueness_is_an_inspection_condition(self):
        """T3 about 0.25 s: two actual synthetic toolchain records and the installed state contract."""
        from support.trust_inputs import trust_environment, trust_fixture
        instance, runtime = surface_state()
        with tempfile.TemporaryDirectory() as directory:
            for identifier in ('TE-one', 'TE-two'):
                environment, binding = trust_environment(trust_fixture(Path(directory), [identifier]),
                    environment_id=identifier, status='active')
                instance['trust_environments'][identifier] = environment
                runtime.setdefault('trust_bindings', {})[identifier] = binding
            instance['active_trust_environment'] = 'TE-one'
            default_state_contract().validate(*at_load(instance, runtime))
            report = self.area(instance, runtime, 'governance_trust')
            self.assertEqual(report['status'], 'blocked')
            self.assertIn('active trust environment is not unique or does not match pointer',
                          [row['message'] for row in report['findings']])

    def test_terminal_task_worker_and_transferred_obligation_are_inspected(self):
        """T3 about 14.1 s including the existing transfer Sim; inspection needs a real closed assessment."""
        from support.governance_cases import transfer_sim, transfer_output
        sim = transfer_sim()
        engine = sim.engine
        from do_math.task_scope import apply_task_assessments
        engine.instance, engine.runtime = apply_task_assessments(sim.instance, sim.runtime,
            transfer_output(sim)['task_assessments'], execution_id='EX-close-transfer-plan',
            input_tasks=deepcopy(sim.runtime['tasks']), clock=sim.clock)
        live = engine._register_execution({'id': 'AC-terminal-worker', 'role': 'research_work',
            'target': 'TK-close-source'}, {'id': 'EX-terminal-worker', 'role': 'research_work', 'status': 'running'})
        self.assertIsNotNone(live)
        instance, runtime = deepcopy((sim.instance, sim.runtime))
        runtime['tasks']['TK-close-target']['completion_obligations'] = [row for row in
            runtime['tasks']['TK-close-target']['completion_obligations'] if not row['id'].startswith('INHERITED-')]
        engine.store.validate_candidate(instance, runtime)
        report = self.area(instance, runtime, 'tasks_activities_executions')
        self.assertEqual(report['status'], 'blocked')
        messages = [row['message'] for row in report['findings']]
        self.assertIn('terminal task has a live worker', messages)
        self.assertIn('transferred obligation target is absent', messages)

    def test_completed_academic_resolution_requires_bytes_and_current_evidence(self):
        """T3 about 46.3 s including the existing solved academic consumer and actual resolution producer."""
        from support.academic_resolution_cases import rejection_case
        sim, eid, resolution = rejection_case()
        engine = sim.engine
        path, raw = 'runtime/artifacts/AB-academic/response.txt', b'External response e\xcc\x81\r\n'
        engine._save({path: raw})
        engine._apply_academic_resolutions({'role': 'research_plan'}, eid,
            [{**resolution, 'evidence_refs': [path, *resolution['evidence_refs']]}])
        engine._save()
        instance, runtime = deepcopy((sim.instance, sim.runtime))
        runtime['status'] = 'completed'
        before = deepcopy((instance, runtime))
        omitted = inspect_state(instance, runtime, requested_areas=['mathematical_effect'])
        self.assertEqual(omitted['status'], 'incomplete')
        self.assertIn('current academic resolution artifact bytes', omitted['areas'][0]['not_checked'])
        reads = []
        def read(ref):
            reads.append(ref)
            return engine.store.read(ref, engine.head)
        report = inspect_state(instance, runtime, requested_areas=['mathematical_effect'], read_artifact=read)
        self.assertEqual(report['status'], 'blocked')
        self.assertEqual(reads, [path])
        self.assertIn('goal: completed runtime has incomplete current academic requirements',
                      [row['message'] for row in report['findings']])
        self.assertEqual((instance, runtime), before)

    def test_duplicate_source_names_and_paths_are_separate_persisted_findings(self):
        instance, runtime = surface_state()
        source = {'id': 'SO-one', 'name': 'same.txt', 'path': 'runtime/artifacts/BA-one/source.txt',
                  'sha256': 'a' * 64, 'bytes': 1}
        instance['sources'] = [source, {**source, 'id': 'SO-two'}]
        default_state_contract().validate(*at_load(instance, runtime))
        result = self.area(instance, runtime, 'record_storage')
        self.assertEqual(result['status'], 'blocked')
        messages = [row['message'] for row in result['findings']]
        self.assertIn('source[1]: duplicate name', messages)
        self.assertIn('source[1]: duplicate path', messages)

    def test_solved_goal_without_an_audit_group_is_blocked(self):
        instance, runtime = surface_state()
        instance['goal_status'] = 'mathematically_solved'
        default_state_contract().validate(*at_load(instance, runtime))
        self.assertError(instance, runtime, 'completed runtime lacks current audit group', 'mathematical_effect')

    def test_duplicate_live_planning_roles_and_missing_selected_task_are_blocked(self):
        from support.record_builders import execution_state
        from do_math import activities, execution_lifecycle
        for role in ('research_preparation', 'research_plan'):
            with self.subTest(role=role):
                instance, runtime = execution_state(role)
                first = runtime['executions']['EX-1']
                second = execution_lifecycle.create_execution(execution_id='EX-two', owner_activity_id='AT-1',
                    actor_kind=first['actor_kind'], input_manifest={}, profile_ref=first['execution_profile_ref'],
                    created_at=first['created_at'])
                second['role'] = role
                activities.assign_execution(runtime, 'AT-1', second)
                runtime['queue'] = [{'id': 'AC-absent', 'role': 'research_work', 'target': 'TK-absent'}]
                default_state_contract().validate({**instance, 'object_format': 'sha1'}, runtime)
                self.assertError(instance, runtime, 'multiple live ' + role + ' executions', 'preparation_selection')
                self.assertError(instance, runtime, 'selected work references absent task', 'preparation_selection')

    def test_capacity_inspection_distinguishes_host_constraints_and_overcommitted_model_slots(self):
        from support.provider_inputs import host_capacity_fixture, PROFILE_CONFIG
        from support.record_builders import execution_state
        instance, _, host = host_capacity_fixture()
        instance = current_state(instance)[0]
        runtime = execution_state('research_work', config=PROFILE_CONFIG)[1]
        from do_math.budget import plan_reservations
        profile = instance['execution_profiles'][runtime['executions']['EX-1']['execution_profile_ref']['id']]
        reservation, = plan_reservations([], instance['capacity_constraints'], profile, owner_id='EX-1')
        constraint = instance['capacity_constraints'][reservation['constraint_id']]
        # The accounting inputs obey each row's balance; aggregate capacity is
        # the inspection's responsibility rather than a row schema condition.
        runtime['reservations'] = {reservation['id']: {**reservation, 'reserved': constraint['work_slots'] + 1}}
        default_state_contract().validate({**instance, 'object_format': 'sha1'}, runtime)
        before = deepcopy((instance, runtime))
        self.assertError(instance, runtime, 'reservation ledger exceeds work capacity', 'tasks_activities_executions')
        self.assertEqual((instance, runtime), before)
        self.assertEqual(instance['capacity_constraints'][host['id']], host)

    def test_external_mapping_requires_the_exact_execution_role_and_ledger_fields(self):
        from support.entry import entry
        operation = external.prepare_operation({'method': 'POST', 'url': 'https://example.test/', 'body': ''},
            'GR-one', 'GS-one', 'OP-one')
        operation.update(execution_id='EX-1')
        instance, runtime = surface_state()
        runtime['external_operations'] = {operation['id']: operation}
        self.assertError(instance, runtime, 'external operation has missing EX execution mapping', 'tasks_activities_executions')
        execution = runtime['executions']['EX-1']
        execution.update(role='external_action', operation_id=operation['id'])
        for field in ('grant_id', 'request_sha256', 'source_ref'):
            execution[field] = operation[field]
        self.assertEqual(self.area(instance, runtime, 'tasks_activities_executions')['status'], 'healthy')
        for field in ('grant_id', 'request_sha256', 'source_ref'):
            old = execution[field]
            execution[field] = 'different'
            self.assertError(instance, runtime, 'external execution ' + field + ' differs from ledger', 'tasks_activities_executions')
            execution[field] = old

    def test_valid_rule_payload_is_not_an_error_list(self):
        from support.observation_inputs import supply_observation_rules
        instance, runtime = surface_state()
        extensions = {}
        supply_observation_rules([{'title': 'fixture'}], extensions)
        rules = extensions['task_conditions'][0]['observation_rules']
        runtime['executions']['EX-1']['observation_rules'] = deepcopy(rules)
        runtime['task_observation_rules'] = {'TK-fixture': deepcopy(rules)}
        self.assertEqual(self.area(instance, runtime, 'self_check_stop')['status'], 'healthy')
        runtime['executions']['EX-1']['observation_rules'][0]['threshold'] = 0
        self.assertError(instance, runtime, 'positive integer', 'self_check_stop')

    def test_domain_created_activity_execution_profiles_are_clean(self):
        instance, runtime = surface_state()
        default_state_contract().validate(*at_load(instance, runtime))
        report = self.area(instance, runtime, 'tasks_activities_executions')
        self.assertEqual(report['status'], 'healthy', report)
        self.assertEqual(report['areas'][0]['checked_invariants'][0], 'load-time state contract validation')
        before = deepcopy(runtime)
        self.area(instance, runtime, 'tasks_activities_executions')
        self.assertEqual(runtime, before)

    def test_execution_state_lineage_profile_and_activity_mutations(self):
        # Execution state, lineage, profile binding and activity ownership are
        # load-time state contract conditions, not repeated by inspection.
        for field, value, message in (
            ('status', 'teleporting', 'runtime/executions/EX-1/status'),
            ('owner_activity_id', 'absent', 'executions references unknown record: absent'),
            ('continuation_of', 'EX-missing', 'executions references unknown record: EX-missing'),
        ):
            with self.subTest(field=field):
                instance, runtime = surface_state()
                runtime['executions']['EX-1'][field] = value
                self.assertRejectedAtLoad(instance, runtime, message)
        with self.subTest(field='execution_profile_ref'):
            instance, runtime = surface_state()
            execution = runtime['executions']['EX-1']
            execution['execution_profile_ref'] = {**execution['execution_profile_ref'], 'id': 'EP-missing'}
            self.assertRejectedAtLoad(instance, runtime, 'profile reference is absent or stale')
        instance, runtime = surface_state()
        profile = next(iter(instance['execution_profiles'].values()))
        profile['role'] = 'changed'
        self.assertRejectedAtLoad(instance, runtime, 'execution profile content differs from its immutable identity')

    def test_separated_knowledge_and_source_mutations(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = surface_state()
        candidate = {'kind': 'theorem', 'title': 'P', 'statement': 'P', 'explanation': 'Argument',
                     'summary': 'P follows', 'lean_code': 'theorem p : True := True.intro',
                     'declaration_names': ['p'], 'dependencies': []}
        instance, kid = knowledge_records.create_candidate(instance, candidate, source_ref='SRC', actor_ref='EX-1', clock=_entry.ports.clock)
        self.assertEqual(self.area(instance, runtime, 'mathematical_effect')['status'], 'healthy')
        # Knowledge references and source descriptors are load-time conditions.
        dangling = deepcopy(instance)
        dangling['knowledge'][kid]['exposition_id'] = 'missing'
        self.assertRejectedAtLoad(dangling, runtime, 'knowledge references unknown record: missing')
        for field, value in (('sha256', 'bad'), ('bytes', -1)):
            with self.subTest(source_field=field):
                broken, unchanged = surface_state()
                broken['sources'] = [{'id': 'SO-1', 'name': 'broken', 'path': 'runtime/broken',
                                      'sha256': 'a' * 64, 'bytes': 0, field: value}]
                self.assertRejectedAtLoad(broken, unchanged, 'research/sources/None/' + field)
        # A published formal result without its verification never loads.
        formal = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]
        formal.update(publication_state='accepted', formal_use='active')
        self.assertRejectedAtLoad(instance, runtime, 'published formal result requires verification evidence')

    def test_formal_results_left_under_a_superseded_environment_are_not_findings(self):
        # A trust transition gives each target a new formal result and leaves the
        # old one, still accepted and active, under the superseded environment.
        from support.entry import entry
        _entry = entry()
        from do_math import knowledge
        from support.knowledge_builders import verified_knowledge
        instance, runtime, kid, _ = verified_knowledge()
        old = instance['knowledge'][kid]['formal_result_id']
        instance['trust_environments']['TE-next'] = {'id': 'TE-next', 'status': 'registered',
                                                     'toolchain': {'version': 'next'}, 'allowed_axioms': []}
        result = {**deepcopy(instance['formal_results'][old]['verification']), 'id': kid,
                  'toolchain': {'version': 'next'}}
        transition = knowledge.begin_transition(instance, 'TE-next', clock=_entry.ports.clock)
        instance = knowledge.activate_transition(instance,
            knowledge.record_transition_result(instance, transition, result), at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.assertEqual(instance['trust_environments']['TE-test']['status'], 'superseded')
        self.assertEqual(instance['formal_results'][old]['formal_use'], 'active')
        self.assertEqual(self.area(instance, runtime, 'mathematical_effect')['status'], 'healthy')

    def test_completion_requires_all_obligations_and_authoritative_waiver(self):
        from support.record_builders import task_contract
        from do_math.execution_profiles import profile_ref
        instance, runtime = surface_state()
        value = task_contract()
        value['status'] = 'completed'
        value['profile_refs'] = [profile_ref(next(p for p in instance['execution_profiles'].values()
                                                  if p['role'] == 'research_work'))]
        value['assessment'] = {'task_id': value['id'], 'decision': 'completed', 'reason': 'Obligations assessed',
                               'item_dispositions': [
                                   {'obligation_id': 'OB-1', 'kind': 'fulfilled', 'evidence_refs': ['EV-1']}],
                               'unresolved': []}
        # Loading checks the dispositions of every recorded assessment.
        loaded = deepcopy(runtime)
        loaded['tasks'][value['id']] = {**deepcopy(value), 'authority_refs': []}
        self.assertRejectedAtLoad(instance, loaded, 'every obligation')
        # A completed task without an assessment is the inspection's own finding.
        runtime['tasks'][value['id']] = {key: item for key, item in value.items() if key != 'assessment'}
        self.assertError(instance, runtime, 'assessment decision', 'tasks_activities_executions')
        runtime['tasks'][value['id']] = value
        value['assessment']['item_dispositions'].append(
            {'obligation_id': 'OB-2', 'kind': 'waived', 'authority_ref': 'missing', 'evidence_refs': []})
        self.assertError(instance, runtime, 'authority', 'tasks_activities_executions')

    def test_solved_goal_requires_current_complete_audits(self):
        instance, runtime = surface_state()
        instance.update(goal_status='mathematically_solved', goal_assessment_basis='GB')
        instance['goal_judgments'] = [{'id': 'GJ-1', 'execution_id': 'EX-1', 'basis': 'GB', 'required': 1,
                                       'slot': 'one', 'decision': 'satisfied', 'scope_complete': True}]
        self.assertEqual(self.area(instance, runtime, 'mathematical_effect')['status'], 'healthy')
        instance['goal_judgments'][0]['current'] = False
        self.assertError(instance, runtime, 'current agreeing audits', 'mathematical_effect')

    def test_supplement_request_must_match_pending_review_owner(self):
        instance, runtime = surface_state()
        runtime['review_cycles'] = {'RC': {'id': 'RC', 'status': 'working', 'knowledge_id': 'KN',
            'research': {'RQ': {'status': 'pending', 'action': {'slot': 'initial-0'}}}}}
        runtime['queue'] = [{'role': 'supplemental_research', 'target': 'KN',
            'review_cycle_id': 'RC', 'research_request_id': 'RQ', 'requesting_slot': 'wrong'}]
        self.assertError(instance, runtime, 'queued investigation is not linked', 'preparation_selection')

    def test_external_error_http_remains_unknown_and_reconciliation_is_distinct(self):
        from support.entry import entry
        _entry = entry()
        from do_math.record_schemas import RECORDS, REFERENCES
        instance, runtime = surface_state()
        operation = external.prepare_operation({'method': 'POST', 'url': 'https://example.test/', 'body': ''},
                                               'GR', 'SRC', 'OP')
        operation['producer_executions'] = ['EX-1']
        jsonschema.validate(operation, RECORDS['external_operations'])
        self.assertIn(('EX-1', 'executions'), list(REFERENCES['external_operations'](operation)))
        with self.assertRaisesRegex(jsonschema.ValidationError, "1 is not of type 'string'"):
            jsonschema.validate({**operation, 'producer_executions': [1]}, RECORDS['external_operations'])
        # An actual domain transport response, not a fabricated successful receipt.
        grant = {'id': 'GR', 'status': 'active', 'allowed_origins': ['https://example.test'],
                 'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/'], 'credential_env': {}}
        operation = external.execute_operation(operation, grant,
            transport=lambda *_: {'http_status': 500, 'body': b'uncertain'}, persist=lambda row: row, clock=_entry.ports.clock, environment=_entry.environment)
        runtime['external_operations'] = {'OP': operation}
        self.assertEqual(operation['status'], 'unknown')
        self.assertEqual(self.area(instance, runtime, 'tasks_activities_executions')['status'], 'healthy')
        # One operation record decides these facts, so the storage contract rejects them.
        operation['succeeded'] = False
        self.assertRejectedAtLoad(instance, runtime, 'definitive success')
        operation['succeeded'] = None
        operation['handling'] = 'reconciled'
        self.assertRejectedAtLoad(instance, runtime, 'reconciled handling')
        del operation['handling']
        operation['status'] = 'cancelled'
        self.assertRejectedAtLoad(instance, runtime, 'confirmed untransmitted')

    def test_capability_evidence_id_must_match_its_content_at_load(self):
        # Readers use the stored ID without rehashing; a changed row is rejected here instead.
        from support.entry import entry
        _entry = entry()
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles, capability_evidence
        profiles = build_profiles({**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}, host=_entry.ports.host)
        profile = next(iter(profiles['execution_profiles'].values()))
        row = capability_evidence(profile, {'identity': {'host': 'fixture'}, 'verified': True,
            'supported': {'jsonl': True}}, observed_at='2026-01-01T00:00:00+00:00')
        instance = {**profiles, 'capability_evidence': {row['id']: row}}
        default_state_contract().validate(*at_load(instance, {}))
        row['identity'] = {'host': 'forged'}
        self.assertRejectedAtLoad(instance, {}, 'capability evidence ID differs from its content')

    def test_execution_outcome_is_a_closed_value_at_load(self):
        instance, runtime = surface_state()
        runtime['executions']['EX-1'].update(status='ended', ended_at='2026-01-01T00:00:00+00:00',
                                             outcome='finished')
        self.assertRejectedAtLoad(instance, runtime, 'outcome')

    def test_reservation_requires_balanced_settlement_and_existing_owner(self):
        # Reservation accounting and references are load-time conditions; admission
        # reads only reservations that passed them (budget.plan_reservations).
        instance, runtime = surface_state()
        constraint = next(iter(instance['capacity_constraints']))
        balanced = {'id': 'R', 'constraint_id': constraint, 'unit': 'session',
            'state': 'settled', 'reserved': 1, 'confirmed_consumed': 1,
            'returned': 0, 'owner_kind': 'execution', 'owner_id': 'EX-1', 'evidence_refs': ['EV-1']}
        for change, message in (
            ({'confirmed_consumed': 0, 'evidence_refs': []}, 'settled reservation must account for reserved exactly'),
            ({'reserved': -1}, 'reserved'),
            ({'constraint_id': 'CC-missing'}, 'reservations references unknown record: CC-missing'),
            ({'owner_id': 'EX-missing'}, 'reservations references unknown record: EX-missing'),
        ):
            with self.subTest(change=change):
                runtime['reservations'] = {'R': {**balanced, **change}}
                self.assertRejectedAtLoad(instance, runtime, message)
        # The inspection keeps the execution-side owner check.
        runtime['reservations'] = {'R': {**balanced, 'owner_id': 'EX-other'}}
        runtime['executions']['EX-1']['capacity'] = {'reservation_ids': ['R']}
        self.assertError(instance, runtime, 'execution reservation does not resolve to its owner',
                         'tasks_activities_executions')

    def test_requested_area_never_reuses_other_domain_findings(self):
        instance, runtime = surface_state()
        # An execution reservation without its ledger row is a tasks_activities_executions finding.
        runtime['executions']['EX-1']['capacity'] = {'reservation_ids': ['R-missing']}
        self.assertError(instance, runtime, 'execution reservation does not resolve to its owner',
                         'tasks_activities_executions')
        self.assertEqual(self.area(instance, runtime, 'governance_trust')['status'], 'healthy')
        report = self.area(instance, runtime, 'start_import_input')
        self.assertEqual(report['status'], 'incomplete')
        self.assertTrue(report['areas'][0]['not_checked'])

    def test_unknown_version_and_old_state_are_not_new_contract_success(self):
        # Version and lifecycle are load-time conditions; inspection receives only loaded states.
        instance, runtime = surface_state()
        instance['feature_version'] = 99
        self.assertRejectedAtLoad(instance, runtime, 'research/feature_version')
        runtime['feature_version'] = 99
        self.assertRejectedAtLoad(instance, runtime, 'feature_version')
        instance, runtime = surface_state()
        with self.assertRaisesRegex(ValueError, '^runtime/status/'):
            default_state_contract().validate({**instance, 'object_format': 'sha1'}, runtime)


class BatchedInspectionTests(unittest.TestCase):
    def inspect(self, refs, single, batch=None):
        return inspect_state(*storage_state(refs), requested_areas=['record_storage'],
                             read_artifact=single, read_artifacts=batch)

    def test_batch_keeps_each_reference_check_and_binary_bytes(self):
        files = {'runtime/artifacts/BA-1/empty': b'',
                 'runtime/artifacts/BA-1/raw': b'\x00\xff\r\nblob missing\n'}
        refs = [artifact(path, raw) for path, raw in files.items()]
        refs.append(artifact(next(iter(files)), b'', sha256='0' * 64))
        expected = self.inspect(refs, files.__getitem__)
        single = Mock(side_effect=AssertionError('normal batch must not read files again'))
        batch = Mock(side_effect=lambda paths: {path: files[path] for path in paths})
        self.assertEqual(self.inspect(refs, single, batch), expected)
        self.assertEqual(expected['status'], 'blocked')
        # The area names each invariant once, however many references it checked.
        self.assertEqual(expected['areas'][0]['checked_invariants'].count('artifact bytes'), 1)
        batch.assert_called_once_with(list(files))
        single.assert_not_called()

    def test_failed_batch_preserves_individual_error_order_and_scope(self):
        files = {'runtime/artifacts/BA-1/bad': b'changed',
                 'runtime/artifacts/BA-1/good': b'good'}
        paths = [*files, 'runtime/artifacts/BA-1/missing']
        refs = [artifact(paths[0], b'original'), artifact(paths[1], b'good'), artifact(paths[2], b'')]

        def read(path):
            if path not in files:
                raise FileNotFoundError('missing fixture: ' + path)
            return files[path]

        expected = self.inspect(refs, read)
        single = Mock(side_effect=read)
        batch = Mock(side_effect=GitStateStoreError('one requested blob is missing'))
        self.assertEqual(self.inspect(refs, single, batch), expected)
        self.assertEqual([call.args[0] for call in single.call_args_list], paths)
        self.assertEqual([row['status'] for row in expected['findings']], ['blocked', 'incomplete'])

    def test_next_inspection_reads_fresh_bytes(self):
        path = 'runtime/artifacts/BA-1/raw'
        files = {path: b'original'}
        refs = [artifact(path, files[path])]
        batch = Mock(side_effect=lambda paths: {name: files[name] for name in paths})
        self.assertEqual(self.inspect(refs, files.__getitem__, batch)['status'], 'healthy')
        files[path] = b'changed'
        self.assertEqual(self.inspect(refs, files.__getitem__, batch)['status'], 'blocked')
        self.assertEqual(batch.call_count, 2)

    def test_empty_or_unavailable_batch_needs_no_new_reader_contract(self):
        single = Mock(return_value=b'single')
        batch = Mock(return_value={})
        self.assertIs(prefetch_artifacts([], single, batch), single)
        batch.assert_not_called()
        self.assertIs(prefetch_artifacts(['one'], single), single)
        read = prefetch_artifacts(['one'], single, batch)
        # The batch omits a requested path absent from the snapshot.
        with self.assertRaisesRegex(ValueError, 'artifact is missing: one'):
            read('one')
        self.assertEqual(read('another'), b'single')


class EngineEntryInspectionTests(unittest.TestCase):
    def test_engine_entry_checks_presence_and_length_while_check_compares_bytes(self):
        """The run/controls entry inspection (``_inspect_before_write``) reads stored lengths only; ``check`` compares bytes.

        Over the in-process Git fake every artifact byte read is a
        ``read_objects`` port call and every length query an ``object_info``
        one. Changed, removed and shortened artifacts are later commits of
        another writer. The repository answers lengths it published itself from
        memory, so length queries reach Git only on those later commits; there
        the fake moves ``engine.head`` at the first artifact query, and a later
        query that read the engine's head instead of the snapshot it observed
        would name another commit.
        About 0.5 s, over the 0.2 s unit budget: the real engine loads and
        validates the stored state, and three more commits are loaded again.
        """
        from support.entry import entry
        _entry = entry()
        output_path = 'runtime/artifacts/BA-output/result.bin'
        input_path = 'runtime/artifacts/BA-input/input.txt'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clock, backend = FakeClock(), ObservedGit()
            repository = record_store(root / 'repository', backend=backend, clock=clock)
            instance, runtime = at_load(*surface_state())
            instance['workspace'] = str(root / 'work')
            first = repository.initialize(instance, runtime)
            files = {output_path: b'\x00\xff'}
            runtime['executions']['EX-1'].update(
                output_files=[{**artifact(output_path, files[output_path]), 'path': 'result.bin'}],
                input_bundle='BA-input', input_manifest=archived_role_input('BA-input', first, files))
            head = repository.save_with_state(first, instance, runtime, artifacts=files)[0]
            engine = ResearchEngine(repository.repository, INSTANCE_ID, ports=fake_ports(clock, backend), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
            self.assertEqual(engine.head, head)
            manifest_paths = sorted(path for path in files if path.startswith('runtime/artifacts/BA-input/'))

            def move_head(operation, arguments):
                if operation in ('object_info', 'read_objects') and any(':runtime/artifacts/' in spec
                                                                        for spec in arguments[0]):
                    engine.head = first
            backend.before = move_head

            def named_commits(operation, since):
                return {spec.partition(':')[0] for specs in backend.artifact_specs(operation, since) for spec in specs}

            mark = len(backend.calls)
            engine._inspect_before_write()
            # Entry to run/controls reads no artifact bytes: same-length changes are check's.
            self.assertNotIn('read_objects', backend.operations(mark))
            mark = len(backend.calls)
            self.assertTrue(engine.check(requested_areas=['start_import_input'])['passed'])
            # One batch read of every archived role input, at the loaded snapshot; no single-file reads.
            reads = backend.artifact_specs('read_objects', mark)
            self.assertEqual(len(reads), 1)
            self.assertEqual(sorted(reads[0]), [head + ':' + path for path in manifest_paths])

            # The start_import_input area compares each archived role input, prompt included.
            changed = rewrite_commit(repository, head, {input_path: b'exact prompX'})
            engine._reload()
            self.assertEqual(engine.head, changed)
            mark = len(backend.calls)
            engine._inspect_before_write()
            self.assertNotIn('read_objects', backend.operations(mark))
            self.assertEqual(named_commits('object_info', mark), {changed})
            self.assertEqual(engine.head, first)  # the fake did move it
            result = engine.check(requested_areas=['start_import_input'])
            self.assertFalse(result['passed'])
            self.assertIn('EX-1: input artifact bytes differ: prompt',
                          [row['message'] for row in result['inspection']['findings']])

            removed = rewrite_commit(repository, changed, {input_path: None})
            engine._reload()
            with self.assertRaisesRegex(ValueError, 'current input artifact is missing: EX-1'):
                engine._inspect_before_write()
            # Both batch readers leave a path absent from the snapshot out of their result.
            result = engine.check(requested_areas=['start_import_input'])
            self.assertEqual(result['snapshot'], removed)
            self.assertIn('EX-1: input artifact is missing: prompt',
                          [row['message'] for row in result['inspection']['findings']])

            shortened = rewrite_commit(repository, removed, {output_path: b'\x00'})
            engine._reload()
            self.assertEqual(engine.head, shortened)
            with self.assertRaisesRegex(ValueError, 'repaired before publication'):
                engine._inspect_before_write()
            self.assertTrue(all(len(specs) == len(manifest_paths)
                                for specs in backend.artifact_specs('read_objects')))


class CheckAreaTests(unittest.TestCase):
    def test_cleanup_aborted_attempt_is_not_healthy(self):
        instance, runtime = surface_state()
        runtime['history'] = [{'kind': 'maintenance_cleanup_failed', 'execution_id': 'EX-maint',
                               'paths': ['runs/EX-1'], 'completed_paths': [],
                               'reason': 'root inaccessible', 'next_owner': 'maintenance'}]
        result = inspect_state(instance, runtime, requested_areas=['record_storage'])
        self.assertEqual(result['status'], 'degraded')

    def test_cleanup_history_is_the_degraded_source(self):
        instance, runtime = surface_state()
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-maint',
            'result': {'status': 'degraded', 'deleted': [], 'failures': [
                {'path': 'runs/EX-1', 'error': 'locked', 'next_owner': 'maintenance'}]}})
        result = inspect_state(instance, runtime, requested_areas=['record_storage'])
        self.assertEqual(result['status'], 'degraded')
        self.assertTrue(any('runs/EX-1' in str(row) for row in result['findings']))
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-maint-2',
            'result': {'status': 'healthy', 'deleted': ['runs/EX-1'], 'failures': []}})
        self.assertEqual(inspect_state(instance, runtime, requested_areas=['record_storage'])['status'], 'healthy')

    def test_area_errors_are_not_copied_to_unrelated_areas(self):
        result = inspect_state({'sources': [{'sha256': 'a' * 64}]}, {'activities': {}, 'executions': {}, 'tasks': {}},
                               requested_areas=['record_storage', 'tasks_activities_executions'])
        self.assertTrue(any(f['area'] == 'record_storage' and 'source[0]: missing name' in f['message']
                            for f in result['findings']))
        self.assertFalse(any(f['area'] == 'tasks_activities_executions' and 'source[0]' in f['message']
                             for f in result['findings']))

    def test_requested_check_areas_distinguish_unchecked_from_healthy(self):
        instance = {"sources": [], "knowledge": {}, "trust_environments": {}}
        runtime = {"tasks": {}, "executions": {}, "queue": [], "status": "ready", "question_links": []}
        report = inspect_state(instance, runtime, requested_areas=["record_storage"])
        self.assertEqual(report["status"], "healthy")
        self.assertEqual(report["not_checked"], [])
        self.assertEqual(report["areas"][0]["name"], "record_storage")
        unknown = inspect_state(instance, runtime, requested_areas=["not_an_area"])
        self.assertEqual(unknown["status"], "incomplete")
        self.assertEqual(unknown["not_checked"], ["not_an_area"])
        self.assertEqual(unknown["areas"], [{"name": "not_an_area", "status": "incomplete", "checked": False,
                                             "findings": 1}])
        self.assertEqual(unknown["findings"][0]["next_owner"], "operator")


if __name__ == '__main__':
    unittest.main()

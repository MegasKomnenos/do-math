"""Records the product's producers make survive storage, and a damaged field is refused for its own reason.

Each test builds a record with the real producer (tasks, governance, host
capacity, executions, checkpoints, external operations, questions, knowledge,
review cycles, ...), stores it through the real ``ResearchRepository`` on the
in-process Git fake (``repository``, layer 2) and reads it back; then it
breaks one field and checks that the storage contract refuses it. Producers
that are engine mixins (layer 2) run on the real ``ResearchEngine`` on the port
fakes over the stored state (``engine_on``), and the engine's own save
publishes their result through the storage contract.
"""
from support.observation_clock import scripted_clock
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest

import jsonschema
from jsonschema import Draft202012Validator, ValidationError

from do_math import contracts, knowledge_io
from do_math.canonical import exact_content_hash
from do_math.record_schemas.schemas import RECORDS
from support.record_builders import execution_state
from support.state_builders import current_state
from support.review_inputs import reviewed_candidate
from support.fakes.clock import FakeClock
from support.storage_records import (INSTANCE_ID, RecordingGit, approved_governance_instance, engine_on, fake_ports,
                                     record_store, reference_fixture_instance, task_with_reference_locators)


class ProducerCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository_path = self.root / 'repository'
        self.clock, self.backend = FakeClock(), RecordingGit()
        self.repository = record_store(self.repository_path, backend=self.backend, clock=self.clock)

    def engine_on(self, instance, runtime):
        """``(engine, head)``: the real engine on the port fakes over this state, stored in this test's repository."""
        return engine_on(self.repository, instance, runtime, workspace=self.root / 'work',
                         ports=fake_ports(self.clock, self.backend))


class TaskRecordTests(ProducerCase):
    def test_wire_task_description_survives_storage_and_binds_contract(self):
        from do_math.contracts import TASK_CANDIDATE, task_candidate_record
        from do_math.planning import contract_hash
        task = task_with_reference_locators()
        wire = {key: deepcopy(value) for key, value in task.items() if key in TASK_CANDIDATE['properties']}
        wire.update(revises_task_id=None, description='Exact task explanation e\u0301\r\n')
        task = task_candidate_record(wire, task_id=task['id'])
        task.pop('revises_task_id')
        task['status'] = 'planned'
        before = contract_hash(task)
        head = self.repository.initialize(reference_fixture_instance(),
                                          current_state(runtime={'tasks': {task['id']: task}})[1])
        _, instance, runtime = self.repository.load(head)
        saved = runtime['tasks'][task['id']]
        self.assertEqual(saved['description'], wire['description'])
        self.assertEqual(contract_hash(saved), before)
        self.assertNotEqual(contract_hash({**saved, 'description': 'Changed explanation'}), before)
        description = '^runtime/tasks/TK-reference-locators/description: '
        for value, reason in (('', description + "'' should be non-empty$"),
                              ('   ', description + r"'   ' does not match '\\\\S'$"),
                              (3, description + "3 is not of type 'string'$"),
                              (None, description + "None is not of type 'string'$")):
            with self.subTest(description=value):
                changed = deepcopy(runtime)
                changed['tasks'][task['id']]['description'] = value
                with self.assertRaisesRegex(ValueError, reason):
                    self.repository.validate_candidate(instance, changed, head)

    def test_task_input_and_basis_locators_survive_actual_git_storage(self):
        task = task_with_reference_locators()
        self.assertIn('context:goal', task['basis_refs'])
        self.assertIn('source:NatAddZero.lean', task['inputs'])
        head = self.repository.initialize(reference_fixture_instance(),
                                          current_state(runtime={'tasks': {task['id']: task}})[1])
        saved = self.repository.load(head)[2]['tasks'][task['id']]
        for field in ('inputs', 'basis_refs', 'reuse', 'dependencies', 'authority_refs', 'profile_refs'):
            self.assertEqual(saved[field], task[field])

    def test_task_source_path_locators_keep_exact_unicode_in_git(self):
        task = task_with_reference_locators()
        refs = ['source:e\u0301.lean', 'input/sources/\u212a.lean',
                'runtime/artifacts/BA-source/report.md', 'context:policy', 'tool:lean']
        task.update(inputs=refs, basis_refs=refs)
        head = self.repository.initialize(reference_fixture_instance(),
                                          current_state(runtime={'tasks': {task['id']: task}})[1])
        saved = self.repository.load(head)[2]['tasks'][task['id']]
        self.assertEqual(saved['inputs'], refs)
        self.assertEqual(saved['basis_refs'], refs)

    def test_task_locator_storage_does_not_widen_record_or_profile_authority(self):
        task = task_with_reference_locators()
        task.update(inputs=[], basis_refs=[])
        head = self.repository.initialize(reference_fixture_instance(),
                                          current_state(runtime={'tasks': {task['id']: task}})[1])
        _, instance, runtime = self.repository.load(head)
        for field in ('reuse', 'dependencies', 'authority_refs', 'profile_refs'):
            with self.subTest(field=field):
                changed = deepcopy(runtime)
                changed['tasks'][task['id']][field] = ['context:goal']
                with self.assertRaisesRegex(ValueError, field):
                    self.repository.validate_candidate(instance, changed, head)
        changed = deepcopy(runtime)
        changed['tasks'][task['id']]['profile_refs'][0]['id'] = 'GR-reference'
        with self.assertRaisesRegex(ValueError, '^task profile reference does not identify an execution profile$'):
            self.repository.validate_candidate(instance, changed, head)
        self.assertEqual(self.repository.load(head)[2], runtime)

    def test_task_dependencies_resolve_tasks_or_existing_knowledge(self):
        from support.entry import entry
        _entry = entry()
        from do_math.knowledge_io import ensure_ontology
        from do_math.knowledge_records import create_candidate
        instance = ensure_ontology(current_state()[0])
        instance, kid = create_candidate(instance, {'kind': 'observation', 'statement': 'prior result',
                                                    'dependencies': []}, source_ref='input', actor_ref='user', clock=_entry.ports.clock)
        task = {'id': 'TK-1', 'revision': 1, 'question': 'Check this result', 'status': 'planned',
                'scope': {'included': ['result'], 'excluded': []},
                'expected': {'outputs': ['assessment'], 'research_change': 'Check result'},
                'progress_criteria': [{'id': 'p', 'claim': 'gather evidence'}],
                'completion_obligations': [{'id': 'o', 'claim': 'assess result', 'judges': ['research_plan']}],
                'dependencies': [kid]}
        runtime = current_state(runtime={'tasks': {task['id']: task}})[1]
        checked = self.repository.validate_candidate(instance, runtime)
        self.assertEqual(checked['runtime']['tasks']['TK-1']['dependencies'], [kid])
        task['dependencies'] = ['K-missing']
        with self.assertRaisesRegex(ValueError, 'unknown record'):
            self.repository.validate_candidate(instance, runtime)

    def test_actual_plan_disposition_and_repetition_request_round_trip(self):
        from support.role_answers import candidate, disposition
        instance, runtime = execution_state('research_plan')
        task = {**candidate(), 'id': 'TK-1', 'revision': 1, 'status': 'planned'}
        task.pop('revises_task_id')
        runtime['tasks'] = {task['id']: task}
        engine, _ = self.engine_on(instance, runtime)
        output = {'dispositions': [disposition(task['id'], kind='not_selected')],
                  'task_assessments': [], 'preparation_requests': ['Refine the contract']}
        output['dispositions'][0]['revisit']['at'] = '2026-09-21T00:00:00Z'
        output['dispositions'][0]['uncertainty'] = 'Contract refinement remains'
        engine._apply_task_plan(output, 'EX-1', deepcopy(engine.runtime['tasks']), [task['id']])
        engine._save()
        _, _, loaded = self.repository.load()
        self.assertEqual(loaded['tasks'][task['id']]['selection_disposition']['execution_id'], 'EX-1')
        self.assertEqual(loaded['queue'][0]['requested_by'], 'EX-1')

    def test_actual_repetition_binding_is_a_closed_queue_contract(self):
        from do_math.revisions import bind_repetition_bases
        instance, runtime = current_state(runtime={'tasks': {}, 'queue': [{'id': 'AC-repeat', 'role': 'research_plan'}]})
        action = runtime['queue'][0]
        bind_repetition_bases(instance, runtime, action)
        head = self.repository.initialize(instance, runtime)
        self.assertEqual(self.repository.load(head)[2]['queue'][0]['repetition_bases'], action['repetition_bases'])
        action['repetition_bases']['invented_lineage'] = 'a' * 64
        with self.assertRaisesRegex(ValueError, r"repetition_bases: Additional properties are not allowed "
                                                r"\('invented_lineage' was unexpected\)$"):
            self.repository.validate_candidate(instance, runtime, head)


class QueueRecordTests(ProducerCase):
    def test_scoped_review_research_request_survives_action_storage(self):
        from support.review_inputs import deferred_research_cycle
        cycle, _ = deferred_research_cycle()
        request_id = next(iter(cycle['research']))
        action = {'id': 'AC-investigation', 'role': 'supplemental_research',
                  'research_request_id': request_id, 'slot': 'research-' + request_id, 'stage': 'investigating'}
        self.assertIn(':', request_id)
        head = self.repository.initialize(*current_state(runtime={'queue': [action]}))
        self.assertEqual(self.repository.load(head)[2]['queue'], [action])

    def test_cleanup_scope_preserves_exact_user_request_and_execution_references(self):
        instance, runtime = execution_state()
        action = {'id': 'AC-cleanup', 'role': 'maintenance', 'requested_by': 'UC-cleanup',
                  'cleanup_execution_ids': ['EX-1']}
        runtime['queue'] = [action]
        runtime['history'] = [{'kind': 'user_control', 'request': {'id': 'UC-cleanup', 'origin': 'user',
            'action': 'request', 'config': {'role': 'maintenance', 'cleanup_execution_ids': ['EX-1']}}}]
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(loaded['queue'][0], action)
        for change in ('missing_execution', 'different_request', 'not_user', 'wrong_role'):
            with self.subTest(change=change):
                broken = deepcopy(loaded)
                if change == 'missing_execution':
                    broken['queue'][0]['cleanup_execution_ids'] = ['EX-absent']
                elif change == 'different_request':
                    broken['history'][0]['request']['config']['cleanup_execution_ids'] = []
                elif change == 'not_user':
                    broken['history'][0]['request']['origin'] = 'engine'
                else:
                    broken['queue'][0]['role'] = 'research_work'
                with self.assertRaisesRegex(ValueError, 'cleanup'):
                    self.repository.validate_candidate(saved, broken)

    def test_failed_execution_wait_preserves_actual_failure_and_snapshot(self):
        instance, runtime = execution_state()
        action = {'id': 'AC-failed', 'role': 'formal_check'}
        runtime['waiting_actions'] = {action['id']: {'action': action, 'kind': 'execution_failure',
            'failure_kind': 'execution_failure', 'reason': None, 'execution_id': 'EX-1', 'input_snapshot': 'a' * 40}}
        head = self.repository.initialize(instance, runtime)
        _, instance, loaded = self.repository.load(head)
        self.assertEqual(loaded['waiting_actions'], runtime['waiting_actions'])
        loaded['waiting_actions'][action['id']]['execution_id'] = 'EX-missing'
        with self.assertRaisesRegex(ValueError, 'waiting action reference'):
            self.repository.validate_candidate(instance, loaded)

    def test_actual_impact_request_has_closed_nested_plan_schema(self):
        from support.knowledge_impact import ImpactCase
        owner = ImpactCase()
        owner.setUp()
        action = {'id': 'AC-review', 'role': 'maintenance', 'stage': 'impact_review',
                  'input_basis': {'impact_review': owner.request()}}
        validator = Draft202012Validator(RECORDS['queue'])
        validator.validate(action)
        instance, runtime = execution_state('research_work')
        instance.update(owner.instance)
        producer = runtime['executions'].pop('EX-1')
        producer['id'] = 'EX-producer'
        runtime['executions'][producer['id']] = producer
        runtime['activities']['AT-1']['assigned_execution_ids'] = [producer['id']]
        runtime['queue'] = [deepcopy(action)]
        head = self.repository.initialize(instance, runtime)
        loaded = self.repository.load(head)[2]
        self.assertEqual(loaded['queue'][0], action)
        loaded['queue'][0]['input_basis']['impact_review']['plans']['bundle']['digest'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'plan hash'):
            self.repository.validate_candidate(instance, loaded)
        from do_math.knowledge import plan_digest
        for case, reason in (('producer', 'impact review original execution is missing'),
                              ('basis', 'impact review frozen plan references do not resolve')):
            broken = deepcopy(runtime)
            request = broken['queue'][0]['input_basis']['impact_review']
            if case == 'producer':
                request['producer_execution_id'] = 'EX-missing'
            else:
                plan = request['plans']['bundle']
                plan['basis']['KN-missing'] = '0' * 64
                plan['digest'] = plan_digest(plan)
            with self.subTest(case=case), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                self.repository.validate_candidate(instance, broken)
            self.assertEqual(self.repository.load(head)[2]['queue'], [action])
        action['input_basis']['impact_review']['plans']['bundle']['unregistered'] = True
        with self.assertRaisesRegex(ValidationError, r"^Additional properties are not allowed \('unregistered' was unexpected\)"):
            validator.validate(action)

    def test_actual_input_metrics_overflow_and_validity_basis_round_trip(self):
        from do_math.context_store import fit_context
        from do_math.contracts import prompt_metrics
        from do_math.knowledge import capture_basis
        instance, runtime = execution_state()
        execution = runtime['executions']['EX-1']
        execution['input_metrics'] = prompt_metrics('prompt', {'required': 'body'}, {}, [])
        execution['validity_basis'] = capture_basis(instance, runtime, [])
        fitted = fit_context({'required': 'body' * 50}, max_bytes=10,
                             workspace=self.repository_path / 'overflow', mandatory_keys=['required'], role='research_plan',
                             profile_id=execution['execution_profile_ref']['id'], activity_id='AT-1')
        runtime['queue'] = [{'id': 'AC-overflow', 'role': 'research_plan',
                             'input_overflow': fitted['overflow'], 'overflow_activity_id': 'AT-1'}]
        head = self.repository.initialize(instance, runtime)
        loaded = self.repository.load(head)[2]
        self.assertEqual(loaded['executions']['EX-1']['validity_basis'], [])
        self.assertEqual(loaded['queue'][0]['input_overflow'], fitted['overflow'])
        runtime['queue'][0]['input_overflow']['unregistered'] = True
        with self.assertRaisesRegex(ValueError, r"input_overflow: Additional properties are not allowed "
                                                r"\('unregistered' was unexpected\)$"):
            self.repository.validate_candidate(instance, runtime)

    def test_queue_preserves_actual_model_selection_producer(self):
        from do_math.model_policy import selection
        instance, runtime = execution_state('research_plan')
        runtime['queue'] = [{'id': 'AC-plan', 'role': 'research_plan'}]
        action = runtime['queue'][0]
        action['model_selection'] = selection(instance['config'], action, {}, {}, instance=instance)
        head = self.repository.initialize(instance, runtime)
        _, published, loaded = self.repository.load(head)
        self.assertEqual(published, {**instance, 'object_format': 'sha1'})
        self.assertEqual(loaded['queue'][0]['model_selection'], action['model_selection'])
        wrong = deepcopy(loaded)
        wrong['queue'][0]['model_selection']['profile_ref']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, '^profile reference is absent or stale$'):
            self.repository.validate_candidate(instance, wrong)
        wrong = deepcopy(loaded)
        wrong['queue'][0]['model_selection']['model'] += '-different'
        with self.assertRaises(ValueError) as rejected:
            self.repository.save_with_state(head, instance, wrong)
        self.assertIs(type(rejected.exception), ValueError)
        self.assertEqual(str(rejected.exception), 'model selection differs from the pinned role/model profile')
        self.assertEqual(self.repository.load(), (head, published, loaded))



class ExecutionRecordTests(ProducerCase):
    def test_unbounded_activity_and_execution_nulls_keep_their_meaning_after_storage(self):
        from do_math import activities, execution_window, reporting
        from do_math.execution_lifecycle import transition_execution
        from do_math.repair_execution import recovery_attempt_counts
        import csv
        import io
        import json

        instance, runtime = execution_state('research_work')
        work = self.root / 'window'
        work.mkdir()
        window = execution_window.publish(work, 'EX-1', None, instance['config'],
            clock=self.clock.monotonic, wall_clock=self.clock.wall())
        self.assertEqual(json.loads((work / '.control' / 'execution-window.json').read_bytes()), window)
        execution = runtime['executions']['EX-1']
        execution['execution_window'] = window
        transition_execution(execution, 'ended', at=self.clock.now(), outcome='cancelled')
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        activity, execution = loaded['activities']['AT-1'], loaded['executions']['EX-1']
        for field in ('stage', 'execution_limit'):
            self.assertIn(field, activity)
            self.assertIsNone(activity[field])
        for field in ('continuation_of', 'result_disposition'):
            self.assertIn(field, execution)
            self.assertIsNone(execution[field])
        self.assertIn('reason', execution['transitions'][0])
        self.assertIsNone(execution['transitions'][0]['reason'])
        for field in ('effective_deadline_at', 'remaining_ms_at_start', 'finish_notice_at'):
            self.assertIn(field, execution['execution_window'])
            self.assertIsNone(execution['execution_window'][field])
        self.assertEqual(execution['execution_window']['deadline_source'], 'none')
        self.assertEqual(execution['execution_window']['effective_notice_ms'], 0)
        self.assertFalse(execution_window.deadline_passed(None, clock=self.clock.monotonic))
        self.assertFalse(execution_window.request_finish(work, None, instance['config'],
            clock=self.clock.monotonic, now_iso=self.clock.now()))
        self.assertFalse((work / '.control' / 'finish-request.json').exists())
        self.assertIsNone(activities.successor_state(loaded, 'EX-1'))
        self.assertTrue(recovery_attempt_counts(execution))
        # A null activity limit admits a second real attempt, rather than being zero.
        from do_math.execution_lifecycle import create_execution
        second = create_execution(execution_id='EX-2', owner_activity_id='AT-1', actor_kind=execution['actor_kind'],
            input_manifest={}, profile_ref=execution['execution_profile_ref'], created_at=self.clock.now())
        second['role'] = execution['role']
        activities.assign_execution(loaded, 'AT-1', second)
        self.assertEqual(activity['assigned_execution_ids'], ['EX-1', 'EX-2'])
        self.repository.validate_candidate(saved, loaded, head)
        value = reporting.timeline(self.repository_path, INSTANCE_ID, snapshot=head,
            backend=self.backend, clock=self.clock)
        row, = value['rows']
        self.assertIsNone(row['continuation_of'])
        self.assertIsNone(row['effective_deadline_at'])
        self.assertIsNone(row['started_at_local'])
        rendered, = csv.DictReader(io.StringIO(reporting.timeline_csv(value)))
        self.assertEqual(rendered['continuation_of'], '')
        self.assertEqual(rendered['effective_deadline_at'], '')
        self.assertEqual(self.repository.load(head)[2]['executions']['EX-1'], execution)

    def test_actual_host_profile_reservation_round_trip_and_authority_refs(self):
        """About 0.2-0.45 s, over the 0.2 s unit budget: host-resource profile sealing, a slot reservation and four storage-contract validations on the in-process Git fake."""
        from support.entry import entry
        _entry = entry()
        import platform
        from do_math import execution_profiles as profiles, governance
        from do_math.activities import assign_execution
        from do_math.execution_lifecycle import create_execution
        from do_math.session_slots import SessionSlots
        instance, runtime = execution_state()
        source = governance.preserve_source('GS-host', 'Disposable test approval: local jobs 3, memory 4096, CPU 8000; '
                                            'reserve 1/1024/1000', origin='user')
        instance['governance_sources'] = {source['id']: source}
        constraint = profiles.host_constraint(host_id=platform.node(),
            limits={'jobs': 3, 'memory_bytes': 4096, 'cpu_rate_basis_points': 8000},
            control_reserve={'jobs': 1, 'memory_bytes': 1024, 'cpu_rate_basis_points': 1000},
            authority_refs=[source['id']])
        instance['capacity_constraints'][constraint['id']] = constraint
        instance['host_capacity_ref'] = constraint['id']
        execution = runtime['executions']['EX-1']
        original = profiles.resolve_profile(instance['execution_profiles'], execution['execution_profile_ref'])
        profile = profiles.with_host_resources(original, constraint,
                                               {'jobs': 1, 'memory_bytes': 1024, 'cpu_rate_basis_points': 1000})
        instance['execution_profiles'][profile['id']] = profile
        execution = create_execution(execution_id='EX-host', owner_activity_id='AT-1', actor_kind='machine',
                                     input_manifest={}, profile_ref=profiles.profile_ref(profile),
                                     created_at='2026-09-20T00:00:00Z')
        execution['role'] = profile['role']
        assign_execution(runtime, 'AT-1', execution)
        self.assertTrue(SessionSlots(runtime, instance, clock=_entry.ports.clock, host_id=_entry.host_id, jobs=_entry.ports.jobs).acquire('EX-host', profile=profile, execution=execution,
                                                                current_time=100))
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(loaded['executions']['EX-host']['capacity']['provider'], None)
        self.assertEqual({row['unit'] for row in loaded['reservations'].values()},
                         {'jobs', 'memory_bytes', 'cpu_rate_basis_points'})
        for mutation in ('tampered_limit', 'host_mismatch', 'missing_authority'):
            with self.subTest(mutation=mutation):
                broken = deepcopy(saved)
                if mutation == 'tampered_limit':
                    broken['capacity_constraints'][constraint['id']]['memory_bytes'] += 1
                elif mutation == 'missing_authority':
                    broken['governance_sources'] = {}
                else:
                    body = deepcopy(profile)
                    body['host_resources']['host_id'] = 'other-host'
                    bad = profiles.seal_profile(body)
                    broken['execution_profiles'][bad['id']] = bad
                with self.assertRaisesRegex(ValueError, 'host|authority'):
                    self.repository.validate_candidate(broken, loaded)

    def test_adopted_host_authoring_retains_shared_constraint_pointer(self):
        """About 0.2-0.3 s, over the 0.2 s unit budget: the adopted profile editions are built and the state passes the storage contract three times."""
        from support.entry import entry
        _entry = entry()
        import platform
        from do_math import execution_profiles as profiles, governance
        instance, runtime = execution_state()
        source = governance.preserve_source('GS-host-config', 'Explicit disposable host-policy test approval', origin='user')
        instance['governance_sources'] = {source['id']: source}
        constraint = profiles.host_constraint(host_id=platform.node(),
            limits={'jobs': 3, 'memory_bytes': 4096, 'cpu_rate_basis_points': 8000},
            control_reserve={'jobs': 1, 'memory_bytes': 1024, 'cpu_rate_basis_points': 1000},
            authority_refs=[source['id']])
        instance['config']['host_resources'] = {'constraint': constraint, 'demands_by_role': {
            role: {'jobs': 1, 'memory_bytes': 1024, 'cpu_rate_basis_points': 1000} for role in profiles.HOST_ROLES}}
        adopted = profiles.build_profiles(instance['config'], host=_entry.ports.host)
        for family in ('execution_profiles', 'capacity_constraints'):
            instance[family].update(adopted[family])
        instance['role_profile_refs'] = adopted['role_profile_refs']
        instance['host_capacity_ref'] = adopted['host_capacity_ref']
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(saved['host_capacity_ref'], constraint['id'])
        self.assertEqual(saved['config']['host_resources'], instance['config']['host_resources'])
        saved['host_capacity_ref'] = 'CP-absent'
        with self.assertRaisesRegex(ValueError, '^host_capacity_ref references unknown record: CP-absent$'):
            self.repository.validate_candidate(saved, loaded)

    def test_configure_preserves_selected_profile_edition_not_all_historical_editions(self):
        """About 0.25-0.3 s, over the 0.2 s unit budget: two profile editions are built and the state passes the storage contract four times."""
        from support.entry import entry
        _entry = entry()
        from do_math.execution_profiles import build_profiles
        instance, runtime = execution_state()
        old_ref = runtime['executions']['EX-1']['execution_profile_ref']
        instance['config']['call_timeout_seconds'] += 1
        editions = build_profiles(instance['config'], host=_entry.ports.host)
        instance['execution_profiles'].update(editions['execution_profiles'])
        instance['capacity_constraints'].update(editions['capacity_constraints'])
        instance['role_profile_refs'] = editions['role_profile_refs']
        checked = self.repository.validate_candidate(instance, runtime)
        self.assertEqual(checked['instance']['role_profile_refs'], editions['role_profile_refs'])
        self.assertIn(old_ref['id'], checked['instance']['execution_profiles'])
        head = self.repository.initialize(instance, runtime)
        self.assertEqual(self.repository.load(head)[1]['role_profile_refs'], editions['role_profile_refs'])
        bad = deepcopy(instance)
        selected_role = next(iter(bad['role_profile_refs']))
        bad['role_profile_refs'][selected_role][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, '^profile reference is absent or stale$'):
            self.repository.validate_candidate(bad, runtime)

    def test_actual_execution_window_preserves_integer_measurement_and_owner(self):
        from support.entry import entry
        _entry = entry()
        from do_math.execution_lifecycle import transition_execution
        from do_math.execution_window import publish
        instance, runtime = execution_state()
        work = self.repository_path / 'window'
        work.mkdir()
        window = publish(work, 'EX-1', 12.75, instance['config'], clock=lambda: 12.0, wall_clock=_entry.ports.clock.wall())
        runtime['executions']['EX-1']['execution_window'] = window
        # Same values written by ENGINE's should_stop callback; the lifecycle
        # owner still controls the independent execution status/stop-phase axes.
        execution = runtime['executions']['EX-1']
        for status in ('starting', 'running'):
            transition_execution(execution, status, at='2026-09-20T00:00:00Z')
        execution.update(stop_reason='submission_intent', stop_observed_at='2026-09-20T00:00:01Z')
        transition_execution(execution, 'stopping', at='2026-09-20T00:00:01Z')
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(loaded['executions']['EX-1']['execution_window']['remaining_ms_at_start'], 750)
        loaded['executions']['EX-1']['execution_window']['execution_id'] = 'EX-other'
        with self.assertRaisesRegex(ValueError, 'execution window'):
            self.repository.validate_candidate(saved, loaded)

    def test_checkpoint_observation_evidence_uses_actual_same_cas_bytes(self):
        from support.entry import entry
        _entry = entry()
        from do_math.observations import preserve_checkpoint
        instance, runtime = execution_state()
        head = self.repository.initialize(instance, runtime)
        raw = b'{"type":"public_message","message":"observed"}\n'
        reference = 'runtime/artifacts/BA-observation/provider-evidence/events.jsonl'
        checkpoint, _ = preserve_checkpoint(self.repository_path / 'missing-checkpoint',
                                            artifact_prefix='runtime/artifacts/BA-observation/checkpoint', max_bytes=4096, clock=_entry.ports.clock)
        checkpoint.update(observation_sources=[{'artifact_ref': reference, 'path': 'events.jsonl',
                                                'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}],
                          observation_evidence_complete=True, observation_evidence_omitted=[])
        runtime['checkpoints'] = {'EX-1': checkpoint}
        with self.assertRaisesRegex(ValueError, 'artifact evidence'):
            self.repository.validate_candidate(instance, runtime, head)
        head = self.repository.save_with_state(head, instance, runtime, artifacts={reference: raw})[0]
        _, instance, loaded = self.repository.load(head)
        self.assertEqual(loaded['checkpoints']['EX-1'], checkpoint)
        missing = '^artifact evidence missing or hash differs: ' + reference + '$'
        for change, reason in (('bytes', missing),
                               ('omissions', '^complete observation evidence cannot contain omissions$'),
                               ('final', missing)):
            with self.subTest(change=change):
                broken = deepcopy(loaded)
                row = broken['checkpoints']['EX-1']
                if change == 'bytes':
                    row['observation_sources'][0]['bytes'] += 1
                elif change == 'omissions':
                    row['observation_evidence_omitted'] = [{'path': 'missing', 'reason': 'read_error'}]
                else:
                    row['final_observation'] = deepcopy(checkpoint)
                    row['final_observation']['observation_sources'][0]['sha256'] = '0' * 64
                with self.assertRaisesRegex(ValueError, reason):
                    self.repository.validate_candidate(instance, broken, head)

    def test_actual_submission_authority_revocation_round_trip(self):
        """About 0.35-0.5 s, over the 0.2 s unit budget: a maintenance submission sealed on disk, two publications and three validations through the storage contract."""
        from do_math.execution_lifecycle import record_submission_intent, transition_execution
        from support.execution_inputs import sealed_maintenance_submission
        instance, runtime = execution_state('maintenance')
        head = self.repository.initialize(instance, runtime)
        with tempfile.TemporaryDirectory() as workspace:
            intent, artifacts = sealed_maintenance_submission(workspace, 'EX-1')
        execution = runtime['executions']['EX-1']
        for status in ('starting', 'running'):
            transition_execution(execution, status, at='2026-09-20T00:00:00Z')
        record_submission_intent(execution, intent,
                                 {'id': 'CT-submit', 'kind': 'submit_intent', 'state': 'accepted', 'execution_id': 'EX-1'},
                                 at='2026-09-20T00:00:01Z')
        head = self.repository.save_with_state(head, instance, runtime, artifacts=artifacts)[0]
        _, instance, runtime = self.repository.load(head)
        self.assertEqual(runtime['executions']['EX-1']['authority_revocation']['receipt_id'], 'CT-submit')
        for field, value in (('receipt_id', 'CT-other'), ('state', 'rejected'), ('kind', 'self_check')):
            with self.subTest(field=field):
                broken = deepcopy(runtime)
                if field == 'receipt_id':
                    broken['executions']['EX-1']['authority_revocation'][field] = value
                else:
                    broken['executions']['EX-1']['submission_receipt'][field] = value
                with self.assertRaisesRegex(ValueError, 'revocation'):
                    self.repository.validate_candidate(instance, broken)

    def test_actual_input_preparation_begin_and_cancel_round_trip(self):
        """About 0.2 s, at the 0.2 s unit budget: two publications and a validation through the storage contract."""
        from do_math.execution_lifecycle import begin_preparation, end_preparation
        instance, runtime = execution_state()
        execution = runtime['executions']['EX-1']
        begin_preparation(execution, at='2026-09-20T00:00:00Z')
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        end_preparation(runtime['executions']['EX-1'], at='2026-09-20T00:01:00Z',
                        stage='packing', reason='input overflow', cancelled=True)
        head = self.repository.save_with_state(head, instance, runtime)[0]
        saved = self.repository.load(head)[2]['executions']['EX-1']
        self.assertEqual(saved['outcome'], 'cancelled')
        self.assertEqual(saved['input_preparation']['reason'], 'input overflow')
        runtime['executions']['EX-1']['input_preparation']['unregistered'] = True
        with self.assertRaisesRegex(ValueError, r"^runtime/executions/EX-1/input_preparation: Additional properties are "
                                                r"not allowed \('unregistered' was unexpected\)$"):
            self.repository.validate_candidate(instance, runtime)

    def test_actual_profiles_activities_and_observation_producers(self):
        from support.entry import entry
        _entry = entry()
        from do_math.observations import ObservationTracker
        instance, runtime = execution_state()
        tracker = ObservationTracker('EX-1', self.repository_path, {'observation_mode': 'deadline_only'},
                                      time_port=scripted_clock(lambda: 1.25))
        fact = tracker.fact('observation_fact', {'type': 'provider_report', 'cost': 0.125}, 1.5)
        runtime['observation_facts'] = {fact['id']: fact}
        head = self.repository.initialize(instance, runtime)
        _, saved, state = self.repository.load(head)
        self.assertEqual(state['observation_facts'][fact['id']], fact)
        self.assertEqual(saved['role_profile_refs'], instance['role_profile_refs'])
        self.assertIn('research/role_profile_refs/state.json', self.repository.list_files('research/', head))
        selection = next(row for row in self.repository.load_records(head)[3] if row['family'] == 'role_profile_refs')
        self.assertTrue(all(set(ref) == {'id', 'revision', 'sha256'} for refs in selection['record'].values()
                            for ref in refs))
        broken = deepcopy(state)
        broken['executions']['EX-1']['execution_profile_ref']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'profile'):
            self.repository.validate_candidate(saved, broken, head)
        broken = deepcopy(state)
        broken['observation_facts'][fact['id']]['event_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'event.*hash'):
            self.repository.validate_candidate(saved, broken, head)

    def test_actual_external_uncertainty_reconciliation_and_retry_round_trip(self):
        from support.entry import entry
        _entry = entry()
        from do_math import external, governance as gov
        instance = approved_governance_instance()
        source_id = next(iter(instance['governance_sources']))
        instance, runtime, _ = gov.apply_decision(instance, current_state(runtime={'queue': [], 'history': []})[1],
            {'kind': 'grant', 'grant': {'id': 'GR-http', 'kind': 'http', 'reuse': 'reusable',
             'allowed_origins': ['https://example.test'], 'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/']}},
            source_ref=source_id, clock=_entry.ports.clock)
        operation = external.prepare_operation({'method': 'POST', 'url': 'https://example.test/action'}, 'GR-http',
                                               source_id)
        # Domain requests acquire durable IDs at the lifecycle application
        # boundary; this focused external-ledger fixture supplies that identity.
        for action in runtime['queue']:
            action.setdefault('id', self.clock.new_id('AC'))
            action.setdefault('lineage_id', action['id'])
        runtime['external_operations'] = {operation['id']: operation}
        head = self.repository.initialize(instance, runtime)

        def persist(row):
            nonlocal head
            runtime['external_operations'][row['id']] = deepcopy(row)
            head = self.repository.save_with_state(head, instance, runtime)[0]
            self.assertEqual(self.repository.load(head)[2]['external_operations'][row['id']], row)
        unknown = external.execute_operation(operation, instance['grants']['GR-http'], persist=persist,
                                             transport=lambda *_: {'http_status': 503, 'body': b'uncertain'},
                                             runtime=runtime, clock=_entry.ports.clock, environment=_entry.environment)
        self.assertEqual(unknown['status'], 'unknown')
        self.assertIn('credential_env', unknown)
        self.assertIsNone(unknown['credential_env'])
        self.assertIn('succeeded', unknown)
        self.assertIsNone(unknown['succeeded'])
        self.assertNotIn('effect_absent', unknown)
        self.assertTrue(external.request_binding_current(unknown))
        with self.assertRaises(ValueError) as rejected:
            external.validate_operation(unknown, instance['grants']['GR-http'], _entry.ports.clock.now(), runtime=runtime)
        self.assertIs(type(rejected.exception), ValueError)
        self.assertEqual(str(rejected.exception), 'operation is not startable')

        _, saved_instance, saved_runtime = self.repository.load(head)
        for changes, reason in (
                ({'request_sha256': '0' * 64}, 'external operation request/key differs from sealed bytes'),
                ({'status': 'confirmed', 'succeeded': False}, 'confirmed external operation requires success evidence'),
                ({'status': 'failed', 'effect_absent': False}, 'failed external operation requires effect-absence evidence'),
                ({'status': 'unknown', 'succeeded': True}, 'unknown external effect has a definitive success value'),
                ({'status': 'cancelled', 'transmitted': True}, 'cancelled external effect was not confirmed untransmitted'),
                ({'handling': 'reconciled', 'reconciliation': {}}, 'reconciled handling lacks external effect evidence')):
            with self.subTest(changes=changes):
                damaged = deepcopy(saved_runtime)
                damaged['external_operations'][operation['id']].update(changes)
                with self.assertRaises(ValueError) as rejected:
                    self.repository.save_with_state(head, saved_instance, damaged)
                self.assertIs(type(rejected.exception), ValueError)
                self.assertEqual(str(rejected.exception), reason)
                self.assertEqual(self.repository.load(), (head, saved_instance, saved_runtime))
        proof = {'operation_id': operation['id'], 'request_sha256': operation['request_sha256'],
                 'idempotency_key': operation['idempotency_key'], 'evidence_ref': 'synthetic-remote-receipt',
                 'observed_at': '2026-09-20T00:00:00Z', 'fact': 'effect_absent'}
        absent = external.reconcile_operation(unknown, proof, 'failed', source='user', effect_absent=True)
        persist(absent)
        self.assertIs(absent['succeeded'], False)
        self.assertIs(absent['effect_absent'], True)
        self.assertIn('external_id', absent)
        self.assertIsNone(absent['external_id'])
        self.assertIn('idempotency_evidence', absent['reconciliation'])
        self.assertIsNone(absent['reconciliation']['idempotency_evidence'])
        retry = external.prepare_retry(absent, {'kind': 'effect_absent', 'request_sha256': operation['request_sha256'],
                                                'idempotency_key': operation['idempotency_key'],
                                                'evidence_ref': proof['evidence_ref']}, source='user', now_iso=_entry.ports.clock.now())
        persist(retry)
        self.assertEqual(self.repository.load(head)[2]['external_operations'][operation['id']]['previous_outcome'],
                         'failed')
        _, saved_instance, saved_runtime = self.repository.load(head)
        damaged = deepcopy(saved_runtime)
        damaged['external_operations'][operation['id']]['retry_evidence']['request_sha256'] = '0' * 64
        with self.assertRaises(ValueError) as rejected:
            self.repository.save_with_state(head, saved_instance, damaged)
        self.assertIs(type(rejected.exception), ValueError)
        self.assertEqual(str(rejected.exception), 'external retry evidence differs from the operation')
        self.assertEqual(self.repository.load(), (head, saved_instance, saved_runtime))



class GovernanceRecordTests(ProducerCase):
    def test_governance_actual_approval_and_semantics(self):
        from do_math import governance as gov
        head = self.repository.initialize(approved_governance_instance(), current_state()[1])
        _, instance, runtime = self.repository.load(head)
        self.assertEqual(gov.governance_view(instance)['goal'], 'Prove P')
        instance['governance']['CH-1']['content']['goal'] = 'Something else'
        with self.assertRaisesRegex(ValueError, 'approved proposal'):
            self.repository.validate_candidate(instance, runtime, head)

    def test_academic_resolution_accepts_only_resolved_sealed_artifact_evidence(self):
        from do_math import academic
        instance, runtime = execution_state('research_plan')
        instance.update(approved_governance_instance())
        basis = {'goal_ref': 'CH-1', 'records': []}
        runtime['executions']['EX-1'].update(role='research_plan', input_solution_basis=basis)
        runtime['external_rejections'] = [{'id': 'RJ-1', 'actor': 'reviewer', 'text': 'objection',
                                           'source_ref': 'input', 'solution_basis': basis}]
        head = self.repository.initialize(instance, runtime)
        path = 'runtime/artifacts/BA-1/reply.txt'
        raw = b'preserved answer'
        academic.record_resolution(instance, runtime, basis, {'id': 'RJ-1', 'decision': 'resolved',
                                   'evidence': 'verified reply', 'evidence_refs': [path]}, execution_id='EX-1',
                                   resolve_evidence=lambda ref: raw if ref == path else None)
        with self.assertRaisesRegex(ValueError, 'artifact evidence'):
            self.repository.validate_candidate(instance, runtime, head)
        saved = self.repository.save_with_state(head, instance, runtime, artifacts={path: raw})[0]
        _, instance, runtime = self.repository.load(saved)
        self.assertEqual(runtime['academic_resolution_records'][0]['evidence_hashes'][path],
                         hashlib.sha256(raw).hexdigest())

        damaged = deepcopy(runtime)
        damaged['academic_resolution_records'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError) as rejected:
            self.repository.save_with_state(saved, instance, damaged)
        self.assertIs(type(rejected.exception), ValueError)
        self.assertEqual(str(rejected.exception), 'academic resolution seal/evidence binding is invalid')
        self.assertEqual(self.repository.load(), (saved, instance, runtime))
        broken = deepcopy(runtime)
        row = broken['academic_resolution_records'][0]
        row['evidence_hashes'][path] = '0' * 64
        row['sha256'] = exact_content_hash({k: v for k, v in row.items() if k != 'sha256'})
        with self.assertRaisesRegex(ValueError, 'artifact evidence'):
            self.repository.validate_candidate(instance, broken, saved)

        # The actual resolution producer's cross-family edges are mandatory,
        # independently of its well-formed hashes and preserved artifact bytes.
        for field, missing in (('rejection_id', 'RJ-absent'), ('execution_id', 'EX-absent'),
                               ('evidence_refs', 'KN-absent')):
            with self.subTest(reference=field):
                damaged = deepcopy(runtime)
                record = damaged['academic_resolution_records'][0]
                if field == 'evidence_refs':
                    record[field] = [*record[field], missing]
                    record['evidence_hashes'][missing] = hashlib.sha256(b'unknown record').hexdigest()
                else:
                    record[field] = missing
                record['sha256'] = exact_content_hash({key: value for key, value in record.items() if key != 'sha256'})
                with self.assertRaisesRegex(ValueError,
                        '^academic_resolution_records references unknown record: ' + missing + '$'):
                    self.repository.validate_candidate(instance, damaged, saved)
                self.assertEqual(self.repository.load(saved)[2], runtime)
                self.assertEqual(self.repository.read(path, saved), raw)

    def test_grant_question_kind_survives_storage(self):
        # The engine marks the user question of an external request that names no grant
        # (engine._apply_extensions); the status question view reads that mark.
        from support.entry import entry
        _entry = entry()
        from do_math import questions
        instance, runtime = execution_state('research_work')
        question = questions.link(runtime, execution_id='EX-1', field='extensions/external_requests/0/purpose',
                                  owner='user', targets=['EX-1'], reason='External action requires a user grant', clock=_entry.ports.clock)
        question['question_kind'] = 'grant'
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        row, = loaded['question_links']
        self.assertEqual(row['question_kind'], 'grant')
        for field in ('resolution_ref', 'checked_by'):
            self.assertIn(field, row)
            self.assertIsNone(row[field])
        self.assertEqual(questions.open_links(loaded, 'user'), [row])
        from do_math.question_engine import question_view, user_questions
        view = question_view(saved, loaded, lambda paths: self.repository.read_many(paths, head))
        self.assertIn('text', view[0])
        self.assertIsNone(view[0]['text'])
        self.assertEqual(view[0]['source_status'], 'unavailable')
        self.assertEqual(user_questions(view), [])
        questions.resolve_user(loaded, [row['id']], resolution_ref='EX-1', affected_ids=['EX-1'])
        next_head = self.repository.save_with_state(head, saved, loaded)[0]
        _, saved, resolved = self.repository.load(next_head)
        self.assertEqual(questions.open_links(resolved, 'user'), [])
        self.assertEqual(resolved['question_links'][0]['resolution_ref'], 'EX-1')
        self.assertEqual(resolved['question_links'][0]['unresolved_target_ids'], [])
        self.assertIsNone(resolved['question_links'][0]['checked_by'])


class KnowledgeRecordTests(ProducerCase):
    def test_relation_claim_endpoint_basis_survives_storage_and_remains_typed(self):
        from support.entry import entry
        _entry = entry()
        from do_math import knowledge
        from support.knowledge_builders import knowledge_candidate
        instance, runtime = current_state()
        endpoints = []
        for title in ('source', 'target'):
            instance, runtime, kid = knowledge_io.import_candidate(instance, runtime,
                knowledge_candidate(title=title, lean_code='', declaration_names=[]),
                source_ref='fixture:input', actor_ref='fixture:user', clock=_entry.ports.clock)
            endpoints.append(kid)
        claim = {'kind': 'formally_implies', 'source': endpoints[0], 'target': endpoints[1],
                 'confirmed_scope': 'True implies True'}
        instance, runtime, kid = knowledge_io.import_candidate(instance, runtime,
            knowledge_candidate(title='relation proof', relation_claim=claim),
            source_ref='fixture:input', actor_ref='fixture:user', clock=_entry.ports.clock)
        expected = deepcopy(instance['knowledge'][kid]['relation_endpoint_basis'])
        head = self.repository.initialize(instance, runtime)
        _, saved, running = self.repository.load(head)
        self.assertEqual(saved['knowledge'][kid]['relation_endpoint_basis'], expected)
        self.assertTrue(knowledge.validate_basis(expected, saved, running)['valid'])
        for invalid in ({}, [{'id': endpoints[0], 'sha256': 'bad', 'status': 'active'}],
                        [{'id': endpoints[0], 'sha256': 'a' * 64}]):
            with self.subTest(invalid=invalid):
                changed = deepcopy(saved)
                changed['knowledge'][kid]['relation_endpoint_basis'] = invalid
                with self.assertRaisesRegex(ValueError, 'relation_endpoint_basis'):
                    self.repository.validate_candidate(changed, running, head)

    def test_relation_schema_and_domain_kind_evidence_are_both_enforced(self):
        from support.entry import entry
        _entry = entry()
        from do_math import knowledge_records as kr
        instance = knowledge_io.ensure_ontology(current_state()[0])
        for text in ('one', 'two'):
            instance, _ = kr.create_candidate(instance, {'kind': 'observation', 'statement': text, 'dependencies': []},
                                              source_ref='input', actor_ref='user', clock=_entry.ports.clock)
        ids = list(instance['knowledge'])
        instance, relation_id = knowledge_io.import_relation(instance, {'kind': 'supports', 'source': ids[0],
                                                                        'target': ids[1], 'evidence': 'input'},
                                                             source_ref='source', actor_ref='author', clock=_entry.ports.clock)
        head = self.repository.initialize(instance, current_state()[1])
        _, saved, runtime = self.repository.load(head)
        self.assertEqual(self.repository.read_record(relation_id, head)['family'], 'relations')
        saved['relations'][0].pop('evidence')
        with self.assertRaisesRegex(ValueError, 'evidence_required'):
            self.repository.validate_candidate(saved, runtime, head)

    def test_installed_initialization_and_knowledge_producers_round_trip(self):
        from support.entry import entry
        _entry = entry()
        from do_math.initialization import initialize_state
        from do_math.knowledge_io import ensure_ontology
        from do_math.knowledge_records import create_candidate
        instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal='question', workspace=self.repository_path,
                                             config={}, source_input='question', clock=_entry.ports.clock, host=_entry.ports.host)
        instance = ensure_ontology(instance)
        instance, kid = create_candidate(instance, {'kind': 'observation', 'statement': 'a bounded observation',
                                                    'dependencies': []}, source_ref='user-input', actor_ref='user', clock=_entry.ports.clock)
        head = self.repository.initialize(instance, runtime)
        _, loaded, _ = self.repository.load(head)
        self.assertEqual(loaded['knowledge'][kid], instance['knowledge'][kid])
        self.assertEqual(self.repository.read_record(kid, head)['family'], 'knowledge')
        bad = deepcopy(loaded)
        bad['knowledge'][kid]['exposition_id'] = 'XP-absent'
        with self.assertRaisesRegex(ValueError, 'unknown record'):
            self.repository.save_with_state(head, bad, runtime)

    def test_actual_uncertainty_text_and_object_preserve_wire_meaning(self):
        from support.entry import entry
        _entry = entry()
        from do_math import submission
        wire = submission.extension_schema({'role': 'research_work'})
        for value in ('Not a proof', {'claim': 'Not a proof', 'scope': 'finite search only'}):
            with self.subTest(value=value):
                jsonschema.validate({'knowledge_metadata': [{'title': 'Bounded', 'uncertainty_assessment': value}]}, wire)
                instance, runtime, kid = knowledge_io.import_candidate(*current_state(),
                    {'kind': 'observation', 'title': 'Bounded', 'statement': 'Finite search',
                     'explanation': 'Bounded search only', 'summary': 'No proof', 'lean_code': '',
                     'declaration_names': [], 'dependencies': [], 'uncertainty_assessment': value},
                    source_ref='input', actor_ref='user', clock=_entry.ports.clock)
                checked = self.repository.validate_candidate(instance, runtime)
                self.assertEqual(checked['instance']['knowledge'][kid]['uncertainty_assessment'], value)

    def test_actual_review_cycle_and_identity_producer_round_trip(self):
        instance, runtime, kid, aid = reviewed_candidate(self.repository_path)
        cycle = runtime['review_cycles']['RC-1']
        self.assertEqual((cycle['status'], cycle['decision']), ('unresolved', 'unresolved'))
        self.assertEqual(instance['identity_assessments'][aid]['decision'], 'unresolved')
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(saved['identity_assessments'][aid]['review_cycle_id'], 'RC-1')
        self.assertEqual(loaded['review_cycles']['RC-1']['sealed'], cycle['sealed'])
        broken = deepcopy(loaded)
        broken['review_cycles'] = {}
        with self.assertRaisesRegex(ValueError, 'unknown record'):
            self.repository.validate_candidate(saved, broken)
        for field, value, reason in (
                ('basis', {**saved['identity_assessments'][aid]['basis'], 'formal': '0' * 64}, 'identity assessment premise hash differs from immutable inputs'),
                ('decision', 'mismatch', 'identity assessment differs from its sealed review'),
                ('scope_complete', not saved['identity_assessments'][aid]['scope_complete'], 'identity assessment does not reproduce the sealed review result')):
            with self.subTest(field=field):
                damaged = deepcopy(saved)
                damaged['identity_assessments'][aid][field] = value
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    self.repository.validate_candidate(damaged, loaded)
        # Nonmatching historical assessments can be independently recorded;
        # a positive identity claim must bind the actual sealed review.
        standalone = deepcopy(saved)
        standalone['identity_assessments'][aid].pop('review_cycle_id')
        self.repository.validate_candidate(standalone, loaded)
        standalone['identity_assessments'][aid]['decision'] = 'match'
        with self.assertRaisesRegex(ValueError, '^identity match requires a sealed review cycle$'):
            self.repository.validate_candidate(standalone, loaded)
        damaged = deepcopy(loaded)
        next(iter(damaged['review_cycles']['RC-1']['results'].values()))['execution_id'] = 'EX-missing'
        with self.assertRaisesRegex(ValueError, '^review result requires its actual identity-review execution$'):
            self.repository.validate_candidate(saved, damaged)
        self.assertEqual(self.repository.load(head), (head, saved, loaded))

    def test_staged_review_producer_keeps_transient_candidate_and_real_transition(self):
        """About 0.3-0.35 s, over the 0.2 s unit budget: two synthetic trust toolchains are hashed and the real engine loads, saves and is validated on the in-process Git fake."""
        from support.entry import entry
        _entry = entry()
        from support.trust_inputs import trust_fixture, trust_environment
        from support.knowledge_builders import formal_evidence
        from do_math import knowledge as k
        from do_math.review_policy import build_review_policy
        instance, runtime, kid, _ = reviewed_candidate(self.repository_path, verified=True)
        # The legacy engine double registers a second synthetic trust environment; only its records are used.
        eid = 'TE-synthetic-staged'
        environment, binding = trust_environment(trust_fixture(self.repository_path, ['synthetic-staged']),
                                                  environment_id=eid, status='registered')
        instance['trust_environments'][eid] = environment
        runtime['trust_bindings'][eid] = binding
        instance['review_policy'] = build_review_policy(reviewer_count=1, max_rounds=1)
        transition = k.begin_transition(instance, eid, clock=_entry.ports.clock)
        transition = k.record_transition_result(instance, transition, {'id': kid, **formal_evidence(instance, kid, eid)})
        runtime['trust_transitions'][transition['id']] = transition
        runtime.setdefault('queue', [])
        engine, _ = self.engine_on(instance, runtime)
        before = deepcopy(engine.instance['formal_results'])
        cid = engine._start_staged_identity_review(transition['id'], kid)
        engine._save()
        _, saved, loaded = self.repository.load()
        self.assertEqual(saved['formal_results'], before)
        self.assertEqual(loaded['review_cycles'][cid]['transition_id'], transition['id'])
        broken = deepcopy(loaded)
        broken['review_cycles'][cid]['staged_candidate']['transition_basis'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'staged review'):
            self.repository.validate_candidate(saved, broken)
        for field in ('target_environment', 'proposal'):
            broken = deepcopy(loaded)
            staged = broken['review_cycles'][cid]['staged_candidate']
            if field == 'target_environment': staged[field]['id'] = 'TE-absent'
            else: staged[field]['statement'] = 'substituted proposition'
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,
                    '^staged review does not bind its actual transition target/environment$'):
                self.repository.validate_candidate(saved, broken)

    def test_verified_identity_and_environment_continuity_round_trip(self):
        """About 0.35-0.4 s, over the 0.2 s unit budget: two synthetic trust toolchains are hashed and the state passes the storage contract four times."""
        from support.entry import entry
        _entry = entry()
        from support.trust_inputs import trust_fixture, trust_environment
        from support.knowledge_builders import formal_evidence
        from do_math import knowledge as k
        instance, runtime, kid, aid = reviewed_candidate(self.repository_path, verified=True)
        self.assertEqual((runtime['review_cycles']['RC-1']['status'], runtime['review_cycles']['RC-1']['decision']),
                         ('completed', 'match'))
        self.assertEqual(instance['identity_assessments'][aid]['decision'], 'match')
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        formal_id = instance['knowledge'][kid]['formal_result_id']
        for field, value, reason in (
                ('trust_environment_id', None, 'sealed formal result requires trust environment'),
                ('publication_state', 'candidate', 'formal publication state contradicts verification')):
            with self.subTest(field=field):
                broken = deepcopy(instance)
                if field == 'trust_environment_id':
                    broken['formal_results'][formal_id].pop(field)
                else:
                    broken['formal_results'][formal_id][field] = value
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    self.repository.validate_candidate(broken, runtime)
        broken = deepcopy(instance)
        broken['formal_results'][formal_id]['lean_code'] += '\n-- changed after sealing\n'
        with self.assertRaisesRegex(ValueError, '^sealed formal result changed: ' + formal_id + '$'):
            self.repository.validate_candidate(broken, runtime, head)
        self.assertEqual(self.repository.load(), (head, instance, runtime))
        inactive = deepcopy(instance)
        inactive['trust_environments'][inactive['active_trust_environment']]['status'] = 'registered'
        with self.assertRaisesRegex(ValueError, '^active trust environment reference is not active$'):
            self.repository.validate_candidate(inactive, runtime)
        use = k.assess_use(instance['knowledge'][kid], instance)
        self.assertTrue(use['valid'], use)
        # The legacy engine double registers the next synthetic trust environment; only its records are used.
        eid = 'TE-synthetic-next'
        environment, binding = trust_environment(trust_fixture(self.repository_path, ['synthetic-next']),
                                                  environment_id=eid, status='registered')
        instance['trust_environments'][eid] = environment
        runtime['trust_bindings'][eid] = binding
        transition = k.begin_transition(instance, eid, clock=_entry.ports.clock)
        transition = k.record_transition_result(instance, transition, {'id': kid, **formal_evidence(instance, kid, eid)})
        instance = k.activate_transition(instance, transition, at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        transition['status'] = 'active'
        runtime['trust_transitions'][transition['id']] = transition
        next_head = self.repository.save_with_state(head, instance, runtime)[0]
        _, saved, loaded = self.repository.load(next_head)
        inherited = next(a for a in saved['identity_assessments'].values() if a.get('previous_assessment_id') == aid)
        self.assertTrue(inherited['continuity_comparison']['equivalent'])
        for change, reason in (('comparison', '^identity continuity differs from its sealed source and transition$'),
                               ('review', '^identity_assessments references unknown record: RC-missing$')):
            with self.subTest(change=change):
                broken = deepcopy(saved)
                row = broken['identity_assessments'][inherited['id']]
                if change == 'comparison':
                    row['continuity_comparison']['equivalent'] = False
                else:
                    row['review_cycle_id'] = 'RC-missing'
                with self.assertRaisesRegex(ValueError, reason):
                    self.repository.validate_candidate(broken, loaded)


class RecordSchemaTests(unittest.TestCase):
    """Stored record schemas checked on producer output alone (``record_schemas``), without a store."""

    def test_task_input_invalidation_keeps_request_and_reason(self):
        fields = RECORDS['tasks']['properties']
        # The pending input signal is the input request's ID; consumption removes it.
        Draft202012Validator(fields['newinput']).validate('UC-source')
        Draft202012Validator(fields['assessment']['properties']['invalidated_reason']).validate(
            'Required source content changed')
        for value, reason in ((False, "^False is not of type 'string'"), (True, "^True is not of type 'string'"),
                              (3, "^3 is not of type 'string'")):
            with self.subTest(value=value), self.assertRaisesRegex(ValidationError, reason):
                Draft202012Validator(fields['newinput']).validate(value)

    def test_scoped_external_operation_keeps_actual_producer_fields(self):
        from do_math.external import prepare_operation
        row = prepare_operation({'method': 'POST', 'url': 'https://example.test/action'}, 'GR-1', 'SO-1',
                                target_id='TK-1', purpose='publish', subject='result', actor_kind='ai')
        Draft202012Validator(RECORDS['external_operations']).validate(row)
        with self.assertRaisesRegex(ValidationError,
                                    r"^Additional properties are not allowed \('unregistered_scope' was unexpected\)"):
            Draft202012Validator(RECORDS['external_operations']).validate({**row, 'unregistered_scope': True})

    def test_academic_assessment_binds_declared_task_assessment_hash(self):
        from do_math.state_contract import default_state_contract
        schema = default_state_contract().family('runtime', 'academic_assessments').schema
        row = {'requirement_id': 'R-1', 'solution_basis': {'goal_ref': 'CH-1', 'records': []},
               'requirements_sha256': 'a' * 64, 'decision': 'unresolved', 'evidence': [],
               'assessor': 'research_plan', 'execution_id': 'EX-1', 'task_id': 'TK-1',
               'task_assessment_sha256': 'b' * 64}
        jsonschema.validate([row], schema)
        row['task_assessment_sha256'] = 'not-a-hash'
        with self.assertRaisesRegex(ValidationError, r"^'not-a-hash' does not match '\^\[0-9a-f\]\{64\}\$'"):
            jsonschema.validate([row], schema)


class ProducerStorageContractTests(unittest.TestCase):
    def test_accepted_uncertainty_metadata_matches_registered_storage_shape(self):
        from support.entry import entry
        _entry = entry()
        from do_math import submission
        from do_math.state_contract import default_state_contract
        from support.record_builders import research_work_context, two_observation_output
        wire = submission.extension_schema({'role': 'research_work'})
        registered = default_state_contract().family('research', 'knowledge').schema
        output = two_observation_output()
        output['integration_bundles'][0]['members'].append('activity-extensions.json/knowledge_metadata/0')
        workspace = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for value in ('Not a proof', {'claim': 'Not a proof', 'scope': 'finite search only'}, None, [], 7, False):
            with self.subTest(value=value):
                extension = {'knowledge_metadata': [{'title': 'A', 'uncertainty_assessment': value}]}
                valid = isinstance(value, (str, dict))
                errors = list(Draft202012Validator(wire).iter_errors(extension))
                self.assertEqual(not errors, valid)
                issues = submission.payload_issues(output, contracts.schema_for('research_work'),
                                                   research_work_context(), extension, workspace, clock=_entry.ports.clock)
                self.assertEqual(not issues, valid, issues)
                proposed = {**output['knowledge'][0], 'uncertainty_assessment': value}
                if not valid:
                    self.assertTrue(any(row['rule_id'] == 'schema.type' and
                                        row['path'].endswith('/uncertainty_assessment') for row in issues), issues)
                    with self.assertRaisesRegex(ValueError, 'uncertainty_assessment'):
                        knowledge_io.import_candidate({}, {}, proposed,
                                                      source_ref='fixture:submission', actor_ref='fixture:author', clock=_entry.ports.clock)
                    continue
                state, _, kid = knowledge_io.import_candidate({}, {}, proposed,
                                                              source_ref='fixture:submission', actor_ref='fixture:author', clock=_entry.ports.clock)
                Draft202012Validator(registered).validate(state['knowledge'][kid])
                self.assertEqual(state['knowledge'][kid]['uncertainty_assessment'], value)


class SchemaIngressTests(ProducerCase):
    def test_operational_disposition_variant_is_validated_at_storage(self):
        """A public failure/review prefix creates the actual disposition; about 10 s cold."""
        from support.cross_states import assert_event, failure_ready, queued
        sim = failure_ready()
        action = queued(sim, 'operational_review')
        self.assertIsNotNone(action)
        assert_event(sim, action, 'operation', 'continue')
        published = deepcopy(sim.engine.store.load())
        head, instance, runtime = published
        self.assertTrue(runtime['operational_dispositions'])
        identifier, record = next(iter(runtime['operational_dispositions'].items()))
        self.assertEqual(record['disposition']['kind'], 'continue')
        damaged = deepcopy(runtime)
        damaged['operational_dispositions'][identifier]['disposition']['kind'] = 'unsupported-disposition'
        before = deepcopy(damaged)
        with self.assertRaisesRegex(ValueError, '^operational disposition kind is unsupported$'):
            sim.engine.store.save_with_state(head, instance, damaged)
        self.assertEqual(damaged, before)
        self.assertEqual(sim.engine.store.load(), published)

    def test_capability_and_import_seals_reject_damage_before_publication(self):
        """The two records come from real public activation; about 7 s cold."""
        from support.sim import Sim
        sim = Sim.activated()
        published = deepcopy(sim.engine.store.load())
        head, instance, runtime = published
        self.assertTrue(instance['capability_evidence'])
        self.assertTrue(runtime['intent_imports'])
        capability_id = next(iter(instance['capability_evidence']))
        import_id = next(iter(runtime['intent_imports']))
        damaged_i, damaged_r = deepcopy((instance, runtime))
        capability = damaged_i['capability_evidence'].pop(capability_id)
        capability['id'] = 'CE-' + '0' * 64
        damaged_i['capability_evidence'][capability['id']] = capability
        cases = [(damaged_i, damaged_r, 'capability evidence ID differs from its content')]
        damaged_i, damaged_r = deepcopy((instance, runtime))
        damaged_r['intent_imports'][import_id]['sha256'] = '0' * 64
        cases.append((damaged_i, damaged_r, 'sealed intent import hash mismatch'))
        for candidate_i, candidate_r, reason in cases:
            with self.subTest(reason=reason):
                before = deepcopy((candidate_i, candidate_r))
                with self.assertRaises(ValueError) as caught:
                    sim.engine.store.save_with_state(head, candidate_i, candidate_r)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual((candidate_i, candidate_r), before)
                self.assertEqual(sim.engine.store.load(), published)

    def test_cold_lifecycle_validation_checks_original_bytes_and_current_projection(self):
        from do_math.initialization import initialize_state
        from do_math.record_schemas import validate_lifecycle
        from support.entry import entry
        port = entry().ports
        instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal='정확한 원문',
            workspace=self.repository_path, config={}, source_input='정확한 원문', clock=port.clock, host=port.host)
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        self.assertIsNone(validate_lifecycle(instance, runtime))
        self.assertTrue(self.repository.contract.validate(instance, runtime))
        damaged = deepcopy(instance)
        damaged['lifecycle']['immutable_input']['sha256'] = '0' * 64
        before = deepcopy((damaged, runtime))
        with self.assertRaisesRegex(ValueError, '^immutable input bytes or hash differs$'):
            self.repository.contract.validate(damaged, runtime)
        self.assertEqual((damaged, runtime), before)
        cases = [
            ({**instance, 'lifecycle': None}, runtime,
             'current lifecycle contract: the lifecycle and the runtime status are required'),
            (instance, {**runtime, 'status': None},
             'current lifecycle contract: the lifecycle and the runtime status are required'),
            ({**instance, 'lifecycle': {**instance['lifecycle'], 'permanently_closed': True}}, runtime,
             'current lifecycle contract: a permanently closed instance cannot have a live projection'),
            *[(instance, {**runtime, 'last_observed_utc': value},
               'current lifecycle contract: the persisted UTC high-water is absent or invalid')
              for value in (None, 'invalid+00:00', '2090-01-01T00:00:00+09:00')],
        ]
        for candidate_i, candidate_r, reason in cases:
            with self.subTest(reason=reason):
                before = deepcopy((candidate_i, candidate_r))
                with self.assertRaises(ValueError) as caught:
                    validate_lifecycle(candidate_i, candidate_r)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual((candidate_i, candidate_r), before)

    def test_registered_metadata_references_cover_adoption_profiles_events_and_trust(self):
        """Public activation builds the four actual metadata families (about 7 s cold)."""
        from support.sim import Sim
        sim = Sim.activated()
        request = sim.control('input', text='Retain the current natural-number domain and the pending input.')
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(request['request_id'])['effect'], 'applied')
        head, instance, runtime = sim.engine.store.load()
        lifecycle = instance['lifecycle']
        check, adoption = lifecycle['intent_check'], lifecycle['adoption']
        self.assertTrue(runtime['pending_events'])
        self.assertTrue(runtime['trust_bindings'])
        expected_lifecycle = [(lifecycle['input_id'], 'inputs'),
            (check['interpretation_execution_id'], 'executions'),
            (check['check_execution_id'], 'executions'),
            (adoption['initial_profile_ref']['id'], 'execution_profiles'),
            *[(identifier, 'grants') for identifier in adoption['initial_grant_ids']],
            *[(identifier, 'grants') for identifier in adoption['research_grant_ids']]]
        cases = (
            ('research', 'lifecycle', lifecycle, expected_lifecycle),
            ('research', 'role_profile_refs', instance['role_profile_refs'],
             [(reference['id'], 'execution_profiles') for refs in instance['role_profile_refs'].values()
              for reference in refs]),
            ('runtime', 'pending_events', runtime['pending_events'],
             [(identifier, 'events') for identifier in runtime['pending_events']]),
            ('runtime', 'trust_bindings', runtime['trust_bindings'],
             [(identifier, 'trust_environments') for identifier in runtime['trust_bindings']]),
        )
        for root, name, value, expected in cases:
            with self.subTest(family=name):
                self.assertTrue(expected)
                self.assertEqual(list(sim.engine.store.contract.family(root, name).references(value)), expected)
        self.assertEqual(sim.engine.store.load(), (head, instance, runtime))
        self.assertEqual(sim.model.calls, [])

    def test_profile_coordinates_are_rejected_before_publication(self):
        from do_math.execution_profiles import profile_ref
        instance, runtime = execution_state()
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        foreign = next(p for p in instance['execution_profiles'].values()
                       if p['role'] != runtime['executions']['EX-1']['role'])
        constraint_id = next(p['ai']['capacity_refs'][0] for p in instance['execution_profiles'].values()
                             if p.get('ai', {}).get('capacity_refs'))
        baseline = deepcopy((instance, runtime))
        for fault, reason in (
                ('actor', 'execution/profile actor or role mismatch'),
                ('selection', 'selected profile belongs to a different role'),
                ('host_pointer', 'adopted host capacity reference names another constraint kind'),
                ('capacity_reference', 'profile references unknown capacity constraint'),
                ('concurrency', 'concurrency constraint lacks its model or slot limit')):
            with self.subTest(fault=fault):
                changed, running = deepcopy(baseline)
                if fault == 'actor':
                    running['executions']['EX-1']['actor_kind'] = 'ai'
                elif fault == 'selection':
                    changed['role_profile_refs']['formal_check'] = [profile_ref(foreign)]
                elif fault == 'host_pointer':
                    changed['host_capacity_ref'] = constraint_id
                elif fault == 'capacity_reference':
                    del changed['capacity_constraints'][constraint_id]
                else:
                    del changed['capacity_constraints'][constraint_id]['accounting_unit']
                with self.assertRaises(ValueError) as rejected:
                    self.repository.save_with_state(head, changed, running)
                self.assertIs(type(rejected.exception), ValueError)
                self.assertEqual(str(rejected.exception), reason)
                self.assertEqual(self.repository.load(), (head, *baseline))

    def test_kind_semantics_reject_corruption_of_registered_candidates(self):
        instance, runtime = current_state()
        instance, token = knowledge_io.register_kind_definition(instance, {
            'family': 'relation', 'token': 'derived_observation',
            'meaning': 'An explicitly proposed mathematical relation',
            'constraints': {'mathematical_claim': True}},
            source_ref='input', actor_ref='user', clock=self.clock)
        definition = knowledge_io.lookup_definition(instance, 'relation', token)
        identifier = definition['id']
        self.assertEqual(definition['constraints'], {
            'mathematical_claim': True, 'requires_formal_results': True,
            'requires_assessments': True})
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        builtin_id = next(key for key, row in instance['kind_definitions'].items() if row.get('builtin'))
        for fault, reason in (
                ('builtin', 'builtin kind differs from installed definition'),
                ('duplicate', 'multiple current definitions of one kind'),
                ('checked', 'checked kind lacks its check reference'),
                ('active', 'active kind lacks approval reference'),
                ('formal', 'mathematical relation kind cannot waive formal evidence'),
                ('assessment', 'mathematical relation kind cannot waive formal evidence')):
            with self.subTest(fault=fault):
                changed = deepcopy(instance)
                row = changed['kind_definitions'][identifier]
                if fault == 'builtin':
                    changed['kind_definitions'][builtin_id]['meaning'] += ' corrupted'
                elif fault == 'duplicate':
                    other = deepcopy(row)
                    other['id'] = 'KD-duplicate'
                    changed['kind_definitions'][other['id']] = other
                elif fault == 'checked':
                    row['status'] = 'checked'
                elif fault == 'active':
                    # Deliberately malformed authority: this is a rejection input.
                    row.update(status='active', check_ref='untrusted-check')
                else:
                    row['constraints']['requires_formal_results' if fault == 'formal'
                                       else 'requires_assessments'] = False
                with self.assertRaises(ValueError) as rejected:
                    self.repository.save_with_state(head, changed, runtime)
                self.assertIs(type(rejected.exception), ValueError)
                self.assertEqual(str(rejected.exception), reason)
                self.assertEqual(self.repository.load(), (head, instance, runtime))

    def test_response_storage_requires_its_actual_obligation_and_execution(self):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.activities import assign_execution
        from do_math.execution_lifecycle import create_execution, transition_execution
        from do_math.execution_profiles import resolve_profile
        from do_math.observations import ObservationTracker, tracker_config
        from support.observation_inputs import acknowledge, observation_rule, observe, self_check_response, write_checkpoint

        instance, runtime = execution_state('research_work', config={**DEFAULT_CONFIG,
            'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5})
        execution = runtime['executions']['EX-1']
        transition_execution(execution, 'starting', at=self.clock.now())
        transition_execution(execution, 'running', at=self.clock.now())
        profile = resolve_profile(instance['execution_profiles'], execution['execution_profile_ref'])
        tracker = ObservationTracker(execution['id'], self.repository_path,
            tracker_config(profile, initial_self_check_rules=[observation_rule(
                required_evidence=['workspace:checkpoint.json'])]), time_port=self.clock)
        write_checkpoint(self.repository_path, counters={'attempts': 2})
        obligation = next(row for row in observe(tracker, {'type': 'tick'}) if row['kind'] == 'self_check_due')
        acknowledge(tracker, obligation['id'])
        response = tracker.record_self_check_response(self_check_response(obligation),
                                                      available_evidence_refs={'workspace:checkpoint.json'})
        self.assertEqual(response['kind'], 'self_check_received')
        runtime['self_check_obligations'] = tracker.stored_obligations()
        runtime['self_check_responses'] = {response['id']: response}
        other = create_execution(execution_id='EX-other', owner_activity_id='AT-1',
            actor_kind=profile['actor_kind'], input_manifest={},
            profile_ref=execution['execution_profile_ref'], created_at=self.clock.now())
        other['role'] = profile['role']
        assign_execution(runtime, 'AT-1', other)
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        self.assertEqual(runtime['self_check_responses'][response['id']], response)
        self.assertEqual(runtime['self_check_obligations'][obligation['id']]['response_ref'], response['id'])
        for field, value, reason in (
                ('obligation_id', 'SC-absent', 'self-check response references unknown obligation'),
                ('execution_id', other['id'], 'self-check response execution differs from obligation')):
            with self.subTest(field=field):
                changed = deepcopy(runtime)
                changed['self_check_responses'][response['id']][field] = value
                with self.assertRaises(ValueError) as rejected:
                    self.repository.save_with_state(head, instance, changed)
                self.assertIs(type(rejected.exception), ValueError)
                self.assertEqual(str(rejected.exception), reason)
                self.assertEqual(self.repository.load(), (head, instance, runtime))


if __name__ == '__main__':
    unittest.main()

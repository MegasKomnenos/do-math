"""Stop reasons reach a running model call only as a flag the owner sets (``call_engine``, ``parallel.ModelCalls``, ``scheduler``).

Each case prepares one AI action on the Sim's real engine and storage and
starts its call the way the scheduler does: ``_call_steps`` prepares it and
yields the runner arguments, the Job port fake launches a Job whose identity the
owner records through ``on_started``, and the calls port starts a calculation
that only reads its stop flag. The deterministic calls port runs a calculation
only while the owner hands it the turn, so the calculation reads its flag and
hands the turn back until the owner's next wait. One stop reason then changes
through its actual path: the owner's publication or its time comparison must
set the flag and record the stopping transition once, and the calculation reads
the flag in its next turn without asking the owner anything.
"""
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
import sys
import unittest
from copy import deepcopy

from do_math.execution_lifecycle import record_submission_intent
from do_math.knowledge import plan_impact, revision_roots
from do_math.windows_job import process_identity
from support.state_builders import charter_change, policy_change
from do_math.engine import ResearchEngine
from support.engine_lifecycle import ObservedCalls, applied, clear_work, code_of, queue_work, task
from support.fakes.calls import owner_turn
from support.sim import Sim, warm_template

setUpModule = warm_template
WAIT = 'fixture: a model call that only waits'


def observation(title, statement, **fields):
    return {'kind': 'observation', 'title': title, 'statement': statement, 'summary': 'A bounded computation.',
            'explanation': 'Exact finite computation.', 'lean_code': '', 'declaration_names': [], 'dependencies': [],
            **fields}


def imported(sim, candidate):
    """Import one knowledge candidate by public control; returns its ID."""
    before = set(sim.instance['knowledge'])
    applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
    kid, = set(sim.instance['knowledge']) - before
    return kid


def prepare_preparation(sim):
    clear_work(sim)
    sim.engine._enqueue('research_preparation', reason='Prepare the bounded stop fixture')
    sim.engine._save()
    return {}


def prepare_record(sim):
    """A preparation bound to an imported record that cites a source file (``root / 'basis.txt'``)."""
    source = sim.root / 'basis.txt'
    source.write_text('original', encoding='utf-8')
    applied(sim, 'source', config={'path': str(source)})
    name = sim.instance['sources'][0]['name']
    kid = imported(sim, observation('Computation', 'The result is one.', source_refs=[name]))
    clear_work(sim)
    # A preparation bound to the record reads it and, through it, the source.
    sim.engine._enqueue('research_preparation', kid, reason='Prepare follow-up work on the imported record')
    sim.engine._save()
    return {'kid': kid}


def prepare_goal_audit(sim):
    e = sim.engine
    clear_work(sim)
    e._ensure_goal_audit_requests(e._goal_basis_key(), 'EX-goal-request')
    e.runtime['queue'] = [a for a in e.runtime['queue'] if a['role'] == 'goal_audit'][:1]
    e._save()
    return {}


def prepare_work(sim):
    """Research work queued on a reviewed task whose input is an imported record."""
    kid = imported(sim, observation('Input fact', 'The result is one.'))
    clear_work(sim)
    task(sim.engine, 'TK-stop', inputs=[kid])
    queue_work(sim.engine, 'TK-stop')
    sim.engine._save()
    return {'kid': kid}


PREPARE = {'preparation': prepare_preparation, 'record': prepare_record,
           'goal_audit': prepare_goal_audit, 'work': prepare_work}


class CallPreparationBoundaryTests(unittest.TestCase):
    def test_review_preparation_publishes_an_actual_scope_admission_refusal(self):
        """T3 19.8 s: the owner-path review template and real abandoned attempts establish budget refusal."""
        from do_math.execution_lifecycle import transition_execution
        from do_math.review_cycle import minimum_scope_executions, resource_disposition
        from support.review_sim import opened_sim, cycle_of
        from support.provider_probes import ObservedCalls
        sim = opened_sim()
        engine = sim.engine
        cycle = cycle_of(sim)
        action = next(row for row in sim.runtime['queue'] if row['role'] == 'identity_review')
        self.assertEqual(action['stage'], 'scope')
        limit = cycle['activity_execution_limit']
        slots = max(cycle['review_policy']['minimum_initial_slots'], len(cycle['retained_reviewer_slots']))
        count = 0
        while minimum_scope_executions(slots, cycle['max_rounds'], count + 1) <= limit:
            execution = engine._register_execution(action,
                {'id': 'EX-abandoned-' + str(count), 'role': 'identity_review'})
            self.assertIsNotNone(execution)
            transition_execution(execution, 'ended', at=sim.clock.now(), outcome='cancelled')
            count += 1
        self.assertGreater(count, 0)
        engine._save()
        before = set(sim.runtime['executions'])
        with ObservedCalls(register=ResearchEngine._register_execution) as calls:
            self.assertIs(engine._prepare_call(action), True)
        self.assertEqual(len(calls.calls['register']), 1)
        self.assertEqual(set(sim.runtime['executions']), before)
        cycle = sim.runtime['review_cycles'][cycle['id']]
        record = resource_disposition(cycle)
        self.assertEqual(record['reason'], 'review_scope_unaffordable')
        self.assertEqual(len(record['executions_used']), count)
        self.assertEqual(record['limit'], limit)
        self.assertFalse(any(row.get('review_cycle_id') == cycle['id'] for row in sim.runtime['queue']))
        self.assertEqual(engine.store.load()[2], sim.runtime)

    def test_failed_and_rejected_results_preserve_a_public_pause_and_the_raw_result(self):
        """T3 10.2 s: one real input per result checks settlement and the public pause."""
        from do_math.canonical import canonical_json
        for error_kind in ('execution_failure', 'output_validation'):
            with self.subTest(error_kind=error_kind), self.unstarted_call(artifact_limit=4096) as (sim, prepared):
                applied(sim, 'pause', text='Keep the owner paused while this result returns')
                if error_kind == 'output_validation':
                    (prepared['workspace'] / 'large-report.md').write_bytes(b'x' * 8192)
                result = {'status': 'failed', 'output': None, 'usage': {}, 'error': 'bounded returned failure',
                          'error_kind': error_kind}
                sim.engine._receive_call(prepared, result)
                execution = sim.runtime['executions'][prepared['execution_id']]
                self.assertEqual(sim.runtime['status'], 'paused')
                self.assertEqual(execution['status'], 'ended')
                self.assertEqual(execution['outcome'], 'execution_incomplete')
                wait = sim.runtime['waiting_actions'][prepared['action']['id']]
                self.assertEqual(wait['kind'], 'execution_failure' if error_kind == 'execution_failure' else 'submission_failure')
                self.assertEqual(wait['execution_id'], execution['id'])
                self.assertEqual(wait['next_owner'], 'operational_review')
                head, _, saved = sim.engine.store.load()
                self.assertEqual(saved, sim.runtime)
                self.assertEqual(sim.engine.store.read(execution['result_ref'], head), canonical_json(result))
                self.assertFalse(any(row['state'] == 'held' and row['owner_id'] == execution['id']
                                     for row in sim.runtime['reservations'].values()))

    def test_failed_live_review_keeps_a_public_pause_and_requests_its_parent_stop(self):
        """T3 8.6 s: prepare the actual parent and independent observer before their public pause."""
        from support.engine_control import running_work
        sim = Sim.activated()
        with running_work(sim) as parent:
            with self.unstarted_call(sim=sim, role='operational_review', target=parent.execution_id,
                                     live=True) as (_, prepared):
                applied(sim, 'pause', text='Keep the live review and its parent paused')
                sim.engine._receive_call(prepared, {'status': 'failed', 'output': None, 'usage': {},
                                                   'error': 'independent live observer failed'})
                target = sim.runtime['executions'][parent.execution_id]
                self.assertEqual(target['stop_requested'], 'operating_review_unavailable')
                self.assertEqual(target['after_stop'], {'decision': 'wait',
                    'reason': 'Live operational review did not finish: independent live observer failed'})
                self.assertEqual(sim.runtime['status'], 'paused')
                self.assertEqual(sim.runtime['executions'][prepared['execution_id']]['outcome'], 'execution_incomplete')
                self.assertEqual(sim.engine.store.load()[2], sim.runtime)

    @contextmanager
    def unstarted_call(self, *, artifact_limit=None, sim=None, role='maintenance', target=None, **action_fields):
        """Real published input; the receiving boundary gets a local no-start receipt."""
        from do_math import launch
        from do_math.execution_lifecycle import transition_execution
        sim = Sim.activated() if sim is None else sim
        if artifact_limit is not None:
            applied(sim, 'configure', config={'max_artifact_bytes': artifact_limit})
        clear_work(sim)
        sim.engine._enqueue(role, target, reason='Receive one bounded call result', **action_fields)
        sim.engine._save()
        prepared = sim.engine._prepare_call(sim.runtime['queue'][0])
        self.assertIsInstance(prepared, dict)
        identifier = prepared['execution_id']
        # No process was launched in this layer-2 receive scenario.
        launch.mark_returned(sim.runtime['executions'][identifier]['launch_ticket'],
                             {'launch_not_created': True})
        sim.engine._save()  # Public controls reload; keep the actual no-start receipt durable.
        try:
            yield sim, prepared
        finally:
            execution = sim.runtime['executions'][identifier]
            if execution['status'] != 'ended':
                self.assertTrue(sim.engine._session_slots().release(identifier))
                transition_execution(execution, 'stopping', at=sim.clock.now())
                transition_execution(execution, 'ended', at=sim.clock.now(), outcome='execution_incomplete')
                sim.engine._remove_action(prepared['action'])
                sim.engine._settle_activity(identifier)
                sim.engine._live_execution_ids.discard(identifier)
                sim.engine._trackers.pop(identifier, None)
                sim.engine._transport.close(prepared['binding'], reason='Fixture no-start receipt')
                sim.engine._transport_bindings.pop(identifier, None)
                sim.engine._save()

    def test_capability_evidence_must_identify_the_attempted_profile(self):
        """T3 observation: 16.8 s; a real published input reaches the result boundary."""
        from do_math.execution_profiles import profile_ref
        with self.unstarted_call() as (sim, prepared):
            self.assertIs(sim.engine._call_stop_requested(prepared), False)
            reference = profile_ref(prepared['profile'])
            evidence = next(row for row in sim.instance['capability_evidence'].values()
                            if row['execution_profile_ref'] != reference)
            stored = sim.engine.store.load(sim.engine.head)
            with self.assertRaises(ValueError) as caught:
                sim.engine._receive_call(prepared, {'status': 'failed', 'output': None, 'usage': {},
                    'capability_evidence': deepcopy(evidence)})
            self.assertEqual(str(caught.exception), 'capability evidence differs from the attempted profile')
            self.assertEqual(sim.engine.store.load(sim.engine.head), stored)
            self.assertEqual(sim.instance['capability_evidence'], stored[1]['capability_evidence'])

    def test_incomplete_output_preservation_parks_the_submission_with_raw_result(self):
        """T3 observation: 20.8 s; preserve raw bytes and a failed submission in the real store."""
        import json
        with self.unstarted_call(artifact_limit=4096) as (sim, prepared):
            (prepared['workspace'] / 'large-report.md').write_bytes(b'x' * 8192)
            output = sim.model.responder.respond('maintenance', prepared['context'], prepared['workspace'])
            sim.engine._receive_call(prepared, {'status': 'completed', 'output': output, 'usage': {}})
            execution = sim.runtime['executions'][prepared['execution_id']]
            self.assertEqual((execution['status'], execution['error_kind'], execution['outputs_complete']),
                             ('ended', 'submission_failure', False))
            self.assertEqual(execution['error'], 'required execution artifacts could not be preserved')
            wait = sim.runtime['waiting_actions'][prepared['action']['id']]
            self.assertEqual((wait['kind'], wait['execution_id']), ('submission_failure', execution['id']))
            preserved = json.loads(sim.engine.store.read(execution['result_ref'], sim.engine.head))
            self.assertEqual((preserved['status'], preserved['output']), ('completed', output))

    def test_academic_requirement_edition_change_stops_its_prepared_call(self):
        """T3 observation: 207.2 s includes the existing solved academic template's construction."""
        from do_math import academic
        from support.academic_scenes import consumer_sim, MANUSCRIPT
        sim = consumer_sim()
        identifier = next(task['id'] for task in sim.runtime['tasks'].values()
                          if task.get('academic_requirement_id'))
        with self.unstarted_call(sim=sim, role='research_preparation', target=identifier) as (sim, prepared):
            previous = sim.runtime['executions'][prepared['execution_id']]['academic_requirements_sha256']
            requirement = deepcopy(MANUSCRIPT)
            requirement['criteria'].append('Explain the newly requested scope.')
            applied(sim, 'decision', config={'change': charter_change(sim.engine,
                academic_requirements=[requirement])})
            self.assertNotEqual(previous, academic.current_requirements(sim.instance)['sha256'])
            self.assertTrue(sim.engine._call_stop_requested(prepared))
            execution = sim.runtime['executions'][prepared['execution_id']]
            self.assertEqual(execution['status'], 'stopping')
            self.assertEqual(execution['academic_requirements_sha256'], previous)
            self.assertTrue(execution['currentness_changes'])

    def test_late_result_is_preserved_after_a_complete_goal_audit(self):
        """T3 observation: 49.1 s; reuse the complete audit group and apply a real scope decision."""
        from support.academic_scenes import consumer_sim, decide_requirements
        # This scene already has every configured goal auditor's verdict.
        # The user withdraws the remaining academic obligations, so completion
        # is real even though this unrelated local result has not been received.
        with self.unstarted_call(sim=consumer_sim()) as (sim, prepared):
            decide_requirements(sim.engine, [])
            sim.engine._ensure_academic_followup()
            sim.engine._save()
            self.assertEqual(sim.runtime['status'], 'completed')
            sim.engine._receive_call(prepared, {'status': 'failed', 'output': None,
                'usage': {}, 'error': 'The obsolete local attempt ended.'})
            execution = sim.runtime['executions'][prepared['execution_id']]
            self.assertEqual(execution['result_disposition'], {'kind': 'preserved_after_goal_completion'})
            self.assertNotIn(prepared['action']['id'], {row['id'] for row in sim.runtime['queue']})
            self.assertEqual(sim.runtime['status'], 'completed')

    def test_changed_installation_pauses_before_registering_an_attempt(self):
        """T3 4.1 s: a copied installation supplies an actual code change and repeated owner checks."""
        from support.storage_finish_installation import copy_installation
        sim = Sim.activated()
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='Check installation before preparation')
        sim.engine._save()
        installation = copy_installation(sim.root / 'changed-installation')
        engine = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports,
            codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id,
            installation_root=installation)
        self.assertTrue(engine._check_installation(force=True))
        path = installation / 'scripts/do_math/call_engine.py'
        path.write_bytes(path.read_bytes() + b'\n# Changed installed source.\n')
        before = deepcopy(engine.runtime['executions'])
        self.assertIs(engine._prepare_call(engine.runtime['queue'][0]), False)
        self.assertEqual(engine.runtime['executions'], before)
        self.assertEqual(engine.runtime['status'], 'paused')
        message = 'Installed code or role documents changed. Restart the executor to load one consistent version, then resume.'
        self.assertEqual(engine.runtime['questions'].count(message), 1)
        self.assertEqual(engine.store.load(engine.head)[2], engine.runtime)
        self.assertFalse(engine._check_installation(force=True))
        self.assertEqual(engine.runtime['questions'].count(message), 1)
        self.assertEqual(engine.store.load(engine.head)[2], engine.runtime)

    def test_preparation_failure_does_not_park_an_already_ended_execution(self):
        from support.governance_sim import returned
        sim = Sim.activated()
        clear_work(sim)
        execution = returned(sim.engine, {'id': 'AC-ended-input', 'role': 'maintenance'}, 'EX-ended-input')
        sim.engine._save()
        stored = sim.engine.store.load(sim.engine.head)
        error = ValueError('failure outside private input preparation')
        with self.assertRaises(ValueError) as caught:
            sim.engine._fail_input_preparation(sim.root / 'unused', execution['id'], error)
        self.assertIs(caught.exception, error)
        self.assertEqual(sim.engine.store.load(sim.engine.head), stored)
        self.assertEqual((sim.instance, sim.runtime), stored[1:])

    def test_revision_writer_prevents_a_new_reader_attempt(self):
        from do_math import revisions
        from do_math.execution_lifecycle import transition_execution
        from support.planning_contract_inputs import prepared_sim, only_task
        from support.planning_owner import enqueue
        sim = prepared_sim()
        identifier = only_task(sim)['id']
        writer = enqueue(sim.engine, 'research_preparation', revision_targets=revisions.capture_targets(
            sim.instance, sim.runtime, [identifier]))
        execution = sim.engine._register_execution(writer,
            {'id': 'EX-contract-writer', 'role': 'research_preparation', 'status': 'running'})
        reader = queue_work(sim.engine, identifier)
        before = set(sim.runtime['executions'])
        self.assertIs(sim.engine._prepare_call(reader), False)
        self.assertEqual(set(sim.runtime['executions']), before)
        self.assertEqual(reader['dispatch_wait']['kind'], 'contract_revision')
        self.assertTrue(reader['dispatch_wait']['blockers'])
        self.assertEqual(reader['dispatch_wait']['blockers'],
                         sim.engine._revision_dispatch_waits(reader))
        for status in ('stopping', 'ended'):
            transition_execution(execution, status, at=sim.clock.now(),
                **({'outcome': 'execution_incomplete'} if status == 'ended' else {}))


class StopFlagHarness(unittest.TestCase):
    case = 'preparation'

    def setUp(self):
        self.sim = Sim.activated()
        self.engine = self.sim.engine
        value = PREPARE[self.case](self.sim)
        self.kid = value.get('kid')
        self.source = self.sim.root / 'basis.txt'
        self.sim.jobs.programs.append((lambda argv: argv[2:3] == [WAIT], lambda argv, cwd, env: 0))

    @contextmanager
    def running(self):
        """One started call of the first queued action whose calculation only reads its flag."""
        sim, e = self.sim, self.engine
        e._calls = sim.ports.calls.new(on_returned=e._local_call_returned, on_observation_error=e._observation_failed)
        steps = e._call_steps(e.runtime['queue'][0])
        arguments = next(steps)
        # The Job stays unresumed, so it holds a live process the whole time, as a running call's does.
        job = sim.jobs.launch([sys.executable, '-c', WAIT], cwd=arguments['workspace'],
                              name=arguments['launch_ticket']['job_name'])
        reads, flags = [], []

        def calculate(should_stop, **_):
            flags.append(should_stop)
            while True:
                reads.append(should_stop())
                if reads[-1]:
                    return {'status': 'stopped', 'output': None, 'usage': {}, 'error': 'flag observed'}
                owner_turn()  # wait for the owner, as a call waiting on its process does
        try:
            arguments['on_started']({**process_identity(job), 'job_name': job.name})
            future = e._calls.start_call(steps, calculate, arguments, execution_id=arguments['execution_id'])
            self.assertFalse(future.stop.is_set(), 'nothing requires a stop at start')
            e._calls.wait(0)  # the calculation's first turn: it reads its flag and hands the turn back
            self.assertEqual(reads, [False])
            self.assertEqual(flags, [future.stop.is_set], 'the calculation reads only its stop flag')
            self.future, self.reads = future, reads
            yield e, arguments['execution_id'], future, reads
        finally:
            e._calls.close()
            steps.close()
            e._calls = None
            job.terminate()
            self.assertTrue(job.wait(10))
            job.close()

    def assertStopped(self, engine, execution_id, future, reads, reason=None):
        self.assertTrue(future.stop.is_set())
        self.assertIsNone(getattr(future, 'judge_error', None))
        execution = engine.runtime['executions'][execution_id]
        self.assertEqual(execution['status'], 'stopping')
        self.assertEqual([row['to'] for row in execution['transitions']].count('stopping'), 1)
        if reason is not None:
            self.assertEqual(execution['stop_reason'], reason)
        engine._calls.wait(0)  # the owner hands the call its next turn and nothing else
        self.assertTrue(reads and reads[-1], 'the calculation observes the flag without an owner round trip')
        self.assertTrue(future.done())

    def apply(self, action, **kwargs):
        """The owner pass applies a queued public control; its publication judges stops."""
        e = self.engine
        request = self.sim.control(action, text=kwargs.pop('text', 'stop flag fixture control'), **kwargs)
        e._apply_inbox(pump=False)
        e._upkeep()
        rejected = [row for row in e.runtime['history'] if row.get('kind') == 'rejected_user_control'
                    and row.get('request', {}).get('id') == request['request_id']]
        self.assertEqual(rejected, [])


class PreparationStopTests(StopFlagHarness):
    """One preparation (an operational role): lifecycle, authority, governance and clock reasons."""

    def test_pause_publishes_a_stop(self):
        with self.running() as (e, eid, future, reads):
            self.apply('pause', text='Stop the running preparation')
            self.assertStopped(e, eid, future, reads, 'user_pause')

    def test_close_publishes_a_stop(self):
        with self.running() as (e, eid, future, reads):
            self.apply('close', text='Close the research')
            self.assertStopped(e, eid, future, reads, 'closed')

    def test_revoked_grant_publishes_a_stop(self):
        with self.running() as (e, eid, future, reads):
            from do_math.governance import authorize
            action = deepcopy(e.runtime['executions'][eid]['action'])
            self.assertIs(authorize(e.instance, action, self.sim.clock.now(), runtime=e.runtime)['allowed'], True)
            e._action_lifecycle_gate(deepcopy(action))
            grant = e.runtime['executions'][eid]['grant_id']
            self.apply('decision', config={'change': {'kind': 'revoke', 'grant_id': grant}})
            self.assertIs(authorize(e.instance, action, self.sim.clock.now(), runtime=e.runtime)['allowed'], False)
            with self.assertRaisesRegex(ValueError, '^research authority: no current grant permits this action$'):
                e._action_lifecycle_gate(deepcopy(action))
            self.assertStopped(e, eid, future, reads)

    def test_governance_revision_publishes_a_stop(self):
        with self.running() as (e, eid, future, reads):
            self.apply('decision', config={'change': policy_change(e, 'A newly effective policy.')})
            # The policy decision marks its consumers; the judgment also records the changed revision.
            self.assertStopped(e, eid, future, reads, 'governance_changed')
            self.assertTrue(e.runtime['executions'][eid]['currentness_changes'])

    def test_goal_change_publishes_a_stop(self):
        with self.running() as (e, eid, future, reads):
            self.apply('decision', config={'change': charter_change(e, goal='Prove a revised target')})
            self.assertStopped(e, eid, future, reads)

    def test_accepted_submission_intent_publishes_a_stop(self):
        with self.running() as (e, eid, future, reads):
            execution = e.runtime['executions'][eid]
            # The transport acceptance path ends with this publication (engine._publish_control_request).
            record_submission_intent(execution, {'candidate_id': 'SC-fixture', 'manifest': [],
                'output_ref': 'runtime/artifacts/BA-x/output.json'}, {'id': 'CT-fixture', 'kind': 'submit_intent',
                'state': 'accepted', 'execution_id': eid, 'received_at': self.sim.clock.now()})
            self.assertFalse(future.stop.is_set(), 'an unpublished change is not a stop reason')
            e._save()
            self.assertStopped(e, eid, future, reads, 'submission_intent')

    def test_unpublished_owner_change_is_published_by_the_next_pass(self):
        with self.running() as (e, eid, future, reads):
            e.runtime['executions'][eid]['stop_requested'] = 'operational_retry'
            self.assertFalse(future.stop.is_set())
            e._settle_stops()
            self.assertStopped(e, eid, future, reads, 'operational_retry')

    def test_call_deadline_and_finish_notice_are_clock_comparisons(self):
        with self.running() as (e, eid, future, reads):
            notice, deadline = e._stop_deadlines[eid]
            finish = Path(e.instance['workspace']) / 'runs' / eid / 'workspace' / '.control' / 'finish-request.json'
            e._settle_stops()  # the owner's first time comparison sets its clock reference
            self.sim.advance(notice + .001 - self.sim.clock.monotonic())
            e._settle_stops()
            self.assertTrue(finish.exists())
            self.assertFalse(future.stop.is_set(), 'a finish notice does not revoke authority')
            self.sim.advance(deadline + .001 - self.sim.clock.monotonic())
            e._settle_stops()
            self.assertStopped(e, eid, future, reads, 'user_or_deadline_stop')

    def test_grant_expiry_is_a_clock_comparison(self):
        with self.running() as (e, eid, future, reads):
            from do_math.governance import authorize
            action = deepcopy(e.runtime['executions'][eid]['action'])
            self.assertIs(authorize(e.instance, action, self.sim.clock.now(), runtime=e.runtime)['allowed'], True)
            e._action_lifecycle_gate(deepcopy(action))
            grant = e.instance['grants'][e.runtime['executions'][eid]['grant_id']]
            later = datetime.fromisoformat(grant['expires_at']) + timedelta(seconds=1)
            e._settle_stops()
            self.assertFalse(future.stop.is_set())
            # Only the wall clock passes the expiry; the call deadline's monotonic clock stays.
            self.sim.clock.set_wall(later)
            self.assertIs(authorize(e.instance, action, self.sim.clock.now(), runtime=e.runtime)['allowed'], False)
            with self.assertRaisesRegex(ValueError, '^research authority: no current grant permits this action$'):
                e._action_lifecycle_gate(deepcopy(action))
            e._settle_stops()
            self.assertStopped(e, eid, future, reads, 'authority_changed')

    def test_conversation_lease_expiry_stops_under_the_pause_policy(self):
        e = self.engine
        self.sim.control('conversation', text='attach the conversation', config={
            'operation': 'attach', 'id': 'CV-fixture', 'generation': 1, 'lease_seconds': 60, 'disconnect_policy': 'pause'})
        e._apply_inbox(pump=False)
        e._upkeep()
        self.assertEqual(e.runtime['conversations']['CV-fixture']['status'], 'connected')
        with self.running() as (e, eid, future, reads):
            e._settle_stops()
            self.assertFalse(future.stop.is_set())
            self.sim.advance(61)
            e._settle_stops()
            self.assertStopped(e, eid, future, reads, 'conversation_lost')

    def test_failed_observation_is_the_recorded_stop_reason(self):
        with self.running() as (e, eid, future, reads):
            e._observation_failed(eid, ValueError('provider row differs'))
            self.assertStopped(e, eid, future, reads, 'observation_failed: ValueError: provider row differs')


class RecordStopTests(StopFlagHarness):
    """An execution bound to a record: knowledge and source changes reach it through publication."""

    case = 'record'

    def test_knowledge_revision_publishes_a_decision_basis_stop(self):
        with self.running() as (e, eid, future, reads):
            impact = plan_impact(e.instance, e.runtime, revision_roots(e.instance, self.kid), [])
            self.apply('knowledge', config={'operation': 'revise', 'id': self.kid,
                'changes': {'statement': 'The result is two.'}, 'declared_impact': impact['computed_impact'],
                'reason': 'Correct the computation.'})
            self.assertStopped(e, eid, future, reads)
            self.assertTrue(e.runtime['executions'][eid]['currentness_changes'])

    def test_source_change_publishes_a_currentness_stop(self):
        with self.running() as (e, eid, future, reads):
            self.source.write_text('corrected', encoding='utf-8')
            self.apply('source', config={'path': str(self.source)})
            self.assertStopped(e, eid, future, reads)
            self.assertTrue(e.runtime['executions'][eid]['currentness_changes'])


class GoalAuditStopTests(StopFlagHarness):
    """A goal audit judges one complete basis; any published basis change stops it."""

    case = 'goal_audit'

    def test_administrative_history_does_not_stop_but_content_change_does(self):
        from support.knowledge_builders import knowledge_candidate
        kid = imported(self.sim, knowledge_candidate())
        prepare_goal_audit(self.sim)
        with self.running() as (e, eid, future, reads):
            original = e.runtime['executions'][eid]['action']['basis']
            cycle_id = e._start_identity_review(kid)
            e._save()
            self.assertEqual(e.store.load()[1]['knowledge'][kid]['review_cycle_id'], cycle_id)
            e._calls.judge()
            self.assertEqual(e._goal_basis_key(), original)
            self.assertFalse(future.stop.is_set())
            self.assertEqual(e.runtime['executions'][eid]['status'], 'running')
            self.assertFalse(e.runtime['executions'][eid].get('currentness_changes'))
            e.instance['knowledge'][kid]['title'] = 'Corrected evidence'
            e._save()
            self.assertStopped(e, eid, future, reads)
            changes = e.runtime['executions'][eid]['currentness_changes']
            self.assertTrue(any(row.get('field') == 'goal_audit_basis' for row in changes), changes)

    def test_goal_basis_change_publishes_a_stop_and_is_judged_once_per_head(self):
        with self.running() as (e, eid, future, reads):
            with ObservedCalls(basis=code_of(ResearchEngine._goal_basis_key)) as computed:
                e._calls.judge()
                e._calls.judge()
            self.assertFalse(future.stop.is_set())
            self.assertLessEqual(len(computed.calls['basis']), 1, 'one goal basis per published head')
            self.assertEqual(e._goal_basis_memo[0], e.head)
            self.apply('knowledge', config={'operation': 'import', 'candidate': observation(
                'New evidence', 'A new fact.', summary='A new fact.', explanation='Imported during the audit.')})
            self.assertStopped(e, eid, future, reads)
            changes = e.runtime['executions'][eid]['currentness_changes']
            self.assertTrue(any(row.get('field') == 'goal_audit_basis' for row in changes), changes)


class WorkStopTests(StopFlagHarness):
    """Research work on a reviewed task: use conditions and the task contract."""

    case = 'work'

    def test_unusable_input_publishes_a_use_condition_stop(self):
        with self.running() as (e, eid, future, reads):
            impact = plan_impact(e.instance, e.runtime, revision_roots(e.instance, self.kid), [])
            self.apply('knowledge', config={'operation': 'invalidate', 'id': self.kid,
                'declared_impact': impact['computed_impact'], 'reason': 'The input was found wrong.'})
            self.assertStopped(e, eid, future, reads)
            changes = e.runtime['executions'][eid]['currentness_changes']
            self.assertTrue(any(row.get('field') == 'required_use_conditions' for row in changes), changes)

    def test_changed_task_contract_stops_once_the_owner_publishes_it(self):
        with self.running() as (e, eid, future, reads):
            e.runtime['tasks']['TK-stop']['question'] = 'Does P hold for every case?'
            self.assertFalse(future.stop.is_set(), 'an unpublished change is not a stop reason')
            e._settle_stops()
            self.assertStopped(e, eid, future, reads, 'authority_changed')


if __name__ == '__main__':
    unittest.main()

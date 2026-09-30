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

from do_math.execution_lifecycle import record_submission_intent
from do_math.knowledge import plan_impact, revision_roots
from do_math.windows_job import process_identity
from research_fixtures import charter_change, policy_change
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
            grant = e.runtime['executions'][eid]['grant_id']
            self.apply('decision', config={'change': {'kind': 'revoke', 'grant_id': grant}})
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
            grant = e.instance['grants'][e.runtime['executions'][eid]['grant_id']]
            later = datetime.fromisoformat(grant['expires_at']) + timedelta(seconds=1)
            e._settle_stops()
            self.assertFalse(future.stop.is_set())
            # Only the wall clock passes the expiry; the call deadline's monotonic clock stays.
            self.sim.clock.set_wall(later)
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

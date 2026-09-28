"""Stop reasons reach a running calculation only as a flag set by the owner.

Each case starts one real AI execution (real Git state, real local Job) and
changes one stop reason through its actual path. The owner's publication or
its time comparison must set the calculation's flag and record the stopping
transition once. The calculation itself never pumps the owner.
"""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import control
from do_math.execution_lifecycle import record_submission_intent
from do_math.parallel import ModelCalls
from do_math.engine import ResearchEngine
from research_fixtures import charter_change, policy_change, restore_template
from state_fixtures import active_instance
from runner_fixtures import ScriptedRunner
from research_fixtures import FixtureAdapter, clock_ports


CONFIG = {'operator_enabled': False, 'scholarly_enabled': False, 'lean_command': ['test-lean'],
          'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}


def apply(engine, repository, action, **kwargs):
    """The owner pass applies a queued public control; returns its rejection records."""
    request = control(repository, engine.instance['id'], action, **kwargs)
    engine._apply_inbox(pump=False)
    engine._upkeep()
    return [row for row in engine.runtime['history'] if row.get('kind') == 'rejected_user_control'
            and row.get('request', {}).get('id') == request['request_id']]


def applied(engine, repository, action, **kwargs):
    rejected = apply(engine, repository, action, **kwargs)
    if rejected:
        raise AssertionError('The fixture control was rejected: ' + repr(rejected))


def prepare_preparation(engine, root):
    engine._enqueue('research_preparation', reason='Prepare the bounded stop fixture')
    engine._save()
    return {}


def prepare_record(engine, root):
    """A preparation bound to an imported record that cites a source file (``root / 'basis.txt'``)."""
    repository = root / 'repository'
    source = root / 'basis.txt'
    source.write_text('original', encoding='utf-8')
    applied(engine, repository, 'source', config={'path': str(source)})
    name = engine.instance['sources'][0]['name']
    applied(engine, repository, 'knowledge', config={'operation': 'import', 'candidate': {
        'kind': 'observation', 'title': 'Computation', 'statement': 'The result is one.',
        'summary': 'A bounded computation.', 'explanation': 'Exact finite computation.',
        'lean_code': '', 'declaration_names': [], 'dependencies': [], 'source_refs': [name]}})
    kid = next(iter(engine.instance['knowledge']))
    engine.runtime['queue'] = []
    # A preparation bound to the record reads it and, through it, the source.
    engine._enqueue('research_preparation', kid, reason='Prepare follow-up work on the imported record')
    engine._save()
    return {'kid': kid}


def prepare_goal_audit(engine, root):
    engine.runtime['queue'] = []
    engine._ensure_goal_audit_requests(engine._goal_basis_key(), 'EX-goal-request')
    engine.runtime['queue'] = [a for a in engine.runtime['queue'] if a['role'] == 'goal_audit'][:1]
    engine._save()
    return {}


def prepare_work(engine, root):
    """Research work queued on a reviewed task whose input is an imported record."""
    from engine_fixtures import reviewed_task
    from do_math.execution_lifecycle import transition_execution
    from research_fixtures import prepared_rule_conditions
    applied(engine, root / 'repository', 'knowledge', config={'operation': 'import', 'candidate': {
        'kind': 'observation', 'title': 'Input fact', 'statement': 'The result is one.',
        'summary': 'A bounded computation.', 'explanation': 'Exact finite computation.',
        'lean_code': '', 'declaration_names': [], 'dependencies': []}})
    kid = next(iter(engine.instance['knowledge']))
    grant = next(gid for gid, grant in engine.instance['grants'].items() if 'research_work' in grant.get('roles', []))
    for identifier, role in (('EX-preparation', 'research_preparation'), ('EX-review-TK-stop', 'task_contract_review')):
        # The returned producer and reviewer the sealed task records name.
        execution = engine._register_execution({'id': 'AC-' + identifier, 'role': role},
                                               {'id': identifier, 'role': role, 'status': 'running'})
        at = engine._lifecycle_now().isoformat()
        transition_execution(execution, 'stopping', at=at)
        transition_execution(execution, 'ended', at=at, outcome='execution_incomplete')
    reviewed_task(engine, 'TK-stop', inputs=[kid], authority_refs=[grant],
                  initial_observation_rules=prepared_rule_conditions(['TK-stop'])[0]['observation_rules'])
    engine.runtime['queue'] = []
    engine._enqueue('research_work', 'TK-stop', reason='Work on the reviewed task',
                    model_assessment={'difficulty': 'low', 'importance': 'low', 'reason': 'Bounded fixture'})
    engine._save()
    return {'kid': kid}


PREPARE = {'preparation': prepare_preparation, 'record': prepare_record,
           'goal_audit': prepare_goal_audit, 'work': prepare_work}


def waiting_action(root, shared, *, case):
    """``restore_template`` build: the active state with one AI action waiting to start.

    ``case`` names the action (``PREPARE``). Returns the instance ID and the
    record IDs the case's tests read. A running call cannot be copied (an executor
    recovers it), so each test starts the call itself.
    """
    identifier = active_instance(root, shared, config=CONFIG)
    (root / 'work-0' / 'runs').mkdir(exist_ok=True)
    with patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
        engine = ResearchEngine(root / 'repository', identifier, runner=ScriptedRunner())
        return {'instance_id': identifier, **PREPARE[case](engine, root)}


class StopFlagHarness(unittest.TestCase):
    case = 'preparation'

    def setUp(self):
        self.enterContext(patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()))
        self.root, value = restore_template(waiting_action, case=self.case)
        self.repo = self.root / 'repository'
        self.engine = ResearchEngine(self.repo, value['instance_id'], runner=ScriptedRunner())
        self.kid = value.get('kid')
        self.source = self.root / 'basis.txt'

    @contextmanager
    def running(self):
        """One started operational-role execution whose calculation only reads its flag."""
        from do_math.windows_job import WindowsJob, process_identity
        e = self.engine
        e._calls = ModelCalls(on_returned=e._local_call_returned, on_observation_error=e._observation_failed)
        steps = e._call_steps(e.runtime['queue'][0])
        arguments = next(steps)
        job = WindowsJob([sys.executable, '-c', 'import time; time.sleep(600)'],
                         cwd=arguments['workspace'], name=arguments['launch_ticket']['job_name'])
        release, reads = threading.Event(), []
        def calculate(should_stop, **_):
            while not release.is_set():
                reads.append(should_stop())
                if reads[-1]:
                    return {'status': 'stopped', 'output': None, 'usage': {}, 'error': 'flag observed'}
                time.sleep(.01)
            return {'status': 'stopped', 'output': None, 'usage': {}, 'error': 'released'}
        try:
            arguments['on_started']({**process_identity(job), 'job_name': job.name})
            job.resume()
            future = e._calls.start_call(steps, calculate, arguments, execution_id=arguments['execution_id'])
            self.assertFalse(future.stop.is_set(), 'nothing requires a stop at start')
            yield e, arguments['execution_id'], future, reads
        finally:
            release.set()
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
        if reason is not None:
            self.assertEqual(execution['stop_reason'], reason)
        until = time.monotonic() + 5
        while (not reads or not reads[-1]) and time.monotonic() < until:
            time.sleep(.01)
        self.assertTrue(reads and reads[-1], 'the calculation observes the flag without an owner round trip')

    def apply(self, action, **kwargs):
        """The owner pass applies a queued public control; its publication judges stops."""
        self.assertEqual(apply(self.engine, self.repo, action, **kwargs), [])


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
                'state': 'accepted', 'execution_id': eid, 'received_at': datetime.now(timezone.utc).isoformat()})
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
            workspace = Path(e.instance['workspace']) / 'runs' / eid / 'workspace'
            @contextmanager
            def at(instant):
                # Only the executor's deadline clock moves; the clock guard keeps real
                # time because lifecycle_monotonic stays bound to the engine's first clock.
                saved, e.ports = e.ports, clock_ports(monotonic=lambda: instant)
                try:
                    yield
                finally:
                    e.ports = saved
            e._settle_stops()
            with at(notice + .001):
                e._settle_stops()
            self.assertTrue((workspace / '.control' / 'finish-request.json').exists())
            self.assertFalse(future.stop.is_set(), 'a finish notice does not revoke authority')
            with at(deadline + .001):
                e._settle_stops()
            self.assertStopped(e, eid, future, reads, 'user_or_deadline_stop')

    def test_grant_expiry_is_a_clock_comparison(self):
        with self.running() as (e, eid, future, reads):
            grant = e.instance['grants'][e.runtime['executions'][eid]['grant_id']]
            later = datetime.fromisoformat(grant['expires_at']) + timedelta(seconds=1)
            e._settle_stops()
            self.assertFalse(future.stop.is_set())
            class Clock(datetime):
                @classmethod
                def now(cls, tz=None): return later
            e.lifecycle_clock = lambda: later.isoformat()
            with patch('do_math.governance.datetime', Clock):
                e._settle_stops()
            self.assertStopped(e, eid, future, reads, 'authority_changed')

    def test_conversation_lease_expiry_stops_under_the_pause_policy(self):
        e = self.engine
        offset = [timedelta(0)]
        e.lifecycle_clock = lambda: (datetime.now(timezone.utc) + offset[0]).isoformat()
        control(self.repo, e.instance['id'], 'conversation', config={'operation': 'attach', 'id': 'CV-fixture',
            'generation': 1, 'lease_seconds': 60, 'disconnect_policy': 'pause'})
        e._apply_inbox(pump=False)
        e._upkeep()
        with self.running() as (e, eid, future, reads):
            e._settle_stops()
            self.assertFalse(future.stop.is_set())
            offset[0] = timedelta(seconds=61)
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
            from do_math.knowledge import plan_impact, revision_roots
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
            calls = []
            original = type(e)._goal_basis_key
            def counted(engine):
                calls.append(engine.head)
                return original(engine)
            with patch.object(type(e), '_goal_basis_key', counted):
                e._calls.judge(); e._calls.judge()
                self.assertFalse(future.stop.is_set())
                self.assertLessEqual(len(calls), 1, 'one goal basis per published head')
                self.apply('knowledge', config={'operation': 'import', 'candidate': {
                    'kind': 'observation', 'title': 'New evidence', 'statement': 'A new fact.',
                    'summary': 'A new fact.', 'explanation': 'Imported during the audit.',
                    'lean_code': '', 'declaration_names': [], 'dependencies': []}})
            self.assertStopped(e, eid, future, reads)
            changes = e.runtime['executions'][eid]['currentness_changes']
            self.assertTrue(any(row.get('field') == 'goal_audit_basis' for row in changes), changes)



class WorkStopTests(StopFlagHarness):
    """Research work on a reviewed task: use conditions and the task contract."""

    case = 'work'

    def test_unusable_input_publishes_a_use_condition_stop(self):
        with self.running() as (e, eid, future, reads):
            from do_math.knowledge import plan_impact, revision_roots
            impact = plan_impact(e.instance, e.runtime, revision_roots(e.instance, self.kid), [])
            self.apply('knowledge', config={'operation': 'invalidate', 'id': self.kid,
                'declared_impact': impact['computed_impact'], 'reason': 'The input was found wrong.'})
            self.assertStopped(e, eid, future, reads)
            changes = e.runtime['executions'][eid]['currentness_changes']
            self.assertTrue(any(row.get('field') == 'required_use_conditions' for row in changes), changes)

    def test_changed_task_contract_stops_once_the_owner_publishes_it(self):
        with self.running() as (e, eid, future, reads):
            task = e.runtime['tasks']['TK-stop']
            task['question'] = 'Does P hold for every case?'
            self.assertFalse(future.stop.is_set(), 'an unpublished change is not a stop reason')
            e._settle_stops()
            self.assertStopped(e, eid, future, reads, 'authority_changed')


if __name__ == '__main__':
    unittest.main()

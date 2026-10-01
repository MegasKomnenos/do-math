"""The owner applies a runner's observation batch (``core_engine._observe_running``, layer 2) on a Sim's real engine.

Each test publishes running executions through the product's lifecycle
functions (``support.provider_live``) on a restored active Sim, and hands the
engine the batch a ``ModelRunner`` would deliver. The tracker, the engine's
publication, its rollback and the worker's control surfaces are the product's;
calls are counted with a profile hook (``support.provider_probes``), so no
engine method or store is replaced. A failed publication is a real
compare-and-swap failure: another writer holds the state ref's lock file, as a
concurrent Git ref transaction would.
"""
from copy import deepcopy
import copy
import json
from pathlib import Path
import unittest

from do_math.control_transport import ControlTransport
from do_math.git_store import GitStateStoreConflict
from do_math.observations import ObservationTracker
from support.observation_inputs import acknowledge, observation_rule, observe, write_checkpoint
from support.provider_live import batch, running_execution
from support.provider_probes import ObservedCalls
from support.sim import Sim, warm_template

setUpModule = warm_template
WINDOWS = {'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}
CAS = 'state ref changed before the publish compare-and-swap'


def research_tracker(sim, execution_id, workspace):
    return ObservationTracker(execution_id, workspace, {'observation_rules': [observation_rule()], **WINDOWS},
                              time_port=sim.clock)


def facts_of(runtime, execution_id):
    return [fact for fact in runtime.get('observation_facts', {}).values() if fact['execution_id'] == execution_id]


class RefHeldByAnotherWriter:
    """While open, another writer holds the instance ref's lock, so the next publication fails its compare-and-swap."""

    def __init__(self, sim):
        self.path = sim.repository / '.git' / 'refs' / 'heads' / 'do-math' / (sim.instance_id + '.lock')

    def __enter__(self):
        self.path.write_bytes(b'')
        return self

    def __exit__(self, *exception):
        self.path.unlink()
        return False


class ModelCallObservationTests(unittest.TestCase):
    def test_a_model_calls_stream_reaches_the_owner_as_its_observation_facts(self):
        """The wiring the other tests enter directly: runner, calls port and owner apply a real call's stream.

        About 2 s, at the Sim budget: a template restore and one owner pass that runs a model call.
        """
        sim = Sim.activated()
        before = set(sim.runtime['executions'])
        sim.step()  # the queued research preparation runs through the Job fake, the model double and the runner
        (execution_id,) = [eid for eid in sim.runtime['executions'] if eid not in before]
        stream = Path(sim.instance['workspace']) / 'runs' / execution_id / 'evidence' / 'stdout.jsonl'
        rows = stream.read_bytes().splitlines()
        facts = sorted(facts_of(sim.runtime, execution_id), key=lambda fact: fact['source']['start_offset'])
        self.assertEqual([json.loads(fact['event_json']) for fact in facts], [json.loads(row) for row in rows])
        applied = sim.runtime['executions'][execution_id]['observation_stream']
        self.assertEqual((applied['end_offset'], applied['local_termination_confirmed']), (stream.stat().st_size, True))


class ReminderApplicationTests(unittest.TestCase):
    def test_engine_answers_reminder_without_opening_model_review(self):
        sim = Sim.activated()
        workspace = running_execution(sim, 'EX-reminder', 'research_work')
        # A checkpointing role with no checkpoint after one observation interval: the reminder alone is due.
        tracker = ObservationTracker('EX-reminder', workspace, {'observation_mode': 'event_driven',
            'research_self_checks': False, 'observation_interval_seconds': 300, 'checkpoint_expected': True},
            time_port=sim.clock)
        sim.advance(300)
        queue = deepcopy(sim.runtime['queue'])
        head = sim.engine.head
        with ObservedCalls(enqueue=type(sim.engine)._enqueue) as calls:
            sim.engine._observe_running('EX-reminder', tracker, batch(sim, [], workspace / 'stdout.jsonl'))
        self.assertTrue((workspace / '.control/observation-feedback.json').exists())
        self.assertEqual(calls.count('enqueue'), 0)
        self.assertEqual(sim.runtime['queue'], queue)
        self.assertTrue(tracker.checkpoint_reminded)
        self.assertNotEqual(sim.engine.head, head)  # the applied tick is published


class OwnerCallClassificationTests(unittest.TestCase):
    def test_owner_distinguishes_preview_and_boundary_from_self_check(self):
        sim = Sim.activated()
        for provider in ('codex', 'claude'):
            for kind in ('submission_preview', 'safety_boundary', 'self_check'):
                with self.subTest(provider=provider, kind=kind):
                    execution_id = 'EX-' + provider + '-' + kind.replace('_', '-')
                    workspace = running_execution(sim, execution_id, 'research_work')
                    tracker = research_tracker(sim, execution_id, workspace)
                    write_checkpoint(workspace, counters={'attempts': 2})
                    obligation = next(row for row in observe(tracker, {'type': 'tick'})
                                      if row['kind'] == 'self_check_due')
                    # The worker has received and polled the request, so a research action now misses it.
                    acknowledge(tracker, obligation['id'])
                    tool = 'control_self_check' if kind == 'self_check' else 'control_submit'
                    arguments = ({'self_check_id': obligation['id']} if kind == 'self_check' else
                        {'request_id': 'NEXT', 'kind': kind, 'payload': {'inflight_calls': False, 'call_ids': []}})
                    event = ({'type': 'item.started', 'item': {'id': 'CALL', 'type': 'mcp_tool_call',
                        'server': 'execution_control', 'tool': tool, 'arguments': arguments}}
                        if provider == 'codex' else {'type': 'assistant', 'message': {'content': [
                            {'type': 'tool_use', 'id': 'CALL', 'name': 'mcp__execution_control__' + tool,
                             'input': arguments}]}})
                    sim.engine._observe_running(execution_id, tracker, batch(sim, [event], workspace / 'stdout.jsonl',
                        start=tracker.observation_source['end_offset']))
                    missed = 'research_action_before_response' if kind == 'submission_preview' else None
                    self.assertEqual(tracker.obligations[obligation['id']].get('missed_reason'), missed)
                    self.assertEqual('CALL' in tracker.self_check_call_ids, kind == 'self_check')
                    self.assertEqual('CALL' in tracker.boundary_call_ids, kind == 'safety_boundary')
                    # The owner published what the tracker judged.
                    self.assertEqual(sim.runtime['self_check_obligations'][obligation['id']].get('missed_reason'), missed)


class CapturedCheckpointTests(unittest.TestCase):
    def test_checkpoint_capture_preserves_its_evidence_before_live_file_changes(self):
        sim = Sim.activated()
        sim.control('configure', text='Small artifacts', config={'max_artifact_bytes': 4096})
        sim.engine.process_controls()
        self.assertEqual(sim.instance['config']['max_artifact_bytes'], 4096)
        workspace = running_execution(sim, 'EX-capture', 'research_work')
        proof = b'exact submitted source'
        (workspace / 'proof.lean').write_bytes(proof)
        (workspace / 'checkpoint.json').write_text(json.dumps({'current_claim': 'candidate',
            'evidence_paths': ['proof.lean'], 'attempts': [], 'remaining_work': ['check'],
            'next_step': 'verify', 'progress_state': 'working'}), encoding='utf-8')
        tracker = ObservationTracker('EX-capture', workspace, {'observation_mode': 'deadline_only'}, time_port=sim.clock)
        sim.engine._observe_running('EX-capture', tracker, batch(sim, [], workspace / 'stdout.jsonl'))
        record = sim.runtime['checkpoints']['EX-capture']
        self.assertEqual(len(record.get('evidence_files', [])), 1)
        (workspace / 'proof.lean').write_bytes(b'changed later')
        self.assertEqual(sim.engine.store.read(record['evidence_files'][0]['artifact_ref'], sim.engine.head), proof)


class DeadlineOnlyApplicationTests(unittest.TestCase):
    def test_rejected_input_of_a_deadline_only_execution_is_recorded_without_a_review(self):
        # A deadline_only execution opens no recursive review, so its rejected input carries no followup.
        sim = Sim.activated()
        workspace = running_execution(sim, 'EX-maintenance', 'maintenance')
        tracker = ObservationTracker('EX-maintenance', workspace, {'observation_mode': 'deadline_only'},
                                     time_port=sim.clock)
        sim.engine._observe_running('EX-maintenance', tracker, batch(
            sim, [{'type': 'turn.started', 'execution_id': 'EX-other'}], workspace / 'stdout.jsonl'))
        rejected = [json.loads(fact['event_json']) for fact in sim.runtime['observation_facts'].values()
                    if json.loads(fact['event_json']).get('kind') == 'observation_input_rejected']
        self.assertEqual(len(rejected), 1)
        self.assertNotIn('followup', rejected[0])
        self.assertFalse(any(a['role'] == 'operational_review' for a in sim.runtime['queue']))

    def test_terminated_stream_replay_preserves_events_without_live_reviews(self):
        sim = Sim.activated()
        workspace = running_execution(sim, 'EX-replay', 'research_work')
        tracker = ObservationTracker('EX-replay', workspace, {'observation_mode': 'periodic',
            'observation_interval_seconds': 300}, time_port=sim.clock)
        started = sim.clock.monotonic()
        sim.advance(900)
        events = [{'type': 'turn.started'}, {'type': 'item.started',
                  'item': {'id': 'old-command', 'type': 'command_execution'}}]
        # Rows received past the periodic interval, from a stream whose Job has ended.
        replay = batch(sim, events, workspace / 'stdout.jsonl', terminated=True, received_monotonic=started + 301.25)
        before = set(sim.runtime.get('observation_facts', {}))
        with ObservedCalls(save=type(sim.engine)._save) as calls:
            sim.engine._observe_running('EX-replay', tracker, replay)
        self.assertFalse(any(a['role'] == 'operational_review' for a in sim.runtime['queue']))
        # Every fact the replay wrote, of any execution: exactly two, both of this execution.
        added = {key: fact for key, fact in sim.runtime['observation_facts'].items() if key not in before}
        self.assertEqual(sorted(fact['execution_id'] for fact in added.values()), ['EX-replay', 'EX-replay'])
        self.assertEqual(calls.count('save'), 1)
        self.assertFalse(tracker.obligations)


class ObservationTransactionTests(unittest.TestCase):
    def test_failed_observation_publication_does_not_advance_the_tracker(self):
        sim = Sim.activated()
        workspace = running_execution(sim, 'EX-one', 'research_work', bind=True)
        tracker = research_tracker(sim, 'EX-one', workspace)
        before = deepcopy((sim.engine.instance, sim.engine.runtime))
        write_checkpoint(workspace, counters={'attempts': 2})
        with ObservedCalls(request=ControlTransport.request_self_check) as calls:
            with RefHeldByAnotherWriter(sim), self.assertRaisesRegex(GitStateStoreConflict, CAS):
                sim.engine._observe_running('EX-one', tracker, batch(sim, [], workspace / 'stdout.jsonl'))
            self.assertEqual(tracker.counters, {})
            self.assertEqual((sim.engine.instance, sim.engine.runtime), before)
            self.assertEqual(calls.count('request'), 0)
            sim.engine._observe_running('EX-one', tracker, batch(sim, [], workspace / 'stdout.jsonl'))
            self.assertEqual(tracker.counters, {'attempts': 2})
            obligations = sim.runtime['self_check_obligations']
            self.assertTrue(obligations)
            self.assertEqual(calls.count('request'), 1)
        (obligation_id,) = [key for key, value in obligations.items() if value['execution_id'] == 'EX-one']
        self.assertTrue((workspace / '.control/self-checks' / (obligation_id + '.json')).is_file())

    def test_failed_observation_rolls_back_to_the_published_state_without_copying_it_first(self):
        sim = Sim.activated()
        workspace = running_execution(sim, 'EX-one', 'research_work')
        tracker = research_tracker(sim, 'EX-one', workspace)
        before = deepcopy(sim.engine.runtime)
        # The owner's own copies (``do_math.core_engine``): does any of them copy the state it would roll back to?
        copies = ObservedCalls(copy=copy.deepcopy, capture={'copy': lambda arguments: (
            arguments['x'] is before or arguments['x'] == before)})
        with copies, RefHeldByAnotherWriter(sim), self.assertRaisesRegex(GitStateStoreConflict, CAS):
            sim.engine._observe_running('EX-one', tracker, batch(sim, [], workspace / 'stdout.jsonl'))
        self.assertGreater(copies.count('copy', caller='do_math.core_engine'), 0)  # the tracker copy is observed
        self.assertFalse(any(copies.captured('copy', caller='do_math.core_engine')))
        self.assertEqual(sim.engine.runtime, before)
        self.assertEqual(tracker.counters, {})

    def test_idle_observation_tick_neither_copies_nor_publishes_the_runtime(self):
        sim = Sim.activated()
        workspace = running_execution(sim, 'EX-one', 'research_work')
        tracker = research_tracker(sim, 'EX-one', workspace)
        engine = sim.engine
        # The first tick reports the unmeasured rule signal; the next one has nothing new.
        with ObservedCalls(save=type(engine)._save) as first:
            engine._observe_running('EX-one', tracker, batch(sim, [], workspace / 'stdout.jsonl'))
        self.assertEqual(first.count('save'), 1)
        before, head = deepcopy(engine.runtime), engine.head
        runtime = engine.runtime
        with ObservedCalls(save=type(engine)._save, copy=copy.deepcopy,
                           capture={'copy': lambda arguments: arguments['x'] is runtime}) as second:
            engine._observe_running('EX-one', tracker, batch(sim, [], workspace / 'stdout.jsonl'))
        self.assertEqual(second.count('save'), 0)
        self.assertFalse(any(second.captured('copy', caller='do_math.core_engine')))
        self.assertEqual(engine.runtime, before)
        self.assertEqual(engine.head, head)


RULE = {"id": "checkpoints", "operator": "checkpoint_count_gte",
        "subject": {"kind": "checkpoint", "id": "$execution"},
        "basis": {"source": "checkpoint", "unit": "count"},
        "threshold": 2, "required_evidence": ["contract"]}


def task_rule_responder():
    """The default responder, whose preparation gives each candidate task the execution-bound ``RULE``."""
    from support.default_responder import DefaultResponder

    class TaskRuleResponder(DefaultResponder):
        def respond(self, role, ctx, workspace):
            out = super().respond(role, ctx, workspace)
            if role == 'research_preparation':
                path = workspace / 'activity-extensions.json'
                extensions = json.loads(path.read_bytes())
                for row in extensions.get('task_conditions', []):
                    row['observation_rules'] = [deepcopy(RULE)]
                path.write_text(json.dumps(extensions), encoding='utf-8')
            return out
    return TaskRuleResponder()


def ready_task(sim):
    from do_math import planning
    context = sim.engine._evaluation_context()
    return next((tid for tid, task in sim.runtime['tasks'].items() if planning.task_ready(
        task, sim.instance, sim.runtime, evaluation_context=context)['state'] == 'ready'), None)


def trackers_made():
    """The execution ID and configuration of every observation tracker the engine makes."""
    return ObservedCalls(tracker=ObservationTracker.__init__, capture={'tracker': lambda arguments: (
        arguments['execution_id'], deepcopy(arguments['config']))})


class TaskObservationRoleTests(unittest.TestCase):
    """A task's initial rules reach only a research work call, bound to its execution; the task keeps its own rules.

    The public flow prepares one task whose initial rules are ``RULE`` and
    approves its contract; the engine then starts a call on it, and the
    tracker it makes is rebuilt from the configuration it passed.
    """

    def check(self, sim, config, execution_id, role, task_id):
        tracker = ObservationTracker(execution_id, Path(sim.root), config, time_port=sim.clock)
        self.assertEqual(tracker.research_self_checks, role == 'research_work')
        self.assertEqual(bool(tracker.rules), role == 'research_work')
        if tracker.rules:
            self.assertEqual(tracker.rules[0]['subject']['id'], execution_id)
        self.assertEqual(sim.runtime['tasks'][task_id]['initial_observation_rules'], [RULE])

    def test_a_research_work_call_binds_the_tasks_initial_rules_to_its_execution(self):
        """About 6-9 s, over the 2 s Sim budget: the public flow runs a preparation, a contract review, a plan and the research call."""
        sim = Sim.activated()
        sim.model.responder = task_rule_responder()
        sim.run_until(lambda s: any(a['role'] == 'research_work' for a in s.runtime['queue']), max_steps=4)
        task_id = next(a for a in sim.runtime['queue'] if a['role'] == 'research_work')['target']
        self.assertEqual(sim.runtime['tasks'][task_id]['initial_observation_rules'], [RULE])
        with trackers_made() as calls:
            sim.run_until(lambda s: any(e.get('role') == 'research_work' for e in s.runtime['executions'].values()),
                          max_steps=2)
        (execution_id, config), = [(eid, config) for eid, config in calls.captured('tracker')
                                   if sim.runtime['executions'][eid]['role'] == 'research_work']
        self.assertEqual(sim.runtime['executions'][execution_id]['action']['target'], task_id)
        self.check(sim, config, execution_id, 'research_work', task_id)

    def test_a_supplemental_research_call_takes_no_task_rules_or_self_checks(self):
        """About 4-6 s, over the 2 s Sim budget: the public flow runs a preparation and a contract review before the call."""
        from do_math.execution_profiles import profile_ref
        from support.model import rebound

        def offer_supplemental_profiles(out, ctx):
            # The candidate may also be worked by supplemental research: bind the supplied profiles of that role too.
            current = ctx.get('role_profile_refs', {}).get('supplemental_research')
            refs = [profile_ref(p) for p in ctx['execution_profiles'] if p['role'] == 'supplemental_research'
                    and (current is None or profile_ref(p) in current)]
            for row in out.get('candidates', []):
                row['profile_refs'] = row['profile_refs'] + refs
        sim = Sim.activated()
        sim.model.responder = task_rule_responder()
        sim.model.on('research_preparation').reply(rebound(offer_supplemental_profiles))
        sim.run_until(ready_task, max_steps=4)
        task_id = ready_task(sim)
        self.assertEqual(sim.runtime['tasks'][task_id]['initial_observation_rules'], [RULE])
        # The user requests supplemental research on the ready task; the engine starts it from its queue.
        sim.control('request', text='Supplement the task', config={'role': 'supplemental_research', 'target': task_id})
        sim.engine.process_controls()
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'supplemental_research')
        with trackers_made() as calls:
            steps = sim.engine._call_steps(action)
            try:
                self.assertIsInstance(next(steps), dict, 'the supplemental call did not start')
            finally:
                steps.close()
        (execution_id, config), = calls.captured('tracker')
        self.assertEqual(sim.runtime['executions'][execution_id]['role'], 'supplemental_research')
        self.check(sim, config, execution_id, 'supplemental_research', task_id)


if __name__ == '__main__':
    unittest.main()

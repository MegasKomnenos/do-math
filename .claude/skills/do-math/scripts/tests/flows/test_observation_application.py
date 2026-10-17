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
from datetime import timedelta
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
    def test_owner_delayed_tick_does_not_open_utc_obligations_before_its_receipt_time(self):
        sim = Sim.activated()
        execution_id = 'EX-delayed-utc'
        workspace = running_execution(sim, execution_id, 'research_work', bind=True)
        at = (sim.clock.wall() + timedelta(seconds=2)).isoformat()
        tracker = ObservationTracker(execution_id, workspace, {
            'observation_mode': 'event_driven', 'research_self_checks': True,
            'observation_rules': [observation_rule('wall_time_reached', 'clock', 'UTC', at)],
            'observation_interval_seconds': 300, **WINDOWS}, time_port=sim.clock)
        tracker.schedule_review('RECHECK', at=at, reason='inspect recovery', basis_ref=execution_id)
        stream = workspace / 'stdout.jsonl'
        incoming = batch(sim, [], stream)
        sim.advance(1000)
        queue = deepcopy(sim.runtime['queue'])
        sim.engine._observe_running(execution_id, tracker, incoming)
        self.assertFalse(tracker.obligations)
        self.assertFalse(tracker.explicit_reviews['RECHECK']['fired'])
        self.assertEqual(sim.runtime['queue'], queue)
        applied = sim.runtime['executions'][execution_id]['observation_stream']
        self.assertEqual((applied['received_at'], applied['applied_at']), (incoming.received_at, sim.clock.now()))
        self.assertFalse(applied['local_termination_confirmed'])
        sim.engine._observe_running(execution_id, tracker, batch(sim, [], stream))
        obligation, = tracker.obligations.values()
        self.assertEqual(obligation['snapshot']['observed_at'], sim.clock.now())
        self.assertEqual(obligation['opened_offset_ms'], 1000000)
        self.assertIn('delivered_request_sha256', obligation)
        review, = [action for action in sim.runtime['queue'] if action['role'] == 'operational_review']
        self.assertEqual(review['target'], execution_id)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

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


class OperationalReviewTriggerTests(unittest.TestCase):
    def test_self_check_receipts_dispatch_only_required_reviews_and_replay_never_duplicates(self):
        from do_math.control_protocol import SELF_CHECK_PROGRESS, SELF_CHECK_RESPONSE_SCHEMA
        from support.engine_control import running_work
        from support.observation_inputs import self_check_response
        from support.cross_contracts import assert_call_records
        from support.model import Answer

        progress_values = ('progress', 'no_progress', 'contract_mismatch')
        statuses = ('normal', 'defect', 'indeterminate')
        self.assertEqual(set(progress_values), set(SELF_CHECK_PROGRESS))
        self.assertEqual(set(statuses), set(SELF_CHECK_RESPONSE_SCHEMA['properties']['rule_results']['items']['properties']['status']['enum']))
        cases = [(progress, status, False, False) for progress in progress_values for status in statuses]
        cases += [('no_progress', 'normal', True, False), ('progress', 'normal', False, True)]
        for progress, status, repeated, bad_evidence in cases:
            with self.subTest(progress=progress, status=status, repeated=repeated, bad_evidence=bad_evidence):
                sim = Sim.activated()
                sim.control('configure', text='Review after two unanswered progress attempts',
                            config={'no_progress_limit': 2})
                sim.engine.process_controls()
                self.assertEqual(sim.instance['config']['no_progress_limit'], 2)
                rules = [observation_rule(threshold=1, repeat_interval=1,
                    required_evidence=['workspace:checkpoint.json'])]
                with running_work(sim, rules=rules) as call:
                    def answer_round(number, answer_progress, answer_status, invalid=False):
                        write_checkpoint(call.workspace, counters={'attempts': number})
                        call.observe({'type': 'tick'})
                        obligation, = [row for row in call.tracker.obligations.values() if row['status'] == 'open']
                        response = self_check_response(obligation, answer_status,
                            [] if answer_status == 'indeterminate' else None)
                        response['progress'] = answer_progress
                        if invalid:
                            response['rule_results'][0]['evidence_refs'] = ['EV-unavailable']
                        delivery = call.self_check(obligation['id'], response)
                        call.receive()
                        receipt = call.receipt(delivery['request_id'])
                        self.assertEqual(receipt['state'], 'rejected' if invalid else 'accepted', receipt)
                        return obligation, response, receipt

                    if repeated:
                        answer_round(1, 'no_progress', 'normal')
                        self.assertFalse(any(a['role'] == 'operational_review' for a in sim.runtime['queue']))
                    obligation, response, receipt = answer_round(2 if repeated else 1, progress, status, bad_evidence)
                    expected = int(status != 'normal' or progress == 'contract_mismatch' or repeated or bad_evidence)
                    queued = [a for a in sim.runtime['queue'] if a['role'] == 'operational_review']
                    self.assertEqual(len(queued), expected)
                    if expected:
                        self.assertEqual(queued[0]['target'], call.execution_id)
                        self.assertEqual(queued[0]['obligation_ids'], [obligation['id']])
                    before = assert_call_records(self, sim)
                    sim.model.on('operational_review', target=call.execution_id).reply(Answer(lambda out, ctx: {
                        **out, 'disposition': {'kind': 'continue', 'basis_refs': [ctx['execution_to_review']['id']],
                            'next_owner': 'research_work', 'reason': 'Examine the received self-check.', 'next_review': None}}))
                    with sim.engine.store.writer_lock():
                        sim.engine._reload()
                        sim.engine._run_parallel(max_steps=1)
                    after = assert_call_records(self, sim)
                    self.assertEqual(after['operational_review'] - before['operational_review'], expected)
                    for row in sim.runtime['executions'].values():
                        if row['role'] == 'operational_review':
                            self.assertEqual(row['outcome'], 'output_accepted', row.get('error'))
                    redelivery = call.self_check(obligation['id'], response)
                    call.receive()
                    self.assertEqual(call.receipt(redelivery['request_id']), receipt)
                    with sim.engine.store.writer_lock():
                        sim.engine._reload()
                        sim.engine._run_parallel(max_steps=1)
                    self.assertEqual(assert_call_records(self, sim), after)
                    self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_stored_review_schedule_calls_once_at_its_deadline_only_while_target_runs(self):
        """A real accepted continue creates the schedule; owner passes consume it once."""
        from do_math.execution_lifecycle import transition_execution
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.model import Answer

        for state in ('no_schedule', 'before', 'at', 'after', 'stopping', 'ended',
                      'tracker_at', 'tracker_after', 'restart_before', 'restart_after', 'tracker_restart'):
            with self.subTest(state=state):
                sim = Sim.activated()
                sim.model.responder = DefaultResponder(preparation_candidates=[])
                sim.step()
                def owner_pass():
                    # Continue this owner rather than reenter run's recovery path,
                    # which deliberately stops a predecessor left by another owner.
                    with sim.engine.store.writer_lock():
                        sim.engine._reload()
                        sim.engine._run_parallel(max_steps=1)

                target = 'EX-scheduled-review'
                workspace = running_execution(sim, target, 'research_work', bind=True)
                write_checkpoint(workspace)
                tracker = ObservationTracker(target, workspace,
                    {'observation_mode': 'event_driven', 'research_self_checks': False}, time_port=sim.clock)
                tracked = state.startswith('tracker')
                if tracked:
                    sim.engine._trackers[target] = tracker
                sim.engine._observe_running(target, tracker, batch(sim,
                    [{'type': 'turn.started', 'execution_id': 'EX-other'}], workspace / 'stdout.jsonl'))
                at = sim.clock.wall() + timedelta(seconds=30)
                next_review = None if state == 'no_schedule' else {'at': at.isoformat(), 'reason': 'Review preserved progress again'}

                def proceed(out, context, schedule=next_review):
                    return {**out, 'disposition': {'kind': 'continue',
                        'basis_refs': [context['execution_to_review']['id']], 'next_owner': 'research_work',
                        'reason': 'Continue with the explicit next review decision.', 'next_review': schedule}}

                sim.model.on('operational_review', target=target).reply(Answer(proceed)).reply(Answer(
                    lambda out, context: proceed(out, context, schedule=None)))
                owner_pass()
                before = assert_call_records(self, sim)
                self.assertEqual(before['operational_review'], 1)
                saved = sim.runtime['executions'][target]['operational_continuation']
                self.assertEqual(saved['next_review'], next_review)
                disposition_id = saved['disposition_id']
                self.assertEqual(sim.runtime['executions'][target]['status'], 'running')
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['executions'][target]['operational_continuation'], saved)
                if tracked:
                    self.assertEqual(tracker.explicit_reviews[disposition_id]['at'], next_review['at'])
                    self.assertFalse(tracker.explicit_reviews[disposition_id]['fired'])
                restarted = 'restart' in state
                if restarted:
                    sim.restart()
                    self.assertNotIn(target, sim.engine._trackers)
                if state in ('stopping', 'ended'):
                    execution = sim.runtime['executions'][target]
                    transition_execution(execution, 'stopping', at=sim.clock.now(), reason='work stopped')
                    if state == 'ended':
                        transition_execution(execution, 'ended', at=sim.clock.now(), outcome='cancelled')
                    sim.engine._save()
                offset = -1 if state in ('before', 'restart_before') else 1 if state in (
                    'after', 'stopping', 'ended', 'no_schedule', 'tracker_after', 'restart_after', 'tracker_restart') else 0
                sim.advance((at - sim.clock.wall()).total_seconds() + offset)
                if restarted:
                    sim.engine.process_controls()
                    self.assertEqual(sim.runtime['executions'][target]['operational_continuation'], saved)
                    self.assertFalse(any(a['role'] == 'operational_review' and a.get('live')
                                         and a.get('target') == target for a in sim.runtime['queue']))
                    # Public run recovers the old owner; never make its execution running again.
                    sim.engine.run(max_steps=1)
                    self.assertIn(sim.runtime['executions'][target]['status'], ('stopping', 'ended'))
                elif tracked:
                    # A caught-up empty tick is what the runner emits without new stdout rows.
                    sim.engine._schedule_operational_reviews()
                    self.assertNotIn('dispatched_at', sim.runtime['executions'][target]['operational_continuation'])
                    sim.engine._observe_running(target, tracker, batch(sim, [], workspace / 'stdout.jsonl'))
                owner_pass()
                expected = int(state in ('at', 'after', 'tracker_at', 'tracker_after'))
                after = assert_call_records(self, sim)
                self.assertEqual(after['operational_review'] - before['operational_review'], expected,
                    {'target_status': sim.runtime['executions'][target]['status'],
                     'continuation': sim.runtime['executions'][target].get('operational_continuation'),
                     'tracker': target in sim.engine._trackers, 'now': sim.clock.now(),
                     'queue': sim.runtime['queue'], 'waiting': sim.runtime.get('waiting_actions', {})})
                if expected:
                    review = next(row for row in sim.runtime['executions'].values()
                                  if row['role'] == 'operational_review'
                                  and row['action'].get('observation', {}).get('kind') == (
                                      'explicit_review_due' if tracked else 'scheduled_review_due'))
                    if tracked:
                        self.assertTrue(tracker.explicit_reviews[disposition_id]['fired'])
                    else:
                        self.assertEqual(review['action']['observation_refs'], [disposition_id])
                    self.assertEqual(review['action']['target'], target)
                    self.assertEqual(review['outcome'], 'output_accepted', review.get('error'))
                else:
                    self.assertEqual(sim.runtime['executions'][target]['operational_continuation'], saved)
                before_idle = sim.clock.now()
                owner_pass()
                self.assertEqual(sim.clock.now(), before_idle)
                self.assertEqual(assert_call_records(self, sim), after)
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_observation_triggers_open_one_real_review_only_for_a_live_due_target(self):
        """11-B observation subset: actual Tracker -> owner -> model/worker, including duplicate delivery."""
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.model import Answer

        def proceed(out, context):
            return {**out, 'disposition': {'kind': 'continue',
                'basis_refs': [context['execution_to_review']['id']], 'next_owner': 'research_work',
                'reason': 'The preserved observation was examined; continue the same work.', 'next_review': None}}

        cases = ('tool_review_due', 'periodic_review_due', 'explicit_review_due', 'observation_input_rejected')
        for kind in cases:
            for state in ('not_due', 'live_due', 'terminated_due'):
                with self.subTest(trigger=kind, target=state):
                    sim = Sim.activated()
                    sim.model.responder = DefaultResponder(preparation_candidates=[])
                    sim.step()  # consume the actual activation/preparation receipt first
                    before = assert_call_records(self, sim)
                    self.assertEqual(before['operational_review'], 0)
                    execution_id = 'EX-trigger'
                    workspace = running_execution(sim, execution_id, 'research_work', bind=True)
                    write_checkpoint(workspace)
                    tracker = ObservationTracker(execution_id, workspace, {
                        'observation_mode': 'periodic' if kind == 'periodic_review_due' else 'event_driven',
                        'research_self_checks': False, 'tool_review_window_seconds': 2,
                        'observation_interval_seconds': 2}, time_port=sim.clock)
                    stream = workspace / 'stdout.jsonl'
                    if kind == 'explicit_review_due':
                        tracker.schedule_review('review-trigger', at=(sim.clock.wall() + timedelta(seconds=2)).isoformat(),
                                                reason='Examine preserved progress', basis_ref=execution_id)
                    initial = ([{'type': 'item.started', 'item': {'id': 'tool-trigger', 'type': 'command_execution'}}]
                               if kind == 'tool_review_due' else [])
                    first = batch(sim, initial, stream, terminated=state == 'terminated_due')
                    sim.engine._observe_running(execution_id, tracker, first)
                    self.assertFalse(any(action['role'] == 'operational_review' for action in sim.runtime['queue']))
                    if state != 'not_due':
                        sim.advance(3)
                    incoming = ([{'type': 'turn.started', 'execution_id': 'EX-other'}]
                                if kind == 'observation_input_rejected' and state != 'not_due' else [])
                    delivered = batch(sim, incoming, stream, start=first.end_offset, first_row=len(initial),
                                      terminated=state == 'terminated_due')
                    sim.engine._observe_running(execution_id, tracker, delivered)
                    sim.engine._observe_running(execution_id, tracker, delivered)
                    expected = int(state == 'live_due')
                    queued = [action for action in sim.runtime['queue'] if action['role'] == 'operational_review']
                    self.assertEqual(len(queued), expected)
                    if expected:
                        self.assertEqual((queued[0]['target'], queued[0]['live']), (execution_id, True))
                        self.assertEqual(sim.runtime['observations'][execution_id]['kind'], kind)
                    sim.model.on('operational_review', target=execution_id).reply(Answer(proceed))
                    sim.step()
                    after = assert_call_records(self, sim)
                    self.assertEqual(after['operational_review'] - before['operational_review'], expected)
                    reviewed = [row for row in sim.runtime['executions'].values() if row['role'] == 'operational_review']
                    self.assertEqual(len(reviewed), expected)
                    for row in reviewed:
                        self.assertEqual(row['outcome'], 'output_accepted', row.get('error'))
                    sim.step()
                    self.assertEqual(assert_call_records(self, sim), after,
                                     'an accepted review must not be reopened on the next owner pass')
                    self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)


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
        self.assertGreater(copies.count('copy', caller='do_math.observations'), 0)  # publication_candidate copies the tracker
        self.assertFalse(any(copies.captured('copy', caller='do_math.observations')))
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

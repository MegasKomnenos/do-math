"""Repetition lineages on the engine: receipts of real role outputs count, hold and release them
(``revisions``, ``governance.apply_decision``, ``planning``; the engine's receivers ``_collect_submitted_result``,
``_receive_submission``, ``_complete_operational_disposition``, ``process_controls``; layers 2 and 3),
moved from ``test_repetition`` (``RepetitionEngineTests``; the intent rework is ``flows.test_planning_intent_rework``).

The legacy tests ran on the synthetic active template (``ActivatedPurposeHarness``,
with the provider adapter patched), answered a preparation with ``ScriptedRunner``
inside a real Windows Job and drew IDs and times from the system clock. Here a
restored Sim's real engine runs on the port fakes: the model double answers
through the worker with the same ``ScriptedRunner`` responses, the provider
evidence of a finished native final is drawn from the Sim's Jobs and clock ports
(``support.submission_receiver.native_result``), IDs and times come from the
clock port, and the repetition limits are adopted by the public ``configure``
control. Nothing of the engine or its store is replaced.
"""
from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import unittest

from do_math import activities, governance, planning, revisions, submission, task_contracts
from do_math.canonical import canonical_json
from do_math.engine import ResearchEngine
from do_math.execution_lifecycle import end_preparation, transition_execution
from do_math.input_basis import capture_decision_basis
from support.engine_lifecycle import applied, clear_work, ticking_clock
from support.sim import Sim, warm_template
from support.submission_receiver import native_result

setUpModule = warm_template


def limited(**limits):
    """A restored active instance whose repetition limits the user adopted by the public ``configure`` control."""
    sim = Sim.activated()
    applied(sim, 'configure', config=dict(limits))
    return sim


def now(sim):
    return sim.clock.now()


def seed_plan(sim):
    """A plan execution that failed in preparation and whose activity waits for an operational review."""
    engine = sim.engine
    engine.runtime['queue'] = []
    engine._enqueue('research_plan', reason='Regression selection')
    action = engine.runtime['queue'][0]
    execution = engine._register_execution(action, {'id': sim.clock.new_id('EX'), 'role': action['role'], 'status': 'queued'})
    end_preparation(execution, at=now(sim), stage='context', reason='Fixture original failure', cancelled=False)
    engine._remove_action(action)
    activities.wait_for(engine.runtime, execution['owner_activity_id'], reason='receipt failed',
        condition={'execution_id': execution['id']}, next_owner='operational_review', at=now(sim))
    return execution


def issued(sim, action, execution):
    """Seal ``execution``'s role input as the owner does before a provider starts: returns ``(context, schema, workspace)``.

    The role input manifest names the archived prompt saved with it; the owner's
    pre-write inspection requires it to exist.
    """
    engine = sim.engine
    bundle = sim.clock.new_id('BA')
    prefix = 'runtime/artifacts/' + bundle
    prompt = b'exact sealed prompt'
    execution.update(grant_id=action['grant_id'], input_snapshot=engine.head, input_bundle=bundle,
        input_manifest={'prompt': {'artifact_ref': prefix + '/input.txt',
            'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}},
        **planning.governance_revisions(engine.instance))
    execution['decision_basis'] = capture_decision_basis(engine.instance, engine.runtime, engine._decision_references(action))
    workspace = Path(engine.instance['workspace']) / 'runs' / execution['id'] / 'workspace'
    workspace.mkdir(parents=True)
    context = engine._context(action, workspace, execution_id=execution['id'])
    schema = engine._response_schema(action)
    submission.install_tools(workspace, context, schema, engine.instance['config']['max_artifact_bytes'], clock=sim.clock)
    engine._save({prefix + '/input/submission/context.json': canonical_json(context),
                  prefix + '/schema.json': canonical_json(schema), prefix + '/input.txt': prompt})
    return context, schema, workspace


class RepetitionEngineTests(unittest.TestCase):
    def test_empty_preparation_preserves_machine_time_and_opens_one_due_regeneration(self):
        """About 2.2 s, over the 2 s Sim budget: the preparation is one model call through the worker."""
        sim = Sim.activated()
        clear_work(sim)
        engine = sim.engine
        engine._enqueue('research_preparation', reason='No usable candidate in this fixture')
        engine._save()
        # The legacy runner's answer: a preparation without candidates (and so without their extensions).
        from runner_fixtures import ScriptedRunner
        sim.model.responder = ScriptedRunner(preparation_candidates=[])

        def received(s):
            return any(r.get('kind') == 'task_repetition' and r.get('lineage') == 'exhaustion_empty'
                       for r in s.runtime['history'])
        # Every wall-clock read moves the clock, as the legacy test's system clock did: the machine
        # observation and the receipt happen at different times, so the receipt must copy the observation.
        ticking_clock(sim)
        sim.run_until(received, max_steps=3)
        engine = sim.engine
        receipt = next(r for r in engine.runtime['history'] if r.get('kind') == 'task_repetition'
                       and r.get('lineage') == 'exhaustion_empty')
        execution = engine.runtime['executions'][receipt['event_ref']]
        self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
        self.assertLess(execution['observed_at'], execution['ended_at'])
        self.assertEqual(receipt['observed_at'], execution['observed_at'])
        due = datetime.fromisoformat(receipt['regenerate_after'])
        state = deepcopy(engine.runtime)
        state.update(queue=[], status='active')
        early = planning.exhaustion_state(engine.instance, state, now=(due - timedelta(seconds=1)).isoformat())
        self.assertEqual(early['reasons'], ['regeneration_guard'])
        for _ in range(2):
            planning.schedule_reconsideration(engine.instance, state, now=due.isoformat())
        preparations = [a for a in state['queue'] if a['role'] == 'research_preparation']
        self.assertEqual(len(preparations), 1)

    def test_native_plan_failures_reach_receiver_counter_through_preserved_bytes(self):
        sim = limited(selection_failure_limit=3)
        engine = sim.engine
        engine.runtime['queue'] = []
        for index, (raw, expected) in enumerate(((b'{broken', 'output_parse'),
                (b'{"summary":"Missing plan fields"}', 'output_schema'),
                (json.dumps({'summary': 'Invalid population', 'used_sources': [], 'questions': [],
                    'dispositions': [{'task_id': 'TK-missing', 'kind': 'not_selected', 'reason': 'Unknown task',
                        'uncertainty': '', 'parallel_task_ids': [], 'expected_research_change': '',
                        'revisit': {'event_refs': [], 'at': '2100-01-01T00:00:00Z'}, 'missing_inputs': [], 'next_owner': 'research_plan'}],
                    'preparation_requests': [], 'goal_audit': False, 'task_assessments': []}).encode(), 'output_contract'))):
            action = {'id': sim.clock.new_id('AC'), 'role': 'research_plan'}
            engine._action_lifecycle_gate(action)
            execution = engine._register_execution(action, {'id': sim.clock.new_id('EX'), 'role': 'research_plan', 'status': 'running'})
            eid = execution['id']
            context, schema, workspace = issued(sim, action, execution)
            execution = engine.runtime['executions'][eid]
            result = native_result(sim, execution, context, raw, workspace)
            result = engine._collect_submitted_result(execution, result, context, schema, workspace)
            self.assertIn('rejected_submission', result, result.get('error'))
            transition_execution(engine.runtime['executions'][eid], 'stopping', at=now(sim))
            engine._receive_submission(action, result, eid, context, schema, workspace)
            failure = engine.runtime['executions'][eid]
            self.assertEqual(failure['error_kind'], expected, failure.get('integration_result'))
            receipts = [r for r in engine.runtime['history'] if r.get('kind') == 'task_repetition'
                        and r.get('lineage') == 'selection_failure']
            self.assertEqual(len(receipts), index + 1)
            self.assertEqual(receipts[-1]['outcome'], 'rejected')
            self.assertEqual(task_contracts.repetition_lineages(engine.runtime)['selection_failure']['count'], index + 1)
        hold = revisions.repetition_hold(engine.runtime, 'selection_failure', receipts[-1]['lineage_id'])
        self.assertEqual(hold['owner'], 'user')
        engine._save()

    def test_public_continue_releases_exact_hold_and_replay_is_idempotent(self):
        sim = limited(selection_failure_limit=1)
        engine = sim.engine
        target = seed_plan(sim)
        action = activities.continue_activity(engine.runtime, target['id'], at=now(sim), reason='Retry held plan')
        lineage = action['repetition_bases']['selection_failure']
        revisions.record_repetition(engine.instance, engine.runtime, lineage='selection_failure', lineage_id=lineage,
            event_ref=target['id'], outcome='rejected', owner='ai', reason='Missing population')
        hold = revisions.repetition_hold(engine.runtime, 'selection_failure', lineage)
        self.assertEqual(hold['owner'], 'user')
        self.assertTrue(revisions.action_repetition_waits(engine.instance, engine.runtime, action))
        engine._save()
        change = {'kind': 'repetition_continue', 'decision_id': sim.clock.new_id('DC'), 'lineage': 'selection_failure',
            'lineage_id': lineage, 'hold_event_ref': hold['event_ref'], 'allowed_action': revisions.action_scope(action)}
        sim.control('decision', config={'change': change}, text='Continue this held plan.')
        engine.process_controls()
        self.assertFalse(revisions.action_repetition_waits(engine.instance, engine.runtime, action))
        self.assertEqual(task_contracts.repetition_lineages(engine.runtime)['selection_failure']['count'], 0)
        stored = engine.instance['decisions'][change['decision_id']]
        _, replay, _ = governance.apply_decision(engine.instance, engine.runtime, change, source_ref=stored['source_ref'])
        self.assertEqual(replay['history'], engine.runtime['history'])
        stale = {**change, 'decision_id': sim.clock.new_id('DC')}
        with self.assertRaisesRegex(ValueError, 'current repetition hold'):
            governance.apply_decision(engine.instance, engine.runtime, stale, source_ref=stored['source_ref'])

    def test_operational_retry_is_idempotent_and_waits_for_user_at_the_limit(self):
        sim = limited(selection_failure_limit=1)
        engine = sim.engine
        target = seed_plan(sim)
        lineage = target['action']['repetition_bases']['selection_failure']
        revisions.record_repetition(engine.instance, engine.runtime, lineage='selection_failure',
            lineage_id=lineage, event_ref=target['id'], outcome='rejected', owner='ai', reason='Held plan failure')
        review_action = {'id': sim.clock.new_id('AC'), 'role': 'operational_review', 'target': target['id']}
        engine._action_lifecycle_gate(review_action)
        assessor = engine._register_execution(review_action, {'id': sim.clock.new_id('EX'), 'role': 'operational_review', 'status': 'running'})
        disposition = {'kind': 'retry', 'basis_refs': [target['id']], 'next_owner': 'research_plan', 'reason': 'Repair selection',
            'scope': 'Same held plan', 'replay_safety': 'No external effects or accepted bundles'}
        output = {'summary': 'Retry', 'questions': [], 'used_sources': [], 'disposition': disposition, 'task_assessments': []}
        context, schema, workspace = issued(sim, review_action, assessor)
        assessor = engine.runtime['executions'][assessor['id']]
        result = native_result(sim, assessor, context, json.dumps(output).encode(), workspace)
        result = engine._collect_submitted_result(assessor, result, context, schema, workspace)
        self.assertEqual(result['status'], 'completed', result.get('error'))
        transition_execution(engine.runtime['executions'][assessor['id']], 'stopping', at=now(sim))
        received = engine._receive_submission(review_action, result, assessor['id'], context, schema, workspace)
        self.assertEqual(received['status'], 'accepted', received.get('issues'))
        record = next(iter(engine.runtime['operational_dispositions'].values()))
        self.assertEqual(record['status'], 'applied')
        retry = next(a for a in engine.runtime['queue'] if a.get('continuation_of') == target['id'])
        self.assertEqual(retry['id'], target['action']['id'])
        self.assertTrue(revisions.action_repetition_waits(engine.instance, engine.runtime, retry))
        # Another process loading the same repository: the product constructor on the Sim's ports.
        restored = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports)
        restored_retry = next(a for a in restored.runtime['queue'] if a.get('id') == retry['id'])
        self.assertTrue(revisions.action_repetition_waits(restored.instance, restored.runtime, restored_retry))
        engine._complete_operational_disposition(record)
        self.assertEqual(sum(a.get('id') == retry['id'] for a in engine.runtime['queue']), 1)
        change = {'kind': 'repetition_continue', 'decision_id': sim.clock.new_id('DC'), 'lineage': 'selection_failure',
            'lineage_id': lineage, 'hold_event_ref': target['id'], 'allowed_action': revisions.action_scope(retry)}
        sim.control('decision', config={'change': change}, text='Continue this held plan after diagnosis.')
        engine.process_controls()
        retry = next(a for a in engine.runtime['queue'] if a.get('id') == retry['id'])
        self.assertFalse(revisions.action_repetition_waits(engine.instance, engine.runtime, retry))
        successor = engine._register_execution(retry, {'id': sim.clock.new_id('EX'), 'role': 'research_plan', 'status': 'queued'})
        self.assertEqual(successor['continuation_of'], target['id'])
        self.assertEqual(successor['action']['id'], target['action']['id'])
        self.assertFalse(any(r.get('kind') == 'repetition_repair_authorized' for r in engine.runtime['history']))


if __name__ == '__main__':
    unittest.main()

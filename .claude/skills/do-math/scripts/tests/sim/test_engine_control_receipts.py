"""Execution control requests the owner publishes (``core_engine._publish_control_request``, layer 2) on a Sim.

Each test starts one research call as the scheduler does (``support.engine_control.running_work``):
the product fixes its grant, input bundle, control binding and observation
tracker. The worker's requests travel as a worker sends them: its draft through
the workspace submission tool, its boundary report and self-check answer
through the transport, and the owner's inbox pass pumps them into the
publication hook. Observations reach the owner through the call's own
``on_observation`` callback. The legacy tests built these on an engine double
whose ``seal_submission``, ``_save`` and ``_control_evidence_refs`` were
replaced; here the draft is the model double's answer to the call's actual
prompt, a failed publication is a real compare-and-swap failure (another writer
holds the ref), and the evidence a response may cite is the product's judgment.

A test restores the activation template and prepares one research call, about
1.5 s alone and up to 2.5 s in a full run; the test of the two arrival orders
prepares a call for each.
"""
from copy import deepcopy
import unittest

from do_math.git_store import GitStateStoreError
from do_math.submission import PREVIEW_CONTRACT_ID
from research_fixtures import observation_rule, self_check_response, write_checkpoint
from support.engine_control import held_ref, running_work
from support.provider_probes import ObservedCalls
from support.sim import Sim, warm_template

setUpModule = warm_template
CAS = 'state ref changed before the publish compare-and-swap'
# The task's rule counts two attempts and asks for the execution's own checkpoint as evidence.
CHECKPOINT_RULES = [observation_rule(required_evidence=['workspace:checkpoint.json'])]


def published(engine, captured):
    """A spy on the owner's publications: saves and the requests the transport handed the publication hook."""
    return ObservedCalls(save=type(engine)._save, publish=type(engine)._publish_control_request,
                         capture={'publish': lambda arguments: captured.append(deepcopy(arguments['request']))})


def due(call):
    """The self-check obligation the owner opens once the worker's checkpoint counts two attempts."""
    write_checkpoint(call.workspace, counters={'attempts': 2})
    call.observe({'type': 'tick'})
    return next(row for row in call.tracker.obligations.values() if row['kind'] == 'self_check_due')


class SubmissionReceiptTests(unittest.TestCase):
    def test_receipt_requires_successful_cas_and_replay_does_not_reapply(self):
        """About 2 s, at the Sim budget: a template restore and one research call's preparation are its start."""
        with running_work(Sim.activated()) as call:
            engine, requests = call.engine, []
            before, receipts = engine.head, set(engine.runtime.get('control_receipts', {}))
            with published(engine, requests) as calls:
                delivery = call.draft()
                call.receive()
                receipt = call.receipt(delivery['request_id'])
                self.assertEqual(receipt['state'], 'accepted', receipt)
                self.assertNotEqual(engine.head, before)
                self.assertEqual(receipt['snapshot'], engine.head)
                self.assertEqual(call.execution['status'], 'stopping')
                self.assertNotIn('outcome', call.execution)
                stored = engine.store.load()[2]['control_receipts']
                added = [row for key, row in stored.items() if key not in receipts]
                self.assertEqual([row['request_id'] for row in added], [delivery['request_id']])
                self.assertNotIn('capability', added[0]['request'])
                self.assertIn('capability', requests[0], 'the transport handed the hook the capability it checked')
                replay = engine._publish_control_request(requests[0])
                self.assertEqual((replay['state'], replay['publication_id']), ('accepted', receipt['publication_id']))
                self.assertEqual(calls.count('save'), 1)

    def test_failed_cas_does_not_acknowledge_submission(self):
        """About 2 s, at the Sim budget: a template restore and one research call's preparation are its start."""
        sim = Sim.activated()
        with running_work(sim) as call:
            with held_ref(sim):
                delivery = call.draft()
                call.receive()
            receipt = call.receipt(delivery['request_id'])
            self.assertEqual((receipt['state'], receipt['reason']), ('rejected', CAS))
            self.assertNotIn('submission_receipt', call.execution)
            self.assertNotIn('submission_receipt', call.engine.store.load()[2]['executions'][call.execution_id])


class PreviewReceiptTests(unittest.TestCase):
    def test_preview_control_is_nonpublishing_and_returns_sanitized_result(self):
        """About 2 s, at the Sim budget: a template restore and one research call's preparation are its start."""
        with running_work(Sim.activated()) as call:
            engine, requests = call.engine, []
            before = deepcopy((engine.instance, engine.runtime, engine.head))
            with published(engine, requests) as calls:
                delivery = call.draft(kind='submission_preview')
                call.receive()
                receipt = call.receipt(delivery['request_id'])
                # The owner's own answer: exactly the preview state and the product's preview, nothing published.
                direct = engine._publish_control_request(requests[0])
                expected = engine._preview_submission(call.execution, requests[0]['payload'])
            self.assertEqual((expected['contract_id'], expected['authoritative']), (PREVIEW_CONTRACT_ID, False))
            self.assertEqual(direct, {'state': 'previewed', 'result': expected})
            self.assertEqual((receipt['state'], receipt['result']), ('previewed', expected))
            self.assertEqual(calls.count('save'), 0)
            self.assertEqual((engine.instance, engine.runtime, engine.head), before)


class SafetyBoundaryTests(unittest.TestCase):
    def test_safety_boundary_releases_the_held_deadline_only_after_publication(self):
        """About 2 s, at the Sim budget: a template restore and one research call's preparation are its start."""
        sim = Sim.activated()
        with running_work(sim, rules=CHECKPOINT_RULES) as call:
            engine, requests = call.engine, []
            call.observe({'type': 'item.started', 'item': {'id': 'C', 'type': 'command_execution'}})
            obligation = due(call)
            # The research call C was running when the obligation opened, so its deadline is held.
            self.assertEqual((obligation['deadline_offset_ms'], obligation['deadline_held_offset_ms']), (5000, 0))
            payload = {'inflight_calls': False, 'call_ids': ['C']}
            call.observe({'type': 'item.started', 'item': {'id': 'BOUNDARY', 'type': 'mcp_tool_call',
                'server': 'execution_control', 'tool': 'control_submit', 'arguments': {
                    'request_id': 'boundary-one', 'kind': 'safety_boundary', 'payload': payload}}})
            self.assertIn('BOUNDARY', call.tracker.boundary_call_ids)
            self.assertNotIn('BOUNDARY', call.tracker.self_check_call_ids)
            call.submit('safety_boundary', {'inflight_calls': False, 'call_ids': []}, 'uncovered')
            call.receive()
            self.assertEqual((call.receipt('uncovered')['state'], call.receipt('uncovered')['reason']),
                             ('rejected', 'safe boundary omits observed inflight research calls'))
            with held_ref(sim):
                call.submit('safety_boundary', payload, 'boundary-lost')
                call.receive()
            self.assertEqual((call.receipt('boundary-lost')['state'], call.receipt('boundary-lost')['reason']),
                             ('rejected', CAS))
            self.assertEqual(call.tracker.obligations[obligation['id']]['deadline_held_offset_ms'], 0)
            with published(engine, requests):
                call.submit('safety_boundary', payload, 'boundary-one')
                call.receive()
            receipt = call.receipt('boundary-one')
            self.assertEqual(receipt['state'], 'accepted', receipt)
            self.assertNotIn('deadline_held_offset_ms', call.tracker.obligations[obligation['id']])
            self.assertEqual(call.tracker.obligations[obligation['id']]['deadline_offset_ms'], 5000)
            self.assertEqual(engine.runtime['self_check_obligations'][obligation['id']]['deadline_offset_ms'], 5000)
            saved = engine.store.load()[2]['self_check_obligations'][obligation['id']]
            self.assertNotIn('deadline_held_offset_ms', saved)
            self.assertEqual(saved['deadline_offset_ms'], 5000)
            # A restarted owner replays the published receipt without applying the boundary again.
            sim.restart()
            with published(sim.engine, []) as calls:
                replay = sim.engine._publish_control_request(requests[-1])
            self.assertEqual((replay['state'], replay['publication_id']), ('accepted', receipt['publication_id']))
            self.assertEqual(calls.count('save'), 0)


class SelfCheckReceiptTests(unittest.TestCase):
    def test_rejected_self_check_is_preserved_but_not_acknowledged_as_accepted(self):
        """About 2 s, at the Sim budget: a template restore and one research call's preparation are its start."""
        # The task's rule asks for ``EV-1``, which nothing the execution may cite names.
        with running_work(Sim.activated(), rules=[observation_rule()]) as call:
            engine = call.engine
            obligation = due(call)
            queue = deepcopy(engine.runtime['queue'])
            responses = set(engine.runtime.get('self_check_responses', {}))
            delivery = call.self_check(obligation['id'], self_check_response(obligation))
            call.receive()
            receipt = call.receipt(delivery['request_id'])
            # The receipt the worker reads names the actual rejection error.
            self.assertEqual((receipt['state'], receipt['reason']),
                             ('rejected', 'self-check response rejected: evidence_not_current'))
            added = [row for key, row in engine.runtime['self_check_responses'].items() if key not in responses]
            self.assertEqual([row['kind'] for row in added], ['self_check_rejected'])
            self.assertEqual(engine.runtime['queue'][:len(queue)], queue)
            review, = engine.runtime['queue'][len(queue):]
            self.assertEqual((review['role'], review['target'], review['live']),
                             ('operational_review', call.execution_id, True))
            self.assertTrue((call.workspace / '.control/observation-feedback.json').is_file())

    def test_self_check_transport_and_native_call_bind_in_both_arrival_orders(self):
        """About 3 to 4.5 s, over the 2 s Sim budget: each arrival order needs its own restored instance and research call."""
        for first in ('native', 'receipt'):
            with self.subTest(first=first), running_work(Sim.activated(), rules=CHECKPOINT_RULES) as call:
                engine, requests = call.engine, []
                obligation = due(call)
                response = self_check_response(obligation)
                payload = {'self_check_id': obligation['id'], 'response': response}
                event = {'type': 'item.started', 'item': {'id': 'CALL-SC', 'type': 'mcp_tool_call',
                         'server': 'execution_control', 'tool': 'control_self_check', 'arguments': payload}}
                queue = deepcopy(engine.runtime['queue'])
                if first == 'native':
                    call.observe(event)  # the owner's own observation publication is not the request's
                with published(engine, requests) as calls:
                    delivery = call.self_check(obligation['id'], response)
                    call.receive()
                receipt = call.receipt(delivery['request_id'])
                self.assertEqual(receipt['state'], 'accepted', receipt)
                if first == 'receipt':
                    call.observe(event)
                tracker = call.tracker
                self.assertEqual(tracker.obligations[obligation['id']]['status'], 'answered')
                self.assertEqual(tracker.control_calls['CALL-SC']['payload_sha256'],
                                 tracker.control_requests[delivery['request_id']]['payload_sha256'])
                self.assertEqual(tracker.control_requests[delivery['request_id']]['receipt_id'],
                                 receipt['publication_id'])
                self.assertEqual(engine.runtime['queue'], queue)
                with calls:  # the same count continues: publication and replay publish once in all
                    replay = engine._publish_control_request(requests[0])
                self.assertEqual((replay['state'], replay['publication_id']), ('accepted', receipt['publication_id']))
                self.assertEqual(calls.count('save'), 1)

    def test_self_check_response_and_its_rule_update_are_saved(self):
        """About 2 s, at the Sim budget: a template restore and one research call's preparation are its start."""
        with running_work(Sim.activated(), rules=CHECKPOINT_RULES) as call:
            obligation = due(call)
            # The answer cites the execution's own checkpoint, which the product's evidence rule admits.
            response = {**self_check_response(obligation), 'rule_proposal': {'current_revision': 0,
                'reason': 'Check again at the next attempt pair',
                'rules': [observation_rule(repeat_interval=2, required_evidence=['workspace:checkpoint.json'])]}}
            self.assertEqual(response['rule_results'][0]['evidence_refs'], ['workspace:checkpoint.json'])
            responses = set(call.engine.runtime.get('self_check_responses', {}))
            delivery = call.self_check(obligation['id'], response)
            call.receive()
            receipt = call.receipt(delivery['request_id'])
            self.assertEqual(receipt['state'], 'accepted', receipt)
            _, _, stored = call.engine.store.load()
            added = [row for key, row in stored['self_check_responses'].items() if key not in responses]
            self.assertEqual([row['kind'] for row in added], ['self_check_received'])
            record = added[0]
            self.assertEqual(record['rule_update']['kind'], 'observation_rules_accepted')
            self.assertEqual(stored['self_check_obligations'][obligation['id']]['status'], 'answered')

    def test_self_check_failed_publication_does_not_publish_tracker_binding(self):
        """About 2 s, at the Sim budget: a template restore and one research call's preparation are its start."""
        sim = Sim.activated()
        with running_work(sim, rules=CHECKPOINT_RULES) as call:
            engine = call.engine
            obligation = due(call)
            delivery = call.self_check(obligation['id'], self_check_response(obligation))
            head = engine.head
            ref = sim.repository / '.git' / 'refs' / 'heads' / 'do-math' / sim.instance_id
            original = ref.read_bytes()
            # The ref names an object nobody wrote: the publication fails, and so does the reload
            # that would find a receipt committed before the acknowledgment was lost.
            ref.write_bytes(b'0' * 40 + b'\n')
            try:
                with self.assertRaisesRegex(GitStateStoreError, '^state ref points to an unreadable object$'):
                    engine.store.load()
                call.receive()
            finally:
                ref.write_bytes(original)
            receipt = call.receipt(delivery['request_id'])
            self.assertEqual((receipt['state'], receipt['reason']), ('rejected', 'state ref points to an unreadable object'))
            self.assertEqual(engine.head, head)
            self.assertEqual(call.tracker.control_requests, {})
            self.assertEqual(call.tracker.obligations[obligation['id']]['status'], 'open')


if __name__ == '__main__':
    unittest.main()

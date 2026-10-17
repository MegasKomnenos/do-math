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
from support.observation_inputs import observation_rule, self_check_response, write_checkpoint
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
    def test_self_check_cites_own_obligation_and_verified_workspace_but_drops_a_foreign_reference(self):
        """T3 4.3 s: the live call fixes the actual input and checkpoint-backed obligation."""
        with running_work(Sim.activated(), rules=CHECKPOINT_RULES) as call:
            obligation = due(call)
            response = self_check_response(obligation,
                evidence=[obligation['id'], 'workspace:checkpoint.json', 'KN-not-in-this-input'])
            before = deepcopy((call.engine.head, call.engine.instance, call.engine.runtime))
            self.assertEqual(call.engine._control_evidence_refs(call.execution, response),
                             {obligation['id'], 'workspace:checkpoint.json'})
            self.assertEqual((call.engine.head, call.engine.instance, call.engine.runtime), before)

    def test_check_summary_refuses_disagreement_between_ordered_event_receipt_and_intent(self):
        with running_work(Sim.activated()) as call:
            engine = call.engine
            delivery = call.draft()
            call.receive()
            self.assertEqual(call.receipt(delivery['request_id'])['state'], 'accepted')
            head, _, runtime = engine.store.load()
            self.assertEqual(engine._submission_check_summary(head, runtime)['status'], 'verified')
            for case, reason in (
                    ('native', 'native check event differs from its execution'),
                    ('target', 'central check event differs from its receipt'),
                    ('intent', 'saved accepted submission has no matching central check evidence')):
                broken = deepcopy(runtime)
                event = next(row for row in broken['events'] if row['kind'] == 'submission_checked'
                             and row['target'] == call.execution_id)
                if case == 'native':
                    receipt = deepcopy(broken['control_receipts'][event['source_ref']])
                    event.setdefault('basis', {}).update(origin='native_final', receipt=receipt)
                elif case == 'target': event['target'] = 'EX-other'
                else:
                    broken['executions'][call.execution_id]['submission_intent']['check_ref'] = 'runtime/artifacts/BA-other/check.json'
                with self.subTest(case=case):
                    summary = engine._submission_check_summary(head, broken)
                    self.assertEqual((summary['status'], summary['error']), ('incomplete', reason))
                    self.assertEqual(engine.store.load()[2], runtime)

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
    def test_preview_rechecks_pause_authority_clock_and_workspace_input(self):
        from datetime import timedelta
        from do_math.control_protocol import SUBMISSION_PREVIEW
        sim = Sim.activated()
        with running_work(sim) as call:
            engine = call.engine
            request = {**call.binding, 'request_id': 'preview-guard', 'kind': SUBMISSION_PREVIEW,
                       'payload': {'draft_path': 'absent.json'}}
            before_i, before_r = deepcopy(engine.instance), deepcopy(engine.runtime)
            for case, reason in [('pause', 'the current pause does not authorize this recovery'),
                    ('grant', 'execution authority no longer permits this request'),
                    ('input', 'preview input or authority could not be verified'),
                    ('clock', 'clock regression prevents new acceptance')]:
                engine.instance, engine.runtime = deepcopy(before_i), deepcopy(before_r)
                if case == 'pause': engine.runtime['status'] = 'paused'
                elif case == 'grant': engine.instance['grants'][call.binding['grant_id']]['status'] = 'revoked'
                elif case == 'input': del call.execution['input_bundle']
                elif case == 'clock': sim.clock.set_wall(sim.clock.wall() - timedelta(seconds=60))
                state = deepcopy((engine.head, engine.instance, engine.runtime))
                with self.subTest(case=case):
                    self.assertEqual(engine._publish_control_request(request), {'state': 'rejected', 'reason': reason})
                    self.assertEqual((engine.head, engine.instance, engine.runtime), state)
            engine.instance, engine.runtime = before_i, before_r

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
                with self.assertRaisesRegex(GitStateStoreError, '^state ref points to an unreadable object$'):
                    call.receive()
            finally:
                ref.write_bytes(original)
            receipt = call.receipt(delivery['request_id'])
            self.assertIsNone(receipt, 'an unreadable head cannot establish a final delivery outcome')
            self.assertEqual(engine.head, head)
            self.assertEqual(call.tracker.control_requests, {})
            self.assertEqual(call.tracker.obligations[obligation['id']]['status'], 'open')
            call.receive()
            self.assertEqual(call.receipt(delivery['request_id'])['state'], 'accepted')




class BoundRequestRejectionTests(unittest.TestCase):
    def test_two_transports_collide_in_both_orders_without_reapplying_or_blocking_publication(self):
        import hashlib
        import json
        from pathlib import Path
        from do_math.control_transport import ControlTransport
        reason = 'safe boundary call IDs must identify observed calls of this execution'
        reused = 'request_id was reused with different content'
        for first in (0, 1):
            with self.subTest(first=first), running_work(Sim.activated()) as call:
                engine = call.engine
                bindings = [call.binding, engine._transport.issue(call.execution_id,
                            call.binding['grant_id'], workspace=call.workspace)]
                requests, paths, originals = [], [], []
                for index, binding in enumerate(bindings):
                    ControlTransport.worker_submit(binding, request_id='RQ-shared', kind='safety_boundary',
                        payload={'inflight_calls': False, 'call_ids': [f'foreign-{index}']})
                    path = Path(binding['endpoint']) / 'inbox' / 'RQ-shared.json'
                    paths.append(path)
                    originals.append(path.read_bytes())
                    requests.append(json.loads(originals[-1]))
                # receive first explicitly; sorted/random endpoint names cannot choose the order for us.
                before = deepcopy((engine.head, engine.instance, engine.runtime))
                captured = []
                with published(engine, captured) as calls:
                    receipt = engine._transport.receive(requests[first], publish=engine._publish_control_request)
                    self.assertEqual((receipt['state'], receipt['reason']), ('rejected', reason))
                    self.assertEqual(engine._transport.receive(requests[first],
                        publish=engine._publish_control_request), receipt)
                    with self.assertRaisesRegex(ValueError, '^' + reused + '$'):
                        engine._transport.receive(requests[1-first], publish=engine._publish_control_request)
                    fresh = ControlTransport(engine._transport.root, clock=engine.ports.clock)
                    rows = fresh.pump(engine._publish_control_request)
                    conflicting = ControlTransport.worker_receipt(bindings[1-first], 'RQ-shared')
                    self.assertEqual(conflicting, {'request_id': 'RQ-shared', 'state': 'rejected',
                        'stage': 'delivery_validation', 'reason': reused,
                        'source': 'inbox/RQ-shared.json',
                        'source_sha256': hashlib.sha256(originals[1-first]).hexdigest(),
                        'source_bytes': len(originals[1-first])})
                    self.assertEqual(ControlTransport.worker_receipt(bindings[first], 'RQ-shared'), receipt)
                    self.assertEqual(calls.count('publish'), 1)
                    self.assertEqual(calls.count('save'), 0)
                    self.assertEqual((engine.head, engine.instance, engine.runtime), before)
                    self.assertEqual([path.read_bytes() for path in paths], originals)
                    self.assertEqual(fresh.pump(engine._publish_control_request), rows)
                    self.assertEqual(ControlTransport(engine._transport.root, clock=engine.ports.clock).pump(
                        engine._publish_control_request), rows)
                    delivery = call.draft()
                    call.receive()
                    accepted = call.receipt(delivery['request_id'])
                    self.assertEqual(accepted['state'], 'accepted')
                    self.assertEqual(accepted['snapshot'], engine.head)
                    after = deepcopy((engine.head, engine.instance, engine.runtime))
                    call.receive()
                    self.assertEqual((engine.head, engine.instance, engine.runtime), after)
                    self.assertEqual(calls.count('save'), 1)
                    self.assertEqual(calls.count('publish'), 2)
                _, stored_instance, stored = engine.store.load()
                self.assertEqual((stored_instance, stored), (engine.instance, engine.runtime))
                added = [r for r in stored['control_receipts'].values()
                         if r['request_id'] == delivery['request_id']]
                self.assertEqual(len(added), 1)
                self.assertFalse(any(r['request_id'] == 'RQ-shared' for r in stored['control_receipts'].values()))
                self.assertEqual(stored['executions'][call.execution_id]['status'], 'stopping')

    def test_workspace_draft_paths_reject_exactly_and_a_later_draft_is_published(self):
        from support.ingress import NOT_TEXTS, PATHS
        from do_math.control_transport import ControlTransport
        with running_work(Sim.activated()) as call:
            before = deepcopy((call.engine.head, call.engine.instance, call.engine.runtime))
            cases = [(value, 'submission requires a workspace-relative draft_path') for value in NOT_TEXTS]
            for index, (value, reason) in enumerate(cases):
                with self.subTest(path=value):
                    rid = f'RQ-draft-path-{index}'
                    call.submit('submit_intent', {'draft_path': value}, rid)
                    call.receive()
                    receipt = call.receipt(rid)
                    self.assertEqual((receipt['state'], receipt['reason']), ('rejected', reason))
                    self.assertEqual((call.engine.head, call.engine.instance, call.engine.runtime), before)
            fresh = ControlTransport(call.engine._transport.root, clock=call.engine.ports.clock)
            receipts = fresh.pump(call.engine._publish_control_request)
            self.assertEqual(len(receipts), len(cases))
            self.assertEqual((call.engine.head, call.engine.instance, call.engine.runtime), before)
            for index, value in enumerate(PATHS):
                with self.subTest(path=value):
                    domain_before = deepcopy((call.engine.instance, call.execution,
                        call.engine.runtime['queue'], call.engine.runtime['reservations']))
                    rid = f'RQ-invalid-path-{index}'
                    call.submit('submit_intent', {'draft_path': value}, rid)
                    call.receive()
                    receipt = call.receipt(rid)
                    self.assertEqual((receipt['state'], receipt['reason']),
                                     ('rejected', 'candidate validation failed'))
                    check = receipt['result']
                    self.assertEqual((check['passed'], check['capture_eligible']), (False, False))
                    issue, = check['issues']
                    self.assertEqual(issue['rule_id'], 'submission.read')
                    self.assertEqual(issue['message'], 'unsafe relative path: .' if value == ''
                                     else 'submission draft must be inside this workspace')
                    self.assertEqual((call.engine.instance, call.execution, call.engine.runtime['queue'],
                                      call.engine.runtime['reservations']), domain_before)
            rejected = deepcopy((call.engine.head, call.engine.instance, call.engine.runtime))
            ControlTransport(call.engine._transport.root, clock=call.engine.ports.clock).pump(
                call.engine._publish_control_request)
            self.assertEqual((call.engine.head, call.engine.instance, call.engine.runtime), rejected)
            delivery = call.draft()
            call.receive()
            self.assertEqual(call.receipt(delivery['request_id'])['state'], 'accepted')
            self.assertEqual(call.engine.store.load()[2]['executions'][call.execution_id]['status'], 'stopping')

    def test_missing_draft_and_foreign_tool_boundary_do_not_change_the_execution(self):
        from do_math.control_protocol import SUBMIT_INTENT, SAFETY_BOUNDARY
        with running_work(Sim.activated()) as call:
            for kind, payload, rid, reason in (
                (SUBMIT_INTENT, {}, 'missing-draft',
                 'submission requires a workspace-relative draft_path'),
                (SAFETY_BOUNDARY, {'inflight_calls': False, 'call_ids': ['unobserved-call']},
                 'foreign-boundary', 'safe boundary call IDs must identify observed calls of this execution'),
            ):
                with self.subTest(kind=kind):
                    before = deepcopy((call.engine.head, call.execution,
                                       call.engine.runtime.get('control_receipts', {})))
                    call.submit(kind, payload, rid)
                    call.receive()
                    receipt = call.receipt(rid)
                    self.assertEqual((receipt['state'], receipt['reason']), ('rejected', reason))
                    self.assertEqual((call.engine.head, call.execution,
                                      call.engine.runtime.get('control_receipts', {})), before)
            # A malformed request cannot poison a later normal, bound submission.
            delivery = call.draft()
            call.receive()
            receipt = call.receipt(delivery['request_id'])
            self.assertEqual(receipt['state'], 'accepted')
            stored = call.engine.store.load(call.engine.head)[2]
            accepted = [r for r in stored['control_receipts'].values()
                        if r['execution_id'] == call.execution_id and r['kind'] == SUBMIT_INTENT]
            self.assertEqual(len(accepted), 1)
            self.assertEqual(accepted[0]['request_id'], delivery['request_id'])

    def test_repeated_stop_judgment_preserves_the_first_stop_time_and_checkpoint(self):
        from support.engine_lifecycle import applied
        sim = Sim.activated()
        with running_work(sim) as call:
            applied(sim, 'pause', text='stop the running bound call')
            self.assertIs(call.arguments['should_stop'](), True)
            row = deepcopy(call.execution)
            head = call.engine.head
            files = {str(p.relative_to(call.workspace)): p.read_bytes()
                     for p in (call.workspace / '.control').rglob('*') if p.is_file()}
            self.assertTrue(files)
            self.assertEqual(row['status'], 'stopping')
            self.assertIn('stop_observed_at', row)
            sim.advance(1)
            self.assertIs(call.arguments['should_stop'](), True)
            self.assertEqual(call.execution, row)
            self.assertEqual(call.engine.head, head)
            self.assertEqual({str(p.relative_to(call.workspace)): p.read_bytes()
                              for p in (call.workspace / '.control').rglob('*') if p.is_file()}, files)
            self.assertEqual(call.engine.store.load(head)[2]['executions'][call.execution_id], row)

    def test_self_check_response_must_name_the_obligation_in_its_delivery(self):
        from do_math.control_protocol import SELF_CHECK_RESPONSE
        with running_work(Sim.activated(), rules=CHECKPOINT_RULES) as call:
            obligation = due(call)
            response = self_check_response(obligation)
            response['obligation_id'] = 'SC-another-obligation'
            before = deepcopy((call.engine.head, call.engine.runtime))
            call.submit(SELF_CHECK_RESPONSE,
                        {'self_check_id': obligation['id'], 'response': response}, 'wrong-obligation')
            call.receive()
            receipt = call.receipt('wrong-obligation')
            self.assertEqual((receipt['state'], receipt['reason']),
                             ('rejected', 'self-check response refers to another issued obligation'))
            self.assertEqual((call.engine.head, call.engine.runtime), before)
            self.assertEqual(call.tracker.obligations[obligation['id']]['status'], 'open')
            delivery = call.self_check(obligation['id'], self_check_response(obligation))
            call.receive()
            self.assertEqual(call.receipt(delivery['request_id'])['state'], 'accepted')
            self.assertEqual(call.tracker.obligations[obligation['id']]['status'], 'answered')
class DeliveryFailureTests(unittest.TestCase):
    def test_feedback_file_failure_keeps_the_durable_receipt_and_retries_delivery(self):
        """T3 9.3 s: actual self-check publication separates durable acceptance from file delivery."""
        import json
        with running_work(Sim.activated(), rules=CHECKPOINT_RULES) as call:
            obligation = due(call)
            response = {**self_check_response(obligation), 'rule_proposal': {'current_revision': 0,
                'reason': 'Check again at the next attempt pair',
                'rules': [observation_rule(repeat_interval=2, required_evidence=['workspace:checkpoint.json'])]}}
            destination = call.workspace / '.control' / 'observation-feedback.json'
            destination.mkdir()
            delivery = call.self_check(obligation['id'], response)
            call.receive()
            receipt = call.receipt(delivery['request_id'])
            self.assertEqual(receipt['state'], 'accepted', receipt)
            identifier = receipt['publication_id']
            stored = deepcopy(call.engine.store.load()[2]['control_receipts'][identifier])
            failure, = [row for row in call.engine.runtime['history']
                        if row.get('kind') == 'feedback_delivery_failed' and row.get('receipt_id') == identifier]
            self.assertTrue(failure['error'])
            call.engine._upkeep(schedule_reviews=False)
            self.assertNotIn(identifier, call.engine._feedback_delivered)
            self.assertEqual(call.engine.store.load()[2]['control_receipts'][identifier], stored)
            destination.rmdir()
            call.engine._upkeep(schedule_reviews=False)
            self.assertIn(identifier, call.engine._feedback_delivered)
            feedback = json.loads(destination.read_bytes())
            self.assertEqual((feedback['kind'], feedback['active_revision']), ('observation_rules_accepted', 1))
            self.assertEqual(call.engine.store.load()[2]['control_receipts'][identifier], stored)
            self.assertEqual(call.tracker.obligations[obligation['id']]['status'], 'answered')

    def test_unobserved_execution_accepts_a_boundary_but_rejects_a_self_check(self):
        """T3 7.3 s: a real restart retains the issued request and loses the old owner's tracker."""
        from do_math.control_protocol import SAFETY_BOUNDARY, SELF_CHECK_RESPONSE
        from support.submission_receiver import history
        scene = history()
        engine = scene.engine
        boundary = {**scene.binding, 'request_id': 'boundary-without-tracker', 'kind': SAFETY_BOUNDARY,
                    'payload': {'inflight_calls': False, 'call_ids': []}}
        receipt = scene.transport.receive(boundary, publish=engine._publish_control_request)
        self.assertEqual(receipt['state'], 'accepted', receipt)
        report = engine.runtime['executions'][scene.execution_id]['safe_boundary_report']
        self.assertEqual(report, {'receipt_id': receipt['publication_id'], 'inflight_calls': False, 'call_ids': []})
        self.assertEqual(engine.store.load()[2]['executions'][scene.execution_id]['safe_boundary_report'], report)
        # The old owner's issued request survives on the delivery surface, while
        # a restarted owner's in-memory tracker does not survive.
        sim = Sim.activated()
        with running_work(sim, rules=CHECKPOINT_RULES) as call:
            obligation = due(call)
            response = self_check_response(obligation)
            transport = call.engine._transport
            request = {**call.binding, 'request_id': 'self-check-without-tracker', 'kind': SELF_CHECK_RESPONSE,
                       'payload': {'self_check_id': response['obligation_id'], 'response': response}}
            sim.restart()
            engine = sim.engine
            self.assertEqual(engine._trackers, {})
            before = deepcopy((engine.head, engine.instance, engine.runtime))
            rejected = transport.receive(request, publish=engine._publish_control_request)
            self.assertEqual((rejected['state'], rejected['reason']), ('rejected', 'self-check has no current tracker'))
            self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_a_self_check_poll_checkpoint_is_preserved_without_counting_new_research(self):
        """T3 5.0 s: an observed control poll fixes the checkpoint's actual self-check lineage."""
        from do_math.control_protocol import CONTROL_SERVER, SELF_CHECK_TOOL
        import hashlib
        with running_work(Sim.activated(), rules=CHECKPOINT_RULES) as call:
            obligation = due(call)
            count, counters = call.tracker.checkpoint_count, deepcopy(call.tracker.counters)
            call.observe({'type': 'item.started', 'item': {'id': 'self-check-poll', 'type': 'mcp_tool_call',
                'server': CONTROL_SERVER, 'tool': SELF_CHECK_TOOL, 'arguments': {'self_check_id': obligation['id']}}})
            write_checkpoint(call.workspace, counters={'attempts': 3})
            raw = (call.workspace / 'checkpoint.json').read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            call.observe({'type': 'tick'})
            self.assertIn(digest, call.tracker.self_check_checkpoints)
            self.assertEqual((call.tracker.checkpoint_count, call.tracker.counters), (count, counters))
            stored = call.engine.store.load()[2]['checkpoints'][call.execution_id]
            self.assertEqual(stored['sha256'], digest)
            self.assertEqual(call.engine.store.read(stored['artifact_ref'], call.engine.head), raw)

if __name__ == '__main__':
    unittest.main()

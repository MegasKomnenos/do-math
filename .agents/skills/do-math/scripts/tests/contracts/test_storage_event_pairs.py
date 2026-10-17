"""Five event/receipt storage families: real producers, cold decode and content."""
from copy import deepcopy
from functools import cache
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import assert_pair
from do_math.state_contract import StateContract, default_state_contract
from support.storage_event_pairs import (FAMILIES, family_pair, lifecycle_samples,
    control_samples, bundle_samples, external_samples, trust_samples, digest, reader)


class EventStoragePairs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.addClassCleanup(cls._prepare.cache_clear)

    @classmethod
    @cache
    def _prepare(cls):
        # These real product scenes belong to the selected test consumer.
        cls.life, life, cls.due = lifecycle_samples(Path(cls.directory.name) / 'lifecycle')
        cls.bundle, bundles = bundle_samples()
        cls.external, external, cls.evidence = external_samples()
        cls.trust, trust, cls.transition = trust_samples()
        # Sim's activation template restores one fixed live path. Finish the
        # bundle scene before restoring control there; lifecycle owns its root.
        cls.control, controls, cls.requests = control_samples()
        cls.samples = life + controls + bundles + external + trust

    def test_all_five_families_receive_real_publications_and_write_every_field(self):
        self._prepare()
        for family in FAMILIES:
            with self.subTest(family=family):
                assert_pair(self, family_pair(default_state_contract(), family, self.samples), self.samples)

    def test_exact_event_content_sequence_pending_and_open_evidence(self):
        self._prepare()
        for branch, runtime in self.samples:
            with self.subTest(branch=branch):
                rows = runtime['events']
                self.assertEqual([r['event_seq'] for r in rows], list(range(1, len(rows) + 1)))
                self.assertEqual(runtime['event_cursor'], len(rows))
                self.assertEqual(len(runtime['pending_events']), len(set(runtime['pending_events'])))
                self.assertTrue(set(runtime['pending_events']) <= {r['id'] for r in rows})
        runtime = self.external.runtime
        reconciled, = [r for r in runtime['events'] if r['kind'] == 'external_operation_reconciled']
        confirmed, = [r for r in runtime['events'] if r['kind'] == 'external_operation_confirmed']
        retried, = [r for r in runtime['events'] if r['kind'] == 'external_operation_retry_prepared']
        self.assertEqual(reconciled['evidence'], self.evidence)
        self.assertEqual((reconciled['outcome'], retried['previous_status']), ('failed', 'failed'))
        operation = runtime['external_operations'][confirmed['target']]
        self.assertEqual(confirmed['request_sha256'], operation['request_sha256'])
        self.assertEqual(confirmed['source_ref'], operation['source_ref'])
        stopped, = [r for r in self.trust.runtime['events'] if r['kind'] == 'trust_target_stopped']
        self.assertEqual(stopped['transition_id'], self.transition)
        execution = self.trust.runtime['executions'][stopped['execution_id']]
        self.assertEqual(stopped['artifact_ref'], execution['result_ref'])
        import json
        raw = self.trust.engine.store.read(stopped['artifact_ref'], self.trust.engine.head)
        self.assertEqual(json.loads(raw)['status'], 'stopped')
        audit, = [r for r in self.life.runtime['events'] if r['kind'] == 'goal_audit_completed']
        self.assertEqual(audit['judgment_ids'], sorted(j['id'] for j in self.life.instance['goal_judgments']))
        self.assertEqual(audit['basis_sha256'], self.life.engine._goal_basis_key())
        self.assertEqual((audit['outcome'], audit['next_owner']), ('not_established', 'research_plan'))
        exhausted = [r for _, runtime in self.samples for r in runtime['events'] if r['kind'] == 'research_exhausted']
        self.assertTrue(exhausted)
        for event in exhausted:
            self.assertEqual(event['basis_sha256'], digest(event['basis']))
        for event in self.life.runtime['events']:
            if 'opened_at' in event:
                self.assertEqual(event['opened_at'], event['at'])
            if event['kind'].startswith('conversation_'):
                self.assertEqual((event['target'], event['generation']), ('event-lease', 1))
                if event['kind'] == 'conversation_lost':
                    self.assertEqual(event['reason'], 'explicit_detach')
            if event['kind'] == 'user_decision_applied':
                self.assertEqual(self.life.instance['decisions'][event['decision_id']]['source_ref'], event['source_ref'])
            if event['kind'] == 'task_readiness_lost':
                from do_math.planning import CONTRACT_REVIEW_MISSING
                self.assertEqual(event['errors'], [CONTRACT_REVIEW_MISSING])
                self.assertEqual(event['basis'], {'dispatch_occupied': False})
        unsealed, = [r for r in self.bundle.engine.runtime['events'] if r['kind'] == 'submission_unsealed']
        self.assertEqual(unsealed['execution_id'], self.bundle.execution_id)
        self.assertEqual(unsealed['evidence_refs'], [self.bundle.engine.runtime['executions'][self.bundle.execution_id]['submission_check_ref']])
        self.assertEqual(unsealed['reason'], 'worker output did not pass through the central submit capture')

    def test_receipts_preserve_safe_requests_submission_artifacts_and_parent(self):
        self._prepare()
        engine = self.control.engine
        rows = engine.runtime['control_receipts']
        self.assertEqual({r['state'] for r in rows.values()}, {'accepted', 'rejected'})
        for request in self.requests:
            matches = [r for r in rows.values() if r['request_id'] == request['request_id']]
            if request['kind'] == 'submission_preview':
                self.assertEqual(matches, [])
                continue
            receipt, = matches
            safe = {k: v for k, v in request.items() if k != 'capability'}
            self.assertIn('capability', request)
            self.assertEqual(receipt['request'], safe)
            self.assertEqual(receipt['request_sha256'], digest(safe))
            self.assertEqual((receipt['execution_id'], receipt['kind']), (request['execution_id'], request['kind']))
            self.assertEqual(receipt['received_at'], self.control.clock.now())
            parent = reader(engine).load(receipt['parent_snapshot'])[2]
            self.assertNotIn(receipt['id'], parent.get('control_receipts', {}))
            if receipt['kind'] == 'submit_intent':
                self.assertEqual(receipt['payload']['origin'], 'explicit_tool')
                import hashlib
                for artifact in receipt['payload']['submission_check']['artifacts']:
                    raw = engine.store.read(artifact['path'], engine.head)
                    self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
                                     (artifact['bytes'], artifact['sha256']))
            else:
                self.assertNotIn('payload', receipt)

    def test_core_integrations_bind_exact_output_members_and_fixed_input(self):
        self._prepare()
        scene = self.bundle
        receipts = scene.engine.runtime['integrations']
        self.assertTrue({'IN-A', 'IN-B'} <= set(receipts))
        output = {k: v for k, v in scene.output.items()
                  if k not in {'integration_bundles', 'repair_responses', 'knowledge', 'relations'}}
        # The split producer hashes only the values owned by each declaration.
        for declaration in scene.output['integration_bundles']:
            ident = declaration['integration_id']
            receipt = receipts[ident]
            values = {}
            for coordinate in declaration['members']:
                values[coordinate] = output if coordinate == 'output' else scene.output['knowledge'][int(coordinate.rsplit('/', 1)[1])]
            self.assertEqual(receipt['payload_sha256'], digest({'declaration': declaration, 'values': values}))
            self.assertEqual(receipt['members'], declaration['members'])
            self.assertEqual((receipt['execution_id'], receipt['input_snapshot']),
                             (scene.execution_id, scene.context['snapshot']))
            if 'output' in declaration['members']:
                self.assertEqual(receipt['response_sha256'], digest(output))
            else:
                self.assertNotIn('response_sha256', receipt)

    def test_unproduced_optional_is_detected_on_same_reverse_walk(self):
        self._prepare()
        for family in FAMILIES:
            definition = default_state_contract().family('runtime', family)
            if family in {'pending_events', 'event_cursor'}:
                pair = family_pair(default_state_contract(), family, self.samples)
                self.assertEqual(pair.fields, frozenset({'/value'}))
                continue
            schema = deepcopy(definition.schema)
            schema['properties']['unproduced_optional'] = {'type': 'string'}
            contract = StateContract()
            contract.register_family('runtime', family, shape=definition.shape,
                schema=schema, validator=definition.validator, references=definition.references,
                identity=definition.identity)
            with self.subTest(family=family), self.assertRaisesRegex(AssertionError, 'unproduced_optional'):
                assert_pair(self, family_pair(contract, family, self.samples), self.samples)

    def test_removed_fields_and_nonreference_pending_are_refused_before_publication(self):
        self._prepare()
        engine = self.control.engine
        before = engine.store.load(engine.head)
        removed = {
            'events': ('created_at', 'actor_ref', 'record_refs', 'activity_id', 'from', 'to', 'status',
                'affected_ids', 'environment_id', 'execution_ids', 'task_ids', 'revision', 'detail', 'scope', 'affected'),
            'control_receipts': ('grant_id', 'snapshot', 'publication_id', 'payload_sha256', 'transport_id')}
        for family, fields in removed.items():
            for field in fields:
                runtime = deepcopy(before[2])
                if family == 'events':
                    row = deepcopy(runtime['events'][-1])
                    row.pop('event_seq')
                    row['id'] = 'EV-removed-field'
                    runtime['events'].append(row)
                else:
                    row = next(iter(runtime[family].values()))
                row[field] = 'unused'
                with self.subTest(family=family, field=field), self.assertRaisesRegex(
                        ValueError, 'Additional properties are not allowed.*' + field):
                    engine.store.save_with_state(engine.head, before[1], runtime)
                self.assertEqual(engine.store.load(), before)
        for value in ([{'id': before[2]['events'][0]['id']}], [0], ['EV-unknown']):
            runtime = deepcopy(before[2])
            runtime['pending_events'] = value
            reason = 'references unknown event' if value == ['EV-unknown'] else 'requires distinct event references'
            with self.subTest(pending=value), self.assertRaisesRegex(ValueError, reason):
                engine.store.save_with_state(engine.head, before[1], runtime)
            self.assertEqual(engine.store.load(), before)

    def test_consumption_keeps_later_input_and_unselected_pending_then_survives_reload(self):
        self._prepare()
        from support.storage_event_pairs import keep
        engine = self.life.engine
        event = next(r for r in engine.runtime['events'] if r['kind'] == 'task_new_input')
        original = deepcopy(engine.runtime['events'])
        pending = list(engine.runtime['pending_events'])
        task = engine.runtime['tasks'][event['target']]
        task['newinput'] = 'RQ-later'
        engine._consume_action_events({'event_refs': [event['id']]}, 'AUDITOR')
        self.assertEqual(task['newinput'], 'RQ-later')
        self.assertEqual(engine.runtime['pending_events'], [ref for ref in pending if ref != event['id']])
        history = engine.runtime['history'][-1]
        self.assertEqual(history, {'kind': 'event_consumption', 'event_ids': [event['id']],
            'execution_id': 'AUDITOR', 'consumed_at': self.life.clock.now()})
        task['newinput'] = event['request_id']
        engine._consume_action_events({'event_refs': [event['id']]}, 'AUDITOR')
        self.assertNotIn('newinput', task)
        engine._save()
        restored = keep(engine, [], 'consumed')
        self.assertEqual(restored['events'], original)
        self.assertNotIn(event['id'], restored['pending_events'])


if __name__ == '__main__':
    unittest.main()

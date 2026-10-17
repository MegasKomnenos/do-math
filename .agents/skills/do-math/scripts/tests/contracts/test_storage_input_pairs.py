"""Stored source/input/held-extension values: fields and independent contents."""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import assert_pair
from do_math.canonical import exact_content_hash
from do_math.knowledge_records import proposal_view
from do_math.state_contract import StateContract, default_state_contract
from support.storage_input_pairs import (FAMILIES, family_pair, keep,
    pending_kind_scene, public_input_samples, reader, review_insight_scene)
from support.storage_kind_checks import kind_checker


class StorageInputPairTests(unittest.TestCase):
    def test_public_sources_and_inputs_preserve_original_bytes_order_and_heads(self):
        """About 3.5 s: two public initializations, source/input CAS and a cold restart."""
        with tempfile.TemporaryDirectory() as directory:
            sim, samples, name, raw, requests = public_input_samples(Path(directory))
            for root, family in FAMILIES[:2]:
                assert_pair(self, family_pair(default_state_contract(), root, family, samples), samples)
            by_name = dict(samples)
            self.assertEqual(by_name['empty sources and initial input'][0]['sources'], [])
            first, = by_name['initial file'][0]['sources']
            self.assertEqual((first['name'], first['sha256'], first['bytes']),
                             (name, hashlib.sha256(raw).hexdigest(), len(raw)))
            self.assertEqual(reader(sim.engine).read(first['path'], sim.engine.head), raw)
            self.assertEqual(by_name['same initial bytes'][0]['sources'], [first])
            changed, = by_name['changed bytes'][0]['sources']
            self.assertEqual((changed['id'], changed['revision'], changed['history'], changed['status']),
                             (first['id'], 2, [first], 'active'))
            self.assertTrue(changed['path'].endswith('/source.bin'))
            self.assertEqual(changed['source_ref'], requests[1][1]['request_id'])
            self.assertEqual((changed['bytes'], changed['sha256']),
                (len(raw + b'next\r\n'), hashlib.sha256(raw + b'next\r\n').hexdigest()))
            self.assertEqual(reader(sim.engine).read(changed['path'], sim.engine.head), raw + b'next\r\n')
            self.assertEqual(by_name['same changed bytes'][0]['sources'], [changed])
            added = by_name['new source'][0]['sources'][-1]
            self.assertEqual((added['name'], added['revision'], added['status']), ('추가.bin', 1, 'active'))
            self.assertNotIn('history', added)
            self.assertEqual(reader(sim.engine).read(added['path'], sim.engine.head), b'\x80\x00new\r\n')
            inputs = samples[-1][1][1]['inputs']
            self.assertEqual(len(inputs), 3)
            original = '최초 e\u0301\r\n입력\n'
            self.assertEqual((inputs[0]['text'], inputs[0]['config'], inputs[0]['sha256']),
                (original, {'goal': original}, hashlib.sha256(original.encode('utf-8')).hexdigest()))
            self.assertTrue(inputs[0]['id'].startswith('UI-'))
            self.assertEqual(inputs[0]['created_at'], samples[-1][1][0]['created_at'])
            later = [r for r in requests if r[0] == 'input']
            for record, (_, envelope, (text, config)) in zip(inputs[1:], later):
                self.assertEqual((record['id'], record['text'], record['config'], record['origin'],
                                  record['instance_id'], record['action']),
                                 (envelope['request_id'], text, config, 'user', sim.instance_id, 'input'))
                self.assertEqual(record['created_at'], sim.clock.now())
                self.assertNotIn('sha256', record)
            self.assertLess(inputs[1]['accepted_order'], inputs[2]['accepted_order'])
            self.assertEqual(by_name['replayed and restarted'][1]['inputs'], inputs[:2])
            self.assertOptionalDrift(samples, FAMILIES[:2])
            self.assertRemovedField(sim.engine, 'research', 'sources', 'created_at')

    def assertOptionalDrift(self, samples, families):
        for root, name in families:
            definition = default_state_contract().family(root, name)
            schema = deepcopy(definition.schema)
            if name == 'private_insights':
                self.assertEqual(family_pair(default_state_contract(), root, name, samples).fields,
                                 frozenset({'/value'}))
                continue  # Arbitrary map/item content has no closed named-field inventory.
            target = schema['items'] if name == 'pending_kind_checks' else schema
            target['properties']['unproduced_optional'] = {'type': 'string'}
            contract = StateContract()
            contract.register_family(root, name, shape=definition.shape, schema=schema,
                validator=definition.validator, identity=definition.identity, references=definition.references)
            with self.subTest(family=name), self.assertRaisesRegex(AssertionError, 'unproduced_optional'):
                assert_pair(self, family_pair(contract, root, name, samples), samples)

    def test_pending_kind_items_are_checked_and_only_the_exact_definition_is_resolved(self):
        """About 6.3 s: three independent verdicts with validated publications and cold decodes."""
        for verdict in ('approved', 'revision_required', 'unresolved'):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as directory:
                sim, samples, proposed = pending_kind_scene(Path(directory))
                engine = sim.engine
                assert_pair(self, family_pair(default_state_contract(), 'runtime', 'pending_kind_checks', samples), samples)
                self.assertOptionalDrift(samples, FAMILIES[3:])
                self.assertRemovedField(engine, 'runtime', 'pending_kind_checks', 'execution_id')
                original = deepcopy(engine.runtime['pending_kind_checks'])
                self.assertEqual(len(original), 2)
                for pending, source in zip(original, proposed):
                    self.assertEqual({k: pending[k] for k in ('family', 'token')},
                                     {k: source[k] for k in ('family', 'token')})
                    self.assertEqual((pending['source_ref'], pending['actor_ref']), ('EX-kind-author', 'EX-kind-author'))
                action = next(a for a in engine.runtime['queue'] if a.get('kind_definition_id') == original[0]['definition_id'])
                checker, definition = kind_checker(engine, action, 'EX-kind-reader')
                self.assertEqual(action['kind_definition_sha256'], exact_content_hash(definition))
                self.assertEqual({key: definition[key] for key in proposed[0]}, proposed[0])
                output = dict(definition_id=definition['id'], definition_sha256=exact_content_hash(definition),
                              decision=verdict, findings=[] if verdict == 'approved' else ['명시적 검토 근거 e\u0301'])
                before = deepcopy((engine.head, engine.instance, engine.runtime))
                for changes in ({'definition_id': original[1]['definition_id']}, {'definition_sha256': '0' * 64}):
                    with self.assertRaisesRegex(ValueError, '^kind checker did not read the current exact definition$'):
                        engine._apply_kind_definition_check(action, {**output, **changes}, checker['id'])
                    self.assertEqual((engine.head, engine.instance, engine.runtime), before)
                with self.assertRaisesRegex(ValueError, 'independent|author'):
                    engine._apply_kind_definition_check(action, output, 'EX-kind-author')
                self.assertEqual((engine.head, engine.instance, engine.runtime), before)
                checker['input_basis']['kind_definition']['sha256'] = '0' * 64
                bad = deepcopy((engine.head, engine.instance, engine.runtime))
                with self.assertRaisesRegex(ValueError, '^kind checker did not read the current exact definition$'):
                    engine._apply_kind_definition_check(action, output, checker['id'])
                self.assertEqual((engine.head, engine.instance, engine.runtime), bad)
                checker['input_basis']['kind_definition']['sha256'] = output['definition_sha256']
                engine.instance['kind_definitions'][definition['id']]['meaning'] += ' changed'
                bad = deepcopy((engine.head, engine.instance, engine.runtime))
                with self.assertRaisesRegex(ValueError, '^kind checker did not read the current exact definition$'):
                    engine._apply_kind_definition_check(action, output, checker['id'])
                self.assertEqual((engine.head, engine.instance, engine.runtime), bad)
                engine.instance['kind_definitions'][definition['id']]['meaning'] = definition['meaning']
                engine._apply_kind_definition_check(action, output, checker['id'])
                previous = reader(engine).load(engine.head)
                engine._save()
                keep(engine, samples, verdict, previous=previous)
                self.assertEqual(engine.runtime['pending_kind_checks'], [original[1]])
                installed = reader(engine).load(engine.head)[1]['kind_definitions'][definition['id']]
                self.assertEqual(installed['status'], {'approved': 'active', 'revision_required': 'withdrawn',
                                                      'unresolved': 'candidate'}[verdict])
                self.assertEqual(installed['check'], {**output, 'execution_id': checker['id']})
                if verdict == 'approved':
                    self.assertEqual((installed['checked_by'], installed['activated_by']), (checker['id'], checker['id']))
                else:
                    self.assertTrue(any(a['role'] == 'research_preparation' and a.get('kind_definition_id') == definition['id']
                                        for a in engine.runtime['queue']))
                remaining = next(a for a in engine.runtime['queue'] if a.get('kind_definition_id') == original[1]['definition_id'])
                checker, definition = kind_checker(engine, remaining, 'EX-kind-second-reader')
                engine._apply_kind_definition_check(remaining, {
                    'definition_id': definition['id'], 'definition_sha256': exact_content_hash(definition),
                    'decision': 'approved', 'findings': []}, checker['id'])
                engine._save()
                keep(engine, samples, 'no pending definitions')
                self.assertEqual(engine.runtime['pending_kind_checks'], [])
                assert_pair(self, family_pair(default_state_contract(), 'runtime', 'pending_kind_checks', samples), samples)

    def test_review_insights_stay_private_then_release_in_author_order_and_leave_other_cycle(self):
        """About 40 s: two complete registered review scenes and ten validated/cold publications."""
        for unresolved in (False, True):
            with self.subTest(unresolved=unresolved), tempfile.TemporaryDirectory() as directory:
                engine, samples, primary, other, authored, identifiers = review_insight_scene(Path(directory), unresolved=unresolved)
                assert_pair(self, family_pair(default_state_contract(), 'runtime', 'private_insights', samples), samples)
                self.assertOptionalDrift(samples, FAMILIES[2:3])
                first, second, last = identifiers
                held = dict(samples)[second]
                self.assertEqual(held[1]['private_insights'][primary],
                    [{'source_execution': first, **insight} for insight in authored[0][1]])
                self.assertEqual(held[1]['private_insights'][other],
                    [{'source_execution': second, **insight} for insight in authored[1][1]])
                titles = [row['title'] for row in held[0]['knowledge'].values() if 'title' in row]
                self.assertTrue(all(item['title'] not in titles for _, values in authored for item in values))
                self.assertNotIn(primary, engine.runtime['private_insights'])
                self.assertEqual(engine.runtime['private_insights'][other], held[1]['private_insights'][other])
                self.assertEqual(engine.runtime['review_cycles'][primary]['status'], 'unresolved' if unresolved else 'completed')
                expected = [(first, item) for item in authored[0][1]] + [(last, item) for item in authored[2][1]]
                released = {kid for kid, row in engine.instance['knowledge'].items()
                            if row.get('producer_execution') in (first, last)}
                plan, = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan'
                         and released.intersection(a.get('evidence_refs', []))]
                self.assertIn('Incidental research knowledge is now available', plan['reasons'])
                records = [engine.instance['knowledge'][key] for key in plan['evidence_refs'] if key in released]
                for record, (author, original) in zip(records, expected):
                    proposal = proposal_view(engine.instance, record['id'])
                    self.assertEqual((record['origin_refs'], record['producer_execution']), ([author], author))
                    for field in ('kind', 'title', 'statement', 'summary'):
                        self.assertEqual(proposal[field], original[field])
                self.assertEqual(len(records), len(expected))

    def test_current_kind_withdrawal_does_not_attribute_old_insights_to_the_releasing_reviewer(self):
        """About 20 s: current kind withdrawal during a real cycle, not an obsolete held fixture."""
        with tempfile.TemporaryDirectory() as directory:
            engine, samples, primary, other, authored, identifiers = review_insight_scene(
                Path(directory), withdraw_held=True)
            first, second, last = identifiers
            rejected = [row for row in engine.runtime['history'] if row.get('kind') == 'incidental_insight_not_published']
            self.assertEqual([r['source_execution'] for r in rejected], [first, first])
            self.assertEqual([r['insight'] for r in rejected],
                             [{'source_execution': first, **item} for item in authored[0][1]])
            self.assertTrue(all(r['reason'] == 'unknown knowledge kind: observation' for r in rejected))
            self.assertNotIn(primary, engine.runtime['private_insights'])
            self.assertEqual(engine.runtime['private_insights'][other],
                             [{'source_execution': second, **item} for item in authored[1][1]])
            released = {kid for kid, row in engine.instance['knowledge'].items()
                        if row.get('producer_execution') == last}
            plan, = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan'
                     and released.intersection(a.get('evidence_refs', []))]
            record, = [engine.instance['knowledge'][kid] for kid in plan['evidence_refs'] if kid in released]
            self.assertEqual((record['producer_execution'], proposal_view(engine.instance, record['id'])['title']),
                             (last, authored[2][1][0]['title']))

    def assertRemovedField(self, engine, root, family, field):
        previous = reader(engine).load(engine.head)
        instance, runtime = deepcopy(previous[1:])
        row = (instance if root == 'research' else runtime)[family][0]
        row[field] = 'EX-unused' if field == 'execution_id' else engine.ports.clock.now()
        with self.assertRaisesRegex(ValueError, 'Additional properties are not allowed.*' + field):
            engine.store.save_with_state(engine.head, instance, runtime)
        self.assertEqual(reader(engine).load(), previous)


if __name__ == '__main__':
    unittest.main()

"""A rejected premature import approval must leave a storable owner state."""
from copy import deepcopy
import unittest

from support.governance_sim import approval, checked_bundle, checked_sim, returned


class ImportNullTests(unittest.TestCase):
    def test_unchecked_import_rejection_does_not_enqueue_a_null_check_execution(self):
        """Public rejection/restart and the retained check need real owner publications (Sim soft budget)."""
        sim = checked_sim()
        previous = checked_bundle(sim)
        author = sim.runtime['executions'][previous['execution_id']]['action']
        bundle = sim.engine._apply_governance_intent(author, deepcopy(previous['output']), previous['execution_id'])
        self.assertEqual(bundle['status'], 'checking')
        self.assertNotIn('check', bundle)
        pending = deepcopy(sim.runtime['queue'])
        self.assertTrue(any(a.get('import_id') == bundle['id'] and a.get('stage') == 'check' for a in pending))
        # Validate the actual producer's input state before the rejection.
        sim.engine.store.validate_candidate(sim.instance, sim.runtime)
        request = {'action': 'decision', 'config': {'change': {
            'kind': 'import_approval', 'import_id': bundle['id'],
            'bundle_sha256': bundle['sha256'], 'check_sha256': '0' * 64, 'unit_hashes': {}}}}
        with self.assertRaisesRegex(ValueError, '^approval does not name the exact sealed interpretation and check$'):
            sim.engine._governance_control(request)
        # The rejection is a normal domain outcome; it must remain publishable.
        sim.engine.store.validate_candidate(sim.instance, sim.runtime)
        self.assertEqual(sim.runtime['queue'], pending)
        sim.engine._save()
        control = sim.control('decision', text='Premature exact import approval', config=request['config'],
                              request_id='DC-premature')
        sim.engine.process_controls()
        result = sim.engine.control_result(control['request_id'])
        self.assertEqual((result['effect'], result['reason']),
                         ('rejected', 'approval does not name the exact sealed interpretation and check'))
        self.assertEqual(sim.runtime['queue'], pending)
        saved = deepcopy((sim.instance, sim.runtime))
        sim.restart()
        self.assertEqual((sim.instance, sim.runtime), saved)
        # Redelivery reuses the one rejection; it cannot create a reauthor.
        sim.control('decision', text='Premature exact import approval', config=request['config'],
                    request_id='DC-premature')
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(control['request_id']), result)
        self.assertEqual(sim.runtime['processed_controls'].count(control['request_id']), 1)
        self.assertEqual(sim.runtime['queue'], pending)
        # The actual pending independent check still runs, then exact approval works.
        sim.run_until(lambda s: s.runtime['intent_imports'][bundle['id']]['status'] == 'approved', max_steps=12)
        checked = sim.runtime['intent_imports'][bundle['id']]
        self.assertNotEqual(checked['check']['execution_id'], checked['execution_id'])
        control = sim.control('decision', text='Approve the now checked import', config={'change': approval(checked)})
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(control['request_id'])['effect'], 'applied')
        self.assertEqual(sim.runtime['intent_imports'][bundle['id']]['application']['status'], 'applied')

    def test_original_changed_before_first_check_queues_a_publishable_fresh_interpretation(self):
        """A restored active scene, changed original and persisted restart exceed the Sim soft budget."""
        sim = checked_sim()
        previous = checked_bundle(sim)
        author = sim.runtime['executions'][previous['execution_id']]['action']
        bundle = sim.engine._apply_governance_intent(author, deepcopy(previous['output']), previous['execution_id'])
        action = next(a for a in sim.runtime['queue'] if a.get('import_id') == bundle['id'])
        original = next(row for row in sim.runtime['inputs'] if row['id'] == bundle['input_ref'])
        original['text'] += ' with the updated original'
        before = deepcopy(sim.runtime['queue'])
        with self.assertRaisesRegex(ValueError, '^original source changed before independent check$'):
            sim.engine._apply_governance_intent(action, {}, previous['check']['execution_id'])
        self.assertEqual(sim.runtime['queue'][:-1], before)
        fresh = sim.runtime['queue'][-1]
        self.assertEqual((fresh['role'], fresh['stage'], fresh['target']),
                         ('intent_interpretation', 'interpret', bundle['input_ref']))
        self.assertEqual(fresh['reason'], 'original source changed before independent check')
        self.assertNotIn('previous_import_id', fresh)
        self.assertNotIn('intent_repair', fresh)
        self.assertEqual(sim.runtime['intent_imports'][bundle['id']], bundle)
        sim.engine._save()
        saved = deepcopy((sim.instance, sim.runtime))
        sim.restart()
        self.assertEqual((sim.instance, sim.runtime), saved)
        output = deepcopy(bundle['output'])
        output['import_units'][0]['source_range']['end'] = len(original['text'])
        created = sim.engine._apply_governance_intent(fresh, output, previous['execution_id'])
        self.assertIsNone(created['previous_id'])
        self.assertEqual(created['source']['text'], original['text'])
        self.assertNotIn('repair', created['output'])
        sim.engine.store.validate_candidate(sim.instance, sim.runtime)

    def test_failed_and_unresolved_checks_keep_the_actual_repair_basis(self):
        for decision in ('revision_required', 'unresolved'):
            with self.subTest(decision=decision):
                sim = checked_sim()
                previous = checked_bundle(sim)
                author = sim.runtime['executions'][previous['execution_id']]['action']
                bundle = sim.engine._apply_governance_intent(author, deepcopy(previous['output']), previous['execution_id'])
                action = next(a for a in sim.runtime['queue'] if a.get('import_id') == bundle['id'])
                sim.runtime['queue'].remove(action)
                checker = returned(sim.engine, action, 'EX-null-check')
                output = {key: deepcopy(value) for key, value in previous['check'].items()
                          if key not in {'execution_id', 'sha256'}}
                output.update(bundle_sha256=bundle['sha256'], decision=decision, scope_complete=True,
                              findings=['Reconsider the original meaning'])
                checked = sim.engine._apply_governance_intent(action, output, checker['id'])
                self.assertEqual(checked['status'], decision)
                retry = next(a for a in sim.runtime['queue'] if a.get('previous_import_id') == bundle['id'])
                self.assertEqual(retry['intent_repair'], {
                    'import_id': bundle['id'], 'previous_sha256': bundle['sha256'],
                    'check_execution_id': checker['id'], 'findings': output['findings']})
                self.assertEqual(retry['lineage_id'], author.get('lineage_id', bundle['execution_id']))
                sim.engine._save()
                saved = deepcopy((sim.instance, sim.runtime))
                sim.restart()
                self.assertEqual((sim.instance, sim.runtime), saved)

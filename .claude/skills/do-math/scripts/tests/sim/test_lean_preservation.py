"""G2: default compiler facts survive actual worker, verifier, recording and reload."""
from copy import deepcopy
import json
import unittest

from do_math import knowledge_records, trust_validation
from do_math.canonical import exact_content_hash
from support.knowledge_formal_engine import ReturnedValues, attempts, run_formal, scene
from support.lean_preservation import assert_default_result, recorded_defaults
from support.provider_probes import ObservedCalls


class LeanPreservationTests(unittest.TestCase):
    def test_both_default_sources_preserve_complete_evidence_after_reload(self):
        for name, facts in recorded_defaults().items():
            with self.subTest(declaration=name):
                sim, action = scene(source=facts['source'], declarations=(name,))
                with ReturnedValues(trust_validation.verify_formal) as returned, \
                        ObservedCalls(record=knowledge_records.record_formal_result) as recorded:
                    run_formal(sim, action)
                result, = returned.values
                execution, = attempts(sim)
                # Entire lower result crosses the real recording and artifact boundaries.
                arguments, = recorded.captured('record')
                sealed = {**result, 'execution_id': execution['id'], 'artifact_ref': execution['result_ref']}
                self.assertEqual(arguments['verification'], sealed)
                self.assertEqual(json.loads(sim.engine.store.read(execution['result_ref'], sim.engine.head)), result)
                formal_id = sim.instance['knowledge']['K1']['formal_result_id']
                before = deepcopy(sim.instance['formal_results'][formal_id])
                self.assertEqual(before['verification'], sealed)
                sim.restart()
                stored = sim.instance['formal_results'][formal_id]
                self.assertEqual(stored, before)
                self.assertEqual(exact_content_hash(stored), exact_content_hash(before))
                self.assertEqual(stored['verification'], sealed)
                assert_default_result(self, stored['verification'], name)

    def test_changed_default_sources_do_not_acquire_recorded_evidence(self):
        for name, facts in recorded_defaults().items():
            with self.subTest(declaration=name):
                sim, action = scene(source=facts['source'] + '\n', declarations=(name,))
                with ReturnedValues(trust_validation.verify_formal) as returned, \
                        ObservedCalls(record=knowledge_records.record_formal_result) as recorded:
                    run_formal(sim, action)
                result, = returned.values
                self.assertEqual(result['status'], 'failed')
                self.assertIn('unregistered synthetic Lean source/declarations', result['stderr'])
                self.assertEqual(recorded.count('record'), 0)
                execution, = attempts(sim)
                self.assertEqual(json.loads(sim.engine.store.read(execution['result_ref'], sim.engine.head)), result)
                before = deepcopy(sim.instance['formal_results'])
                sim.restart()
                self.assertEqual(sim.instance['formal_results'], before)
                self.assertTrue(all(not row.get('verification') for row in before.values()))

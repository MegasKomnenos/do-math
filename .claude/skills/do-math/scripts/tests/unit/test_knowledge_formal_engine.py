"""Exact formal-result preservation and publication comparison on real storage."""
from copy import deepcopy
import hashlib
import json
import sys
import unittest

from support.knowledge_formal_engine import SOURCE, attempts, scene, warm_scenes
from support.provider_probes import ObservedCalls


def setUpModule():
    warm_scenes()


class FormalBindingConnections(unittest.TestCase):
    def test_failed_result_uses_the_fixed_command_fingerprint_and_axioms(self):
        """About 0.5 s: real machine-step preparation and storage consume the legacy failed result."""
        sim, action = scene(source=SOURCE, declarations=('t',), python_command=True)
        environment = deepcopy(sim.engine._formal_environment())
        sim.instance['config']['lean_command'] = ['unapproved-config-command']
        steps = sim.engine._formal_steps(action)
        _, arguments = next(steps)
        self.assertEqual(arguments['lean_command'], [sys.executable])
        self.assertNotIn('timeout_seconds', arguments)
        self.assertEqual(arguments['expected_toolchain'], environment['toolchain'])
        self.assertEqual(set(arguments['allowed_axioms']), set(environment['allowed_axioms']))
        with self.assertRaises(StopIteration) as completed:
            steps.send({'status': 'failed', 'reason': 'compiler double, no proof claim'})
        self.assertIsNone(completed.exception.value)
        execution, = attempts(sim)
        self.assertEqual(execution['formal_status'], 'failed')
        self.assertEqual(execution['outcome'], 'execution_incomplete')

    def test_exact_compiler_keys_and_source_survive_result_artifacts(self):
        """~0.52 s: real repository validation and artifact publication preserve the arbitrary compiler payload."""
        sim, action = scene(source=SOURCE, declarations=('t',), python_command=True)
        sim.instance['config']['lean_command'] = ['unapproved-config-command']
        result = {'status': 'failed', 'reason': 'compiler double retains exact names',
                  'axioms': {'\N{KELVIN SIGN}': [], 'K': []}}
        steps = sim.engine._formal_steps(action)
        _, arguments = next(steps)
        with self.assertRaises(StopIteration) as completed:
            steps.send(result)
        self.assertIsNone(completed.exception.value)
        execution, = attempts(sim)
        head = sim.engine.head
        raw = sim.engine.store.read(execution['result_ref'], head)
        self.assertEqual(json.loads(raw), result)
        source_ref = execution['result_ref'].replace('formal.json', 'proposal.lean')
        source = sim.engine.store.read(source_ref, head)
        self.assertEqual(arguments['source'], SOURCE)
        self.assertEqual(source, SOURCE.encode('utf-8'))
        self.assertEqual(hashlib.sha256(source).hexdigest(), hashlib.sha256(SOURCE.encode('utf-8')).hexdigest())
        sim.restart()
        loaded = sim.engine.store.load(head)[2]['executions'][execution['id']]
        self.assertEqual(loaded['result_ref'], execution['result_ref'])
        self.assertEqual(sim.engine.store.read(loaded['result_ref'], head), raw)
        self.assertEqual(sim.engine.store.read(source_ref, head), SOURCE.encode('utf-8'))

    def test_publication_signature_distinguishes_exact_unicode_payload(self):
        """~0.45 s: a restored public state and two real publications distinguish exact Unicode bytes."""
        sim, _ = scene(source='-- "e\N{COMBINING ACUTE ACCENT}"', declarations=('t',))
        engine = sim.engine
        head = engine.head
        with ObservedCalls(published=engine.store.published_state) as observed:
            self.assertTrue(engine._unchanged())
        call, = observed.captured('published')
        self.assertEqual(call['head'], head)
        fid = sim.instance['knowledge']['K1']['formal_result_id']
        sim.instance['formal_results'][fid]['lean_code'] = '-- "é"'
        self.assertFalse(engine._unchanged())
        engine._save()
        self.assertNotEqual(engine.head, head)

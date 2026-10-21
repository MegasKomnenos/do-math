"""Fixed intent imports wait for actual evidence and receive a fresh independent check.

These scenes cross the worker submission, QU handler and first repository reader;
the model and host ports are doubles. No research instance or live CLI is used.
"""
from copy import deepcopy
import tempfile
import unittest

from do_math import governance
from do_math.canonical import exact_content_hash
from support.engine_lifecycle import applied
from support.model import ModelDouble
from support.sim import Sim, warm_template

setUpModule = warm_template


from support.intent_evidence import (EvidenceResponder, evidence_waits, waiting_sim,
                                     initial_waiting_sim, authorize_initial_evidence)


class IntentEvidenceFlowTests(unittest.TestCase):
    def test_question_receipt_rechecks_same_import_and_restores_check_history(self):
        from support.storage_action_pairs import StoredActions, intent_evidence_samples, action_pair, waiting_pair
        samples = StoredActions(self)
        sim, original = intent_evidence_samples(samples)
        before_runtime = samples.samples[0][1][1]
        before = len([e for e in before_runtime['executions'].values() if e['role'] == 'intent_interpretation'
                      and e['action'].get('stage') == 'interpret'])
        bundle = sim.runtime['intent_imports'][original['id']]
        self.assertEqual((bundle['sha256'], bundle['source'], bundle['output']),
                         (original['sha256'], original['source'], original['output']))
        self.assertEqual(bundle['check_history'], [original['check']])
        self.assertEqual(bundle['check']['decision'], 'approved')
        self.assertNotEqual(bundle['check']['execution_id'], original['check']['execution_id'])
        self.assertEqual(len([e for e in sim.runtime['executions'].values() if e['role'] == 'intent_interpretation'
            and e['action'].get('stage') == 'interpret']), before)
        self.assertFalse(evidence_waits(sim))
        self.assertEqual(governance.import_seal(bundle), original['sha256'])
        sim.restart()
        self.assertEqual(sim.runtime['intent_imports'][original['id']], bundle)
        self.assertFalse(sim.engine._resume_import_check_waits())
        self.assertFalse(any(a.get('import_check_release') for a in sim.runtime['queue']))
        contract = sim.engine.store.contract
        for pair, fields in ((action_pair(contract, samples.samples), {'import_check_release'}),
                             (waiting_pair(contract, samples.samples), {'bundle_sha256', 'source_sha256',
                                'check_sha256', 'question_ids', 'question_scopes', 'question_resolution_basis', 'evidence_basis'})):
            for _, state in samples.samples:
                pair.receive(state)
            self.assertTrue(fields <= set().union(*(pair.written(state) for _, state in samples.samples)))
        # The real producer samples also feed the broad execution corpus. Check
        # this new field directly here without running that unrelated population.
        checker = sim.runtime['executions'][bundle['check']['execution_id']]
        self.assertTrue(checker['import_check_basis']['records'])
        for fault, reason in (('history_hash', 'sealed check changed'), ('bundle', 'check read a different import'),
                              ('independence', 'independent checker execution required'),
                              ('release', 'evidence release required'),
                              ('same_basis', 'check evidence release differs from the unresolved import')):
            changed = deepcopy(sim.runtime)
            damaged = changed['intent_imports'][bundle['id']]
            if fault == 'history_hash':
                damaged['check_history'][0]['sha256'] = '0' * 64
            elif fault == 'bundle':
                damaged['check']['bundle_sha256'] = '0' * 64
                damaged['check']['sha256'] = exact_content_hash({k: v for k, v in damaged['check'].items() if k != 'sha256'})
            elif fault == 'independence':
                damaged['check_history'][0]['execution_id'] = damaged['execution_id']
                damaged['check_history'][0]['sha256'] = exact_content_hash({k: v for k, v in damaged['check_history'][0].items() if k != 'sha256'})
            elif fault == 'release':
                changed['history'] = [r for r in changed['history'] if r.get('kind') != 'import_check_evidence_resumed']
            else:
                release = next(r for r in changed['history'] if r.get('kind') == 'import_check_evidence_resumed')
                old = release['previous']
                release['basis'] = {'questions': deepcopy(old['question_resolution_basis']), 'records': deepcopy(old['evidence_basis'])}
                release['sha256'] = exact_content_hash({k: v for k, v in release.items() if k != 'sha256'})
                check = damaged['check']
                changed['executions'][check['execution_id']]['action']['import_check_release'] = release['sha256']
                check['reconsideration_ref'] = release['sha256']
                check['sha256'] = exact_content_hash({k: v for k, v in check.items() if k != 'sha256'})
            with self.subTest(fault=fault), self.assertRaisesRegex(ValueError, reason):
                contract.validate(sim.instance, changed)
        with self.assertRaisesRegex(ValueError, 'evidence release required'):
            governance.check_import(sim.instance, sim.runtime, bundle['id'], bundle['check'],
                                    execution_id=original['check']['execution_id'], clock=sim.clock)

    def test_actual_content_change_releases_once_and_pause_is_preserved(self):
        sim = waiting_sim(evidence_ref='source:check-evidence.txt')
        wait, = evidence_waits(sim)
        bundle = deepcopy(sim.runtime['intent_imports'][wait['import_id']])
        applied(sim, 'pause', text='Keep research paused')
        path = sim.root / 'check-evidence.txt'
        path.write_bytes(b'New actual source evidence.\n')
        applied(sim, 'source', config={'path': str(path)})
        self.assertFalse(sim.engine._resume_import_check_waits())
        self.assertEqual(sim.instance['lifecycle']['state'], 'paused')
        self.assertEqual(sim.runtime['intent_imports'][bundle['id']], bundle)
        applied(sim, 'resume', text='Resume the authorized synthetic instance')
        # The normal control owner already runs upkeep after applying resume.
        self.assertFalse(sim.engine._resume_import_check_waits())
        release = next(r for r in sim.runtime['history'] if r.get('kind') == 'import_check_evidence_resumed')
        self.assertFalse(all(s['resolved'] for s in release['basis']['questions'].values()))
        self.assertNotEqual(release['basis']['records'], wait['evidence_basis'])
        self.assertEqual(sim.runtime['intent_imports'][bundle['id']]['sha256'], bundle['sha256'])
        self.assertFalse(any(a.get('intent_repair') for a in sim.runtime['queue']))
        self.assertEqual(len([a for a in sim.runtime['queue'] if a.get('import_check_release')]), 1)
        sim.run_until(lambda s: s.runtime['intent_imports'][bundle['id']].get('application', {}).get('status') == 'applied', max_steps=6)
        self.assertEqual(sim.runtime['intent_imports'][bundle['id']]['check_history'], [bundle['check']])

    def test_repeated_unresolved_does_not_consume_the_same_receipt_again(self):
        sim = waiting_sim(repeat=True)
        sim.run_until(lambda s: bool(evidence_waits(s)) and len(s.runtime['intent_imports'][evidence_waits(s)[0]['import_id']]['check_history']) == 1
            and all(e['status'] == 'ended' for e in s.runtime['executions'].values()), max_steps=8)
        wait, = evidence_waits(sim)
        self.assertTrue(all(s['resolved'] for s in wait['question_resolution_basis'].values()))
        queue = deepcopy(sim.runtime['queue'])
        self.assertFalse(sim.engine._resume_import_check_waits())
        sim.restart()
        self.assertFalse(sim.engine._resume_import_check_waits())
        self.assertEqual(sim.runtime['queue'], queue)
        self.assertEqual(len([r for r in sim.runtime['history'] if r.get('kind') == 'import_check_evidence_resumed']), 1)
        bundle = deepcopy(sim.runtime['intent_imports'][wait['import_id']])
        # A premature exact-approval request cannot turn missing evidence into reauthor work.
        request = sim.control('decision', text='Premature approval', config={'change': {'kind': 'import_approval',
            'import_id': bundle['id'], 'bundle_sha256': bundle['sha256'],
            'check_sha256': bundle['check']['sha256'], 'unit_hashes': {}}})
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(request['request_id'])['effect'], 'rejected')
        self.assertEqual(evidence_waits(sim), [wait])
        self.assertFalse(any(a.get('intent_repair') for a in sim.runtime['queue']))
        target = next(r for r in sim.runtime['inputs'] if r['id'] == bundle['input_ref'])
        target['text'] += ' Actual changed original.'
        self.assertTrue(sim.engine._resume_import_check_waits())
        self.assertFalse(evidence_waits(sim))
        rework, = [a for a in sim.runtime['queue'] if a.get('intent_repair')]
        self.assertEqual(rework['stage'], 'interpret')
        self.assertNotIn('previous_import_id', rework)
        self.assertEqual(sim.runtime['intent_imports'][bundle['id']], bundle)

    def test_initialization_uses_the_same_wait_without_reinterpreting(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        sim = initial_waiting_sim(directory.name)
        # Only the interpreter is initially authorized. Its missing-evidence handler
        # remains a real queued obligation until the user grants that initial role.
        wait, = evidence_waits(sim)
        original = deepcopy(sim.runtime['intent_imports'][wait['import_id']])
        self.assertEqual(sim.instance['lifecycle']['state'], 'initializing')
        sim.engine._queue_initial_intent()
        self.assertFalse(any(a['role'] == 'intent_interpretation' for a in sim.runtime['queue']))
        authorize_initial_evidence(sim)
        sim.run_until(lambda s: s.instance['lifecycle']['state'] == 'active', max_steps=8)
        bundle = sim.runtime['intent_imports'][original['id']]
        self.assertEqual((bundle['sha256'], bundle['check_history']), (original['sha256'], [original['check']]))
        self.assertEqual(sim.instance['lifecycle']['intent_check']['check_execution_id'], bundle['check']['execution_id'])
        self.assertFalse(any(a.get('previous_import_id') == bundle['id'] for a in sim.runtime['queue']))

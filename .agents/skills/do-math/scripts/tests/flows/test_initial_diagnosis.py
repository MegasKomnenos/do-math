"""A rejected initial interpretation during public activation: one bounded repair, one maintenance diagnosis,
then the diagnosis's decision (``repair_execution``'s initialization routing, layer 2, on the real engine).

The model double answers the interpretation with a non-output every time, so
each attempt is rejected by the engine's receiving check; the maintenance
role answers the diagnosis. The initial grant covers both initialization roles.
"""
import tempfile
import unittest

from support.model import amend, raw
from support.sim import Sim
from support.role_input_requirements import observe_judgment_inputs

REJECTED = raw({'not': 'an interpretation'}, expected_receipt='rejected')


def _interpretations(sim):
    return [call['action'] for call in sim.model.calls if call['role'] == 'intent_interpretation']


def _diagnoses(sim):
    return [call['action'] for call in sim.model.calls if call['role'] == 'maintenance']


class DiagnosisFlow(unittest.TestCase):
    """An initializing Sim whose interpretation is always rejected; ``activate`` answers the diagnosis with ``decision``."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.sim = Sim(directory.name)
        self.sim.model.on('intent_interpretation', stage='interpret').reply(REJECTED)

    def activate(self, decision):
        self.sim.model.on('maintenance').reply(amend(initial_submission_diagnosis=decision))
        with observe_judgment_inputs(self) as prepared:
            with self.assertRaisesRegex(AssertionError, 'public activation did not reach active'):
                self.sim.activate(initial_roles=('intent_interpretation', 'maintenance'))
        self.assertEqual(len([row for row in prepared if row['action'].get('initial_submission_diagnosis')]), 1)
        self.assertTrue(any(row['action'].get('continuation_of') for row in prepared))


class InitialDiagnosisTests(DiagnosisFlow):
    def test_a_retry_decision_continues_the_interpretation_once_and_opens_no_second_diagnosis(self):
        """About 10 s, over the 2 s Sim budget: the public activation with four real model calls through the worker."""
        self.activate({'decision': 'retry', 'guidance': 'Answer with the interpretation schema'})
        first, repaired, retried = _interpretations(self.sim)
        self.assertEqual((first.get('repair_attempt'), repaired['repair_attempt'], repaired['continuation_of']),
                         (None, 1, self.sim.runtime['executions'][repaired['continuation_of']]['id']))
        diagnosis, = _diagnoses(self.sim)
        self.assertTrue(diagnosis['initial_submission_diagnosis'])
        self.assertEqual(diagnosis['target'], retried['continuation_of'])
        self.assertEqual((retried['repair_attempt'], retried['diagnosis_attempt']), (2, 1))
        self.assertIn('initial_execution_retry_started', [row.get('kind') for row in self.sim.runtime['history']])
        wait, = self.sim.runtime['waiting_actions'].values()
        self.assertEqual((wait['kind'], wait['next_owner'], wait['action']['id']), ('output_validation', 'maintenance', first['id']))
        self.assertNotIn('diagnosis', wait)
        self.assertEqual(self.sim.instance['lifecycle']['state'], 'initializing')

    def test_a_wait_decision_holds_the_interpretation_with_the_diagnosis_guidance(self):
        """About 8 s, over the 2 s Sim budget: the public activation with three real model calls through the worker."""
        self.activate({'decision': 'wait', 'guidance': 'The user must restate the goal'})
        self.assertEqual(len(_interpretations(self.sim)), 2)
        diagnosis, = _diagnoses(self.sim)
        wait, = self.sim.runtime['waiting_actions'].values()
        self.assertEqual((wait['reason'], wait['next_owner']), ('The user must restate the goal', 'maintenance'))
        self.assertEqual({key: wait['diagnosis'][key] for key in ('decision', 'guidance')},
                         {'decision': 'wait', 'guidance': 'The user must restate the goal'})
        maintenance = self.sim.runtime['executions'][wait['diagnosis']['execution_id']]
        self.assertEqual((maintenance['role'], maintenance['outcome'], maintenance['action']['target']),
                         ('maintenance', 'output_accepted', diagnosis['target']))


class DiagnosisGuardTests(DiagnosisFlow):
    """The diagnosis's own guards, called on the engine where the wait decision's flow leaves it (about 8 s each)."""

    def held(self):
        """About 8 s: the wait decision's flow; returns the maintenance action, the wait and the failed interpretation."""
        self.activate({'decision': 'wait', 'guidance': 'The user must restate the goal'})
        wait, = self.sim.runtime['waiting_actions'].values()
        maintenance = self.sim.runtime['executions'][wait['diagnosis']['execution_id']]
        return maintenance['action'], wait, self.sim.runtime['executions'][wait['execution_id']]

    def test_a_diagnosis_output_needs_guidance_and_allows_one_retry(self):
        """About 8 s, over the 2 s Sim budget: the public activation with three real model calls through the worker."""
        action, wait, _ = self.held()
        engine = self.sim.engine
        with self.assertRaisesRegex(ValueError, 'initial diagnosis requires concrete repair or waiting guidance'):
            engine.apply_initial_diagnosis(action, {'initial_submission_diagnosis': {'decision': 'retry', 'guidance': ' '}},
                                           'EX-diagnosis')
        wait['action']['diagnosis_attempt'] = 1
        with self.assertRaisesRegex(ValueError, 'initial diagnosis allows one bounded follow-up'):
            engine.apply_initial_diagnosis(action, {'initial_submission_diagnosis': {'decision': 'retry', 'guidance': 'Retry'}},
                                           'EX-diagnosis')

    def test_a_diagnosis_owns_only_the_ended_failure_of_initialization(self):
        """About 8 s, over the 2 s Sim budget: the public activation with three real model calls through the worker."""
        action, wait, failed = self.held()
        engine = self.sim.engine
        with self.assertRaisesRegex(ValueError, 'initial diagnosis must identify an ended interpretation'):
            engine.initial_diagnosis_input({**action, 'target': 'EX-absent'})
        wait['execution_id'] = 'EX-other'
        with self.assertRaisesRegex(ValueError, 'initial diagnosis no longer owns this failure'):
            engine.initial_diagnosis_input(action)
        engine.instance['lifecycle']['state'] = 'active'
        with self.assertRaisesRegex(ValueError, 'initial submission diagnosis requires initialization'):
            engine.initial_diagnosis_input(action)
        self.assertEqual(failed['role'], 'intent_interpretation')

    def test_a_retry_that_fails_its_authority_check_returns_to_maintenance_with_the_error(self):
        """About 9 s, over the 2 s Sim budget: the public activation with three real model calls through the worker."""
        action, wait, _ = self.held()
        engine = self.sim.engine
        wait['diagnosis']['decision'] = 'retry'
        self.sim.advance(3 * 86400)  # past the initial grant's expiry
        engine.continue_initial_retries()
        wait = engine.runtime['waiting_actions'][wait['action']['id']]
        self.assertTrue(wait['diagnosis']['retry_error'])
        self.assertEqual((wait['next_owner'], wait['reason']), ('maintenance', wait['diagnosis']['retry_error']))
        _, _, stored = engine.store.load()
        self.assertEqual(stored['waiting_actions'][wait['action']['id']]['diagnosis']['retry_error'],
                         wait['diagnosis']['retry_error'])
        before = len(engine.runtime['history'])
        engine.continue_initial_retries()  # a recorded retry error is not retried again
        self.assertEqual(len(engine.runtime['history']), before)


if __name__ == '__main__':
    unittest.main()

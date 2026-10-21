"""4-B/13-B: independently checked imports leave both waits by public decisions.

Four actual activation/active scenes took 11.1s after template preparation;
they retain the real worker, public decisions, storage and owner preparation.
"""
from copy import deepcopy
import unittest

from do_math.wait_rules import IMPORT_ACTION_WAITS
from support.engine_lifecycle import applied
from support.governance_cases import question_sim, question_bundle, initial_question_sim
from support.governance_sim import checked_sim, checked_bundle, approval, initial_checked_sim
from support.wait_reporting import assert_wait_report
from support.intent_evidence import (waiting_sim, initial_waiting_sim, evidence_bundle, authorize_initial_evidence)


def setUpModule():
    checked_sim()
    question_sim()
    initial_checked_sim()
    initial_question_sim()


CASES = {
    'import_application_authority': ((checked_sim, initial_checked_sim), checked_bundle),
    'import_user_decision': ((question_sim, initial_question_sim), question_bundle),
    'import_check_evidence': ((waiting_sim, initial_waiting_sim), evidence_bundle),
}


class ImportWaitContractTests(unittest.TestCase):
    def test_every_import_wait_has_a_public_exact_once_exit_and_a_real_status_row(self):
        self.assertEqual(set(CASES), IMPORT_ACTION_WAITS)
        exercised = set()
        for kind in IMPORT_ACTION_WAITS:
            builds, find_bundle = CASES[kind]
            for build in builds:
                sim = build()
                state = sim.instance['lifecycle']['state']
                with self.subTest(kind=kind, state=state):
                    self.exercise_wait(sim, find_bundle, kind)
                    exercised.add((kind, state))
        self.assertEqual(exercised, {(kind, state) for kind in IMPORT_ACTION_WAITS
                                    for state in ('active', 'initializing')})

    def exercise_wait(self, sim, find_bundle, kind):
        bundle = find_bundle(sim)
        identifier, entry = next((key, row) for key, row in sim.runtime['waiting_actions'].items()
                                 if row['kind'] == kind and row['import_id'] == bundle['id'])
        assert_wait_report(self, sim.engine, identifier)
        held = deepcopy((sim.instance, sim.runtime))
        for _ in range(2):
            sim.engine._resume_import_question_waits()
            sim.engine._after_governance_import(bundle['id'])
            self.assertEqual((sim.instance, sim.runtime), held)
        if kind == 'import_check_evidence':
            if sim.instance['lifecycle']['state'] == 'initializing':
                authorize_initial_evidence(sim)
            # The existing maintenance worker seals the answer; it is not a
            # permission to reinterpret the original or approve its meaning.
            sim.run_until(lambda s: identifier not in s.runtime.get('waiting_actions', {}), max_steps=4)
            history = [row for row in sim.runtime['history']
                       if row.get('kind') == 'import_check_evidence_resumed'
                       and row['previous']['action']['id'] == identifier]
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]['previous'], entry)
            next_id = history[0]['action_id']
            next_actions = [a for a in sim.runtime['queue'] if a['id'] == next_id]
            next_actions += [e['action'] for e in sim.runtime['executions'].values()
                             if e['action']['id'] == next_id]
            self.assertEqual(len({a['id'] for a in next_actions}), 1)
            for action in next_actions:
                self.assertEqual((action['stage'], action['import_id'], action['target']),
                                 ('check', bundle['id'], bundle['input_ref']))
                self.assertEqual(action['import_check_release'], history[0]['sha256'])
            released = deepcopy((sim.instance, sim.runtime))
            for _ in range(2):
                self.assertFalse(sim.engine._resume_import_check_waits())
                self.assertEqual((sim.instance, sim.runtime), released)
            sim.engine._save()
            self.assertNotIn(identifier, sim.engine.store.load()[2].get('waiting_actions', {}))
            return
        if kind == 'import_application_authority':
            change = approval(bundle)
        else:
            question = next(row for row in sim.runtime['question_links']
                            if row.get('source_id') == bundle['id'] and row['blocks'])
            change = {'kind': 'question_answer', 'text': 'The domain is natural numbers',
                      'target_ids': [sim.instance['id']], 'resolves_questions': [question['id']]}
        applied(sim, 'decision', config={'change': change}, request_id='UC-import-exit')
        sim.step()
        self.assertNotIn(identifier, sim.runtime.get('waiting_actions', {}))
        if kind == 'import_application_authority':
            self.assertEqual(sim.runtime['intent_imports'][bundle['id']]['application']['status'], 'applied')
        else:
            queued = [row for row in sim.runtime['queue']
                      if row.get('intent_repair', {}).get('import_id') == bundle['id']]
            started = [row['action'] for row in sim.runtime['executions'].values()
                       if row.get('action', {}).get('intent_repair', {}).get('import_id') == bundle['id']]
            self.assertLessEqual(len(queued), 1)
            self.assertLessEqual(len(started), 1)
            self.assertEqual(len({row['id'] for row in [*queued, *started]}), 1)
            for row in [*queued, *started]:
                self.assertEqual(row['previous_import_id'], bundle['id'])
                self.assertEqual(row['target'], bundle['input_ref'])
            history = [row for row in sim.runtime['history']
                       if row.get('kind') == 'import_question_wait_resumed' and row['action_id'] == identifier]
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]['previous'], entry)
            resolved = next(row for row in sim.runtime['question_links'] if row['id'] == question['id'])
            self.assertIsNone(question['resolution_ref'])
            self.assertEqual(resolved['status'], 'resolved')
            self.assertEqual(history[0]['resolution_refs'], [resolved['resolution_ref']])
        released = deepcopy((sim.instance, sim.runtime))
        applied(sim, 'decision', config={'change': change}, request_id='UC-import-exit')
        sim.engine._resume_import_question_waits()
        self.assertEqual((sim.instance, sim.runtime), released)
        sim.engine._save()
        self.assertNotIn(identifier, sim.engine.store.load()[2].get('waiting_actions', {}))

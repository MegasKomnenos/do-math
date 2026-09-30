"""The initial intent's evidence and the grants of an initializing instance (``initialization``, ``governance``), moved from ``test_initial_intent_connection``.

``record_fixtures.applied_initial_intent`` builds the state: an adopted charter,
the user's input preserved as its own source, and one interpretation unit
authored by ``EX-author``, checked by ``EX-check`` and applied (the fixture
fails when the import was not applied from that preserved source, preserved
rule K-44). Every test calls the product functions on that state.
"""
import hashlib
import unittest

from do_math import governance as gov
from do_math.initialization import initial_intent_evidence
from record_fixtures import applied_initial_intent

# A combining accent and the Kelvin sign: text that Unicode normalization would change.
UNSTABLE = 'e\N{COMBINING ACUTE ACCENT} and \N{KELVIN SIGN} are exact source text'


class InitialIntentConnectionTests(unittest.TestCase):
    def test_applied_import_uses_original_input_reference_and_exact_bytes(self):
        for text in ['A mathematical goal', UNSTABLE]:
            with self.subTest(text=text):
                instance, runtime, _ = applied_initial_intent(text)
                self.assertEqual(initial_intent_evidence(instance, runtime), {
                    'input_sha256': hashlib.sha256(text.encode()).hexdigest(),
                    'interpretation_execution_id': 'EX-author', 'check_execution_id': 'EX-check'})

    def test_changed_input_or_unapplied_result_cannot_complete_initialization(self):
        instance, runtime, bid = applied_initial_intent('A mathematical goal')
        runtime['intent_imports'][bid].pop('application')
        with self.assertRaisesRegex(ValueError, '^initial input requires a sealed, fully checked applied import$'):
            initial_intent_evidence(instance, runtime)
        instance, runtime, bid = applied_initial_intent('A mathematical goal')
        runtime['intent_imports'][bid]['input_ref'] = 'UI-other'
        with self.assertRaisesRegex(ValueError, '^initial input has no applied independent import$'):
            initial_intent_evidence(instance, runtime)

    def test_initial_grants_wait_for_activation_to_open_research(self):
        instance, runtime, _ = applied_initial_intent('A mathematical goal')
        instance, runtime, _ = gov.apply_decision(instance, runtime, {'kind': 'grant', 'grant': {
            'id': 'GR-work', 'kind': 'local', 'roles': ['research_work'], 'reuse': 'reusable'}}, source_ref='GS-adoption')
        self.assertEqual(runtime['queue'], [])
        self.assertEqual(instance['grants']['GR-work']['status'], 'active')

    def test_grant_change_is_plan_basis_and_not_the_plan_execution_authority(self):
        instance, runtime, _ = applied_initial_intent('A mathematical goal')
        instance['lifecycle']['state'] = 'active'
        instance, runtime, _ = gov.apply_decision(instance, runtime, {'kind': 'grant', 'grant': {
            'id': 'GR-plan', 'kind': 'local', 'roles': ['research_plan'], 'reuse': 'reusable'}}, source_ref='GS-adoption')
        runtime['queue'] = []
        instance, runtime, event = gov.apply_decision(instance, runtime, {'kind': 'grant', 'grant': {
            'id': 'GR-work', 'kind': 'local', 'roles': ['research_work'], 'reuse': 'reusable'}}, source_ref='GS-adoption')
        self.assertEqual(len(runtime['queue']), 1)
        action = runtime['queue'][0]
        authorization = gov.authorize(instance, action, runtime=runtime)
        self.assertTrue(authorization['allowed'], authorization)
        self.assertEqual(authorization['grant_id'], 'GR-plan')
        self.assertEqual(action['decision_id'], event['id'])


if __name__ == '__main__':
    unittest.main()

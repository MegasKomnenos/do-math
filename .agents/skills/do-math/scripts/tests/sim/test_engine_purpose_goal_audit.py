"""The purpose scenario's goal audit answer against the schema the engine gives a goal audit call.

``governance_engine._governance_schema`` (layer 2) widens the role schema with
the instance's additional-audit population; the test asks a real engine on an
initialized Sim for it, as the engine does when it prepares the call. The
answer is the legacy ``PurposeAnswers``'s, which the purpose flows' model double
gives (``support.engine_purpose.PurposeResponder``).
"""
from pathlib import Path
import tempfile
import unittest
from copy import deepcopy
from types import SimpleNamespace

import jsonschema

from do_math.contracts import schema_for
from support.purpose_answers import PurposeAnswers
from support.role_answers import seal_response
from support.engine_purpose import PurposeResponder, drive
from support.engine_context import central_check_knowledge, context_engine


class GoalAuditAnswerTests(unittest.TestCase):
    def test_goal_fixture_declares_the_empty_additional_audit_population(self):
        with tempfile.TemporaryDirectory() as directory:
            instance, runtime, _, _ = central_check_knowledge()
            engine = context_engine(instance, runtime)
            action = {'role': 'goal_audit'}
            context = engine._context(action, Path(directory))
            self.assertTrue(context['eligible_knowledge'])
            output = PurposeAnswers().answer('goal_audit', context, None)
            seal_response(output, context, Path(directory))
            schema = engine._governance_schema(action, schema_for('goal_audit'))
            self.assertIn('additional_audits', schema['required'])
            jsonschema.validate(output, schema)
        self.assertEqual(output['additional_audits'], [])

    def test_goal_input_refusals_reach_drive_even_if_the_goal_is_already_solved(self):
        """K-32 uses real eligible input, then damages only the evidence under inspection."""
        instance, runtime, _, _ = central_check_knowledge()
        engine = context_engine(instance, runtime)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            valid = engine._context({'role': 'goal_audit'}, workspace)
            responder = PurposeResponder()
            self.assertEqual(responder.respond('goal_audit', valid, workspace)['decision'], 'satisfied')
            for damage, reason in (
                    ('no_formal_evidence', 'Goal audit was scheduled before effective formal evidence existed'),
                    ('no_links', 'Goal audit did not receive the effective final identity assessment'),
                    ('no_assessments', 'Goal audit did not receive the effective final identity assessment'),
                    ('not_match', 'Goal audit did not receive the effective final identity assessment'),
                    ('unrelated_assessment', 'Goal audit did not receive the effective final identity assessment')):
                with self.subTest(damage=damage):
                    context = deepcopy(valid)
                    item = context['eligible_knowledge'][0]
                    if damage == 'no_formal_evidence':
                        context['eligible_knowledge'] = []
                    elif damage == 'no_links':
                        item['links'] = []
                    elif damage == 'no_assessments':
                        item['identity_assessments'] = []
                    elif damage == 'not_match':
                        item['identity_assessments'][0]['decision'] = 'unresolved'
                    else:
                        item['identity_assessments'][0]['id'] = 'IA-unrelated'
                    responder = PurposeResponder()
                    with self.assertRaisesRegex(AssertionError, '^' + reason + '$'):
                        responder.respond('goal_audit', context, workspace)
                    self.assertEqual(responder.failures, [reason])
                    sim = SimpleNamespace(model=SimpleNamespace(responder=responder))
                    with self.assertRaisesRegex(AssertionError, '^The purpose responder refused its input: ' + reason + '$'):
                        drive(self, sim, predicate=lambda s: True)

    def test_repair_unexpected_roles_and_nonlive_reviews_are_visible_input_failures(self):
        for role, action, reason in (
                ('research_preparation', {'role': 'research_preparation', 'repair': {'error': 'exact validation failure'}},
                 'A purpose fixture must not silently adapt to an engine validation failure: exact validation failure'),
                ('maintenance', {'role': 'maintenance'}, 'Unexpected fixture role: maintenance'),
                ('operational_review', {'role': 'operational_review', 'live': False},
                 'Unexpected execution failure triggered a non-live operational review')):
            with self.subTest(role=role):
                responder = PurposeResponder()
                with self.assertRaisesRegex(AssertionError, '^' + reason + '$'):
                    responder.respond(role, {'action': action}, None)
                self.assertEqual(responder.failures, [reason])
                with self.assertRaisesRegex(AssertionError, '^The purpose responder refused its input: ' + reason + '$'):
                    drive(self, SimpleNamespace(model=SimpleNamespace(responder=responder)), predicate=lambda s: True)


if __name__ == '__main__':
    unittest.main()

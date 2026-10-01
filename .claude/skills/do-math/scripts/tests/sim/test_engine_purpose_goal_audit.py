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

import jsonschema

from do_math.contracts import schema_for
from support.purpose_answers import PurposeAnswers
from support.role_answers import seal_response
from support.sim import Sim


class GoalAuditAnswerTests(unittest.TestCase):
    def test_goal_fixture_declares_the_empty_additional_audit_population(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = Sim(Path(directory) / 'sim').engine
            action = {'role': 'goal_audit'}
            context = {'action': action, 'additional_audit_input': [], 'eligible_knowledge': [
                {'id': 'KN-goal', 'links': ['fixture-link'], 'identity_assessments': [{'decision': 'match'}]}]}
            output = PurposeAnswers().answer('goal_audit', context, None)
            seal_response(output, context, Path(directory))
            schema = engine._governance_schema(action, schema_for('goal_audit'))
            self.assertIn('additional_audits', schema['required'])
            jsonschema.validate(output, schema)
        self.assertEqual(output['additional_audits'], [])


if __name__ == '__main__':
    unittest.main()

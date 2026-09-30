"""Configuration controls through governance (``governance_engine._configure_candidate``, the public ``configure``).

The operator may not change resource settings, and a public configure keeps
its original receipt across other controls and a restart. The instances are a
restored public activation and a publicly initialized one; controls arrive by
the public path or, for the engine's handler alone, by ``_governance_control``.
"""
from copy import deepcopy
import tempfile
import unittest

from do_math.configuration import DEFAULT_CONFIG
from support.sim import Sim, warm_template

setUpModule = warm_template


def capacity(count):
    """A configure patch setting every model's concurrent work sessions to ``count``."""
    limits = deepcopy(DEFAULT_CONFIG['session_limits'])
    limits['work'] = {model: count for model in limits['work']}
    return {'session_limits': limits}


class ConfigurationAuthorityTests(unittest.TestCase):
    def test_configuration_rejects_operator_resources(self):
        engine = Sim.activated().engine
        before = deepcopy(engine.instance)
        limits = deepcopy(DEFAULT_CONFIG['session_limits'])
        limits['work'] = {model: count + 1 for model, count in limits['work'].items()}
        with self.assertRaisesRegex(ValueError, '^resource settings require a user decision at application time$'):
            engine._governance_control({'action': 'configure', 'origin': 'operator', 'config': {'session_limits': limits}})
        self.assertEqual(engine.instance, before)


class PublicConfigureTests(unittest.TestCase):
    def test_public_configure_preserves_original_result_after_other_control_and_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(directory)
            engine = sim.engine
            first = sim.control('configure', config=capacity(12), request_id='configure-first')
            engine.process_controls()
            original = engine.control_result(first['request_id'])
            self.assertEqual(original['effect'], 'applied')
            self.assertEqual(original['config']['session_limits'], capacity(12)['session_limits'])
            sim.control('configure', config=capacity(14), request_id='configure-second')
            engine.process_controls()
            sim.restart()
            replay = sim.control('configure', config=capacity(12), request_id='configure-first')
            self.assertEqual(replay['snapshot'], original['snapshot'])
            self.assertEqual(replay['config']['session_limits'], capacity(12)['session_limits'])
            self.assertEqual(sim.engine.instance['config']['session_limits'], capacity(14)['session_limits'])
            with self.assertRaisesRegex(ValueError, '^changing resource capacity or model allocation requires a user decision$'):
                sim.control('configure', config=capacity(15), origin='operator')
            with self.assertRaisesRegex(ValueError, '^request_id reused with different payload$'):
                sim.control('configure', config=capacity(16), request_id='configure-first')


if __name__ == '__main__':
    unittest.main()

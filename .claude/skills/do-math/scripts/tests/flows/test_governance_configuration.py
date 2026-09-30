"""A configuration import applies the public configure's transition (``governance_engine.governance_owner_handlers``).

A restored public activation receives a user's input; the model double
interprets it through the worker as a configuration change, the default
responder checks it, and the checked import waits for the user's exact
approval. The approval then goes to the engine's approval handler. The scene
runs two role calls, longer than one Sim test's budget.
"""
from copy import deepcopy
import unittest

from do_math.configuration import DEFAULT_CONFIG
from support.governance_sim import approval, checked_bundle, configuration_change, interpreted, waits
from support.sim import Sim, warm_template

setUpModule = warm_template


class ConfigurationImportTests(unittest.TestCase):
    def test_import_configuration_uses_same_profile_and_slot_transition(self):
        """About 7 s: a restored activation, then the input's interpretation and its independent check as two role calls."""
        sim = Sim.activated()
        patch = {'session_limits': deepcopy(DEFAULT_CONFIG['session_limits'])}
        sim.model.on('intent_interpretation').reply(interpreted(configuration_change(patch)))
        sim.control('input', text='Adopt these exact concurrent capacities')
        sim.run_until(lambda s: waits(s, 'import_application_authority'), max_steps=12)
        engine = sim.engine
        bundle = checked_bundle(sim)
        self.assertEqual([unit['payload'] for unit in bundle['output']['import_units']],
                         [{'kind': 'configuration', 'config': patch}])
        public_i, public_r = engine._configure_candidate(engine.instance, engine.runtime,
                                                         {'action': 'configure', 'origin': 'user', 'config': patch})
        self.assertTrue(engine._governance_control({'id': 'CONF-APPROVE', 'action': 'decision', 'origin': 'user',
            'text': 'Approve exact capacities', 'config': {'change': approval(bundle)}}))
        for field in ('config', 'execution_profiles', 'capacity_constraints', 'role_profile_refs'):
            self.assertEqual(engine.instance[field], public_i[field])
        self.assertEqual(engine.runtime['reservations'], public_r['reservations'])


if __name__ == '__main__':
    unittest.main()

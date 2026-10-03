"""감사 입력과 엔진 판정의 거부는 저장된 생산 상태에서 검증한다."""
from copy import deepcopy
import re
import unittest

from support.governance_sim import checked_sim

class GovernanceConfigurationRejectionTests(unittest.TestCase):
    def test_config_not_object(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        request = {'config': []}
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('configuration patch must be an object') + "$"):
            e._configure_candidate(sim.instance, sim.runtime, request)
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_config_origin(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        request = {'config': {}, 'origin': 'model'}
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('unknown configuration authority') + "$"):
            e._configure_candidate(sim.instance, sim.runtime, request)
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

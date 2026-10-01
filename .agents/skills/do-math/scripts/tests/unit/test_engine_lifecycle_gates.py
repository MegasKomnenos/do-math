"""Lifecycle gate rules as functions of their input (``initialization``, ``record_schemas``; layer 2).

The instance and runtime come from the product's ``initialize_state`` on the
fake clock; profiles come from the product's ``build_profiles``. The legacy
activation test asked the real local host (``LocalHost``); here the host is the
counting fake host, and the test shows the evaluation asked it nothing.
"""
from pathlib import Path
import tempfile
import unittest

from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.initialization import activation_requirements, capability_requirements, initialize_state
from do_math.record_schemas import validate_lifecycle
from support.fakes.clock import FakeClock
from support.fakes.host import ObservedHost


def initialized(instance_id, source_input):
    from support.entry import entry
    _entry = entry()
    with tempfile.TemporaryDirectory() as root:
        return initialize_state(instance_id=instance_id, goal='Prove a theorem', workspace=Path(root) / 'workspace',
                                config={}, source_input=source_input, clock=FakeClock(), host=_entry.ports.host)


class ActivationGateTests(unittest.TestCase):
    def test_initialization_persists_missing_activation_requirements_without_dispatch(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = initialized('RI-test', 'original user request')
        self.assertEqual(instance['lifecycle']['state'], 'initializing')
        self.assertEqual(runtime['status'], 'initializing')
        self.assertEqual(runtime['queue'], [])
        host = ObservedHost()
        missing = activation_requirements(instance, runtime, host=host, at=_entry.ports.clock.now(), clock=_entry.ports.clock)['missing']
        self.assertIn('governance', missing)
        self.assertIn('trust_environment', missing)
        self.assertEqual(host.observations(), (0, 0, 0), 'a new instance has no profile whose CLI to observe')
        self.assertEqual(runtime['availability']['state'], 'blocked')

    def test_capability_gate_reports_missing_evidence_instead_of_assuming_support(self):
        from support.entry import entry
        _entry = entry()
        instance = build_profiles(DEFAULT_CONFIG, host=_entry.ports.host)
        profile = next(p for p in instance['execution_profiles'].values() if p['actor_kind'] == 'ai')
        # A boolean claim on the stored profile is not observed capability evidence.
        profile['capabilities'] = {name: True for name in profile['required_capabilities']}
        result = capability_requirements(instance, profile_ref(profile), current_identity={'host': 'fixture'}, at=_entry.ports.clock.now(), host=_entry.ports.host)
        self.assertNotIn('reason', result)  # judged on evidence, not ended by an invalid reference
        self.assertEqual(result['missing'], sorted(profile['required_capabilities']))
        self.assertFalse(result['satisfied'])

    def test_lifecycle_rules_reject_a_state_without_its_utc_high_water(self):
        instance, runtime = initialized('RI-check', 'input')
        validate_lifecycle(instance, runtime)
        runtime.pop('last_observed_utc')
        with self.assertRaisesRegex(ValueError, '^current lifecycle contract: the persisted UTC high-water is absent or invalid$'):
            validate_lifecycle(instance, runtime)


if __name__ == '__main__':
    unittest.main()

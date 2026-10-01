"""Lifecycle record rules as functions of their input (``record_schemas``, ``initialization``, ``execution_profiles``; layers 1-2).

The instance and runtime come from the product's ``initialize_state``; the
capability observation is the synthetic ``research_fixtures.FixtureAdapter``
description, which the in-memory engine of the legacy tests used as well.
"""
from datetime import datetime, timedelta, timezone
import json
import tempfile
import unittest

from do_math import execution_profiles as profiles
from do_math.canonical import canonical_json
from do_math.configuration import DEFAULT_CONFIG
from do_math.initialization import capability_requirements, initialize_state, original_input_bytes
from do_math.record_schemas import validate_lifecycle
from support.execution_inputs import IDENTITY
from support.fakes.host import FakeHost

AT = datetime(2090, 1, 1, tzinfo=timezone.utc)


def state(source='Original user request'):
    from support.entry import entry
    _entry = entry()
    with tempfile.TemporaryDirectory() as root:
        return initialize_state(instance_id='RI-unicode', goal=source, workspace=root, config=DEFAULT_CONFIG,
                                source_input=source, created_at=AT.isoformat(), clock=_entry.ports.clock, host=_entry.ports.host)


class LifecycleRecordTests(unittest.TestCase):
    def test_terminal_marker_cannot_have_live_projection(self):
        instance, runtime = state()
        instance['lifecycle']['permanently_closed'] = True
        with self.assertRaisesRegex(ValueError, 'permanently closed'):
            validate_lifecycle(instance, runtime)
        runtime['status'] = 'closed'
        validate_lifecycle(instance, runtime)
        self.assertTrue(instance['lifecycle']['permanently_closed'])

    def test_original_unicode_bytes_survive_canonical_roundtrip(self):
        source = 'Cafe\u0301'  # a combining accent, not the precomposed letter
        instance, runtime = state(source)
        restored = json.loads(canonical_json(instance))
        original = restored['lifecycle']['immutable_input']
        self.assertEqual(original_input_bytes(original), source.encode())
        self.assertEqual(original['text'], source)
        self.assertEqual(runtime['inputs'][0]['sha256'], original['sha256'])
        original['text'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'immutable input bytes or hash differs'):
            original_input_bytes(original)


class CapabilityEvidenceTests(unittest.TestCase):
    def test_negative_job_is_not_cleared_by_later_help_probe(self):
        from support.entry import entry
        _entry = entry()
        instance, _ = state()
        instance.update(profiles.build_profiles(instance['config'], host=_entry.ports.host))
        profile = profiles.resolve_profile(instance['execution_profiles'], instance['role_profile_refs']['maintenance'][0])
        reference = profiles.profile_ref(profile)
        positive = profiles.capability_evidence(profile, FakeHost(identity=IDENTITY).cli_describe(profile),
                                                observed_at=(AT + timedelta(seconds=1)).isoformat())
        instance['capability_evidence'] = {positive['id']: positive}
        at = (AT + timedelta(seconds=2)).isoformat()
        self.assertTrue(capability_requirements(instance, reference, current_identity=IDENTITY, at=at, host=_entry.ports.host)['satisfied'],
                        'the help probe alone satisfies the profile')
        negative = profiles.structural_failure_evidence(profile, IDENTITY, observed_at=AT.isoformat(),
                                                         execution_id='EX-failed', evidence_ref='failure.json')
        instance['capability_evidence'] = {row['id']: row for row in (negative, positive)}
        outcome = capability_requirements(instance, reference, current_identity=IDENTITY, at=at, host=_entry.ports.host)
        self.assertFalse(outcome['satisfied'])
        self.assertIn('atomic_local_job', outcome['missing'])


if __name__ == '__main__':
    unittest.main()

"""Activation requirements and observation settings (``initialization``, ``observations``; layer 2).

A new instance comes from ``initialize_state`` with the fake clock, its profiles
from the product's ``build_profiles``; CLI identity comes from the fake host port.
"""
from copy import deepcopy
import tempfile
import unittest

from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles
from do_math.initialization import activation_requirements, initialize_state
from do_math.observations import observation_settings_errors, tracker_config
from support.fakes.clock import FakeClock
from support.fakes.host import FakeHost


class ObservationAdmissionTests(unittest.TestCase):
    def test_profile_role_mode_selection_and_tracker_binding_agree_for_every_produced_profile(self):
        """3-C/B-33: every configured mode and registered role/tier on real producers."""
        from do_math.execution_profiles import OBSERVATION_MODES, PROFILE_ROLES, WORK_ROLES, profile_ref
        from do_math.observations import bind_task_rules, observation_settings_used, task_rules_from_execution
        from support.observation_inputs import observation_rule
        from support.entry import entry
        profiles_seen = set()
        for mode in OBSERVATION_MODES:
            produced = build_profiles({**DEFAULT_CONFIG, 'observation_mode': mode,
                                      'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5},
                                      host=entry().ports.host)
            for profile in produced['execution_profiles'].values():
                with self.subTest(role=profile['role'], tier=profile.get('ai', {}).get('tier'), configured_mode=mode):
                    role = profile['role']
                    expected_mode = mode if role == 'research_work' else 'periodic' if role in WORK_ROLES else 'deadline_only'
                    self.assertEqual(profile['observation']['mode'], expected_mode)
                    research = role == 'research_work'
                    expected_settings = ([] if expected_mode == 'deadline_only' else
                                         ['tool_review_window_seconds', 'observation_interval_seconds'])
                    if research: expected_settings.append('self_check_response_window_seconds')
                    self.assertEqual(observation_settings_used(profile), expected_settings)
                    self.assertEqual(observation_settings_errors(profile), [])
                    rules = [observation_rule(operator='checkpoint_count_gte', subject_kind='checkpoint',
                                              subject_id='$execution')] if research else []
                    bound = bind_task_rules(rules, 'EX-finite-role') if research else []
                    config = tracker_config(profile, initial_self_check_rules=bound)
                    self.assertEqual(config['observation_mode'], expected_mode)
                    self.assertEqual(config['observation_profile_ref'], profile_ref(profile))
                    self.assertIs(config['research_self_checks'], research)
                    self.assertIs(config['checkpoint_expected'], research)
                    self.assertEqual(config['observation_rules'], bound)
                    if research: self.assertEqual(task_rules_from_execution(bound, 'EX-finite-role'), rules)
                    profiles_seen.add(role)
        self.assertEqual(profiles_seen, PROFILE_ROLES)

    def test_default_bootstrap_reports_exact_missing_settings_before_activation(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as root:
            instance, runtime = initialize_state(instance_id='RI-default', goal='A goal', workspace=root,
                                                 config=deepcopy(DEFAULT_CONFIG), source_input='Original request',
                                                 clock=FakeClock(), host=_entry.ports.host)
            instance.update(build_profiles(instance['config'], host=_entry.ports.host))
            result = activation_requirements(instance, runtime, host=FakeHost(), at=_entry.ports.clock.now(), clock=_entry.ports.clock)
            self.assertFalse(result['satisfied'])
            # The current role profiles are the adopted editions; no separate profile list is required.
            self.assertNotIn('profiles', result['missing'])
            self.assertIn('observation_configuration', result['missing'])
            errors = result['observation_errors']
            self.assertEqual({e['field'] for e in errors}, {'tool_review_window_seconds', 'self_check_response_window_seconds'})
            self.assertTrue(all(e['profile_id'] in instance['execution_profiles'] for e in errors))
            self.assertNotIn('intent_interpretation', {e['role'] for e in errors})
            self.assertIn('research_work', {e['role'] for e in errors})
            self.assertEqual(instance['lifecycle']['immutable_input']['text'], 'Original request')

    def test_configured_settings_do_not_require_task_rules_until_execution(self):
        from support.entry import entry
        _entry = entry()
        configured = build_profiles({**DEFAULT_CONFIG, 'tool_review_window_seconds': 60,
                                     'self_check_response_window_seconds': 5}, host=_entry.ports.host)
        self.assertTrue(configured['execution_profiles'])
        for profile in configured['execution_profiles'].values():
            with self.subTest(role=profile['role'], profile=profile['id']):
                self.assertEqual(observation_settings_errors(profile), [])
                if profile['role'] == 'research_work':
                    with self.assertRaisesRegex(ValueError, 'rules'):
                        tracker_config(profile)
                else:
                    self.assertIsInstance(tracker_config(profile), dict)

    def test_nonpositive_boolean_and_fractional_millisecond_values_are_rejected(self):
        from support.entry import entry
        _entry = entry()
        profile = next(p for p in build_profiles(DEFAULT_CONFIG, host=_entry.ports.host)['execution_profiles'].values()
                       if p['role'] == 'research_work')
        for value in (None, 0, -1, True, '0.0001', 'NaN'):
            with self.subTest(value=value):
                profile['observation']['settings'].update(tool_review_window_seconds=value,
                                                          self_check_response_window_seconds=5)
                self.assertEqual([e['field'] for e in observation_settings_errors(profile)], ['tool_review_window_seconds'])


AT = '2026-06-01T00:00:00+00:00'


def _instance():
    """A new instance with the product's default profiles and one AI profile's reference."""
    from support.entry import entry
    _entry = entry()
    instance, runtime = initialize_state(instance_id='RI-default', goal='A goal', workspace='work',
                                         config=deepcopy(DEFAULT_CONFIG), source_input='Original request', clock=FakeClock(), host=_entry.ports.host)
    instance.update(build_profiles(instance['config'], host=_entry.ports.host))
    profile = next(p for p in instance['execution_profiles'].values() if p['actor_kind'] == 'ai')
    return instance, runtime, profile


class OriginalInputTests(unittest.TestCase):
    def test_the_original_is_its_exact_text_bytes_and_hash(self):
        from do_math.governance import source_record
        from do_math.initialization import original_input_bytes
        self.assertEqual(original_input_bytes(source_record('Original request')), b'Original request')
        with self.assertRaisesRegex(ValueError, 'immutable input text is missing'):
            original_input_bytes({'sha256': '0' * 64})
        with self.assertRaisesRegex(ValueError, 'immutable input bytes or hash differs'):
            original_input_bytes({**source_record('Original request'), 'bytes': 1})

    def test_initialization_requires_a_nonempty_original(self):
        from support.entry import entry
        _entry = entry()
        for text in ('', '   ', None):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'initialization requires the original nonempty input'):
                initialize_state(instance_id='RI-x', goal='g', workspace='w', config={}, source_input=text, clock=FakeClock(), host=_entry.ports.host)

    def test_an_empty_original_is_missing_at_activation(self):
        from support.entry import entry
        _entry = entry()
        from do_math.governance import source_record
        instance, runtime, _ = _instance()
        self.assertNotIn('immutable_input', activation_requirements(instance, runtime, host=FakeHost(), at=_entry.ports.clock.now(), clock=_entry.ports.clock)['missing'])
        instance['lifecycle']['immutable_input'] = source_record('')
        self.assertIn('immutable_input', activation_requirements(instance, runtime, host=FakeHost(), at=_entry.ports.clock.now(), clock=_entry.ports.clock)['missing'])


class CapabilityRequirementTests(unittest.TestCase):
    def evidence(self, instance, reference, identity, observed_at, capabilities):
        row = {'id': 'CE-' + observed_at, 'execution_profile_ref': reference, 'identity': identity,
               'observed_at': observed_at, 'capabilities': capabilities}
        instance.setdefault('capability_evidence', {})[row['id']] = row
        return row

    def test_a_concrete_local_start_failure_is_not_cleared_by_later_help_output(self):
        from do_math.execution_profiles import profile_ref
        from do_math.initialization import capability_requirements
        instance, _, profile = _instance()
        reference = profile_ref(profile)
        identity = FakeHost().identity
        supported = {name: {'status': 'supported'} for name in profile['required_capabilities']}
        self.evidence(instance, reference, identity, '2026-05-01T00:00:00+00:00', {
            **supported, 'atomic_local_job': {'status': 'unsupported', 'scope': 'actual_local_start_failure'}})
        self.evidence(instance, reference, identity, '2026-05-02T00:00:00+00:00', {
            **supported, 'atomic_local_job': {'status': 'supported', 'scope': 'cli_command_surface_only'}})
        result = capability_requirements(instance, reference, at=AT, host=FakeHost())
        self.assertFalse(result['satisfied'])
        self.assertIn('atomic_local_job', result['missing'])
        self.assertEqual(result['evidence_refs'], ['CE-2026-05-01T00:00:00+00:00', 'CE-2026-05-02T00:00:00+00:00'])
        # Evidence observed after the checked time or of another identity does not count.
        early = capability_requirements(instance, reference, at='2026-04-01T00:00:00+00:00', host=FakeHost())
        self.assertEqual((early['satisfied'], early['evidence_refs']), (False, []))

    def test_a_stale_reference_is_unsatisfied_with_its_reason(self):
        from do_math.execution_profiles import profile_ref
        from do_math.initialization import capability_requirements
        instance, _, profile = _instance()
        stale = {**profile_ref(profile), 'sha256': '0' * 64}
        self.assertEqual(capability_requirements(instance, stale, at=AT, host=FakeHost()),
                         {'satisfied': False, 'missing': [], 'profile_ref': stale, 'reason': 'profile reference is absent or stale'})

    def test_a_machine_profile_needs_no_cli_evidence(self):
        from support.entry import entry
        _entry = entry()
        from do_math.execution_profiles import profile_ref
        from do_math.initialization import capability_requirements
        instance, _, _ = _instance()
        machine = next(p for p in instance['execution_profiles'].values() if p['actor_kind'] == 'machine')
        result = capability_requirements(instance, profile_ref(machine), at=AT, host=_entry.ports.host)
        self.assertEqual(result, {'satisfied': not machine.get('required_capabilities'),
                                  'missing': sorted(set(machine.get('required_capabilities', []))),
                                  'profile_ref': profile_ref(machine), 'evidence_refs': []})


class ProfileReferenceTests(unittest.TestCase):
    def test_a_stale_role_profile_reference_is_missing_profiles_and_a_repeated_one_is_checked_once(self):
        from support.entry import entry
        _entry = entry()
        from do_math.execution_profiles import profile_ref
        instance, runtime, profile = _instance()
        reference = profile_ref(profile)
        instance['role_profile_refs'] = {profile['role']: [reference, reference]}
        once = activation_requirements(instance, runtime, host=FakeHost(), at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.assertNotIn('profiles', once['missing'])
        self.assertEqual(len({(e['profile_id'], e['field']) for e in once['observation_errors']}),
                         len(once['observation_errors']))
        instance['role_profile_refs'][profile['role']].append({**reference, 'sha256': '0' * 64})
        self.assertIn('profiles', activation_requirements(instance, runtime, host=FakeHost(), at=_entry.ports.clock.now(), clock=_entry.ports.clock)['missing'])


class GrantTests(unittest.TestCase):
    NOW = FakeClock().wall()

    def grant(self, **changes):
        return {'kind': 'local', 'status': 'active', 'source_ref': 'S', 'roles': ['intent_interpretation'],
                'expires_at': '2026-02-01T00:00:00+00:00', 'reuse': 'reusable', **changes}

    def current(self, grant, *, initial, adoption=None):
        from do_math.initialization import grant_current
        instance = {'grants': {'GR-1': grant}, 'lifecycle': {'adoption': adoption or {}}}
        return grant_current(instance, 'GR-1', self.NOW, initial=initial)

    def test_an_initial_grant_is_a_current_reusable_local_grant_for_initial_roles(self):
        self.assertTrue(self.current(self.grant(), initial=True))
        for change in ({'kind': 'external'}, {'status': 'revoked'}, {'source_ref': ''}, {'expires_at': None},
                       {'roles': ['research_work']}, {'reuse': 'once'}, {'roles': []},
                       {'expires_at': '2025-12-31T00:00:00+00:00'}):
            with self.subTest(change=change):
                self.assertFalse(self.current(self.grant(**change), initial=True))

    def test_a_research_grant_is_not_an_initialization_grant(self):
        research = self.grant(roles=['research_work'], reuse='once')
        self.assertTrue(self.current(research, initial=False))
        self.assertFalse(self.current({**research, 'initialization_only': True}, initial=False))
        self.assertFalse(self.current(research, initial=False, adoption={'initial_grant_ids': ['GR-1']}))


if __name__ == '__main__':
    unittest.main()

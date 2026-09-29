"""Initialization controls on the real engine: configuration at ``initialize``, adoption and CLI capability probes.

The engine's initialization control (``initialization_engine``, layer 2) is
called on a Sim's engine where a case needs one exact change, and reached by
public controls where the case is the public path. CLI observation comes
from the host port; ``ObservedHost`` counts it and can fail it.
"""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import exact_content_hash
from do_math.execution_profiles import profile_ref
from do_math.initialization import _capability_batch_requirements, capability_requirements, observed_profile_refs
from support.fakes.host import FakeHost
from support.sim import Sim, warm_template

setUpModule = warm_template

WINDOWS = {'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}


class ObservedHost(FakeHost):
    """The fake host with counted CLI observations; ``failures`` raises at the given describe call numbers.

    ``per_profile`` gives each profile its own observation key, as distinct CLI
    installations would, so a batch observes profiles one by one.
    """

    def __init__(self, *, failures=(), per_profile=False, **facts):
        super().__init__(**facts)
        self.key_calls = self.identity_calls = self.describe_calls = 0
        self.failures, self.per_profile = set(failures), per_profile
        self.description = None

    def observations(self):
        """``(key, identity, describe)`` call counts: every CLI observation the host was asked for."""
        return self.key_calls, self.identity_calls, self.describe_calls

    def cli_observation_key(self, profile):
        self.key_calls += 1
        return ('fake', profile['id']) if self.per_profile else super().cli_observation_key(profile)

    def cli_identity(self, profile):
        self.identity_calls += 1
        return super().cli_identity(profile)

    def cli_describe(self, profile):
        self.describe_calls += 1
        if self.describe_calls in self.failures:
            raise RuntimeError('probe failed')
        return deepcopy(self.description) if self.description is not None else super().cli_describe(profile)


def _history_row(sim, request):
    return next(row for row in sim.runtime['history'] if row.get('request', {}).get('id') == request['request_id'])


class InitializeConfigurationTests(unittest.TestCase):
    def test_configuration_outside_the_current_contract_is_rejected_before_creating_an_instance(self):
        # The configuration section is closed: an undeclared key names no setting, and a declared one needs its type.
        for change, message in (({'invented_setting': 1}, 'outside the stored configuration section: invented_setting'),
                                ({'allowed_axioms': ['propext']}, 'outside the stored configuration section: allowed_axioms'),
                                ({'session_limits': None}, 'config/session_limits: None is not of type')):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaisesRegex(ValueError, message):
                    Sim(root, config=change)
                self.assertFalse((root / 'work').exists())
                self.assertEqual(list((root / 'repository' / '.git' / 'refs' / 'heads').iterdir()), [])


class ProbeBatchTests(unittest.TestCase):
    """An initializing instance with the product's default profiles; the probe control is called directly."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.host = ObservedHost()
        self.sim = Sim(directory.name, host=self.host)
        self.engine = self.sim.engine
        self.profiles = [p for p in self.engine.instance['execution_profiles'].values() if p['actor_kind'] == 'ai'][:2]

    def probe(self, **change):
        self.engine._initialization_control({'operation': 'probe', **change}, 'source')

    def test_activation_batch_reuses_only_the_current_provider_observation(self):
        references = [profile_ref(p) for p in self.profiles]
        identity = {'host': 'fixture'}
        self.host.identity = identity
        self.host.description = {'identity': identity, 'verified': True, 'scope': 'cli_command_surface_only',
                                 'supported': {'jsonl': True, 'model': True, 'structured_output': True}}
        self.probe(profile_refs=references)
        self.assertEqual(self.host.identity_calls, 0, 'a probe describes the CLI and asks for no identity')
        at = self.sim.clock.now()
        expected = [capability_requirements(self.engine.instance, ref, current_identity=identity, at=at)
                    for ref in references]
        actual = list(_capability_batch_requirements(self.engine.instance, references, at=at, host=self.host))
        self.assertEqual(actual, expected)
        self.assertEqual(self.host.identity_calls, 1)
        self.assertTrue(all(row['satisfied'] and row['evidence_refs'] for row in actual))
        self.host.identity = {'host': 'changed'}
        fresh = list(_capability_batch_requirements(self.engine.instance, references, at=at, host=self.host))
        self.assertEqual(self.host.identity_calls, 2)
        self.assertTrue(all(not row['satisfied'] and not row['evidence_refs'] for row in fresh))
        bad = dict(references[-1], sha256='0' * 64)
        stale, = _capability_batch_requirements(self.engine.instance, [bad], at=at, host=self.host)
        self.assertEqual(stale, {'satisfied': False, 'profile_ref': bad, 'reason': 'profile reference is absent or stale'})

    def test_batch_preserves_each_profile_and_observed_capability_scope(self):
        self.host.description = {'identity': {'host': 'fixture'}, 'verified': True,
                                 'scope': 'cli_command_surface_only', 'supported': {'jsonl': True, 'local_job': True}}
        self.probe(profile_refs=[profile_ref(p) for p in self.profiles])
        rows = list(self.engine.instance['capability_evidence'].values())
        self.assertEqual({row['execution_profile_ref']['id'] for row in rows}, {p['id'] for p in self.profiles})
        self.assertTrue(all(row['capabilities']['jsonl']['status'] == 'supported' for row in rows))
        self.assertTrue(all(row['capabilities']['local_job']['status'] == 'unknown' for row in rows))

    def test_invalid_reference_is_rejected_before_probing_or_mutating_evidence(self):
        with self.assertRaisesRegex(ValueError, 'profile reference is absent or stale'):
            self.probe(profile_refs=[profile_ref(self.profiles[0]), {'id': 'missing', 'revision': 1, 'sha256': 'a' * 64}])
        self.assertEqual(self.host.observations(), (0, 0, 0))
        self.assertFalse(self.engine.instance.get('capability_evidence'))

    def test_failed_later_observation_does_not_publish_partial_evidence(self):
        self.host.per_profile, self.host.failures = True, {2}
        self.host.description = {'identity': {'host': 'fixture'}}
        with self.assertRaisesRegex(RuntimeError, 'probe failed'):
            self.probe(profile_refs=[profile_ref(p) for p in self.profiles])
        self.assertEqual(self.host.describe_calls, 2)
        self.assertFalse(self.engine.instance.get('capability_evidence'))

    def test_probe_without_named_editions_observes_every_current_ai_role_profile(self):
        self.probe(config_sha256=exact_content_hash(self.engine.instance['config']))
        observed = {row['execution_profile_ref']['id'] for row in self.engine.instance['capability_evidence'].values()}
        current = {ref['id'] for ref in observed_profile_refs(self.engine.instance)
                   if self.engine.instance['execution_profiles'][ref['id']]['actor_kind'] == 'ai'}
        self.assertTrue(current)
        self.assertEqual(observed, current)

    def test_probe_without_named_editions_must_name_the_current_configuration(self):
        for change in ({}, {'config_sha256': '0' * 64}):
            with self.subTest(change=change), self.assertRaisesRegex(
                    ValueError, 'config_sha256 must name the current configuration'):
                self.probe(**change)
        self.assertEqual(self.host.observations(), (0, 0, 0))
        self.assertFalse(self.engine.instance.get('capability_evidence'))

    def test_a_probe_names_one_or_several_distinct_ai_editions(self):
        reference = profile_ref(self.profiles[0])
        machine = next(profile_ref(p) for p in self.engine.instance['execution_profiles'].values()
                       if p['actor_kind'] == 'machine')
        for change, message in (({'profile_ref': reference, 'profile_refs': [reference]}, 'profile_ref or profile_refs, not both'),
                                ({'profile_refs': []}, 'requires exact profile references'),
                                ({'profile_refs': [reference, reference]}, 'must be distinct'),
                                ({'profile_refs': [machine]}, 'requires AI profiles')):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, message):
                self.probe(**change)
        self.assertFalse(self.engine.instance.get('capability_evidence'))


class ActiveProbeTests(unittest.TestCase):
    """An active instance restored from the template."""

    def test_active_probe_refreshes_observation_without_adopting_contract(self):
        sim = Sim.activated()
        engine = sim.engine
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['actor_kind'] == 'ai')
        before = deepcopy(engine.instance)
        evidence = deepcopy(before.get('capability_evidence', {}))
        sim.advance(60)
        engine._initialization_control({'operation': 'probe', 'profile_ref': profile_ref(profile)}, 'source')
        added = set(engine.instance['capability_evidence']) - set(evidence)
        self.assertTrue(added)
        self.assertTrue(all(engine.instance['capability_evidence'][key]['execution_profile_ref'] == profile_ref(profile)
                            for key in added))
        self.assertEqual({k: v for k, v in engine.instance.items() if k != 'capability_evidence'},
                         {k: v for k, v in before.items() if k != 'capability_evidence'})
        for operation in ('adopt', 'governance'):
            with self.subTest(operation=operation), self.assertRaisesRegex(
                    ValueError, 'initialization adoption cannot replace an active contract'):
                engine._initialization_control({'operation': operation}, 'source')

    def test_user_refreshes_exact_active_profile_and_other_authority_is_rejected(self):
        sim = Sim.activated()
        engine = sim.engine
        self.assertEqual(engine.instance['lifecycle']['state'], 'active')
        before = deepcopy(engine.instance['lifecycle'])
        reference = deepcopy(engine.instance['role_profile_refs']['maintenance'][0])
        config = {'change': {'kind': 'initialization', 'operation': 'probe', 'profile_ref': reference}}
        with self.assertRaisesRegex(ValueError, 'operator controls are limited'):
            sim.control('decision', config=config, origin='operator')
        request = sim.control('decision', config=config)
        engine.process_controls()
        self.assertEqual(engine.control_result(request['request_id'])['effect'], 'applied')
        self.assertEqual(engine.instance['lifecycle'], before)
        rows = list(engine.instance['capability_evidence'].values())
        self.assertTrue(any(row['execution_profile_ref'] == reference for row in rows))
        evidence = deepcopy(engine.instance['capability_evidence'])
        bad = deepcopy(config)
        bad['change']['profile_ref']['sha256'] = '0' * 64
        request = sim.control('decision', config=bad)
        engine.process_controls()
        self.assertEqual(engine.control_result(request['request_id'])['effect'], 'rejected')
        self.assertIn('profile reference is absent or stale', _history_row(sim, request)['reason'])
        self.assertEqual(engine.instance['capability_evidence'], evidence)
        self.assertEqual(engine.instance['lifecycle'], before)
        _, stored, _ = engine.store.load()
        self.assertEqual(stored['capability_evidence'], evidence)


class ActivationEvidenceTests(unittest.TestCase):
    """The initial intent evidence and activation requirements of a publicly activated instance."""

    def setUp(self):
        self.sim = Sim.activated()
        self.engine = self.sim.engine

    def requirements(self):
        from do_math.initialization import activation_requirements
        return activation_requirements(self.engine.instance, self.engine.runtime, at=self.sim.clock.now(),
                                       owner_handlers=self.engine.governance_owner_handlers(), host=self.sim.ports.host)

    def test_the_applied_independent_import_is_the_initial_intent_evidence(self):
        from do_math.initialization import initial_intent_evidence
        instance, runtime = self.engine.instance, self.engine.runtime
        handlers = self.engine.governance_owner_handlers()
        evidence = initial_intent_evidence(instance, runtime, owner_handlers=handlers)
        self.assertEqual(evidence, instance['lifecycle']['intent_check'])
        self.assertEqual(self.requirements()['missing'], [])
        # A superseded or other input's import is passed over.
        runtime['intent_imports']['II-later'] = {'input_ref': instance['lifecycle']['input_id'], 'superseded_by': 'II-x'}
        runtime['intent_imports']['II-other'] = {'input_ref': 'UI-other'}
        self.assertEqual(initial_intent_evidence(instance, runtime, owner_handlers=handlers), evidence)
        checker = runtime['executions'][evidence['check_execution_id']]
        checker['intent_import_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'initial interpretation execution evidence does not resolve'):
            initial_intent_evidence(instance, runtime, owner_handlers=handlers)
        self.assertIn('independent_intent', self.requirements()['missing'])

    def test_a_changed_intent_receipt_or_unadopted_review_policy_is_missing(self):
        """About 3.5 s, over the 2 s Sim budget: two template restores, one for each changed record."""
        lifecycle = self.engine.instance['lifecycle']
        lifecycle['intent_check'] = {**lifecycle['intent_check'], 'check_execution_id': 'EX-other'}
        self.assertEqual(self.requirements()['missing'], ['independent_intent'])
        self.sim = Sim.activated()
        self.engine = self.sim.engine
        self.engine.instance['lifecycle']['adoption']['review_policy_sha256'] = '0' * 64
        self.assertEqual(self.requirements()['missing'], ['review_policy'])

    def test_the_working_view_is_the_instance_with_its_governance_fields(self):
        from do_math.governance import governance_view
        from do_math.initialization import governance_working_view
        instance = self.engine.instance
        view = governance_working_view(instance)
        charter = governance_view(instance)['charter']
        self.assertEqual(view, {**instance, **governance_view(instance)})
        self.assertEqual((view['goal'], view['goal_revision'], view['id']),
                         (charter['content']['goal'], charter['revision'], instance['id']))
        self.assertNotIn('goal', instance)

    def test_completing_another_input_is_not_the_initial_intent(self):
        self.assertFalse(self.engine._complete_initial_intent('UI-other'))


class InitialAdoptionTests(unittest.TestCase):
    """Adoption fields on an initializing instance whose windows are configured; grants arrive by public control."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.sim = Sim(directory.name, config=WINDOWS)
        self.engine = self.sim.engine

    def grant(self, identifier, roles):
        expiry = (self.sim.clock.wall() + timedelta(days=1)).isoformat()
        self.sim.control('decision', text='grant', config={'change': {'kind': 'grant', 'grant': {
            'id': identifier, 'kind': 'local', 'roles': roles, 'reuse': 'reusable', 'expires_at': expiry}}})
        self.engine.process_controls()
        self.assertIn(identifier, self.engine.instance['grants'])

    def adopt(self, **change):
        self.engine._initialization_control(change, 'UI-adopt')

    def test_each_adoption_field_refuses_what_it_does_not_name(self):
        research = next(profile_ref(p) for p in self.engine.instance['execution_profiles'].values()
                        if p['role'] == 'research_work')
        cases = [({'operation': 'other'}, 'initialization operation must be governance, adopt or probe'),
                 ({'operation': 'governance', 'records': []}, 'exact user-approved governance records required'),
                 ({'conversation_loss_policy': 'ask'}, 'explicit conversation loss policy required'),
                 ({'external_policy': 'open'}, 'external policy must be disabled or explicit_grants'),
                 ({'initial_profile_ref': research}, 'initial profile must permit intent_interpretation'),
                 ({'initial_grant_ids': []}, 'initial_grant_ids must be nonempty'),
                 ({'research_grant_ids': ['GR-absent']}, 'grant is absent, stale or outside initialization scope: GR-absent')]
        for change, message in cases:
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, message):
                self.adopt(**change)
        self.assertEqual(self.engine.instance['lifecycle']['adoption'], {})

    def test_initial_and_research_authority_use_distinct_grants(self):
        self.grant('GR-both', ['intent_interpretation'])
        with self.assertRaisesRegex(ValueError, 'initial and research authority must use distinct grants'):
            self.adopt(initial_grant_ids=['GR-both'], research_grant_ids=['GR-both'])
        self.assertEqual(self.engine.instance['lifecycle']['adoption'], {})

    def test_a_repeated_adoption_names_its_source_once_and_records_each_decision(self):
        self.adopt(conversation_loss_policy='pause')
        self.adopt(external_policy='disabled')
        adoption = self.engine.instance['lifecycle']['adoption']
        self.assertEqual((adoption['source_refs'], adoption['external_policy']), (['UI-adopt'], 'disabled'))
        self.assertEqual(self.engine.instance['conversation_loss_policy'], 'pause')
        decisions = [row for row in self.engine.instance['decisions'].values() if row['kind'] == 'initialization']
        self.assertEqual([row['change'] for row in decisions], [{'conversation_loss_policy': 'pause'},
                                                               {'external_policy': 'disabled'}])

    def test_initial_retries_pass_over_empty_and_undiagnosed_waits(self):
        waits = {'AC-empty': {}, 'AC-held': {'kind': 'output_validation', 'diagnosis': {'decision': 'wait'}}}
        self.engine.runtime['waiting_actions'] = deepcopy(waits)
        history = list(self.engine.runtime['history'])
        self.engine.continue_initial_retries()
        self.assertEqual(self.engine.runtime['waiting_actions'], waits)
        self.assertEqual(self.engine.runtime['history'], history)

    def test_the_initial_interpretation_waits_for_its_profile_evidence_grant_and_open_import(self):
        def interpretations():
            return [a for a in self.engine.runtime['queue'] if a['role'] == 'intent_interpretation']
        from do_math.model_policy import selection
        # A public control reloads the published state, so it comes before the direct, unsaved adoption steps.
        self.grant('GR-initial', ['intent_interpretation'])
        instance = self.engine.instance
        reference = selection(instance['config'], {'role': 'intent_interpretation'}, {}, instance['knowledge'],
                              instance=instance)['profile_ref']
        self.adopt(initial_profile_ref=reference)
        self.assertEqual(interpretations(), [], 'no capability evidence yet')
        self.adopt(operation='probe', config_sha256=exact_content_hash(self.engine.instance['config']))
        self.adopt(initial_profile_ref=reference)
        self.assertEqual(interpretations(), [], 'no initial grant adopted yet')
        self.engine.runtime['intent_imports'] = {'II-open': {'input_ref': self.engine.instance['lifecycle']['input_id'],
                                                             'application': {'status': 'awaiting_decision'}}}
        self.adopt(initial_grant_ids=['GR-initial'])
        self.assertEqual(interpretations(), [], 'an import awaits its decision')
        self.engine.runtime['intent_imports'] = {}
        self.engine._queue_initial_intent()
        queued, = interpretations()
        self.assertEqual((queued['target'], queued['profile_ref']), (self.engine.instance['lifecycle']['input_id'], reference))
        self.engine._queue_initial_intent()
        self.assertEqual(len(interpretations()), 1)


class AdoptionTests(unittest.TestCase):
    """Adoption on an initializing instance whose configuration lacks the observation windows (the product default)."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.sim = Sim(self.root)
        self.engine = self.sim.engine

    def test_adopting_a_configuration_whose_role_profiles_lack_settings_is_rejected(self):
        config = self.engine.instance['config']
        with self.assertRaisesRegex(ValueError, 'observation_configuration.*research_work'):
            self.engine._initialization_control({'config_sha256': exact_content_hash(config)}, 'UI-settings')
        self.assertNotIn('config_sha256', self.engine.instance['lifecycle']['adoption'])

    def test_adoption_of_a_configuration_other_than_the_current_one_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'config_sha256 must name the current configuration'):
            self.engine._initialization_control({'config_sha256': '0' * 64}, 'UI-stale')
        self.assertNotIn('config_sha256', self.engine.instance['lifecycle']['adoption'])

    def test_adoption_takes_no_profile_list(self):
        reference = self.engine.instance['role_profile_refs']['research_work'][0]
        with self.assertRaisesRegex(ValueError, 'adoption binds the current role profiles.*profile_refs'):
            self.engine._initialization_control({'profile_refs': [reference]}, 'UI-profiles')
        self.assertEqual(self.engine.instance['lifecycle']['adoption'], {})

    def test_public_default_init_rejects_unready_adoption_then_adopts_the_configured_one(self):
        sim, engine = Sim(self.root / 'public', goal='Preserve this original'), None
        engine = sim.engine
        old = deepcopy(engine.instance['role_profile_refs']['research_work'][0])
        # The operator reads the hash of the configuration it inspected from status.
        unready = engine.status()['config_sha256']
        request = sim.control('decision', config={'change': {'kind': 'initialization', 'config_sha256': unready}})
        engine.process_controls()
        rejected = next(h for h in engine.runtime['history'] if h.get('kind') == 'rejected_user_control'
                        and h['request']['id'] == request['request_id'])
        self.assertIn('tool_review_window_seconds', rejected['reason'])
        self.assertIn('self_check_response_window_seconds', rejected['reason'])
        self.assertEqual(engine.instance['lifecycle']['state'], 'initializing')
        sim.control('configure', config=WINDOWS)
        engine.process_controls()
        fresh = deepcopy(engine.instance['role_profile_refs']['research_work'][0])
        self.assertNotEqual(fresh, old)
        configured = engine.status()['config_sha256']
        self.assertNotEqual(configured, unready)
        second = sim.control('decision', config={'change': {'kind': 'initialization', 'config_sha256': configured}})
        self.assertNotEqual(second['request_id'], request['request_id'])
        engine.process_controls()
        self.assertEqual(engine.control_result(second['request_id'])['effect'], 'applied')
        self.assertEqual(engine.instance['lifecycle']['adoption']['config_sha256'],
                         exact_content_hash(engine.instance['config']))
        self.assertIn(old['id'], engine.instance['execution_profiles'])
        self.assertEqual(engine.instance['lifecycle']['immutable_input']['text'], 'Preserve this original')
        self.assertEqual(engine.runtime['executions'], {})


if __name__ == '__main__':
    unittest.main()

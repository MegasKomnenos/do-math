"""Profile/configuration and acquired reservation outputs meet actual storage contracts."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math import execution_profiles as profiles
from do_math.canonical import canonical_json
from do_math.configuration import DEFAULT_CONFIG
from do_math.engine import ResearchEngine
from do_math.model_policy import TIERS
from do_math.state_contract import default_state_contract
from support.storage_profile_pairs import acquire_profile, acquire_roles, family_receiver, profile_cases, profile_pairs


class StorageProfilePairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.cases = profile_cases(cls.root / 'inputs')

    def test_every_object_family_field_has_an_actual_producer_and_receiver(self):
        for pair in profile_pairs(self.cases):
            written = set()
            samples = pair.samples(self.root)
            self.assertTrue(samples, pair.name)
            for branch, value in samples:
                with self.subTest(family=pair.name, branch=branch):
                    pair.receive(value)
                    written.update(pair.written(value))
            self.assertEqual(written, pair.fields, pair.name)

    def test_stored_profiles_preserve_independent_settings_and_role_branches(self):
        """About 0.4 s: four stored sets of 37 profiles, with independent settings and SHA checks."""
        for case in self.cases:
            with self.subTest(branch=case.name):
                _, instance, runtime = case.store.load(case.head)
                self.assertEqual(runtime['reservations'], {})
                config = instance['config']
                for field, expected in {**DEFAULT_CONFIG, **case.patch}.items():
                    if field != 'host_resources':
                        self.assertEqual(config[field], expected, field)
                self.assertEqual(set(instance['role_profile_refs']), profiles.PROFILE_ROLES)
                for role, refs in instance['role_profile_refs'].items():
                    machine = role in profiles.MACHINE_ROLES
                    self.assertEqual(len(refs), 1 if machine else len(TIERS))
                    for reference in refs:
                        p = instance['execution_profiles'][reference['id']]
                        self.assertEqual({key: p[key] for key in reference}, reference)
                        body = {key: value for key, value in p.items() if key not in {'id', 'sha256'}}
                        raw = canonical_json(body)
                        self.assertEqual(p['sha256'], hashlib.sha256(raw).hexdigest())
                        self.assertEqual(p['id'], 'EP-' + p['sha256'])
                        self.assertEqual((p['role'], p['actor_kind']), (role, 'machine' if machine else 'ai'))
                        self.assertEqual(p['input']['max_input_bytes'], config['max_input_bytes'])
                        self.assertEqual(p['window']['call_timeout_seconds'], config[
                            'operator_timeout_seconds' if role == 'recovery' else 'call_timeout_seconds'])
                        expected_mode = (config['observation_mode'] if role == 'research_work' else
                                         'periodic' if role in profiles.WORK_ROLES else 'deadline_only')
                        self.assertEqual(p['observation']['mode'], expected_mode)
                        self.assertEqual(p['observation']['settings'],
                            {key: config[key] for key in profiles.OBSERVATION_KEYS if key in config})
                        if machine:
                            self.assertNotIn('ai', p)
                            if role in profiles.LEAN_ROLES:
                                self.assertEqual(p['machine']['lean_command'],
                                    config['lean_command'] or case.inputs.ports.host.lean)
                            else:
                                self.assertNotIn('machine', p)
                        else:
                            ai = p['ai']
                            self.assertEqual(ai['provider'], 'claude' if case.name.startswith('claude') else 'codex')
                            self.assertEqual(ai['model'], config['tier_models'][ai['tier']])
                            self.assertEqual(ai['effort'], config['operator_effort'] if role == 'recovery' else config['effort'])
                            self.assertEqual(ai['claude_only_assigned_model'], config['claude_only_assigned_model'])
                            self.assertEqual(ai['scholarly_server'], config['scholarly_server'] if config['scholarly_enabled'] else None)
                            self.assertEqual(len(ai['capacity_refs']), int(role in profiles.WORK_ROLES))
                        hosted = bool(config.get('host_resources')) and role in profiles.HOST_ROLES
                        self.assertEqual('host_resources' in p, hosted)
                        self.assertEqual(p['host_capacity_refs'], [instance['host_capacity_ref']] if hosted else [])

    def test_scalar_host_reference_preserves_bound_authority_and_absence(self):
        family = default_state_contract().family('research', 'host_capacity_ref')
        receive = family_receiver(family)
        for case in self.cases:
            instance = case.instance
            with self.subTest(branch=case.name):
                if not case.patch.get('host_resources'):
                    self.assertNotIn('host_capacity_ref', instance)
                    continue
                reference = instance['host_capacity_ref']
                receive(reference)
                constraint = instance['capacity_constraints'][reference]
                requested = case.patch['host_resources']['constraint']
                self.assertEqual((constraint['scope'], constraint['host_id']), ('instance_on_host', case.inputs.host_id))
                for key in ('max_jobs', 'memory_bytes', 'cpu_rate_basis_points', 'control_reserve'):
                    self.assertEqual(constraint[key], requested[key])
                self.assertNotIn('configuration:request', constraint['authority_refs'])
                self.assertEqual(instance['config']['host_resources']['constraint'], constraint)
                for ref in constraint['authority_refs']:
                    source = instance['governance_sources'][ref]
                    self.assertEqual(source['origin'], 'user')
                    original = json.loads(source['text'])['host_resources']
                    self.assertEqual(original, case.patch['host_resources'])
                    self.assertEqual(source['sha256'], hashlib.sha256(source['text'].encode('utf-8')).hexdigest())

    def test_actual_acquire_and_release_preserve_zero_one_and_many_reservations(self):
        """About 0.8 s: six real initialize/admit/settle storage branches; no native Job starts."""
        family = default_state_contract().family('runtime', 'reservations')
        receive, written, sizes = family_receiver(family), set(), set()
        base, hosted = self.cases[:2]
        scenes = [(base, ['maintenance'], set()), (base, ['research_work'], {'execution'}),
                  (hosted, ['trust_check'], set()),
                  (hosted, ['external_action'], {'jobs', 'memory_bytes', 'cpu_rate_basis_points'}),
                  (hosted, ['research_work'], {'execution', 'jobs', 'memory_bytes', 'cpu_rate_basis_points'}),
                  (hosted, ['research_work', 'maintenance'],
                   {'execution', 'jobs', 'memory_bytes', 'cpu_rate_basis_points'})]
        for index, (case, roles, units) in enumerate(scenes):
            with self.subTest(roles=roles, host=case.name):
                store, slots, head, instance, runtime = acquire_roles(self.root / f'admit-{index}', case, roles)
                loaded = store.load(head)[2]
                self.assertEqual(loaded['reservations'], runtime['reservations'])
                sizes.add(len(loaded['reservations']))
                self.assertEqual({row['unit'] for row in loaded['reservations'].values()}, units)
                for row in loaded['reservations'].values():
                    receive(row)
                    written.update(row)
                    execution = loaded['executions'][row['owner_id']]
                    self.assertIn(row['id'], execution['capacity']['reservation_ids'])
                    self.assertEqual(row['authority_refs'], [execution['execution_profile_ref']])
                    self.assertEqual((row['owner_kind'], row['purpose'], row['state']), ('execution', 'normal', 'held'))
                    amount = {'execution': 1, 'jobs': 1, 'memory_bytes': 134217728,
                              'cpu_rate_basis_points': 2000}[row['unit']]
                    self.assertEqual((row['reserved'], row['confirmed_consumed'], row['returned']), (amount, 0, 0))
                    constraint = instance['capacity_constraints'][row['constraint_id']]
                    self.assertEqual(constraint['kind'], 'concurrency' if row['unit'] == 'execution' else 'host')
                for eid in runtime['executions']:
                    self.assertTrue(slots.release(eid))
                settled = store.save_with_state(head, instance, runtime)[0]
                after = store.load(settled)[2]['reservations']
                for row in after.values():
                    receive(row)
                    written.update(row)
                    self.assertEqual((row['state'], row['confirmed_consumed'], row['returned']), ('settled', 0, row['reserved']))
                    self.assertNotIn('reobserve', row)
                    self.assertEqual(row['evidence_refs'][0]['kind'], 'never_resumed')
                self.assertEqual(store.load(head)[2]['reservations'], loaded['reservations'])
                self.assertEqual(case.inputs.ports.jobs.launched, [])
        self.assertEqual(sizes, {0, 1, 3, 4, 7})
        self.assertEqual(written, set(family.schema['properties']))

    def test_configure_keeps_pinned_execution_but_new_reservation_uses_adopted_capacity(self):
        """About 0.4 s: real acquire/configure/reacquire publications and historical snapshot reads."""
        case = self.cases[0]
        store, _, head, instance, runtime = acquire_roles(self.root / 'configure', case, ['research_work'])
        engine = ResearchEngine(store.repository, instance['id'], ports=case.inputs.ports,
            codex_home=case.inputs.codex_home, environment=case.inputs.environment, host_id=case.inputs.host_id)
        old = deepcopy(runtime['executions']['EX-profile-0']['execution_profile_ref'])
        patch = {'call_timeout_seconds': 731, 'session_limits': deepcopy(instance['config']['session_limits'])}
        model = instance['execution_profiles'][old['id']]['ai']['model']
        patch['session_limits']['work'][model] = 1
        changed, state = engine._configure_candidate(engine.instance, engine.runtime, {'config': patch, 'origin': 'user'})
        saved = store.save_with_state(head, changed, state)[0]
        _, adopted, loaded = store.load(saved)
        self.assertEqual(adopted['config']['call_timeout_seconds'], 731)
        self.assertEqual(loaded['executions']['EX-profile-0']['execution_profile_ref'], old)
        self.assertEqual(adopted['execution_profiles'][old['id']]['window']['call_timeout_seconds'], 600)
        self.assertEqual(loaded['reservations'], runtime['reservations'])
        selected = [adopted['execution_profiles'][ref['id']] for ref in adopted['role_profile_refs']['research_work']]
        self.assertTrue(all(p['window']['call_timeout_seconds'] == 731 for p in selected))
        current = next(p for p in selected if p['ai']['model'] == model)
        from do_math.session_slots import SessionSlots
        slots = SessionSlots(loaded, adopted, clock=case.inputs.ports.clock,
            jobs=case.inputs.ports.jobs, host_id=case.inputs.host_id)
        before = deepcopy(loaded)
        self.assertFalse(slots.admission_check(adopted['execution_profiles'][old['id']])['allowed'])
        self.assertEqual(slots.admission_wait['constraint_id'], current['ai']['capacity_refs'][0])
        self.assertEqual(loaded, before)
        self.assertTrue(slots.release('EX-profile-0'))
        execution = acquire_profile(slots, adopted, loaded, old, index=1)
        final = store.save_with_state(saved, adopted, loaded)[0]
        restored = store.load(final)[2]
        self.assertEqual(restored['executions'][execution['id']]['execution_profile_ref'], old)
        new_row, = [row for row in restored['reservations'].values() if row['owner_id'] == execution['id']]
        self.assertEqual(new_row['constraint_id'], current['ai']['capacity_refs'][0])
        self.assertEqual(new_row['authority_refs'], [old])
        self.assertEqual((new_row['reserved'], new_row['state']), (1, 'held'))
        self.assertEqual(store.load(head)[1]['config']['call_timeout_seconds'], 600)


if __name__ == '__main__':
    unittest.main()

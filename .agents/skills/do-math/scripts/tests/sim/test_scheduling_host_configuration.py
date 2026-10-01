"""Host resource configuration on the real engine, and the host-bound runner's start contract.

A user's host approval enters by the public ``initialize`` or ``configure``;
``_configure_candidate`` (``governance_engine``) is the one transition both
apply. It authors the profile editions once per step, refuses an operator's
change of a user decision and any host change while an execution is live,
and keeps the approval record when the approval is removed. The cases run on
a Sim's real engine and storage; build calls are observed on the unchanged
product (``ObservedCalls``). ``HostRunnerTests`` calls the model runner
(``model_runner``, layer 3) on the Jobs and clock port fakes.
"""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

from do_math import execution_profiles
from do_math.configuration import DEFAULT_CONFIG
from do_math.contracts import task_candidate_record
from do_math.initialization import initialize_state
from do_math.model_runner import ModelRunner
from support.provider_inputs import host_capacity_fixture
from support.role_answers import candidate
from support.fakes.clock import FakeClock
from support.fakes.jobs import FakeJobs
from support.provider_probes import ObservedCalls
from support.scheduling_hosts import dispatched, host_configuration
from support.sim import Sim, warm_template

setUpModule = warm_template
LEAN_ROLES = {'formal_check', 'trust_check', 'trust_activate'}


class HostConfigurationTests(unittest.TestCase):
    def test_unstarted_role_defaults_refresh_while_task_profiles_require_preparation(self):
        from support.entry import entry
        _entry = entry()
        engine = Sim.activated().engine
        with tempfile.TemporaryDirectory() as directory:
            config = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}
            instance, runtime = initialize_state(instance_id='RI-host-change', goal='Test profiles',
                                                 workspace=Path(directory), config=config,
                                                 source_input='Test profiles', created_at='2026-09-23T00:00:00Z', clock=_entry.ports.clock, host=_entry.ports.host)
            instance.update(execution_profiles.build_profiles(config, host=_entry.ports.host))
            old = deepcopy(instance['role_profile_refs']['maintenance'][0])
            wire = candidate()
            wire['profile_refs'] = [deepcopy(instance['role_profile_refs']['research_work'][0])]
            task = task_candidate_record(wire, task_id='TK-pinned')
            task.update(status='planned', results=[], reviews=[])
            runtime['tasks'][task['id']] = task
            runtime['queue'] = [{'id': 'AC-default', 'role': 'maintenance', 'profile_ref': old}]
            changed, state = engine._configure_candidate(instance, runtime,
                                                         {'config': {'host_resources': host_configuration()['host_resources']}})
            self.assertIn('host_capacity_ref', changed)
            pending = next(a for a in state['queue'] if a['id'] == 'AC-default')
            self.assertNotEqual(pending['profile_ref'], old)
            self.assertEqual(state['tasks'][task['id']]['profile_refs'], task['profile_refs'])
            self.assertTrue(any(task['id'] in a.get('revision_targets', {}) for a in state['queue']))

    def test_public_init_configure_and_removal(self):
        settings = host_configuration()
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(Path(directory), goal='Temporary configuration test', config=settings)
            store = sim.engine.store
            head, instance, runtime = store.load()
            host_id = instance['host_capacity_ref']
            approval = instance['capacity_constraints'][host_id]['authority_refs'][0]
            self.assertEqual(instance['governance_sources'][approval]['origin'], 'user')
            self.assertNotEqual(approval, 'configuration:request')
            engine = sim.engine
            same, state = engine._configure_candidate(instance, runtime, {'config': {'host_resources': settings['host_resources']}})
            self.assertEqual(same['host_capacity_ref'], host_id)
            with self.assertRaisesRegex(ValueError, 'user'):
                engine._configure_candidate(instance, runtime, {'origin': 'operator', 'config': {'host_resources': None}})
            # Public admission refuses the same operator change instead of queueing a request application rejects.
            with self.assertRaisesRegex(ValueError, 'user decision'):
                sim.control('configure', config={'host_resources': None}, origin='operator')
            held = deepcopy(runtime)
            held['executions']['EX-live'] = {'id': 'EX-live', 'status': 'queued'}
            with self.assertRaisesRegex(ValueError, 'stopped'):
                engine._configure_candidate(instance, held, {'config': {'host_resources': None}})
            removed, state = engine._configure_candidate(instance, runtime, {'config': {'host_resources': None}})
            self.assertNotIn('host_capacity_ref', removed)
            self.assertIn(host_id, removed['capacity_constraints'])
            saved = store.save_with_state(head, removed, state)[0]
            self.assertIsNone(store.load(saved)[1]['config']['host_resources'])
            for profile in same['execution_profiles'].values():
                if profile['role'] in LEAN_ROLES:
                    self.assertNotIn('host_resources', profile)

    def test_host_configuration_builds_profiles_once_per_step(self):
        # Admission only checks the host section; initialization and application each author the editions once.
        settings = host_configuration()
        request = {'host_resources': settings['host_resources']}
        with tempfile.TemporaryDirectory() as directory:
            with ObservedCalls(build=execution_profiles.build_profiles) as built:
                sim = Sim(Path(directory), goal='Profile count test', config=settings)
            self.assertEqual(built.count('build'), 1)
            head, instance, runtime = sim.engine.store.load()
            with ObservedCalls(build=execution_profiles.build_profiles) as built:
                sim.control('configure', config=request)
            self.assertEqual(built.count('build'), 0)
            with ObservedCalls(build=execution_profiles.build_profiles) as built:
                sim.engine._configure_candidate(instance, runtime, {'config': request})
            self.assertEqual(built.count('build'), 1)


class HostRunnerTests(unittest.TestCase):
    def test_host_bound_runner_requires_start_publication_callback(self):
        from support.entry import entry
        _entry = entry()
        _, selected, _ = host_capacity_fixture()
        p = selected["research_work"]
        prompt = execution_profiles.prepare_prompt("test", p)
        jobs, clock = FakeJobs(), FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "work"
            workspace.mkdir()
            with self.assertRaisesRegex(ValueError, "host-bound runner requires on_started publication before resume"):
                ModelRunner(codex_path=sys.executable, jobs=jobs, clock=clock, environment=_entry.environment, host_id=_entry.host_id).run(
                    prompt=prompt, input_seal=execution_profiles.prompt_seal(prompt), output_schema={},
                    workspace=workspace, evidence_dir=root / "evidence", model=p["ai"]["model"],
                    effort=p["ai"]["effort"], timeout_seconds=15, execution_id="EX-no-callback", profile=p,
                    launch_ticket=dispatched('EX-no-callback', p, jobs=jobs, clock=clock))
            self.assertFalse((root / "evidence").exists())
            self.assertEqual(jobs.launched, [], "no Job was created")


if __name__ == '__main__':
    unittest.main()

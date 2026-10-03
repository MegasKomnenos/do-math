"""Layer-3 toolchain code run directly: the host's identity observation, the setup tool's request and evidence
rules, the compiler Job's environment, and the registration and adoption results on the Sim.

The identity observation is the real host port implementation (``formal``,
behind ``local_host.LocalHost``) over real files; it starts no process here.
``setup_lean`` is called only where it reaches no Lean and no Job.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import setup_lean
from do_math import formal, trust_inventory as records
from do_math.initialization import observation_window_warnings
from support.trust_inputs import trust_fixture
from support.sim import Sim

WINDOWS = {'tool_review_window_seconds': 120, 'self_check_response_window_seconds': 60}


class HostIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.request = trust_fixture(self.root, ['synthetic-lean'])

    def test_identity_detects_executable_checker_and_project_input_changes(self):
        from support.entry import entry
        _entry = entry()
        toolchain_identity_errors = formal.toolchain_identity_errors
        self.assertEqual(toolchain_identity_errors(self.request['toolchain'], clock=_entry.ports.clock, jobs=_entry.ports.jobs, environment=_entry.environment, git_backend=_entry.ports.git_backend), [])
        # Each recorded hash holds on its own, even when the executable is also a command file.
        wrong = {**self.request['toolchain'], 'sha256': '0' * 64}
        self.assertEqual(toolchain_identity_errors(wrong, clock=_entry.ports.clock, jobs=_entry.ports.jobs, environment=_entry.environment, git_backend=_entry.ports.git_backend),
                         ['approved toolchain file changed: ' + self.request['toolchain']['executable']])
        lake = Path(self.request['toolchain']['executable']).with_name('lake.exe')
        lake.write_bytes(b'replaced by an update')
        self.assertEqual(toolchain_identity_errors(self.request['toolchain'], clock=_entry.ports.clock, jobs=_entry.ports.jobs, environment=_entry.environment, git_backend=_entry.ports.git_backend),
                         ['approved toolchain file changed: ' + str(lake)])
        # The checker is its running bytes: a copy elsewhere is the same checker,
        # other recorded bytes are not.
        copy = self.root / 'formal.py'
        copy.write_bytes(Path(self.request['toolchain']['verifier_path']).read_bytes())
        moved = {**self.request['toolchain'], 'verifier_path': str(copy)}
        lake_changed = 'approved toolchain file changed: ' + str(lake)
        self.assertEqual(toolchain_identity_errors(moved, clock=_entry.ports.clock, jobs=_entry.ports.jobs, environment=_entry.environment, git_backend=_entry.ports.git_backend), [lake_changed])
        copy.write_bytes(b'another checker')
        other = {**moved, 'verifier_sha256': hashlib.sha256(b'another checker').hexdigest()}
        self.assertEqual(toolchain_identity_errors(other, clock=_entry.ports.clock, jobs=_entry.ports.jobs, environment=_entry.environment, git_backend=_entry.ports.git_backend), ['approved checker is not the running checker', lake_changed])
        project = self.root / 'project'
        project.mkdir()
        (project / 'lean-toolchain').write_text('leanprover/lean4:v4.32.0\n', encoding='utf-8')
        (project / 'lake-manifest.json').write_text('{"packages": []}', encoding='utf-8')
        command = ['lake', '--dir', str(project), 'env', 'lean']
        with tempfile.TemporaryDirectory() as workspace:
            observed = formal._project_identity(command, workspace=Path(workspace),
                                                expected={'manifest_hashes': None, 'source_identity': None}, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
        self.assertEqual(observed['search_paths'], [])
        lake.write_bytes(('CORE_TESTS synthetic bin/lake.exe for synthetic-lean').encode())
        for name, text in (('lean-toolchain', 'leanprover/lean4:v4.33.0\n'), ('lake-manifest.json', '{"packages": [1]}')):
            with self.subTest(name=name):
                original = (project / name).read_bytes()
                (project / name).write_text(text, encoding='utf-8')
                chain = {**self.request['toolchain'], 'configured_command': command, 'project': observed}
                self.assertEqual(toolchain_identity_errors(chain, clock=_entry.ports.clock, jobs=_entry.ports.jobs, environment=_entry.environment, git_backend=_entry.ports.git_backend), ['approved project inputs changed'])
                (project / name).write_bytes(original)


class SetupToolTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_trust_request_names_the_record_and_its_current_baseline(self):
        request = trust_fixture(self.root, ['synthetic-lean'])
        record_path = Path(request['toolchain_record']['path'])
        result = {'record_path': str(record_path), 'binding': records.binding(records.read_record(record_path))}
        written = setup_lean.write_trust_request(result, self.root / 'request.json')
        self.assertEqual(json.loads(Path(written['path']).read_text(encoding='utf-8')), request)
        self.assertEqual((written['toolchain_record'], written['binding']), (request['toolchain_record'], request['binding']))
        with self.assertRaisesRegex(FileExistsError, 'request.json'):
            setup_lean.write_trust_request(result, self.root / 'request.json')

    def test_evidence_inside_a_recorded_root_is_rejected(self):
        from support.entry import entry
        _entry = entry()
        identity = {'executable': str(self.root / 'lean/bin/lean.exe'), 'project': None}
        with self.assertRaisesRegex(ValueError, 'validation evidence must be outside the recorded toolchain and project roots'):
            setup_lean.verify_environment(['test-lean'], self.root / 'lean/evidence', identity, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs)
        self.assertFalse((self.root / 'lean').exists())


class RecordingJobs:
    """A Jobs port that records the launch and stops the run there, before any program starts."""

    def __init__(self):
        self.launches = []

    def launch(self, argv, *, cwd=None, env=None, name=None, resource_limits=None):
        self.launches.append({'argv': list(argv), 'env': dict(env or {}), 'name': name})
        raise RuntimeError('observe job arguments')


class CompilerJobTests(unittest.TestCase):
    def test_compiler_job_does_not_inherit_unregistered_library_overrides(self):
        from support.entry import entry
        _entry = entry()
        jobs = RecordingJobs()
        overrides = {'LEAN_PATH': 'outside', 'LEAN_SYSROOT': 'outside', 'LAKE_HOME': 'outside', 'ELAN_HOME': 'outside'}
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', overrides):
            with self.assertRaisesRegex(RuntimeError, 'observe job arguments'):
                formal._job_run(['unused-compiler'], Path(directory), jobs=jobs, clock=_entry.ports.clock, environment=_entry.environment)
        launch, = jobs.launches
        for name in overrides:
            self.assertNotIn(name, launch['env'])
        self.assertEqual(launch['env'].get('PATH'), os.environ.get('PATH'))
        self.assertTrue(launch['name'].startswith('do-math-formal-'))


class RegistrationWarningTests(unittest.TestCase):
    """The public trust registration and adoption on an initializing Sim whose tool review window is 120 s."""

    def test_adoption_and_registration_results_return_the_warnings(self):
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(directory, config=WINDOWS)
            request = trust_fixture(sim.shared, sim.instance['config']['lean_command'], directory=sim.shared / 'trust')
            path = Path(request['toolchain_record']['path'])
            record = records.read_record(path)
            validation = record['baselines'][0]['validation']
            validation['finished_at'] = '2026-09-20T00:03:59.2Z'  # 239.2 s after started_at
            record['baselines'][0]['validation_sha256'] = records.validation_sha256(validation)
            records.write_record(path, record)
            request['binding'] = records.binding(record)
            results = {}
            for action, config in (('trust', request),
                                   ('decision', {'change': {'kind': 'initialization', 'operation': 'adopt'}}),
                                   ('pause', None)):
                sent = sim.control(action, text='warning check', **({'config': config} if config else {}))
                sim.engine.process_controls()
                row = next(h for h in sim.runtime['history'] if h.get('request', {}).get('id') == sent['request_id'])
                self.assertEqual(row['kind'], 'user_control', row.get('reason'))
                results[action] = row['result']
            expected = observation_window_warnings(sim.instance, sim.runtime)
            self.assertTrue(expected)
            self.assertEqual({row['representative_check_seconds'] for row in expected}, {240})
            self.assertEqual(results['trust']['observation_window_warnings'], expected)
            self.assertEqual(results['decision']['observation_window_warnings'], expected)
            self.assertNotIn('observation_window_warnings', results['pause'])


if __name__ == '__main__':
    unittest.main()

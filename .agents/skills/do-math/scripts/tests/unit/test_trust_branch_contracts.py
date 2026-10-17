"""Uncovered trust contracts using real producers and only external I/O doubles."""
from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import setup_lean
from do_math import formal, trust_inventory as records
from do_math.lean_evidence import LEAN_VERSION, READY_MARKER, VerificationStopped, mathlib_project, portable_bin
from support.entry import entry
from support.knowledge_verifier_jobs import OutputCompiler, worker_jobs
from support.trust_branch_inputs import UnavailableJobs, checker_files, setup_main
from support.trust_inputs import setup_recording


class DiscoveryContracts(unittest.TestCase):
    def test_finished_project_path_and_portable_fallback_have_the_exact_precedence(self):
        with tempfile.TemporaryDirectory() as directory, checker_files(Path(directory) / 'repo/.agents/skills/do-math/scripts/do_math/formal.py'):
            root = formal.toolchain_root()
            self.assertTrue(root.is_relative_to(Path(directory)))
            binary = portable_bin(root)
            binary.mkdir(parents=True)
            lean, lake = binary / 'lean.exe', binary / 'lake.exe'
            lean.write_bytes(b'synthetic discovery file; never executed')
            with patch('shutil.which', return_value='path-lean') as search:
                self.assertEqual(formal.discover_lean(), ['path-lean'])
                project = mathlib_project(root)
                project.mkdir()
                (project / READY_MARKER).write_text(LEAN_VERSION)
                self.assertEqual(formal.discover_lean(), ['path-lean'])
                lake.write_bytes(b'synthetic Lake discovery file')
                search.reset_mock()
                expected = [str(lake), '--dir', str(project), 'env', str(lean)]
                self.assertEqual(formal.discover_lean(), expected)
                search.assert_not_called()
                (project / READY_MARKER).unlink()
            with patch('shutil.which', return_value=None):
                self.assertEqual(formal.discover_lean(), [str(lean)])
                lean.unlink()
                self.assertIsNone(formal.discover_lean())

    def test_shallow_filesystem_without_a_path_lean_returns_no_discovery(self):
        with tempfile.TemporaryDirectory(prefix='do-math-shallow-', dir=Path.cwd().anchor) as directory, checker_files(Path(directory) / 'formal.py'), patch('shutil.which', return_value=None):
            self.assertIsNone(formal.toolchain_root())
            self.assertIsNone(formal.discover_lean())


class ObservationContracts(unittest.TestCase):
    def test_stopped_job_returns_both_raw_streams_after_termination_and_closes(self):
        values = entry()
        compiler = OutputCompiler('raw stdout before cancellation\n')
        def spawn(command, **options):
            options['stderr'].write(b'raw stderr before cancellation\n')
            return compiler(command, **options)
        jobs = worker_jobs(spawn)
        finished = []
        with tempfile.TemporaryDirectory() as directory:
            result = formal._job_run(['owned-compiler'], Path(directory), jobs=jobs,
                clock=values.ports.clock, environment=values.environment,
                should_stop=lambda: True, on_finished=finished.append)
        self.assertEqual(result, (None, compiler.stdout, 'raw stderr before cancellation\n', True))
        job, = jobs.launched
        self.assertTrue(job.done and job.closed)
        self.assertEqual(len(finished), 1)
        self.assertEqual(compiler.commands, [['owned-compiler']])

    def test_project_observation_failure_and_stop_are_not_an_approved_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = setup_recording(directory, kind='project')
            options = {k: fixture[k] for k in ('jobs', 'clock', 'environment', 'git_backend')}
            # The real worker invokes an external compiler that exits with an error.
            compiler = OutputCompiler('unusable project environment', exit_code=7)
            options['jobs'] = worker_jobs(compiler)
            with self.assertRaisesRegex(RuntimeError, '^project environment observation failed: $'):
                formal._project_identity(fixture['command'], workspace=Path(directory), **options)
            self.assertEqual(len(compiler.commands), 1)
            self.assertTrue(all(job.closed and job.done for job in options['jobs'].launched))
            # Cancellation becomes visible at the Job boundary, after the initial file scan.
            options['jobs'] = fixture['jobs']
            with self.assertRaisesRegex(VerificationStopped, '^project environment observation stopped$'):
                formal._project_identity(fixture['command'], workspace=Path(directory),
                    should_stop=lambda: bool(fixture['jobs'].launched), **options)
            self.assertTrue(all(job.closed and job.done for job in fixture['jobs'].launched))

    def test_identity_observation_errors_and_explicit_stop_keep_their_distinct_contracts(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = setup_recording(directory, kind='project')
            options = {k: fixture[k] for k in ('jobs', 'clock', 'environment', 'git_backend')}
            identity = setup_lean.observe_identity(fixture['command'], **options)
            # A missing project is observed through the filesystem, not an internal return patch.
            project = Path(directory) / 'project'
            project.rename(project.with_name('removed-project'))
            errors = formal.toolchain_identity_errors(identity, **options)
            self.assertEqual(len(errors), 1)
            self.assertTrue(errors[0].startswith('approved project inputs could not be observed: '))
            with self.assertRaisesRegex(VerificationStopped, '^verification stopped$'):
                formal.toolchain_identity_errors(identity, should_stop=lambda: True, **options)

    def test_verifier_keeps_process_failure_and_post_compile_stop_out_of_success(self):
        from support.knowledge_verifier_jobs import approved_toolchain
        values = entry()
        with tempfile.TemporaryDirectory() as directory:
            command, identity = approved_toolchain(Path(directory))
            options = dict(source='theorem t : True := True.intro', declarations=['t'],
                workspace=Path(directory), lean_command=command, expected_toolchain=identity,
                clock=values.ports.clock, environment=values.environment, git_backend=values.ports.git_backend)
            result = formal.verify_lean(jobs=UnavailableJobs(), **options)
            self.assertEqual((result['status'], result['reason'], result['launch_not_created']),
                ('failed', 'verification process failed: owned test Job service unavailable', True))
            unstarted = worker_jobs(OutputCompiler())
            result = formal.verify_lean(jobs=unstarted,
                should_stop=lambda: any(Path(directory).glob('*/proposal.lean')), **options)
            self.assertEqual((result['status'], result['reason'], result['launch_not_created']),
                             ('stopped', 'verification stopped', True))
            self.assertEqual(unstarted.launched, [])
            compiler = OutputCompiler('external output kept when parsing is stopped')
            jobs = worker_jobs(compiler)
            def stop_after_completion():
                # Do not stop the polling loop; cancel when the parser next checks.
                return bool(jobs.launched and jobs.launched[0].closed)
            result = formal.verify_lean(jobs=jobs, should_stop=stop_after_completion, **options)
            self.assertEqual((result['status'], result['reason']), ('stopped', 'verification stopped'))
            self.assertEqual(result['stdout'], compiler.stdout)
            self.assertFalse(result['launch_not_created'])
            self.assertEqual(len(compiler.commands), 1)

    def test_worker_os_error_without_errno_is_rethrown_with_its_original_message(self):
        values = entry()
        def unavailable(*args, **kwargs):
            raise OSError('external spawn denied without errno')
        jobs = worker_jobs(unavailable)
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(
                OSError, '^external spawn denied without errno$') as error:
            formal._job_run(['owned-compiler'], Path(directory), preserve_os_error=True,
                jobs=jobs, clock=values.ports.clock, environment=values.environment)
        self.assertIsNone(error.exception.errno)
        self.assertTrue(all(job.done and job.closed for job in jobs.launched))


class SetupContracts(unittest.TestCase):
    def test_script_entry_rejects_an_empty_explicit_command_before_any_installation(self):
        from contextlib import redirect_stdout
        import runpy
        import sys
        with tempfile.TemporaryDirectory() as directory:
            command_file = Path(directory) / 'command.json'
            command_file.write_text('{"lean_command":[]}')
            output = io.StringIO()
            with patch.object(sys, 'argv', [setup_lean.__file__, '--inspect-only', '--command-file', str(command_file)]), redirect_stdout(output):
                with self.assertRaises(SystemExit) as exited:
                    runpy.run_path(setup_lean.__file__, run_name='__main__')
            self.assertEqual(exited.exception.code, 2)
            self.assertEqual(json.loads(output.getvalue()), {'status': 'error',
                'error': 'ValueError: Lean was not found; supply --command-file'})
            self.assertEqual(list(Path(directory).iterdir()), [command_file])

    def test_shallow_installation_reports_its_exact_missing_root_requirements(self):
        values = entry()
        options = dict(ports=values.ports, environment=values.environment)
        with tempfile.TemporaryDirectory(prefix='do-math-shallow-', dir=Path.cwd().anchor) as directory, checker_files(Path(directory) / 'formal.py'):
            code, result, _ = setup_main([], **options)
            self.assertEqual((code, result), (2, {'status': 'error', 'error':
                'ValueError: this installation has no repository root above it; set lean_command explicitly instead'}))
            command_file = Path(directory) / 'command.json'
            command_file.write_text('{"lean_command":["explicit-command"]}')
            code, result, _ = setup_main(['--verify-only', '--command-file', str(command_file)], **options)
            self.assertEqual((code, result), (2, {'status': 'error', 'error':
                'ValueError: this installation has no toolchain root; supply --records-dir and --evidence-dir'}))
            self.assertEqual(values.ports.jobs.launched, [])

    def test_invalid_observed_identity_and_job_error_leave_failed_raw_validation(self):
        values = entry()
        with self.assertRaisesRegex(ValueError, '^toolchain must be an object$'):
            setup_lean.observe_identity([], identity=[], jobs=values.ports.jobs, clock=values.ports.clock,
                environment=values.environment, git_backend=values.ports.git_backend)
        with tempfile.TemporaryDirectory() as directory:
            fixture = setup_recording(Path(directory) / 'installation')
            identity = setup_lean.observe_identity(fixture['command'], **{k: fixture[k]
                for k in ('jobs', 'clock', 'environment', 'git_backend')})
            result = setup_lean.verify_environment(fixture['command'], Path(directory) / 'evidence', identity,
                jobs=UnavailableJobs(), clock=fixture['clock'], environment=fixture['environment'])
            self.assertEqual((result['status'], result['exit_code'], result['stdout'], result['stderr']),
                             ('failed', None, '', ''))
            self.assertEqual(result['error'], 'OSError: owned test Job service unavailable')
            self.assertEqual(json.loads(Path(result['source']).with_name('validation.json').read_bytes()), result)
            self.assertEqual(Path(result['source']).read_bytes(), result['source_text'].encode())

    def test_main_inspects_records_rerecords_and_reports_a_real_content_mismatch(self):
        from dataclasses import replace
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = setup_recording(root / 'installation')
            values = entry()
            ports = replace(values.ports, jobs=fixture['jobs'], clock=fixture['clock'],
                            git_backend=fixture['git_backend'])
            command_file = root / 'command.json'
            command_file.write_text(json.dumps({'lean_command': fixture['command']}))
            common = ['--command-file', str(command_file)]
            options = dict(ports=ports, environment=fixture['environment'])
            code, result, stderr = setup_main(['--inspect-only', *common], **options)
            self.assertEqual((code, result['status'], result['lean_command'], stderr),
                             (0, 'observed', fixture['command'], ''))
            paths = ['--records-dir', str(fixture['records_dir']), '--evidence-dir', str(fixture['evidence_root'])]
            code, created, _ = setup_main(['--verify-only', *common, *paths, '--trust-file', str(root / 'trust.json')], **options)
            self.assertEqual((code, created['status'], created['created']), (0, 'recorded', True))
            self.assertEqual(json.loads((root / 'trust.json').read_bytes())['binding'], created['binding'])
            code, rerecorded, _ = setup_main(['--rerecord', *common, *paths], **options)
            self.assertEqual((code, rerecorded['binding']['baseline']), (0, 1))
            olean = root / 'installation/toolchain/lib/lean/Init/Prelude.olean'
            olean.write_bytes(b'changed real judgment bytes')
            code, result, _ = setup_main(['--check-contents', *common, '--records-dir', str(fixture['records_dir'])], **options)
            self.assertEqual((code, result['status'], result['check']['result']), (1, 'mismatch', 'mismatch'))
            self.assertEqual(records.read_record(created['record_path'])['checks'][-1], result['check'])
            before = Path(created['record_path']).read_bytes()
            code, result, _ = setup_main(['--rerecord', *common, *paths], **options)
            self.assertEqual((code, result['status']), (1, 'refused'))
            self.assertEqual(result['reason'], 'judgment file contents differ from the current baseline; create a new record and register and transition to it')
            self.assertEqual(Path(created['record_path']).read_bytes(), before)

    def test_install_uses_archive_and_external_lake_only_in_its_temporary_root(self):
        # Installation itself is real; download and subprocess are the external boundaries.
        downloads, commands = [], []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'toolchains'
            binary = portable_bin(root)
            def download(url, archive):
                downloads.append((url, Path(archive)))
                with zipfile.ZipFile(archive, 'w') as bundle:
                    for name in ('lean.exe', 'lake.exe'):
                        bundle.writestr((binary / name).relative_to(Path(archive).parent).as_posix(), b'external installation double')
                return str(archive), None
            def execute(command, **options):
                commands.append((command, options))
                if command[1:] == ['update']:
                    (Path(options['cwd']) / 'lake-manifest.json').write_text('{"packages":[]}')
                return subprocess.CompletedProcess(command, 0)
            with patch('urllib.request.urlretrieve', side_effect=download), patch('subprocess.run', side_effect=execute), patch('sys.stderr', new_callable=io.StringIO) as stderr:
                expected = [str(binary / 'lake.exe'), '--dir', str(mathlib_project(root)), 'env', str(binary / 'lean.exe')]
                self.assertEqual(setup_lean.install(root), expected)
                self.assertEqual(setup_lean.install(root), expected)
                # A drifted project input is restored by the next idempotent install.
                (mathlib_project(root) / 'lakefile.toml').write_text('drift')
                self.assertEqual(setup_lean.install(root), expected)
            self.assertEqual(len(downloads), 1)
            self.assertEqual([c[0][1:] for c in commands], [['update'], ['exe', 'cache', 'get'], ['exe', 'cache', 'get'], ['exe', 'cache', 'get']])
            self.assertTrue(all(c[1]['check'] and c[1]['cwd'] == mathlib_project(root) for c in commands))
            self.assertTrue(all(c[1]['env']['PATH'].startswith(str(binary)) for c in commands))
            self.assertIn('downloading ' + setup_lean.LEAN_ZIP, stderr.getvalue())
            self.assertEqual((mathlib_project(root) / 'lakefile.toml').read_text(), setup_lean.PROJECT_FILES['lakefile.toml'])
            self.assertFalse((mathlib_project(root) / READY_MARKER).exists())

    def test_main_marks_ready_after_recording_and_removes_the_marker_on_install_failure(self):
        from dataclasses import replace
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / 'repo/.agents/skills/do-math/scripts/do_math/formal.py'
            with checker_files(installed):
                root = formal.toolchain_root()
                self.assertTrue(root.is_relative_to(Path(directory)))
                fixture = setup_recording(Path(directory) / 'compiler', kind='project')
                values = entry()
                ports = replace(values.ports, jobs=fixture['jobs'], clock=fixture['clock'], git_backend=fixture['git_backend'])
                binary, project = portable_bin(root), mathlib_project(root)
                marker = project / READY_MARKER
                project.mkdir(parents=True)
                marker.write_text('stale success marker')
                def download(url, archive):
                    with zipfile.ZipFile(archive, 'w') as bundle:
                        for relative in ('bin/lean.exe', 'bin/lake.exe', 'bin/libleanshared.dll', 'lib/lean/Init/Prelude.olean'):
                            path = binary.parent / relative
                            bundle.writestr(path.relative_to(Path(archive).parent).as_posix(), b'explicit external compiler double')
                    return str(archive), None
                commands = []
                def execute(command, **options):
                    self.assertFalse(marker.exists())
                    commands.append(command)
                    if command[1:] == ['update']:
                        (project / 'lake-manifest.json').write_text('{"packages":[]}')
                    return subprocess.CompletedProcess(command, 0)
                options = dict(ports=ports, environment=fixture['environment'])
                with patch('urllib.request.urlretrieve', side_effect=download), patch('subprocess.run', side_effect=execute):
                    code, result, stderr = setup_main([], **options)
                self.assertEqual((code, result['status'], result['created']), (0, 'recorded', True))
                self.assertEqual(marker.read_text(), LEAN_VERSION)
                record = records.read_record(result['record_path'])
                self.assertEqual(record['baselines'][0]['validation']['status'], 'verified')
                self.assertEqual(record['identity']['configured_command'], result['lean_command'])
                self.assertEqual(len(fixture['lean'].checks), 1)
                self.assertEqual([c[1:] for c in commands], [['update'], ['exe', 'cache', 'get']])
                self.assertIn('+ ' + str(binary / 'lake.exe'), stderr)
                before = Path(result['record_path']).read_bytes()
                with patch('subprocess.run', side_effect=subprocess.CalledProcessError(7, [str(binary / 'lake.exe')])):
                    code, failure, _ = setup_main([], **options)
                self.assertEqual((code, failure['status']), (2, 'error'))
                self.assertIn('CalledProcessError', failure['error'])
                self.assertFalse(marker.exists())
                self.assertEqual(Path(result['record_path']).read_bytes(), before)



class ImpactAuthorityContracts(unittest.TestCase):
    def test_reviewed_additional_authorities_remain_exact_and_publish_the_reassessment(self):
        from do_math import knowledge, knowledge_io
        from support.engine_lifecycle import clear_work
        from support.sim import Sim
        sim = Sim.activated()
        clear_work(sim)
        engine = sim.engine
        engine.instance, _ = knowledge_io.register_kind_definition(engine.instance,
            {'family': 'relation', 'token': 'bounded_support', 'meaning': 'Research support in a bounded scope',
             'constraints': {'requires_evidence': True}}, source_ref='fixture:kind', actor_ref='user', clock=sim.clock)
        definition = knowledge_io.lookup_definition(engine.instance, 'relation', 'bounded_support')
        environment_id = engine.instance['active_trust_environment']
        environment = deepcopy(engine.instance['trust_environments'][environment_id])
        definition = deepcopy(definition)
        from support.record_builders import observation_knowledge
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            observation_knowledge('Impact root'), source_ref='fixture:observation', actor_ref='user', clock=sim.clock)
        engine._save()
        plan = knowledge.plan_impact(engine.instance, engine.runtime, [kid], [definition['id'], environment_id])
        self.assertTrue(plan['requires_independent_review'])
        affected = sorted(set(plan['computed_impact']) | set(plan['declared_impact']))
        confirmation = {'plan_digest': plan['digest'], 'decision': 'approve', 'review_ref': 'fixture:independent-review',
            'reviewer_ref': 'independent-reviewer', 'producer_ref': 'producer', 'affected_ids': affected}
        engine.instance, engine.runtime = knowledge.apply_impact(engine.instance, engine.runtime, plan,
            reason='reviewed additional scope', independent_confirmation=confirmation, clock=sim.clock)
        self.assertEqual(engine.instance['kind_definitions'][definition['id']], definition)
        self.assertEqual(engine.instance['trust_environments'][environment_id], environment)
        event = engine.runtime['history'][-1]
        self.assertEqual(event, {'kind': 'knowledge_reassessment_required', 'affected_ids': affected,
            'reason': 'reviewed additional scope', 'impact_digest': plan['digest']})
        action, = [a for a in engine.runtime['queue'] if a.get('affected_ids') == affected]
        self.assertEqual(action['role'], 'research_plan')
        engine._save()  # The actual closed storage contract must accept this disposition.
        _, loaded, runtime = engine.store.load()
        self.assertEqual(loaded['kind_definitions'][definition['id']], definition)
        self.assertEqual(loaded['trust_environments'][environment_id], environment)
        self.assertIn(event, runtime['history'])


class EngineTrustContracts(unittest.TestCase):
    def test_environment_invalidated_before_check_fails_without_starting_a_compiler(self):
        """T3 16.8 s including the first formal-scene build: one accepted FR is needed to produce a real transition target."""
        from support.engine_lifecycle import applied, next_environment, transition, run_machine, only
        from support.knowledge_formal_engine import scene, run_formal
        sim, formal_action = scene()
        run_formal(sim, formal_action)
        old = sim.instance['active_trust_environment']
        original_formal = deepcopy(sim.instance['formal_results'])
        target = next_environment(sim, 'invalidated-before-check')
        tid = transition(sim, target)
        only(sim, 'trust_check', 'trust_activate')
        sim.engine._save()
        applied(sim, 'trust', config={'operation': 'invalidate', 'env_id': target,
                                     'reason': 'user rejects the prepared environment'})
        jobs_before = len(sim.jobs.launched)
        action = run_machine(sim, 'trust_check')
        execution, = [e for e in sim.runtime['executions'].values()
                      if e['role'] == 'trust_check' and e['action']['transition_id'] == tid]
        self.assertEqual(len(sim.jobs.launched), jobs_before)
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))
        self.assertNotIn('submission_receipt', execution)
        result = json.loads(sim.engine.store.read(execution['result_ref'], sim.engine.head))
        self.assertEqual((result['status'], result['reason']),
                         ('failed', 'ValueError: trust transition environment was invalidated'))
        self.assertEqual(sim.runtime['trust_transitions'][tid]['results'][action['target']], result)
        self.assertEqual(sim.runtime['trust_transitions'][tid]['status'], 'ready')
        self.assertNotIn(action['id'], [a['id'] for a in sim.runtime['queue']])
        self.assertEqual(sim.instance['active_trust_environment'], old)
        self.assertEqual(sim.instance['trust_environments'][target]['status'], 'invalid')
        self.assertEqual(sim.instance['formal_results'], original_formal)
        self.assertEqual(sim.engine.store.load()[2]['executions'][execution['id']], execution)

    def test_registration_refuses_the_failed_bound_baseline_and_preserves_the_instance(self):
        from support.sim import Sim
        from support.trust_inputs import trust_fixture
        sim = Sim.activated()
        request = trust_fixture(sim.root / 'failed-baseline', sim.instance['config']['lean_command'])
        path = Path(request['toolchain_record']['path'])
        record = records.read_record(path)
        # An external record can have a failed old entry and a usable current
        # entry. The registration must check the exact entry the user bound.
        successful = deepcopy(record['baselines'][0])
        record['baselines'][0]['validation'].update(status='failed', exit_code=9)
        record['baselines'][0]['validation_sha256'] = records.validation_sha256(record['baselines'][0]['validation'])
        record['baselines'].append(successful)
        records.write_record(path, record)
        request['binding'] = records.binding(record, 0)
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^bound toolchain baseline has no successful representative check$'):
            sim.engine._trust_control(request, 'fixture:trust-request')
        self.assertEqual((sim.instance, sim.runtime), before)
        request['binding'] = records.binding(record)
        request['allowed_axioms'] = []
        with self.assertRaisesRegex(ValueError, '^foundation axiom profile differs$'):
            sim.engine._trust_control(request, 'fixture:trust-request')
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_invalidated_fixed_environment_fails_activation_and_preserves_the_old_authority(self):
        from do_math.trust_validation import check_environment
        from support.engine_lifecycle import applied, clear_work, next_environment, transition
        from support.sim import Sim
        sim = Sim.activated()
        clear_work(sim)
        old = sim.instance['active_trust_environment']
        target = next_environment(sim, 'invalidated-activation')
        tid = transition(sim, target)
        sim.engine._save()
        verification = check_environment(sim.instance['trust_environments'][target], sim.runtime['trust_bindings'][target],
                                         host=sim.ports.host, clock=sim.clock)
        self.assertEqual(verification['status'], 'verified')
        applied(sim, 'trust', config={'operation': 'invalidate', 'env_id': target, 'reason': 'target environment defect'})
        sim.engine._finish_trust_transition(tid, verification)
        tr = sim.runtime['trust_transitions'][tid]
        self.assertEqual(tr['status'], 'failed')
        self.assertEqual(tr['history'][-1]['reason'], 'target trust environment changed during transition')
        self.assertEqual(sim.instance['active_trust_environment'], old)
        plans = [a for a in sim.runtime['queue'] if a.get('transition_id') == tid and a['role'] == 'research_plan']
        self.assertEqual(len(plans), 1)
        sim.engine._save()
        self.assertEqual(sim.engine.store.load()[2]['trust_transitions'][tid], tr)

    def test_unobserved_owner_termination_holds_activation_and_preserves_its_result(self):
        from support.engine_lifecycle import clear_work, next_environment, transition, run_machine
        from support.sim import Sim
        sim = Sim.activated()
        clear_work(sim)
        target = next_environment(sim, 'unobserved-activation')
        tid = transition(sim, target)
        observe = sim.jobs.owner_ended
        sim.jobs.owner_ended = lambda identity: None
        try:
            run_machine(sim, 'trust_activate')
        finally:
            sim.jobs.owner_ended = observe
        execution, = [e for e in sim.runtime['executions'].values() if e['role'] == 'trust_activate' and e['action'].get('transition_id') == tid]
        self.assertEqual(execution['status'], 'stopping')
        self.assertEqual(execution['capacity']['local_termination'], 'unknown')
        self.assertNotIn('outcome', execution)
        self.assertIn(execution['action']['id'], [a['id'] for a in sim.runtime['queue']])
        result = json.loads(sim.engine.store.read(execution['result_ref'], sim.engine.head))
        self.assertEqual((result['transition_id'], result['status']), (tid, 'active'))
        self.assertEqual(sim.engine.store.load()[2]['executions'][execution['id']], execution)

    def test_replayed_trust_check_queues_activation_without_another_attempt(self):
        from support.engine_lifecycle import next_environment, transition, run_machine, only
        from support.knowledge_formal_engine import scene, run_formal
        sim, formal_action = scene()
        run_formal(sim, formal_action)
        tid = transition(sim, next_environment(sim, 'replayed-check'))
        only(sim, 'trust_check', 'trust_activate')
        actions = deepcopy([a for a in sim.runtime['queue'] if a['role'] == 'trust_check'])
        for action in actions:
            run_machine(sim, 'trust_check')
        self.assertEqual(sim.runtime['trust_transitions'][tid]['status'], 'ready')
        attempts = deepcopy(sim.runtime['executions'])
        steps = sim.engine._trust_check_steps(actions[0])
        with self.assertRaises(StopIteration) as completed:
            next(steps)
        self.assertIsNone(completed.exception.value)
        self.assertEqual(sim.runtime['executions'], attempts)
        self.assertEqual(sum(a['role'] == 'trust_activate' and a['transition_id'] == tid for a in sim.runtime['queue']), 1)

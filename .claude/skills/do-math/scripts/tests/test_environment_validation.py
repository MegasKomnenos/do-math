"""Toolchain records, identity and olean fingerprints under the accidental-change model."""
from copy import deepcopy
import ctypes
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.local_host import LocalHost
import setup_lean
from do_math import trust_inventory as records
from do_math.canonical import exact_content_hash
from do_math.trust_validation import check_environment, environment_errors, register_request_errors
from research_fixtures import bare_engine, fixture_setup_lean, trust_environment, trust_fixture, validation_fixture


def set_birthtime(path, nanoseconds):
    """Change only the creation time (Windows SetFileTime)."""
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                                   wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    handle = kernel.CreateFileW(str(path), 0x100, 0x7, None, 3, 0x80, None)
    if handle in (None, wintypes.HANDLE(-1).value):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        ticks = nanoseconds // 100 + 116444736000000000
        created = wintypes.FILETIME(ticks & 0xFFFFFFFF, ticks >> 32)
        if not kernel.SetFileTime(handle, ctypes.byref(created), None, None):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)


class ToolchainRecordTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.request = trust_fixture(self.root, ['synthetic-lean'])
        self.environment, self.binding = trust_environment(self.request)
        self.record_path = Path(self.request['toolchain_record']['path'])
        self.olean = Path(self.request['toolchain']['executable']).parents[1] / 'lib/lean/Init/Prelude.olean'

    def record(self):
        return records.read_record(self.record_path)

    def rewrite(self, change):
        record = json.loads(self.record_path.read_text(encoding='utf-8'))
        change(record)
        self.record_path.write_text(json.dumps(record), encoding='utf-8')

    def recorded(self, *, validation=True):
        return fixture_setup_lean(self.request['toolchain'], self.root / 'smoke.lean', validation=validation)

    def rerecord(self):
        with self.recorded():
            return setup_lean.rerecord(['synthetic-lean'], self.record_path.parent, self.root / 'evidence', None)

    def test_current_environment_is_verified_from_record_identity_and_fingerprint(self):
        self.assertEqual(environment_errors(self.environment, self.binding), [])
        self.assertEqual(register_request_errors({k: v for k, v in self.request.items()}), [])
        result = check_environment(self.environment, self.binding, host=LocalHost())
        self.assertEqual(result['status'], 'verified')
        self.assertEqual(result['identity_sha256'], exact_content_hash(self.request['toolchain']))
        self.assertEqual(result['fingerprint_sha256'], self.binding['fingerprint_sha256'])
        self.assertNotIn('rebind', result)
        self.assertEqual(set(self.record()['baselines'][0]['fingerprint']['files']),
                         {'toolchain/bin/libleanshared.dll', 'toolchain/lib/lean/Init/Prelude.olean'})

    def test_unknown_record_field_and_other_schema_are_rejected(self):
        # An identity edited inside one record file no longer matches its digest and ID.
        for change in (lambda r: r.update(unrecognized=True), lambda r: r.update(schema='do-math-toolchain-record/2'),
                       lambda r: r['baselines'][0].update(files=[]), lambda r: r['identity'].update(version='edited')):
            with self.subTest(change=change):
                original = self.record_path.read_bytes()
                self.rewrite(change)
                result = check_environment(self.environment, self.binding, host=LocalHost())
                self.assertEqual(result['status'], 'invalid')
                self.assertIn('toolchain record unavailable', result['errors'][0])
                self.record_path.write_bytes(original)

    def test_success_label_cannot_replace_failed_representative_evidence(self):
        for change in ({'exit_code': 17}, {'status': 'failed'}):
            with self.subTest(change=change):
                original = self.record_path.read_bytes()
                self.rewrite(lambda r: r['baselines'][-1]['validation'].update(change))
                result = check_environment(self.environment, self.binding, host=LocalHost())
                self.assertIn('current toolchain baseline has no successful representative check', result['errors'])
                self.record_path.write_bytes(original)

    def test_search_paths_outside_the_recorded_roots_are_rejected(self):
        identity = deepcopy(self.request['toolchain'])
        project = self.root / 'project'
        identity['project'] = {'manifest_hashes': {}, 'source_identity': {'root': str(project)},
                               'search_paths': [str(project / '.lake/build/lib/lean'), str(self.root / 'outside')]}
        errors = records.identity_errors(identity)
        self.assertEqual(errors, ['Lean search path is outside the recorded toolchain and project roots: '
                                  + str(self.root / 'outside')])
        identity['project']['source_identity']['root'] = str(Path(identity['executable']).parents[1] / 'lib')
        self.assertIn('toolchain and project roots must not overlap', records.identity_errors(identity))

    def test_identity_detects_executable_checker_and_project_input_changes(self):
        from do_math.formal import toolchain_identity_errors
        self.assertEqual(toolchain_identity_errors(self.request['toolchain']), [])
        # Each recorded hash holds on its own, even when the executable is also a command file.
        wrong = {**self.request['toolchain'], 'sha256': '0' * 64}
        self.assertEqual(toolchain_identity_errors(wrong),
                         ['approved toolchain file changed: ' + self.request['toolchain']['executable']])
        lake = Path(self.request['toolchain']['executable']).with_name('lake.exe')
        lake.write_bytes(b'replaced by an update')
        self.assertEqual(toolchain_identity_errors(self.request['toolchain']),
                         ['approved toolchain file changed: ' + str(lake)])
        # The checker is its running bytes: a copy elsewhere is the same checker,
        # other recorded bytes are not.
        copy = self.root / 'formal.py'
        copy.write_bytes(Path(self.request['toolchain']['verifier_path']).read_bytes())
        moved = {**self.request['toolchain'], 'verifier_path': str(copy)}
        lake_changed = 'approved toolchain file changed: ' + str(lake)
        self.assertEqual(toolchain_identity_errors(moved), [lake_changed])
        copy.write_bytes(b'another checker')
        other = {**moved, 'verifier_sha256': hashlib.sha256(b'another checker').hexdigest()}
        self.assertEqual(toolchain_identity_errors(other), ['approved checker is not the running checker', lake_changed])
        project = self.root / 'project'
        project.mkdir()
        (project / 'lean-toolchain').write_text('leanprover/lean4:v4.32.0\n', encoding='utf-8')
        (project / 'lake-manifest.json').write_text('{"packages": []}', encoding='utf-8')
        command = ['lake', '--dir', str(project), 'env', 'lean']
        from do_math.formal import _project_identity
        with tempfile.TemporaryDirectory() as workspace:
            observed = _project_identity(command, workspace=Path(workspace),
                                         expected={'manifest_hashes': None, 'source_identity': None})
        lake.write_bytes(('CORE_TESTS synthetic bin/lake.exe for synthetic-lean').encode())
        for name, text in (('lean-toolchain', 'leanprover/lean4:v4.33.0\n'), ('lake-manifest.json', '{"packages": [1]}')):
            with self.subTest(name=name):
                original = (project / name).read_bytes()
                (project / name).write_text(text, encoding='utf-8')
                chain = {**self.request['toolchain'], 'configured_command': command, 'project': observed}
                self.assertEqual(toolchain_identity_errors(chain), ['approved project inputs changed'])
                (project / name).write_bytes(original)

    def test_fingerprint_detects_size_modification_creation_and_recreation(self):
        original = self.olean.read_bytes()
        info = os.stat(self.olean)
        def restore():
            self.olean.write_bytes(original)
            os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns))
            set_birthtime(self.olean, info.st_birthtime_ns)
            self.assertEqual(check_environment(self.environment, self.binding, host=LocalHost())['status'], 'verified')
        changes = {
            'size': lambda: self.olean.write_bytes(original + b'x'),
            'modification time': lambda: os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9)),
            'creation time': lambda: set_birthtime(self.olean, info.st_birthtime_ns - 10**10),
            'recreated with the same bytes': lambda: (self.olean.unlink(), self.olean.write_bytes(original),
                                                      os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))),
            'added module': lambda: self.olean.with_name('Extra.olean').write_bytes(b'new'),
        }
        for name, change in changes.items():
            with self.subTest(change=name):
                change()
                result = check_environment(self.environment, self.binding, host=LocalHost())
                self.assertEqual(result['status'], 'invalid')
                self.assertIn('olean fingerprint differs', result['errors'][0])
                self.assertTrue(result['changed_files'])
                self.olean.with_name('Extra.olean').unlink(missing_ok=True)
                restore()

    def test_fingerprint_does_not_see_content_changed_with_all_metadata_preserved(self):
        """The declared limit of the accidental-change model; only a content check finds it."""
        info = os.stat(self.olean)
        raw = self.olean.read_bytes()
        with self.olean.open('r+b') as stream:
            stream.write(bytes([raw[0] ^ 1]))
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns))
        self.assertEqual(os.stat(self.olean).st_birthtime_ns, info.st_birthtime_ns)
        self.assertEqual(check_environment(self.environment, self.binding, host=LocalHost())['status'], 'verified')
        with self.recorded():
            result = setup_lean.check_contents(self.record_path.parent, None, ['synthetic-lean'])
        self.assertEqual(result['status'], 'mismatch')
        self.assertEqual(result['check']['mismatched'], ['toolchain/lib/lean/Init/Prelude.olean'])
        blocked = check_environment(self.environment, self.binding, host=LocalHost())
        self.assertEqual(blocked['status'], 'invalid')
        self.assertIn('a content check found files that differ from the current toolchain baseline', blocked['errors'])

    def test_content_check_passes_records_history_and_never_blocks_readers(self):
        with records.writer_lock(self.record_path.parent):
            # Instances only read the record; a running writer never blocks them.
            self.assertEqual(check_environment(self.environment, self.binding, host=LocalHost())['status'], 'verified')
            with self.assertRaises(OSError):
                self.rerecord()
        result = setup_lean.check_contents(self.record_path.parent, self.request['toolchain_record']['id'], None)
        self.assertEqual((result['status'], result['check']['baseline']), ('passed', 0))
        self.assertEqual(self.record()['checks'], [result['check']])
        self.assertEqual(check_environment(self.environment, self.binding, host=LocalHost())['status'], 'verified')

    def test_rerecord_after_metadata_only_change_rebinds_each_instance_once(self):
        other_environment, other_binding = trust_environment(self.request, environment_id='TE-other')
        info = os.stat(self.olean)
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
        self.assertEqual(check_environment(self.environment, self.binding, host=LocalHost())['status'], 'invalid')
        result = self.rerecord()
        self.assertEqual(result['status'], 'recorded')
        record = self.record()
        self.assertEqual(len(record['baselines']), 2)
        self.assertEqual(record['baselines'][1]['content'], record['baselines'][0]['content'])
        current = records.binding(record)
        self.assertEqual(result['binding'], current)
        for environment, binding in ((self.environment, self.binding), (other_environment, other_binding)):
            checked = check_environment(environment, binding, host=LocalHost())
            self.assertEqual(checked['status'], 'verified')
            self.assertEqual(checked['rebind']['previous'], binding)
            self.assertEqual(checked['rebind']['current'], current)
            self.assertEqual(checked['binding'], current)
        followed = check_environment(self.environment, current, host=LocalHost())
        self.assertEqual(followed['status'], 'verified')
        self.assertNotIn('rebind', followed)

    def test_rerecord_refuses_changed_content_identity_or_failed_compile(self):
        with self.olean.open('r+b') as stream:
            stream.write(b'Z')
        with self.assertRaises(setup_lean.Refused) as refused:
            self.rerecord()
        self.assertEqual(refused.exception.result['mismatched'], ['toolchain/lib/lean/Init/Prelude.olean'])
        self.olean.write_bytes(('CORE_TESTS synthetic lib/lean/Init/Prelude.olean for synthetic-lean').encode())
        changed = {**self.request['toolchain'], 'version': 'Lean test 4.33.0'}
        with patch.object(setup_lean, 'observe_identity', return_value=changed):
            with self.assertRaises(setup_lean.Refused) as refused:
                setup_lean.rerecord(['synthetic-lean'], self.record_path.parent, self.root / 'evidence',
                                    self.request['toolchain_record']['id'])
        self.assertIn('identity differs', refused.exception.result['reason'])
        with self.recorded(validation=False), self.assertRaises(setup_lean.Refused) as refused:
            setup_lean.rerecord(['synthetic-lean'], self.record_path.parent, self.root / 'evidence', None)
        self.assertEqual(refused.exception.result['status'], 'failed')
        self.assertEqual(len(self.record()['baselines']), 1)

    def test_rebind_requires_the_current_baseline_and_the_same_identity(self):
        info = os.stat(self.olean)
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
        self.rerecord()
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 2 * 10**9))
        self.assertEqual(check_environment(self.environment, self.binding, host=LocalHost())['status'], 'invalid')
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
        replaced = Path(self.request['toolchain']['executable'])
        replaced.write_bytes(b'different launcher')
        result = check_environment(self.environment, self.binding, identity=False, host=LocalHost())
        self.assertEqual(result['status'], 'invalid')
        self.assertNotIn('rebind', result)

    def test_install_records_once_and_never_appends_a_baseline(self):
        with self.recorded():
            confirmed =setup_lean.record_installation(['synthetic-lean'], self.record_path.parent, self.root / 'evidence')
            self.assertEqual((confirmed['status'], confirmed['created']), ('recorded', False))
            info = os.stat(self.olean)
            os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
            with self.assertRaises(setup_lean.Refused) as refused:
                setup_lean.record_installation(['synthetic-lean'], self.record_path.parent, self.root / 'evidence')
        self.assertEqual(refused.exception.result['status'], 'rerecord_required')
        self.assertEqual(len(self.record()['baselines']), 1)
        changed = {**self.request['toolchain'], 'version': 'Lean test 4.33.0'}
        with fixture_setup_lean(changed, self.root / 'smoke.lean'):
            created =setup_lean.record_installation(['synthetic-lean'], self.record_path.parent, self.root / 'evidence')
        self.assertTrue(created['created'])
        self.assertNotEqual(created['record_id'], self.request['toolchain_record']['id'])
        self.assertEqual(len(list(self.record_path.parent.glob('TC-*.json'))), 2)

    def test_baseline_waits_for_settled_fingerprints_and_refuses_a_changing_install(self):
        # The fixture files were just written, so their fingerprints are inside the racy window.
        with patch.object(setup_lean, 'observe_identity', return_value=deepcopy(self.request['toolchain'])), \
             patch.object(setup_lean.time, 'sleep') as waited, \
             self.assertRaisesRegex(RuntimeError, 'still changing'):
            setup_lean.rerecord(['synthetic-lean'], self.record_path.parent, self.root / 'evidence', None)
        self.assertEqual(waited.call_count, 3)
        self.assertEqual(len(self.record()['baselines']), 1)

    def test_recorded_summary_reports_the_representative_compile_duration(self):
        with self.recorded():
            confirmed = setup_lean.record_installation(['synthetic-lean'], self.record_path.parent, self.root / 'evidence')
        self.assertEqual(confirmed['representative_check_seconds'], 1)

    def test_trust_request_names_the_record_and_its_current_baseline(self):
        result = {'record_path': str(self.record_path), 'binding': records.binding(self.record())}
        written = setup_lean.write_trust_request(result, self.root / 'request.json')
        request = json.loads(Path(written['path']).read_text(encoding='utf-8'))
        self.assertEqual(request, self.request)
        with self.assertRaises(FileExistsError):
            setup_lean.write_trust_request(result, self.root / 'request.json')


class RepresentativeCompileTests(unittest.TestCase):
    def test_validation_preserves_source_output_and_exact_command(self):
        with tempfile.TemporaryDirectory() as directory:
            identity = {'executable': str(Path(directory) / 'lean/bin/lean.exe'), 'project': None}
            with patch('do_math.formal._job_run', return_value=(0, 'ok', '', False)) as run:
                record = setup_lean.verify_environment(['test-lean'], Path(directory) / 'evidence', identity)
            self.assertEqual(record['status'], 'verified')
            self.assertEqual(record['scope'], 'lean_core_representative_proofs')
            self.assertEqual(record['command'], run.call_args.args[0])
            self.assertEqual(record['stdout'], 'ok')
            self.assertEqual(record['source_sha256'], hashlib.sha256(Path(record['source']).read_bytes()).hexdigest())
            preserved = json.loads((Path(record['source']).parent / 'validation.json').read_text(encoding='utf-8'))
            self.assertEqual(preserved, record)

    def test_failure_and_stop_never_produce_verified_evidence(self):
        for returned in [(1, '', 'diagnostic', False), (None, '', '', True)]:
            with self.subTest(returned=returned), tempfile.TemporaryDirectory() as directory:
                identity = {'executable': str(Path(directory) / 'lean/bin/lean.exe'), 'project': None}
                with patch('do_math.formal._job_run', return_value=returned):
                    record = setup_lean.verify_environment(['test-lean'], Path(directory) / 'evidence', identity)
                self.assertEqual(record['status'], 'failed')
                self.assertEqual(record['stderr'], returned[2])

    def test_evidence_inside_a_recorded_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            identity = {'executable': str(Path(directory) / 'lean/bin/lean.exe'), 'project': None}
            with self.assertRaisesRegex(ValueError, 'outside the recorded'):
                setup_lean.verify_environment(['test-lean'], Path(directory) / 'lean/evidence', identity)

    def test_compiler_job_does_not_inherit_unregistered_library_overrides(self):
        from do_math import formal
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict('os.environ',{'LEAN_PATH':'outside','LEAN_SYSROOT':'outside','LAKE_HOME':'outside'}), \
             patch.object(formal,'WindowsJob',side_effect=RuntimeError('observe job arguments')) as job:
            with self.assertRaisesRegex(RuntimeError,'observe job arguments'):
                formal._job_run(['unused-compiler'],Path(directory))
        supplied=job.call_args.kwargs['env']
        self.assertNotIn('LEAN_PATH',supplied)
        self.assertNotIn('LEAN_SYSROOT',supplied)
        self.assertNotIn('LAKE_HOME',supplied)


class ObservationWindowWarningTests(unittest.TestCase):
    """Adopted observation windows against the representative compile of a registered toolchain."""
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        request = trust_fixture(Path(temporary.name), ['synthetic-lean'])
        path = Path(request['toolchain_record']['path'])
        record = records.read_record(path)
        validation = record['baselines'][0]['validation']
        validation['finished_at'] = '2026-09-20T00:03:59.2Z'  # 239.2 s after started_at
        record['baselines'][0]['validation_sha256'] = records.validation_sha256(validation)
        records.write_record(path, record)
        request['binding'] = records.binding(record)
        self.environment, self.binding = trust_environment(request, status='registered')

    def state(self, **windows):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles
        built = build_profiles({**deepcopy(DEFAULT_CONFIG), **windows})
        instance = {**built, 'config': {}, 'trust_environments': {self.environment['id']: self.environment},
                    'lifecycle': {'state': 'initializing', 'adoption': {}}}
        runtime = {'status': 'initializing', 'history': [], 'trust_bindings': {self.environment['id']: self.binding}}
        return instance, runtime

    def test_windows_shorter_than_the_representative_compile_are_warned(self):
        from do_math.initialization import observation_window_warnings
        instance, runtime = self.state(tool_review_window_seconds=120, self_check_response_window_seconds=240)
        warnings = observation_window_warnings(instance, runtime)
        self.assertTrue(warnings)
        self.assertIn('research_work', {row['role'] for row in warnings})
        for row in warnings:
            self.assertEqual({key: row[key] for key in ('field', 'window_seconds', 'environment_id',
                                                         'representative_check_seconds')},
                             {'field': 'tool_review_window_seconds', 'window_seconds': 120,
                              'environment_id': self.environment['id'], 'representative_check_seconds': 240})
        instance, runtime = self.state(tool_review_window_seconds=240, self_check_response_window_seconds=240)
        self.assertEqual(observation_window_warnings(instance, runtime), [])

    def test_the_self_check_response_window_is_not_bound_by_a_compile(self):
        # Research calls such as a compile hold the response deadline (ObservationTracker._hold_deadlines).
        from do_math.initialization import observation_window_warnings
        instance, runtime = self.state(tool_review_window_seconds=240, self_check_response_window_seconds=60)
        self.assertEqual(observation_window_warnings(instance, runtime), [])

    def test_adoption_and_registration_results_return_the_warnings(self):
        from do_math.initialization import observation_window_warnings
        instance, runtime = self.state(tool_review_window_seconds=120, self_check_response_window_seconds=60)
        expected = observation_window_warnings(instance, runtime)
        engine = bare_engine(instance, runtime)
        for action, config in (('trust', {'operation': 'register'}),
                               ('decision', {'change': {'kind': 'initialization', 'operation': 'adopt'}})):
            with self.subTest(action=action):
                engine._record_control_result({'id': 'RQ-' + action, 'action': action, 'config': config})
                self.assertEqual(runtime['history'][-1]['result']['observation_window_warnings'], expected)
        engine._record_control_result({'id': 'RQ-pause', 'action': 'pause', 'config': {}})
        self.assertNotIn('observation_window_warnings', runtime['history'][-1]['result'])


class ActivationProfileTests(unittest.TestCase):
    def test_lean_roles_pin_only_the_command_and_activation_has_no_machine_settings(self):
        from do_math import execution_profiles as profiles
        from do_math.configuration import DEFAULT_CONFIG
        built = profiles.build_profiles({**DEFAULT_CONFIG, 'lean_command': ['synthetic-lean']})
        by_role = {p['role']: p for p in built['execution_profiles'].values() if p['actor_kind'] == 'machine'}
        self.assertNotIn('machine', by_role['trust_activate'])
        for role in ('formal_check', 'trust_check'):
            self.assertEqual(by_role[role]['machine'], {'lean_command': ['synthetic-lean']})
        body = {k: v for k, v in by_role['trust_activate'].items() if k not in {'id', 'sha256'}}
        with self.assertRaisesRegex(ValueError, 'machine profile settings differ'):
            profiles.seal_profile({**body, 'machine': {'mechanism': 'full_environment_scan', 'workers': 4}})
        lean = {k: v for k, v in by_role['formal_check'].items() if k not in {'id', 'sha256'}}
        with self.assertRaisesRegex(ValueError, 'machine profile settings differ'):
            profiles.seal_profile({**lean, 'machine': {'lean_command': ['synthetic-lean'], 'tool_manifest': []}})


if __name__ == '__main__':
    unittest.main()

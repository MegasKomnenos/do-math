"""Trust environments against shared toolchain records (``trust_validation``, ``trust_inventory``; layer 2).

The synthetic toolchain and its record come from ``research_fixtures.trust_fixture``
(real record producers over real files). The file system is real, so the
olean fingerprint sees real size, modification and creation times. The
current identity of the executables and checker is the host port's
observation; here the fake host reports it, and its real side is
``sim.test_toolchain_tools``.
"""
from copy import deepcopy
import ctypes
import json
import os
from pathlib import Path
import tempfile
import unittest

from do_math import trust_inventory as records
from do_math.canonical import exact_content_hash
from do_math.configuration import DEFAULT_CONFIG
from do_math.initialization import observation_window_warnings
from do_math.trust_validation import check_environment, environment_errors, register_request_errors
from support.trust_inputs import trust_environment, trust_fixture, validation_fixture
from support.fakes.host import FakeHost

CHANGED = 'approved toolchain file changed: '


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


class RecordCase(unittest.TestCase):
    """A synthetic toolchain, its record and the environment registering it, checked through the fake host."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.request = trust_fixture(self.root, ['synthetic-lean'])
        self.environment, self.binding = trust_environment(self.request)
        self.record_path = Path(self.request['toolchain_record']['path'])
        self.olean = Path(self.request['toolchain']['executable']).parents[1] / 'lib/lean/Init/Prelude.olean'
        self.host = FakeHost()

    def record(self):
        return records.read_record(self.record_path)

    def rewrite(self, change):
        record = json.loads(self.record_path.read_text(encoding='utf-8'))
        change(record)
        self.record_path.write_text(json.dumps(record), encoding='utf-8')

    def check(self, binding=None, **options):
        from support.entry import entry
        _entry = entry()
        result = check_environment(self.environment, self.binding if binding is None else binding, host=self.host,
                                   **options, clock=_entry.ports.clock)
        from support.engine_context import assert_trust_documents
        assert_trust_documents(self, result, owner='environment_check', expected={
            'environment_id': self.environment['id'], 'toolchain_record': self.environment['toolchain_record']})
        return result


class ToolchainRecordTests(RecordCase):
    def test_documented_environment_branches_keep_absence_and_exact_changes(self):
        from support.engine_context import assert_trust_documents
        from support.doc_code import trust_field_issues
        original = self.record_path.read_bytes()
        def checked(*, status, errors=None, changes=None):
            value = self.check()
            expected = {'environment_id': self.environment['id'],
                        'toolchain_record': self.request['toolchain_record'],
                        'binding': self.binding, 'status': status}
            if errors is not None:
                expected['errors'] = errors
            assert_trust_documents(self, value, owner='environment_check', expected=expected)
            self.assertNotIn('rebind', value)
            if changes is None:
                self.assertNotIn('changed_files', value)
                self.assertNotIn('changed_file_count', value)
            else:
                self.assertEqual(value['changed_files'], changes[:50])
                self.assertEqual(value['changed_file_count'], len(changes))
                self.assertTrue(value['errors'][0].startswith('olean fingerprint differs'))
                broken = deepcopy(value)
                del broken['changed_files']
                self.assertEqual(trust_field_issues('`environment_check.changed_files`',
                    'environment_check', broken), [('actual field', 'environment_check.changed_files')])
                with self.assertRaises(AssertionError):
                    assert_trust_documents(self, {**value, 'changed_file_count': 0},
                        owner='environment_check', expected={'changed_file_count': len(changes)})
            return value
        checked(status='verified', errors=[])
        added = []
        for index in range(55):
            path = self.olean.with_name(f'Extra{index:02d}.olean')
            path.write_bytes(b'explicit extra module')
            added.append(path)
        checked(status='invalid', changes=[f'toolchain/lib/lean/Init/Extra{i:02d}.olean' for i in range(55)])
        self.assertEqual(self.record_path.read_bytes(), original, 'admission never writes a baseline')
        for path in added:
            path.unlink()
        self.olean.write_bytes(b'changed judgment bytes')
        checked(status='invalid', changes=['toolchain/lib/lean/Init/Prelude.olean'])
        self.olean.unlink()
        checked(status='invalid', changes=['toolchain/lib/lean/Init/Prelude.olean'])
        self.record_path.write_bytes(b'{corrupt')
        value = checked(status='invalid')
        self.assertTrue(value['errors'][0].startswith('toolchain record unavailable: '))
        self.assertNotIn('fingerprint_sha256', value)
        self.record_path.unlink()
        missing = checked(status='invalid')
        self.assertIsNone(missing['record_state'])
        self.assertTrue(missing['errors'][0].startswith('toolchain record unavailable: '))
        self.assertNotEqual(value['errors'], missing['errors'])

    def test_live_admission_tracks_added_and_removed_judgment_files_but_ignores_notes(self):
        note = self.olean.parent / 'notes.txt'
        note.write_bytes(b'not a judgment module')
        self.assertEqual(self.check()['status'], 'verified')
        added = self.olean.parent / 'Added.olean'
        added.write_bytes(b'a new judgment module')
        result = self.check()
        self.assertEqual(result['status'], 'invalid')
        self.assertEqual(result['changed_files'], ['toolchain/lib/lean/Init/Added.olean'])
        added.unlink()
        self.assertEqual(self.check()['status'], 'verified')
        self.olean.unlink()
        result = self.check()
        self.assertEqual(result['status'], 'invalid')
        self.assertEqual(result['changed_files'], ['toolchain/lib/lean/Init/Prelude.olean'])

    def test_live_admission_rejects_a_missing_recorded_member_even_when_installed_files_are_unchanged(self):
        self.assertEqual(self.check()['status'], 'verified')
        self.rewrite(lambda r: r['baselines'][0]['fingerprint']['files'].pop('toolchain/lib/lean/Init/Prelude.olean'))
        result = self.check()
        self.assertEqual(result['status'], 'invalid')
        self.assertIn('fingerprint digest differs', result['errors'][0])

    def test_current_environment_is_verified_from_record_identity_and_fingerprint(self):
        self.assertEqual(environment_errors(self.environment, self.binding), [])
        self.assertEqual(register_request_errors({k: v for k, v in self.request.items()}), [])
        result = self.check()
        self.assertEqual(result['status'], 'verified')
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['identity_sha256'], exact_content_hash(self.request['toolchain']))
        self.assertEqual(result['fingerprint_sha256'], self.binding['fingerprint_sha256'])
        self.assertEqual(result['binding'], self.binding)
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
                result = self.check()
                self.assertEqual(result['status'], 'invalid')
                self.assertIn('toolchain record unavailable', result['errors'][0])
                self.record_path.write_bytes(original)

    def test_success_label_cannot_replace_failed_representative_evidence(self):
        for change in ({'exit_code': 17}, {'status': 'failed'}):
            with self.subTest(change=change):
                original = self.record_path.read_bytes()
                def failed_evidence(record):
                    baseline = record['baselines'][-1]
                    baseline['validation'].update(change)
                    baseline['validation_sha256'] = records.validation_sha256(baseline['validation'])
                self.rewrite(failed_evidence)
                result = self.check()
                self.assertEqual(result['status'], 'invalid')
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

    def test_fingerprint_detects_size_modification_creation_and_recreation(self):
        original = self.olean.read_bytes()
        info = os.stat(self.olean)

        def restore():
            self.olean.write_bytes(original)
            os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns))
            set_birthtime(self.olean, info.st_birthtime_ns)
            self.assertEqual(self.check()['status'], 'verified')
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
                result = self.check()
                self.assertEqual(result['status'], 'invalid')
                self.assertIn('olean fingerprint differs', result['errors'][0])
                self.assertTrue(result['changed_files'])
                self.assertEqual(result['changed_file_count'], len(result['changed_files']))
                self.olean.with_name('Extra.olean').unlink(missing_ok=True)
                restore()

    def test_rebind_requires_the_current_baseline_and_the_same_identity(self):
        from support.entry import entry
        _entry = entry()
        info = os.stat(self.olean)
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
        # A second baseline, made by the record producers as setup_lean --rerecord makes it.
        record = self.record()
        fingerprint = records.observe_fingerprint(record['identity'])
        content = records.content_hashes(record['identity'], fingerprint['files'])
        record['baselines'].append(records.new_baseline(fingerprint, content,
                                                        validation_fixture(record['identity'], self.root / 'smoke.lean'), clock=_entry.ports.clock))
        records.write_record(self.record_path, record)
        current = records.binding(record)
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 2 * 10**9))
        result = self.check()
        self.assertEqual(result['status'], 'invalid')
        self.assertIn('olean fingerprint differs', result['errors'][0])
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
        for identity in (True, False):
            with self.subTest(identity=identity):
                rebound = self.check(identity=identity)
                self.assertEqual(rebound['status'], 'verified')
                self.assertEqual(rebound['rebind'], {'previous': self.binding, 'current': current,
                                                     'recorded_at': record['baselines'][1]['recorded_at']})
                self.assertEqual(rebound['binding'], current)
                from support.engine_context import assert_trust_documents
                assert_trust_documents(self, rebound, owner='environment_check', expected={
                    'status': 'verified', 'errors': [], 'binding': current,
                    'rebind': {'previous': self.binding, 'current': current,
                               'recorded_at': record['baselines'][1]['recorded_at']}})
                self.assertNotIn('changed_files', rebound)
                self.assertNotIn('changed_file_count', rebound)
                self.assertEqual(len(self.record()['baselines']), 2)
        replaced = self.request['toolchain']['executable']
        self.host.toolchain_errors = [CHANGED + replaced]
        result = self.check(identity=False)
        self.assertEqual(result['status'], 'invalid')
        self.assertEqual(result['errors'], [CHANGED + replaced])
        self.assertNotIn('rebind', result)
        self.assertNotIn('changed_files', result)


class EnvironmentContractTests(unittest.TestCase):
    """The lexical contracts of a stored environment, its binding and a registration request."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.request = trust_fixture(Path(temporary.name), ['synthetic-lean'])
        self.environment, self.binding = trust_environment(self.request)

    def test_each_environment_rule_names_what_it_refuses(self):
        self.assertEqual(environment_errors(None, self.binding), ['trust environment absent'])
        cases = {
            'unknown field': (lambda e, b: e.update(extra=1), 'trust environment fields differ from the current contract'),
            'missing field': (lambda e, b: e.pop('allowed_axioms'), 'trust environment fields differ from the current contract'),
            'no adoption': (lambda e, b: e.update(source_ref=''), 'trust environment has no explicit adoption'),
            'axioms': (lambda e, b: e.update(allowed_axioms=e['allowed_axioms'][1:]), 'foundation axiom profile differs'),
            'record path': (lambda e, b: e['toolchain_record'].update(path='relative.json'),
                            'toolchain_record requires the absolute path of <record ID>.json and that ID'),
            'record ID': (lambda e, b: e['toolchain_record'].update(id='TC-short'),
                          'toolchain_record requires the absolute path of <record ID>.json and that ID'),
            'binding': (lambda e, b: b.update(baseline=-1),
                        'trust binding requires a baseline index and its fingerprint, content and validation digests'),
            'binding digest': (lambda e, b: b.update(content_sha256='x'),
                               'trust binding requires a baseline index and its fingerprint, content and validation digests'),
            'identity': (lambda e, b: e['toolchain'].update(version=''), 'toolchain.version must be nonempty'),
        }
        for name, (change, message) in cases.items():
            with self.subTest(name):
                environment, binding = deepcopy(self.environment), deepcopy(self.binding)
                change(environment, binding)
                self.assertIn(message, environment_errors(environment, binding))
        self.assertEqual(environment_errors(self.environment, None),
                         ['trust binding requires a baseline index and its fingerprint, content and validation digests'])

    def test_a_registration_request_has_exactly_its_fields(self):
        self.assertEqual(register_request_errors(self.request), [])
        self.assertEqual(register_request_errors({**self.request, 'extra': 1}),
                         ['trust register requires exactly toolchain, allowed_axioms, toolchain_record and binding'])
        self.assertEqual(register_request_errors('register'),
                         ['trust register requires exactly toolchain, allowed_axioms, toolchain_record and binding'])
        moved = deepcopy(self.request)
        moved['toolchain_record']['path'] = str(Path(moved['toolchain_record']['path']).with_name('other.json'))
        self.assertEqual(register_request_errors(moved),
                         ['toolchain_record requires the absolute path of <record ID>.json and that ID'])


class EnvironmentCheckTests(RecordCase):
    """The live check and the formal-use admission that read the record through the host port."""

    def test_the_record_must_be_the_registered_one_with_the_registered_identity(self):
        other = trust_fixture(self.root / 'other', ['other-lean'])
        self.environment['toolchain_record']['path'] = other['toolchain_record']['path']
        result = self.check()
        self.assertEqual(result['status'], 'invalid')
        self.assertEqual(result['errors'], ['toolchain record ID differs from the registered record',
                                            'toolchain record identity differs from the registered environment'])
        self.assertEqual(result['toolchain_record']['path'], other['toolchain_record']['path'])

    def test_the_current_identity_is_observed_only_when_asked(self):
        self.host.toolchain_errors = [CHANGED + 'lean.exe']
        self.assertEqual(self.check()['errors'], [CHANGED + 'lean.exe'])
        self.assertEqual(self.check(identity=False)['status'], 'verified')

    def test_unreadable_judgment_files_invalidate_the_check(self):
        toolchain = Path(self.request['toolchain']['executable']).parents[1]
        toolchain.rename(toolchain.with_name('moved-toolchain'))
        result = self.check()
        self.assertEqual(result['status'], 'invalid')
        self.assertTrue(result['errors'][0].startswith('judgment files unavailable: '), result['errors'])

    def test_record_state_marks_a_record_change_and_a_missing_record(self):
        from do_math.trust_validation import environment_changed, record_state, wait_detail
        state = record_state(self.environment)
        self.assertTrue(state)
        instance = {'active_trust_environment': self.environment['id'],
                    'trust_environments': {self.environment['id']: self.environment}}
        detail = wait_detail(instance)
        self.assertEqual(detail, {'environment_id': self.environment['id'], 'record_state': state})
        self.assertFalse(environment_changed(instance, detail))
        self.rewrite(lambda record: record['checks'].append(
            {'checked_at': 'now', 'baseline': 0, 'result': 'passed', 'mismatched': []}))
        self.assertTrue(environment_changed(instance, detail))
        self.record_path.unlink()
        self.assertIsNone(record_state(self.environment))
        self.assertEqual(wait_detail({'active_trust_environment': None, 'trust_environments': {}}),
                         {'environment_id': None, 'record_state': None})

    def test_formal_verification_runs_only_after_the_environment_is_admitted(self):
        from support.entry import entry
        _entry = entry()
        from do_math.trust_validation import verify_formal
        calls = []

        def verifier(**arguments):
            calls.append(arguments)
            return {'status': 'verified'}
        result = verify_formal(environment=self.environment, binding=self.binding, verifier=verifier, host=self.host,
                               source='theorem', clock=_entry.ports.clock)
        self.assertEqual(calls, [{'source': 'theorem'}])
        self.assertEqual(result['status'], 'verified')
        self.assertEqual(result['environment_check']['status'], 'verified')
        self.olean.write_bytes(b'changed module')
        refused = verify_formal(environment=self.environment, binding=self.binding, verifier=verifier, host=self.host, clock=_entry.ports.clock)
        self.assertEqual(len(calls), 1)
        self.assertEqual({key: refused[key] for key in ('status', 'error_kind', 'launch_not_created')},
                         {'status': 'failed', 'error_kind': 'trust_environment', 'launch_not_created': True})
        self.assertTrue(refused['reason'].startswith('environment admission failed: olean fingerprint differs'))

    def test_formal_use_needs_the_active_valid_environment_and_its_current_identity(self):
        from do_math.trust_validation import EnvironmentUnavailable, require_active_environment
        instance = {'active_trust_environment': self.environment['id'],
                    'trust_environments': {self.environment['id']: self.environment}}
        runtime = {'trust_transitions': {}, 'trust_bindings': {self.environment['id']: self.binding}}
        self.assertEqual(require_active_environment(instance, runtime, host=self.host), self.environment)
        # The olean fingerprint was checked before compiling; publication checks only the current identity.
        self.olean.write_bytes(b'changed module after the formal check')
        self.assertEqual(require_active_environment(instance, runtime, current_identity=True, host=self.host),
                         self.environment)
        self.host.toolchain_errors = [CHANGED + self.request['toolchain']['executable']]
        self.assertEqual(require_active_environment(instance, runtime, host=self.host), self.environment)
        with self.assertRaisesRegex(EnvironmentUnavailable, 'current trust identity required: approved toolchain file changed') as caught:
            require_active_environment(instance, runtime, current_identity=True, host=self.host)
        self.assertEqual(caught.exception.detail['environment_id'], self.environment['id'])
        self.host.toolchain_errors = []
        with self.assertRaisesRegex(ValueError, 'formal admission is blocked during a trust transition'):
            require_active_environment(instance, {**runtime, 'trust_transitions': {'TR-1': {'status': 'checking'}}},
                                       host=self.host)
        self.environment['status'] = 'registered'
        with self.assertRaisesRegex(ValueError, 'approved fixed trust environment required'):
            require_active_environment(instance, runtime, host=self.host)
        self.environment['status'] = 'active'
        with self.assertRaisesRegex(ValueError, 'approved fixed trust environment required: trust binding requires'):
            require_active_environment(instance, {**runtime, 'trust_bindings': {}}, host=self.host)


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
        from support.entry import entry
        _entry = entry()
        from do_math.execution_profiles import build_profiles
        built = build_profiles({**deepcopy(DEFAULT_CONFIG), **windows}, host=_entry.ports.host)
        instance = {**built, 'config': {}, 'trust_environments': {self.environment['id']: self.environment},
                    'lifecycle': {'state': 'initializing', 'adoption': {}}}
        runtime = {'status': 'initializing', 'history': [], 'trust_bindings': {self.environment['id']: self.binding}}
        return instance, runtime

    def test_windows_shorter_than_the_representative_compile_are_warned(self):
        instance, runtime = self.state(tool_review_window_seconds=120, self_check_response_window_seconds=240)
        warnings = observation_window_warnings(instance, runtime)
        self.assertTrue(warnings)
        self.assertIn('research_work', {row['role'] for row in warnings})
        for row in warnings:
            self.assertEqual({key: row[key] for key in ('field', 'window_seconds', 'environment_id',
                                                         'representative_check_seconds')},
                             {'field': 'tool_review_window_seconds', 'window_seconds': 120,
                              'environment_id': self.environment['id'], 'representative_check_seconds': 240})
            self.assertEqual(instance['execution_profiles'][row['profile_id']]['role'], row['role'])
        self.assertEqual(len({row['profile_id'] for row in warnings}), len(warnings))
        instance, runtime = self.state(tool_review_window_seconds=240, self_check_response_window_seconds=240)
        self.assertEqual(observation_window_warnings(instance, runtime), [])

    def test_the_self_check_response_window_is_not_bound_by_a_compile(self):
        # Research calls such as a compile hold the response deadline (ObservationTracker._hold_deadlines).
        instance, runtime = self.state(tool_review_window_seconds=240, self_check_response_window_seconds=60)
        self.assertEqual(observation_window_warnings(instance, runtime), [])

    def test_a_stale_profile_reference_is_passed_over_and_a_repeated_profile_warned_once(self):
        instance, runtime = self.state(tool_review_window_seconds=120, self_check_response_window_seconds=240)
        expected = observation_window_warnings(instance, runtime)
        reference = next(ref for refs in instance['role_profile_refs'].values() for ref in refs
                         if ref['id'] == expected[0]['profile_id'])
        instance['role_profile_refs']['repeated'] = [reference, {**reference, 'sha256': '0' * 64}]
        self.assertEqual(observation_window_warnings(instance, runtime), expected)

    def test_an_invalid_or_unreadable_toolchain_gives_no_warning(self):
        instance, runtime = self.state(tool_review_window_seconds=120, self_check_response_window_seconds=240)
        self.environment['status'] = 'invalid'
        self.assertEqual(observation_window_warnings(instance, runtime), [])
        self.environment['status'] = 'registered'
        runtime['trust_bindings'] = {}
        self.assertEqual(observation_window_warnings(instance, runtime), [])


class ActivationProfileTests(unittest.TestCase):
    def test_lean_roles_pin_only_the_command_and_activation_has_no_machine_settings(self):
        from support.entry import entry
        _entry = entry()
        from do_math import execution_profiles as profiles
        built = profiles.build_profiles({**DEFAULT_CONFIG, 'lean_command': ['synthetic-lean']}, host=_entry.ports.host)
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

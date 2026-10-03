"""Toolchain records, identity and olean fingerprints under the accidental-change model."""
from datetime import datetime, timezone
import os
from pathlib import Path
import tempfile
import unittest

from do_math.local_host import LocalHost
import setup_lean
from do_math import trust_inventory as records
from do_math.trust_validation import check_environment
from support.trust_inputs import trust_environment, trust_fixture
from support.fakes.clock import FakeClock
from support.knowledge_verifier_jobs import OutputCompiler, worker_jobs
from do_math.file_io import RACY_NS



class ToolchainFoundationRecordTests(unittest.TestCase):
    def setUp(self):
        from support.entry import entry
        _entry = entry()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.process_environment = _entry.environment
        self.git_backend = _entry.ports.git_backend
        self.clock = FakeClock(wall=datetime(2090, 1, 1, tzinfo=timezone.utc))
        self.compiler = OutputCompiler('synthetic external compiler result')
        self.jobs = worker_jobs(self.compiler)
        self.host = LocalHost(jobs=self.jobs, clock=self.clock, environment=_entry.environment, git_backend=_entry.ports.git_backend)
        self.request = trust_fixture(self.root, ['synthetic-lean'])
        self.environment, self.binding = trust_environment(self.request)
        self.record_path = Path(self.request['toolchain_record']['path'])
        self.olean = Path(self.request['toolchain']['executable']).parents[1] / 'lib/lean/Init/Prelude.olean'

    def record(self):
        return records.read_record(self.record_path)

    def options(self, **changes):
        return {'identity': self.request['toolchain'], 'jobs': self.jobs, 'clock': self.clock, 'environment': self.process_environment, 'git_backend': self.git_backend, **changes}

    def rerecord(self):
        from support.entry import entry
        _entry = entry()
        return setup_lean.rerecord(['synthetic-lean'], self.record_path.parent, self.root / 'evidence', None,
                                   **self.options())

    def test_foundation_fingerprint_does_not_see_content_changed_with_all_metadata_preserved(self):
        """The declared limit of the accidental-change model; only a content check finds it."""
        from support.entry import entry
        _entry = entry()
        info = os.stat(self.olean)
        raw = self.olean.read_bytes()
        with self.olean.open('r+b') as stream:
            stream.write(bytes([raw[0] ^ 1]))
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns))
        self.assertEqual(os.stat(self.olean).st_birthtime_ns, info.st_birthtime_ns)
        self.assertEqual(check_environment(self.environment, self.binding, host=self.host, clock=self.clock)['status'], 'verified')
        result = setup_lean.check_contents(self.record_path.parent, None, ['synthetic-lean'], **self.options())
        self.assertEqual(result['status'], 'mismatch')
        self.assertEqual(result['check']['mismatched'], ['toolchain/lib/lean/Init/Prelude.olean'])
        blocked = check_environment(self.environment, self.binding, host=self.host, clock=self.clock)
        self.assertEqual(blocked['status'], 'invalid')
        self.assertIn('a content check found files that differ from the current toolchain baseline', blocked['errors'])

    def test_foundation_content_check_passes_records_history_and_never_blocks_readers(self):
        from support.entry import entry
        _entry = entry()
        with records.writer_lock(self.record_path.parent):
            # Instances only read the record; a running writer never blocks them.
            self.assertEqual(check_environment(self.environment, self.binding, host=self.host, clock=self.clock)['status'], 'verified')
            with self.assertRaisesRegex(OSError, "(Permission denied|being used|lock)"):
                self.rerecord()
        result = setup_lean.check_contents(self.record_path.parent, self.request['toolchain_record']['id'], None, **self.options())
        self.assertEqual((result['status'], result['check']['baseline']), ('passed', 0))
        self.assertEqual(self.record()['checks'], [result['check']])
        self.assertEqual(check_environment(self.environment, self.binding, host=self.host, clock=self.clock)['status'], 'verified')

    def test_foundation_rerecord_after_metadata_only_change_rebinds_each_instance_once(self):
        from support.entry import entry
        _entry = entry()
        other_environment, other_binding = trust_environment(self.request, environment_id='TE-other')
        info = os.stat(self.olean)
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
        self.assertEqual(check_environment(self.environment, self.binding, host=self.host, clock=self.clock)['status'], 'invalid')
        result = self.rerecord()
        self.assertEqual(result['status'], 'recorded')
        record = self.record()
        self.assertEqual(len(record['baselines']), 2)
        self.assertEqual(record['baselines'][1]['content'], record['baselines'][0]['content'])
        current = records.binding(record)
        self.assertEqual(result['binding'], current)
        for environment, binding in ((self.environment, self.binding), (other_environment, other_binding)):
            checked = check_environment(environment, binding, host=self.host, clock=self.clock)
            self.assertEqual(checked['status'], 'verified')
            self.assertEqual(checked['rebind']['previous'], binding)
            self.assertEqual(checked['rebind']['current'], current)
            self.assertEqual(checked['binding'], current)
        followed = check_environment(self.environment, current, host=self.host, clock=self.clock)
        self.assertEqual(followed['status'], 'verified')
        self.assertNotIn('rebind', followed)

    def test_foundation_rerecord_refuses_changed_content_identity_or_failed_compile(self):
        from support.entry import entry
        _entry = entry()
        with self.olean.open('r+b') as stream:
            stream.write(b'Z')
        with self.assertRaises(setup_lean.Refused) as refused:
            self.rerecord()
        self.assertEqual(refused.exception.result['mismatched'], ['toolchain/lib/lean/Init/Prelude.olean'])
        self.olean.write_bytes(('CORE_TESTS synthetic lib/lean/Init/Prelude.olean for synthetic-lean').encode())
        changed = {**self.request['toolchain'], 'version': 'Lean test 4.33.0'}
        with self.assertRaises(setup_lean.Refused) as refused:
            setup_lean.rerecord(['synthetic-lean'], self.record_path.parent, self.root / 'evidence',
                                self.request['toolchain_record']['id'], **self.options(identity=changed))
        self.assertIn('identity differs', refused.exception.result['reason'])
        self.compiler.exit_code = 1
        with self.assertRaises(setup_lean.Refused) as refused:
            setup_lean.rerecord(['synthetic-lean'], self.record_path.parent, self.root / 'evidence', None, **self.options())
        self.assertEqual(refused.exception.result['status'], 'failed')
        self.assertEqual(len(self.record()['baselines']), 1)

    def test_foundation_install_records_once_and_never_appends_a_baseline(self):
        from support.entry import entry
        _entry = entry()
        confirmed = setup_lean.record_installation(['synthetic-lean'], self.record_path.parent, self.root / 'evidence', **self.options())
        self.assertEqual((confirmed['status'], confirmed['created']), ('recorded', False))
        info = os.stat(self.olean)
        os.utime(self.olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
        with self.assertRaises(setup_lean.Refused) as refused:
            setup_lean.record_installation(['synthetic-lean'], self.record_path.parent, self.root / 'evidence', **self.options())
        self.assertEqual(refused.exception.result['status'], 'rerecord_required')
        self.assertEqual(len(self.record()['baselines']), 1)
        changed = {**self.request['toolchain'], 'version': 'Lean test 4.33.0'}
        created = setup_lean.record_installation(['synthetic-lean'], self.record_path.parent, self.root / 'evidence',
                                                  **self.options(identity=changed))
        self.assertTrue(created['created'])
        self.assertNotEqual(created['record_id'], self.request['toolchain_record']['id'])
        self.assertEqual(len(list(self.record_path.parent.glob('TC-*.json'))), 2)

    def test_foundation_baseline_waits_for_settled_fingerprints_and_refuses_a_changing_install(self):
        # File metadata is fresh; a frozen clock cannot age it through the racy window.
        from support.entry import entry
        _entry = entry()
        class FrozenClock(FakeClock):
            def sleep(self, seconds):
                self.waited.append(seconds)
        clock = FrozenClock(wall=datetime.now(timezone.utc))
        clock.waited = []
        with self.assertRaisesRegex(RuntimeError, 'still changing'):
            setup_lean.rerecord(['synthetic-lean'], self.record_path.parent, self.root / 'evidence', None,
                                **self.options(clock=clock), racy_ns=RACY_NS)
        self.assertEqual(clock.waited, [RACY_NS / 1e9] * 3)
        self.assertEqual(len(self.record()['baselines']), 1)

    def test_foundation_recorded_summary_reports_the_representative_compile_duration(self):
        from support.entry import entry
        _entry = entry()
        confirmed = setup_lean.record_installation(['synthetic-lean'], self.record_path.parent, self.root / 'evidence',
                                                    **self.options())
        self.assertEqual(confirmed['representative_check_seconds'], 1)


if __name__ == '__main__':
    unittest.main()

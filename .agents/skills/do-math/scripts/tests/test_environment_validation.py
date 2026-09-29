"""Toolchain records, identity and olean fingerprints under the accidental-change model."""
from copy import deepcopy
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
from do_math.trust_validation import check_environment
from research_fixtures import fixture_setup_lean, trust_environment, trust_fixture



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





if __name__ == '__main__':
    unittest.main()

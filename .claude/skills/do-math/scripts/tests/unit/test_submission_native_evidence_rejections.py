"""native_final 미도달: 실제 증거 형식을 유지하고 목표 필드만 손상한다."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import unittest

from do_math.native_final import verified_native_final
from support.fakes.clock import FakeClock
from support.fakes.jobs import FakeJobs
from support.submission_receiver import native_result


class NativeEvidenceRejectionTests(unittest.TestCase):
    def setUp(self):
        self.execution = {'id': 'EX-native', 'grant_id': 'GR-native',
                          'execution_profile_ref': {'id': 'EP-native', 'sha256': 'a' * 64}}
        self.context = {'execution_id': 'EX-native', 'action': {'grant_id': 'GR-native'}}
        self.raw = b'{"summary":"exact bytes"}'
        ports = SimpleNamespace(ports=SimpleNamespace(jobs=FakeJobs([])), clock=FakeClock())
        self.result = native_result(ports, self.execution, self.context, self.raw, Path('C:/workspace'))

    def test_each_artifact_size_presence_and_raw_type_are_revalidated(self):
        for artifact in ('source_request', 'source_prompt', 'stdout', 'final'):
            for changes in ({'bytes': -1}, {'present': False}, {'raw': 'not bytes'}, {'sha256': 0}):
                with self.subTest(artifact=artifact, changes=changes):
                    result = deepcopy(self.result)
                    result['execution']['collect'][artifact].update(changes)
                    with self.assertRaisesRegex(ValueError, '^native artifact hash or size differs: ' + artifact + '$'):
                        verified_native_final(result, self.execution, self.context)

    def test_each_collection_status_and_start_identity_must_match_the_published_execution(self):
        self.assertEqual(verified_native_final(self.result, self.execution, self.context), self.raw)
        for owner in ('collect', 'started', 'worker_status'):
            for key, incorrect in (('execution_id', 'EX-other'),
                                   ('profile_ref', {'id': 'EP-other', 'sha256': 'b' * 64})):
                for absent in (False, True):
                    with self.subTest(owner=owner, key=key, absent=absent):
                        result = deepcopy(self.result)
                        row = (result['execution']['collect']['worker_status'] if owner == 'worker_status'
                               else result['execution'][owner])
                        if absent:
                            row.pop(key)
                        else:
                            row[key] = incorrect
                        before = deepcopy(result)
                        with self.assertRaisesRegex(ValueError, '^native execution/profile binding differs$'):
                            verified_native_final(result, self.execution, self.context)
                        self.assertEqual(result, before)

    def test_authority_and_job_identity_have_separate_rejections(self):
        with self.assertRaisesRegex(ValueError, '^native input or authority binding differs$'):
            verified_native_final(self.result, self.execution,
                                  {**self.context, 'action': {'grant_id': 'GR-other'}})
        for job in ('', 'other-job'):
            result = deepcopy(self.result)
            result['execution']['started']['job_name'] = job
            with self.subTest(job=job), self.assertRaisesRegex(ValueError, '^native Job identity differs from its published process$'):
                verified_native_final(result, self.execution, self.context)

    def test_published_and_collected_integer_forms_return_the_exact_final(self):
        for key in ('pid', 'creation_filetime'):
            execution, result = deepcopy(self.execution), deepcopy(self.result)
            value = int(execution['capacity']['process'][key])
            execution['capacity']['process'][key] = value
            result['execution']['started'][key] = str(value)
            result['execution']['collect']['process_identity'][key] = str(value)
            with self.subTest(key=key):
                self.assertEqual(verified_native_final(result, execution, self.context), self.raw)

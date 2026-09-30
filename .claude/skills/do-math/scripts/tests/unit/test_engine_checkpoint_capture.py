"""A checkpoint capture owns exact bytes of the checkpoint and its evidence (``observations.preserve_checkpoint``, layer 2).

Each test writes a worker's workspace in a temporary folder and calls the
capture directly, as the legacy tests did.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json
from do_math.observations import preserve_checkpoint

CHECKPOINT = {'current_claim': 'original evidence', 'evidence_paths': ['proof.txt'],
              'attempts': ['original checked'], 'remaining_work': ['continue'],
              'next_step': 'continue', 'progress_state': 'working'}


def workspace(test):
    directory = tempfile.TemporaryDirectory()
    test.addCleanup(directory.cleanup)
    return Path(directory.name)


class FinalCheckpointCaptureTests(unittest.TestCase):
    def test_final_capture_owns_exact_raw_and_input_evidence_independently_of_submission_outputs(self):
        root = workspace(self)
        (root / 'input').mkdir()
        (root / 'input/source.txt').write_bytes(b'fixed input')
        value = {**CHECKPOINT, 'evidence_paths': ['input/source.txt']}
        raw = canonical_json(value)
        (root / 'checkpoint.json').write_bytes(raw)
        first, artifacts = preserve_checkpoint(root, artifact_prefix='runtime/artifacts/BA-1/checkpoint', max_bytes=4096)
        self.assertEqual(artifacts[first['artifact_ref']], raw)
        self.assertEqual(artifacts[first['evidence_files'][0]['artifact_ref']], b'fixed input')
        (root / 'input/source.txt').write_bytes(b'changed later')
        same, new_artifacts = preserve_checkpoint(root, previous=first,
                                                  artifact_prefix='runtime/artifacts/BA-2/checkpoint', max_bytes=4096)
        self.assertEqual(same, first)
        self.assertEqual(new_artifacts, {})
        (root / 'checkpoint.json').write_bytes(canonical_json({**value, 'current_claim': 'new claim'}))
        changed, new_artifacts = preserve_checkpoint(root, previous=first,
                                                     artifact_prefix='runtime/artifacts/BA-3/checkpoint', max_bytes=4096)
        self.assertNotEqual(changed['sha256'], first['sha256'])
        self.assertEqual(new_artifacts[changed['evidence_files'][0]['artifact_ref']], b'changed later')

    def test_capture_budget_omissions_and_invalid_final_do_not_invent_evidence(self):
        root = workspace(self)
        (root / 'proof.txt').write_bytes(b'x' * 100)
        raw = canonical_json(CHECKPOINT)
        (root / 'checkpoint.json').write_bytes(raw)
        first, artifacts = preserve_checkpoint(root, artifact_prefix='runtime/artifacts/BA-1/checkpoint', max_bytes=len(raw))
        self.assertEqual(first['evidence_files'], [])
        self.assertEqual(first['evidence_omitted'][0]['path'], 'proof.txt')
        self.assertEqual(sum(map(len, artifacts.values())), len(raw))
        (root / 'checkpoint.json').unlink()
        missing, artifacts = preserve_checkpoint(root, previous=first,
                                                 artifact_prefix='runtime/artifacts/BA-2/checkpoint', max_bytes=4096)
        self.assertEqual(missing['artifact_ref'], first['artifact_ref'])
        self.assertEqual(missing['final_observation']['checkpoint_status'], 'missing')
        self.assertEqual(artifacts, {})
        (root / 'checkpoint.json').write_bytes(raw)
        limited, artifacts = preserve_checkpoint(root, artifact_prefix='runtime/artifacts/BA-3/checkpoint', max_bytes=1)
        self.assertEqual(limited['kind'], 'observed_partial_state')
        self.assertEqual(artifacts, {})


class CheckpointPreservationTests(unittest.TestCase):
    def test_collected_checkpoint_keeps_exact_resume_reference(self):
        value = {'current_claim': 'Partial claim', 'evidence_paths': [], 'attempts': ['Compared the definitions'],
                 'remaining_work': ['Finish the argument'], 'next_step': 'Check the remaining case',
                 'progress_state': 'working', 'counters': {}}
        root = workspace(self)
        raw = json.dumps(value).encode()  # not canonical JSON: the bytes are kept, not re-serialized
        (root / 'checkpoint.json').write_bytes(raw)
        checkpoint, artifacts = preserve_checkpoint(root, artifact_prefix='runtime/artifacts/BA/checkpoint', max_bytes=4096)
        self.assertEqual(checkpoint['kind'], 'worker_checkpoint')
        self.assertEqual(artifacts[checkpoint['artifact_ref']], raw)
        self.assertEqual(checkpoint['sha256'], hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    unittest.main()

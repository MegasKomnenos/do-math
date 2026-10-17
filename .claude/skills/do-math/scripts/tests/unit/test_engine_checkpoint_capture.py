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
    def test_native_capture_refuses_a_changed_input_then_preserves_one_exact_final(self):
        """T3 13.6 s: published input and native receipt need the real repository."""
        from copy import deepcopy
        from support.submission_scenes import native_scene
        from support.submission_receiver import native_result
        scene = native_scene()
        engine = scene.engine
        execution = engine.runtime['executions']['EX-history']
        raw = canonical_json(scene.output)
        result = native_result(scene.sim, execution, scene.context, raw, scene.workspace)
        engine._save()
        execution = engine.runtime['executions']['EX-history']
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^native capture differs from the published input or schema$'):
            engine._capture_native_submission(execution, result, {**scene.context, 'goal': 'unpublished goal'},
                                             scene.schema, scene.workspace, raw)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        receipt = engine._capture_native_submission(execution, result, scene.context, scene.schema, scene.workspace, raw)
        self.assertEqual(receipt['state'], 'accepted')
        execution = engine.runtime['executions'][execution['id']]
        published = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^a different native final was already captured for this execution$'):
            engine._capture_native_submission(execution, result, scene.context, scene.schema, scene.workspace, raw + b' ')
        self.assertEqual((engine.head, engine.instance, engine.runtime), published)
        self.assertEqual(engine.store.read(execution['submission_intent']['output_ref'], engine.head), raw)

    def test_native_incomplete_outputs_preserve_the_central_rejection_and_provider_status(self):
        """T3 15.5 s: real capture must preserve its rejected check and provider status."""
        from support.submission_scenes import native_scene
        from support.submission_receiver import native_result
        from do_math import submission
        import jsonschema
        scene = native_scene()
        engine = scene.engine
        execution = engine.runtime['executions']['EX-history']
        output = scene.output
        jsonschema.Draft202012Validator(scene.schema).validate(output)
        (scene.workspace / 'too-large.txt').write_bytes(b'x' * (engine.instance['config']['max_artifact_bytes'] + 1))
        result = native_result(scene.sim, execution, scene.context, canonical_json(output), scene.workspace)
        collected = engine._collect_submitted_result(execution, result, scene.context, scene.schema, scene.workspace)
        self.assertEqual((collected['status'], collected['provider_result_status'], collected['error_kind']),
                         ('failed', 'completed', 'execution_failure'))
        self.assertTrue(collected['error'].startswith('native final failed central structural validation; see '),
                        collected['error'])
        receipt = next(event['basis']['receipt'] for event in engine.runtime['events']
                       if event['kind'] == 'submission_checked' and event.get('target') == execution['id']
                       and event.get('basis', {}).get('origin') == 'native_final')
        self.assertEqual(receipt['state'], 'rejected')
        check = submission.load_json(engine.store.read(receipt['payload']['submission_check']['check_ref'], engine.head))
        self.assertFalse(check['passed'])
        self.assertNotIn('failure_kind', check)
        self.assertTrue(any(issue['rule_id'] == 'artifact.preservation' and issue['path'] == 'too-large.txt'
                            for issue in check['issues']))
        self.assertEqual(engine.store.load()[2], engine.runtime)

    def test_task_evidence_format_checks_checkpoint_structure_and_declines_unknown_formats(self):
        from do_math.core_engine import _artifact_format_valid
        raw = canonical_json(CHECKPOINT)
        self.assertTrue(_artifact_format_valid({'path': 'runtime/artifacts/BA/checkpoint.json'}, raw))
        self.assertFalse(_artifact_format_valid({'path': 'runtime/artifacts/BA/checkpoint.json'}, b'{}'))
        self.assertTrue(_artifact_format_valid({'path': 'runtime/artifacts/BA/result.json'}, b'{}'))
        self.assertFalse(_artifact_format_valid({'path': 'runtime/artifacts/BA/result.bin'}, b'proof'))
        self.assertFalse(_artifact_format_valid({'path': 'runtime/artifacts/BA/result.md'}, b'\x00'))

    def test_final_capture_owns_exact_raw_and_input_evidence_independently_of_submission_outputs(self):
        from support.entry import entry
        _entry = entry()
        root = workspace(self)
        (root / 'input').mkdir()
        (root / 'input/source.txt').write_bytes(b'fixed input')
        value = {**CHECKPOINT, 'evidence_paths': ['input/source.txt']}
        raw = canonical_json(value)
        (root / 'checkpoint.json').write_bytes(raw)
        first, artifacts = preserve_checkpoint(root, artifact_prefix='runtime/artifacts/BA-1/checkpoint', max_bytes=4096, clock=_entry.ports.clock)
        self.assertEqual(artifacts[first['artifact_ref']], raw)
        self.assertEqual(artifacts[first['evidence_files'][0]['artifact_ref']], b'fixed input')
        (root / 'input/source.txt').write_bytes(b'changed later')
        same, new_artifacts = preserve_checkpoint(root, previous=first,
                                                  artifact_prefix='runtime/artifacts/BA-2/checkpoint', max_bytes=4096, clock=_entry.ports.clock)
        self.assertEqual(same, first)
        self.assertEqual(new_artifacts, {})
        (root / 'checkpoint.json').write_bytes(canonical_json({**value, 'current_claim': 'new claim'}))
        changed, new_artifacts = preserve_checkpoint(root, previous=first,
                                                     artifact_prefix='runtime/artifacts/BA-3/checkpoint', max_bytes=4096, clock=_entry.ports.clock)
        self.assertNotEqual(changed['sha256'], first['sha256'])
        self.assertEqual(new_artifacts[changed['evidence_files'][0]['artifact_ref']], b'changed later')

    def test_capture_budget_omissions_and_invalid_final_do_not_invent_evidence(self):
        from support.entry import entry
        _entry = entry()
        root = workspace(self)
        (root / 'proof.txt').write_bytes(b'x' * 100)
        raw = canonical_json(CHECKPOINT)
        (root / 'checkpoint.json').write_bytes(raw)
        first, artifacts = preserve_checkpoint(root, artifact_prefix='runtime/artifacts/BA-1/checkpoint', max_bytes=len(raw), clock=_entry.ports.clock)
        self.assertEqual(first['evidence_files'], [])
        self.assertEqual(first['evidence_omitted'][0]['path'], 'proof.txt')
        self.assertEqual(sum(map(len, artifacts.values())), len(raw))
        (root / 'checkpoint.json').unlink()
        missing, artifacts = preserve_checkpoint(root, previous=first,
                                                 artifact_prefix='runtime/artifacts/BA-2/checkpoint', max_bytes=4096, clock=_entry.ports.clock)
        self.assertEqual(missing['artifact_ref'], first['artifact_ref'])
        self.assertEqual(missing['final_observation']['checkpoint_status'], 'missing')
        self.assertEqual(artifacts, {})
        (root / 'checkpoint.json').write_bytes(raw)
        limited, artifacts = preserve_checkpoint(root, artifact_prefix='runtime/artifacts/BA-3/checkpoint', max_bytes=1, clock=_entry.ports.clock)
        self.assertEqual(limited['kind'], 'observed_partial_state')
        self.assertEqual(artifacts, {})


class CheckpointPreservationTests(unittest.TestCase):
    def test_collected_checkpoint_keeps_exact_resume_reference(self):
        from support.entry import entry
        _entry = entry()
        value = {'current_claim': 'Partial claim', 'evidence_paths': [], 'attempts': ['Compared the definitions'],
                 'remaining_work': ['Finish the argument'], 'next_step': 'Check the remaining case',
                 'progress_state': 'working', 'counters': {}}
        root = workspace(self)
        raw = json.dumps(value).encode()  # not canonical JSON: the bytes are kept, not re-serialized
        (root / 'checkpoint.json').write_bytes(raw)
        checkpoint, artifacts = preserve_checkpoint(root, artifact_prefix='runtime/artifacts/BA/checkpoint', max_bytes=4096, clock=_entry.ports.clock)
        self.assertEqual(checkpoint['kind'], 'worker_checkpoint')
        self.assertEqual(artifacts[checkpoint['artifact_ref']], raw)
        self.assertEqual(checkpoint['sha256'], hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    unittest.main()

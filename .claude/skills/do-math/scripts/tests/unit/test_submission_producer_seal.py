"""The producer's sealed evidence (``submission``, layer 2): the central seal keeps the snapshot read log, and a check reuses the prepared tool digest."""
import tempfile
import unittest

from do_math import submission
from do_math.canonical import canonical_json
from support.purpose_answers import common
from support.role_answers import seal_response
from support.provider_probes import ObservedCalls
from support.submission_protocol import ProtocolScene, producer_workspace


class SealedReadLogTests(unittest.TestCase):
    def test_sealed_submission_preserves_the_snapshot_read_log(self):
        with tempfile.TemporaryDirectory() as directory:
            scene = ProtocolScene(directory)
            log = scene.workspace / 'checks/reads.jsonl'
            log.parent.mkdir(exist_ok=True)
            log.write_bytes(b'{"request": "DC-1", "status": "ok"}\n')
            sealed = submission.seal_submission(scene.workspace, '.scratch/draft.json', execution_id='EX-worker',
                                                context=scene.context, schema=scene.schema,
                                                max_artifact_bytes=1024 * 1024, clock=scene.clock)
            self.assertEqual(sealed['artifacts']['reads.jsonl'], log.read_bytes())


class ToolDigestTests(unittest.TestCase):
    def test_producer_check_reuses_the_prepared_tool_digest(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            workspace, context = producer_workspace(directory)
            output = {**common("No proposal."), "candidates": []}
            seal_response(output, context, workspace)
            draft = workspace / ".scratch/submission.json"
            draft.parent.mkdir(exist_ok=True)
            draft.write_bytes(canonical_json(output))
            # The legacy test wrapped read_stable with a patch; the unchanged function's calls are observed.
            with ObservedCalls(read=submission.read_stable) as read:
                result = submission._producer_check(workspace, ".scratch/submission.json", [], clock=_entry.ports.clock)
            self.assertEqual(result["tool_sha256"], context["submission_contract"]["tool_sha256"])
            paths = [str(arguments["path"]) for arguments in read.captured("read")]
            self.assertTrue(paths, 'the check read no file')
            # Preparation fixed the archive digest; a tool call never rereads the archive.
            self.assertFalse(any(path.endswith("submission-support.zip") for path in paths), paths)


if __name__ == "__main__":
    unittest.main()

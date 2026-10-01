"""The installed submission tool runs as its own Python process (``input/tools/check_submission.py``).

``submission.install_tools`` ships a support archive and a launcher script
into the producer's workspace; the producer runs that launcher in its own
interpreter, which imports only the archive. What these tests check is that
process boundary itself: the launcher starts, finds the archive, exits with the
check's verdict and writes its record. They run real child interpreters, so
they are boundary tests (tier T4).
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from do_math import contracts, submission
from do_math.canonical import canonical_json
from support.record_builders import research_work_context, two_observation_output
from support.fakes.clock import FakeClock
from test_categories import test_group


def install(workspace, context, schema):
    return submission.install_tools(workspace, context, schema, None, clock=FakeClock())


def run_tool(workspace, *arguments, command=None):
    """One run of the installed launcher in a child interpreter, in the workspace."""
    return subprocess.run([*(command or [sys.executable, "-B", "input/tools/check_submission.py"]), *arguments],
                          cwd=workspace, capture_output=True, text=True, encoding="utf-8", timeout=60)


@test_group('resource')
class InstalledCheckerTests(unittest.TestCase):
    def test_installed_checker_uses_latest_schema_bytes_and_prior_check(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"action": {"role": "maintenance", "id": "AC-1", "target": "TK-1"},
                       "execution_id": "EX-1", "snapshot": "fixed", "kind_definitions": {}}
            schema = contracts.schema_for("maintenance")
            install(workspace, context, schema)
            draft = workspace / ".scratch/draft.json"
            draft.parent.mkdir()
            good = {"summary": "Check", "used_sources": [], "questions": [], "report": "Checked", "remaining_work": [],
                    "integration_bundles": [{"integration_id": "IN-1", "members": ["output"], "impact_set": [],
                                             "authority_refs": []}]}
            self.assertEqual(canonical_json(schema), (workspace / "input/submission/schema.json").read_bytes())
            with zipfile.ZipFile(workspace / "input/tools/submission-support.zip") as archive:
                for name in ("contracts.py", "submission.py", "task_contracts.py"):
                    self.assertEqual((Path(submission.__file__).parent / name).read_bytes(),
                                     archive.read("do_math/" + name))
            records = []
            for value in ({k: v for k, v in good.items() if k != "report"}, good):
                draft.write_text(json.dumps(value), encoding="utf-8")
                process = run_tool(workspace, "--output", str(draft), command=context["submission_contract"]["command"])
                records.append(json.loads(process.stdout))
            self.assertEqual(records[0]["id"], records[1]["previous_producer_check_id"])
            self.assertTrue(records[1]["passed"])
            self.assertTrue(records[1]["repairs"])

    def test_installed_zip_runs_and_seals_real_producer_check(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            ctx = research_work_context()
            ctx["execution_id"] = "EX-1"
            install(workspace, ctx, contracts.schema_for("research_work"))
            (workspace / "response.json").write_text(json.dumps(two_observation_output()), encoding="utf-8")
            result = run_tool(workspace, "--output", "response.json")
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            record = json.loads(result.stdout)
            self.assertTrue(record["passed"])
            self.assertEqual(record, json.loads((workspace / "checks" / (record["id"] + ".json")).read_bytes()))

    def test_parse_failure_is_sealed_without_discarding_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            install(workspace, research_work_context(), contracts.schema_for("research_work"))
            draft = workspace / "response.json"
            original = b'{"broken":'
            draft.write_bytes(original)
            result = run_tool(workspace, "--output", "response.json")
            self.assertEqual(1, result.returncode)
            self.assertEqual(original, draft.read_bytes())
            records = list((workspace / "checks").glob("*.json"))
            self.assertEqual(1, len(records))
            self.assertIn("schema", json.loads(records[0].read_bytes())["not_checked"])


@test_group('resource')
class LivePreviewConnections(unittest.TestCase):
    def test_installed_preview_uses_receiver_domain_callback_without_publication(self):
        """About 6 s: this process's Sim template build, then the child interpreter's start and its one preview request.

        The owner is the Sim's real engine with its own grant (the legacy test
        patched ``governance.authorize`` and stubbed the domain callbacks); it pumps
        the transport until the installed tool's process ends.
        """
        from copy import deepcopy
        from do_math.engine import ResearchEngine
        from do_math.repository import ResearchRepository
        from support.provider_probes import ObservedCalls
        from support.sim import warm_template
        from support.submission_receiver import history
        warm_template()
        scene = history(bound=True)
        engine = scene.engine
        (scene.workspace / "draft.json").write_bytes(canonical_json(scene.output))
        before, head = deepcopy((engine.instance, engine.runtime)), engine.head
        receipts = []
        process = subprocess.Popen([sys.executable, "-B", str(scene.workspace / "input/tools/check_submission.py"),
                                    "--output", "draft.json", "--preview", "--wait-seconds", "20"], cwd=scene.workspace,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            with ObservedCalls(candidate=ResearchEngine._apply_bundle_candidate,
                               validated=ResearchRepository.save_validated,
                               saved=ResearchRepository.save_with_state) as calls:
                for _ in range(1250):  # 25 s of 20 ms polls
                    receipts += scene.transport.pump(engine._publish_control_request)
                    try:
                        process.wait(timeout=0.02)
                        break
                    except subprocess.TimeoutExpired:
                        continue
                receipts += scene.transport.pump(engine._publish_control_request)
        finally:
            if process.poll() is None:
                process.kill()
            stdout, stderr = process.communicate()
        self.assertEqual(process.returncode, 0, stdout + stderr)
        self.assertEqual(calls.count('candidate'), 1)
        self.assertEqual((engine.instance, engine.runtime), before)
        self.assertEqual(engine.head, head)
        self.assertEqual((calls.count('validated'), calls.count('saved')), (0, 0))
        receipt = receipts[0]
        self.assertEqual({row['state'] for row in receipts}, {'previewed'})
        self.assertEqual(receipt["state"], "previewed")
        self.assertTrue(receipt["result"]["passed"], receipt)
        self.assertNotIn("publication_id", receipt)


if __name__ == "__main__":
    unittest.main()


@test_group('resource')
class PreparationCacheTests(unittest.TestCase):
    def copied_process(self, mode):
        from support.storage_finish_installation import copy_installation
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy_installation(root / 'installation')
            worker = Path(__file__).resolve().parents[1] / 'support/storage_finish_preparation.py'
            result = subprocess.run([sys.executable, '-I', '-B', str(worker), str(root), mode],
                                    capture_output=True, text=True, encoding='utf-8', timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)

    def test_same_code_reuses_compression_but_each_workspace_keeps_its_own_context(self):
        self.assertEqual(self.copied_process('contexts'),
                         {'zip_calls': 1, 'compression_count': 1, 'contexts': ['first', 'second']})

    def test_unchanged_code_is_not_reread_and_an_edit_ships_new_bytes(self):
        self.assertEqual(self.copied_process('edits'),
                         {'hash_rereads': 0, 'zip_calls': 0, 'code_opens': 0, 'edited_bytes': 'edition = 2\n'})

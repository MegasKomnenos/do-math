"""The scheduled supervisor: it never calls a model, and its recovery publishes through Git without the engine writer.

The repository is an autospec double or a new empty Git repository; Windows Job facts and
profile capability evidence are synthetic.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles, scheduled_operator
from provider_fixtures import PROFILE_CONFIG
from research_fixtures import git_init


def repository_double(root, instance, runtime, *, published):
    """A ``ResearchRepository`` double (autospec) holding ``(instance, runtime)`` at ``head``.

    Saving publishes ``published``. The recovery path takes its maintenance
    lock in the repository's public ``git_dir``, which names ``root``.
    """
    from contextlib import nullcontext
    from unittest.mock import create_autospec
    from do_math.repository import ResearchRepository
    repo = create_autospec(ResearchRepository, instance=True)
    repo.writer_lock.return_value = nullcontext()
    repo.load.return_value = ("head", instance, runtime)
    repo.save_with_state.return_value = (published, {}, {})
    repo.git_dir = root
    return repo


class SupervisorRecoveryTests(unittest.TestCase):
    def capability_adapter(self, *, supported=True):
        from unittest.mock import Mock
        adapter = Mock()
        identity = {"cli_sha256": "a" * 64, "worker_sha256": "b" * 64, "host": {"node": "fixture"}}
        adapter.capability_identity.return_value = identity
        adapter.describe.return_value = {"scope": "cli_command_surface_only", "identity": identity,
            "verified": True, "supported": {key: supported for key in ("jsonl", "model", "structured_output")}}
        return adapter

    def test_supervisor_does_not_call_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status = {"status": "ready", "operator_enabled": True, "provider_waits": {"providers": {}}}
            with patch.object(scheduled_operator, "read_status", return_value=status), \
                 patch.object(scheduled_operator, "ResearchRepository") as repository, \
                 patch("do_math.submission.install_tools", return_value={}), \
                 patch.object(scheduled_operator, "reconcile_wake", return_value={"status": "not_needed"}), \
                 patch.object(scheduled_operator, "schedule", return_value={"state": "Running"}), \
                 patch.object(scheduled_operator.ModelRunner, "run", side_effect=AssertionError("normal supervision called AI")):
                result = scheduled_operator.check(root, "instance", root)
            self.assertEqual(result["outcome"], "engine_requested")
            # Supervision judges the one status snapshot; it loads no repository state.
            repository.assert_not_called()

    def test_git_publication_and_recovery_exclude_engine_writer(self):
        import subprocess
        from do_math.repository import ResearchRepository
        from do_math.session_slots import SessionSlots
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git_init(root)
            iid = "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV"
            repository = ResearchRepository(root, iid)
            from research_fixtures import current_state
            # Every stored state passes the current lifecycle gate.
            instance, runtime = current_state({**execution_profiles.build_profiles(PROFILE_CONFIG), "id": iid,
                                               "config": {**PROFILE_CONFIG, "operator_enabled": True}, "workspace": str(root)},
                                              {"status": "ready", "executions": {}, "reservations": {}, "provider_waits": {}})
            head = repository.initialize(instance, runtime)
            failure = {"kind": "engine_unavailable", "error": "installation test failure"}
            with repository.writer_lock(), patch.object(scheduled_operator.ModelRunner, "run") as runner:
                self.assertEqual(scheduled_operator.recovery(root, iid, root, failure=failure)["outcome"], "engine_running")
                runner.assert_not_called()
            with patch.object(scheduled_operator.ModelRunner, "run", return_value={"status": "failed", "error": "fixture"}), \
                 patch("do_math.initialization.adapter_for", return_value=self.capability_adapter()):
                result = scheduled_operator.recovery(root, iid, root, failure=failure)
            self.assertEqual(result["outcome"], "recovery_failed")
            new_head, instance, runtime = repository.load()
            self.assertNotEqual(head, new_head)
            execution = runtime["executions"][result["execution_id"]]
            self.assertEqual(execution["role"], "recovery")
            self.assertEqual(execution["status"], "ended")
            self.assertEqual(execution["error"], "fixture")
            self.assertEqual(execution["input_manifest"]["repair_authority"]["source"], "adopted_operator_repair_scope")
            # Recovery is an operational role: it reserves no model slot, and its local capacity is returned.
            self.assertEqual(runtime["reservations"], {})
            self.assertEqual(execution["capacity"]["reservation_ids"], [])
            self.assertEqual(execution["capacity"]["local_termination"], "confirmed")
            self.assertFalse((root / "session-slots").exists())
            self.assertTrue(any("execution_profiles/EP-" in p for p in repository.list_files("research/", new_head)))
            prior_activity = execution["owner_activity_id"]
            with patch.object(scheduled_operator.ModelRunner, 'run') as duplicate:
                held = scheduled_operator.recovery(root, iid, root, failure=failure)
            self.assertEqual(held['reason'], 'same failure and installation already attempted')
            duplicate.assert_not_called()
            real_run = subprocess.run
            def verification(command, **options):
                if len(command) > 1 and Path(command[1]).name == "probe_cli.py":
                    return subprocess.CompletedProcess(command, 0, "verified", "")
                return real_run(command, **options)
            def repaired(**arguments):
                _, _, published = repository.load()
                self.assertEqual(published["executions"][arguments["execution_id"]]["status"], "starting")
                self.assertIn("Do not change research records, goals, budgets, grants", arguments["prompt"])
                from do_math.git_store import GitStateStoreLockError
                with self.assertRaises(GitStateStoreLockError), repository.writer_lock():
                    self.fail("recovery model ran without excluding the engine")
                arguments["on_started"]({"job_name": arguments["launch_ticket"]["job_name"], "pid": 17})
                _, _, published = repository.load()
                self.assertEqual(published["executions"][arguments["execution_id"]]["capacity"]["process"]["pid"], 17)
                return {"status": "completed", "output": {"summary": "fixture repair", "observed_status": "ready",
                    "actions": [], "evidence_paths": [], "user_questions": [], "next_step": "launcher verification"}}
            def restart(*args):
                from do_math.file_io import os_lock
                with repository.writer_lock():
                    # Raises OSError if restart still owns the maintenance lock.
                    with os_lock(repository.git_dir / "do-math-installation-maintenance.lock", blocking=False):
                        pass
                    _, _, published = repository.load()
                    self.assertTrue(all(e["status"] == "ended" and e["capacity"]["local_termination"] == "confirmed"
                                        for e in published["executions"].values()))
                return {"outcome": "engine_requested"}
            with patch.object(scheduled_operator.ModelRunner, "run", side_effect=repaired), \
                 patch("do_math.initialization.adapter_for", return_value=self.capability_adapter()), \
                 patch('do_math.repair_execution.installation_sha256', return_value='b' * 64), \
                 patch.object(scheduled_operator.subprocess, "run", side_effect=verification), \
                 patch.object(scheduled_operator, "wake", side_effect=restart), \
                 patch("do_math.windows_job.named_job_empty", return_value=True):
                # A later observation of the same failure carries its own time; it continues the same activity.
                result = scheduled_operator.recovery(root, iid, root,
                    failure={**failure, "observed_at": "2026-09-28T00:00:00+00:00"})
            self.assertEqual(result["outcome"], "repaired")
            _, _, runtime = repository.load()
            execution = runtime["executions"][result["execution_id"]]
            self.assertEqual(execution["outcome"], "output_accepted")
            self.assertEqual(execution["owner_activity_id"], prior_activity)
            self.assertEqual(len(runtime["activities"][prior_activity]["assigned_execution_ids"]), 2)
            self.assertEqual(runtime["activities"][prior_activity]["status"], "finished")

    def test_recovery_never_restarts_with_unknown_local_termination(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            instance = {**execution_profiles.build_profiles(PROFILE_CONFIG), "config": {**PROFILE_CONFIG, "operator_enabled": True}}
            runtime = {"executions": {}, "reservations": {}, "activities": {}, "status": "ready"}
            repo = repository_double(root, instance, runtime, published="published")
            def model(**arguments):
                self.assertEqual(arguments.get("input_seal"), execution_profiles.prompt_seal(arguments["prompt"]))
                sealed = runtime["executions"][arguments["execution_id"]]["input_manifest"]["prompt"]
                self.assertEqual(sealed, arguments["input_seal"])
                raw_prompt = arguments["prompt"].split(execution_profiles.boundary_prompt(arguments["profile"]))[0]
                self.assertEqual(json.loads(raw_prompt.rsplit("\n", 1)[1])["installation"],
                                 str(root / "live-installation"))
                arguments["on_started"]({"job_name": arguments["launch_ticket"]["job_name"], "pid": 42})
                return {"status": "completed", "output": {"summary": "report is not termination evidence"}}
            with patch.object(scheduled_operator, "ResearchRepository", return_value=repo), \
                 patch("do_math.initialization.adapter_for", return_value=self.capability_adapter()), \
                 patch.object(scheduled_operator, "LIVE_INSTALLATION_ROOT", root / "live-installation", create=True), \
                 patch.object(scheduled_operator.ModelRunner, "run", side_effect=model), \
                 patch.object(scheduled_operator.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "ok", "")) as verify, \
                 patch("do_math.windows_job.named_job_empty", return_value=None), \
                 patch.object(scheduled_operator, "wake") as wake:
                result = scheduled_operator.recovery(root, "test", root,
                    failure={"kind": "engine_unavailable", "error": "fixture"})
            wake.assert_not_called()
            self.assertEqual(result["outcome"], "recovery_termination_unknown")
            self.assertEqual(Path(verify.call_args.args[0][1]), root / "live-installation/scripts/probe_cli.py")
            # The unconfirmed Job keeps the execution at the termination barrier with its output.
            execution = runtime["executions"][result["execution_id"]]
            self.assertEqual(execution["status"], "stopping")
            self.assertEqual(execution["capacity"]["local_termination"], "unknown")
            self.assertEqual(execution["error"],
                             "Local Job termination is unconfirmed; capacity and output remain held for recovery.")
            self.assertEqual(runtime["reservations"], {})

    def test_recovery_requires_current_profile_capability_before_reservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            instance = {**execution_profiles.build_profiles(PROFILE_CONFIG), "config": {**PROFILE_CONFIG, "operator_enabled": True}}
            runtime = {"executions": {}, "reservations": {}, "status": "ready"}
            repo = repository_double(root, instance, runtime, published="capability-published")
            with patch.object(scheduled_operator, "ResearchRepository", return_value=repo), \
                 patch("do_math.initialization.adapter_for", return_value=self.capability_adapter(supported=False)), \
                 patch.object(scheduled_operator.ModelRunner, "run") as runner:
                result = scheduled_operator.recovery(root, "test", root,
                    failure={"kind": "engine_unavailable", "error": "fixture"})
            self.assertEqual(result["outcome"], "recovery_waiting")
            self.assertEqual(result["reason"], "profile_capability_unavailable")
            runner.assert_not_called()
            self.assertFalse(runtime["reservations"])
            evidence = next(iter(instance["capability_evidence"].values()))
            self.assertEqual(evidence["capabilities"]["structured_output"]["status"], "unsupported")

    def test_recovery_cannot_ignore_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scheduled_operator.hold(root, reason="test")
            with patch.object(scheduled_operator.ModelRunner, "run") as runner:
                self.assertEqual(scheduled_operator.recovery(root, "unused", root,
                    failure={"kind": "engine_unavailable", "error": "fixture"})["outcome"], "held")
                runner.assert_not_called()

    def test_recovery_waits_for_unended_execution_without_confirmed_termination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            instance = {**execution_profiles.build_profiles(PROFILE_CONFIG), "config": {**PROFILE_CONFIG, "operator_enabled": True}}
            runtime = {"executions": {"EX-live": {"id": "EX-live", "status": "running"}}, "reservations": {}, "status": "ready"}
            repo = repository_double(root, instance, runtime, published="unused")
            with patch.object(scheduled_operator, "ResearchRepository", return_value=repo), \
                 patch.object(scheduled_operator.ModelRunner, "run") as runner:
                result = scheduled_operator.recovery(root, "test", root,
                    failure={"kind": "engine_unavailable", "error": "fixture"})
            self.assertEqual((result["outcome"], result["execution_id"]), ("recovery_waiting", "EX-live"))
            runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()

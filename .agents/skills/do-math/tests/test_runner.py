"""Small real-process flows with the official checker and a temporary Git repo."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner
from cli_adapter import Command


def fake_session():
    scenario = sys.argv[2]
    session = Path.cwd()
    data = runner.read_json(session / "input.json")
    category, task = data["category"], data["task"]
    output = {"category": category, "references": [], "supersedes": []}
    if category == "plan" and scenario == "plan_failure":
        return 1
    if category == "plan":
        kinds = [event["kind"] for event in task["events"]]
        output.update(reason="Choose the next small step.", research=[], reviews=[], goal_review=None, wait=None)
        if "start" in kinds:
            output["research"] = [{"instructions": "fail" if scenario == "failure" else "prove",
                                   "references": [], "supersedes": [], "effort": "low",
                                   "selection_reason": "Small calculation"}]
        elif "session_failed" in kinds:
            output["wait"] = {"needed": "scope", "reason": "Need user input"}
        elif "user_input" in kinds:
            output["research"] = [{"instructions": "prove", "references": [], "supersedes": []}]
        else:
            output["goal_review"] = {"instructions": "Check the goal", "references": [],
                                     "model": "claude/sonnet", "selection_reason": "Independent CLI"}
    elif category == "research":
        if task["instructions"] == "fail":
            print(json.dumps({"type": "error", "message": "You've hit your usage limit. Try again later."}))
            return 13
        (session / "output/exposition.md").write_text("A small public explanation.\n", encoding="utf-8")
        (session / "output/supplement.txt").write_text("Also public, although not a required field.\n", encoding="utf-8")
        (session / "private.txt").write_text("Not public.\n", encoding="utf-8")
        output.update(results=[{"id": "r1", "exposition": "exposition.md", "verification": "Synthetic fixture only", "lean": None}],
                      failed_attempts=[], open_questions=[])
    else:
        output["target"] = task["target"]
        if task["target"]["kind"] == "goal":
            output["goal"] = {"verdict": "achieved", "reason": "Synthetic goal fixture"}
        else:
            output.update(results=[{"result": "r1", "assessment": {"verdict": "supported", "reason": "Fixture"},
                                    "lean": {"verdict": "not_applicable", "reason": "No Lean"},
                                    "alignment": {"verdict": "not_applicable", "reason": "No Lean"}}],
                          summary="Independent fixture review")
    runner.write_json(session / "output/output.json", output)
    # The actual CLI's stdin is a UTF-8 file, even for this fake process.
    (session / "received-prompt.txt").write_text(sys.stdin.read(), encoding="utf-8")
    if task["instructions"] == "hold":
        (session / "ready").touch()
        while not (session / "release").exists():
            time.sleep(0.02)
    return 7 if category == "research" else 0


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.instance = self.root / "연구 instance"
        self.skill = self.root / "skill"
        self.skill.mkdir()
        for name in ("common.md", "protocol.md", "plan.md", "research.md", "review.md", "RUNTIME.md", "check.py"):
            (self.skill / name).write_text("Temporary test context\n", encoding="utf-8")
        goal = self.root / "goal.md"
        goal.write_text("Synthetic goal\n", encoding="utf-8")
        settings = self.root / "settings.json"
        runner.write_json(settings, {
            "max_sessions": 2,
            "defaults": {name: {"model": "codex/gpt-6.1-sol", "effort": "high"}
                         for name in ("plan", "research", "review")},
            "cli": {"codex": "codex.exe", "claude": "claude.exe"},
            "limit_wait_seconds": 0.6,
            "lean": {"command": ["lean"], "version_command": ["lean", "--version"], "cwd": None, "env": {}}})
        runner.initialize(self.instance, goal, settings)
        self.engine = runner.Runner(self.instance, self.skill)
        self.scenario = "flow"
        self.patch = patch.object(runner, "build_command", self.command)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        for directory in (self.instance / "sessions").iterdir():
            (directory / "release").touch()
            (directory / "CANCEL").touch()
        for host in self.engine.hosts.values():
            host.wait(timeout=10)
        self.temp.cleanup()

    def command(self, cli, model, effort, cwd):
        return Command(runner.provider_for_model(model),
                       [sys.executable, "-B", str(Path(__file__).resolve()), "--fake", self.scenario], Path(cwd))

    def until(self, condition, limit=12):
        deadline = time.monotonic() + limit
        while time.monotonic() < deadline:
            self.engine.tick()
            active = self.engine.active()
            self.assertLessEqual(len(active), 2)
            self.assertLessEqual(sum(s["category"] == "plan" for _, s in active), 1)
            if condition():
                return
            time.sleep(0.025)
        self.fail("Flow did not reach expected state: " + json.dumps(self.engine.state))

    def test_full_flow_publication_and_selection(self):
        self.until(lambda: self.engine.state["complete"] and not self.engine.active())
        state = self.engine.state
        sessions = list(state["sessions"].values())
        self.assertEqual([s["category"] for s in sessions], ["plan", "research", "review", "plan", "review"])
        self.assertEqual(len(list((self.instance / "knowledge").iterdir())), 5)
        self.assertEqual(int(runner.git(self.instance, "rev-list", "--count", "HEAD")), 6)
        research = sessions[1]
        self.assertEqual((research["model"], research["effort"], research["exit_code"]), ("codex/gpt-6.1-sol", "low", 7))
        self.assertEqual((sessions[4]["model"], sessions[4]["effort"]), ("claude/sonnet", "high"))
        public = self.instance / "knowledge" / research["record"]
        self.assertTrue((public / "supplement.txt").is_file())
        self.assertFalse((public / "private.txt").exists())
        for sid, session in state["sessions"].items():
            data = runner.read_json(self.instance / "sessions" / sid / "input.json")
            self.assertEqual(len(data["context"]["common"]), 3)
            if session["category"] == "review":
                prompt = (self.instance / "sessions" / sid / "prompt.txt").read_text(encoding="utf-8")
                research_sid = next(k for k, v in state["sessions"].items() if v["category"] == "research")
                self.assertNotIn(research_sid, json.dumps(data) + prompt)

    def test_stop_limit_failure_wait_and_input(self):
        self.scenario = "failure"
        stop = self.instance / "control/STOP"
        stop.touch()
        self.engine.tick()
        self.assertFalse(self.engine.state["sessions"])
        stop.unlink()
        self.until(lambda: any(s["status"] == "failed" for s in self.engine.state["sessions"].values()))
        self.assertIn("usage_limit", self.engine.blocked())
        count = len(self.engine.state["sessions"])
        self.engine.tick()
        self.assertEqual(len(self.engine.state["sessions"]), count)
        self.until(lambda: self.engine.state["wait"] is not None)
        plan = [sid for sid, s in self.engine.state["sessions"].items() if s["category"] == "plan"][-1]
        events = runner.read_json(self.instance / "sessions" / plan / "input.json")["task"]["events"]
        self.assertEqual([e["kind"] for e in events], ["session_failed"])
        self.assertTrue(events[0]["reason"])
        self.assertEqual((events[0]["category"], events[0]["task"]["instructions"]), ("research", "fail"))
        self.assertTrue(events[0]["limit"] and events[0]["origin"])
        source = self.root / "answer.txt"
        source.write_bytes("자연수에는 0을 포함합니다.\n".encode("utf-8"))
        submitted = Path(runner.submit_input(self.instance, source))
        stop.touch()
        self.engine.tick()
        self.assertIsNone(self.engine.state["wait"])
        self.assertIn("STOP", self.engine.blocked())
        self.assertEqual(submitted.read_bytes(), source.read_bytes())
        stop.unlink()
        self.until(lambda: self.engine.state["complete"] and not self.engine.active())
        self.assertEqual(len(self.engine.state["seen_inputs"]), 1)

    def test_repeated_plan_failures_halt_until_restart(self):
        self.scenario = "plan_failure"
        self.until(lambda: self.engine.state["halted"] and not self.engine.active())
        plans = [s for s in self.engine.state["sessions"].values() if s["category"] == "plan"]
        self.assertEqual([s["status"] for s in plans], ["failed"] * runner.PLAN_FAILURE_LIMIT)
        self.assertIn("halted", self.engine.blocked())
        self.engine.tick()
        self.assertEqual(len(self.engine.state["sessions"]), runner.PLAN_FAILURE_LIMIT)
        # The first plan's consumed start event survives inside the failure chain.
        event = self.engine.state["events"][-1]
        self.assertEqual((event["category"], event["request"]), ("plan", None))
        self.assertEqual(event["task"]["events"][-1]["task"]["events"][-1]["task"]["events"], [{"kind": "start"}])
        self.engine.run()  # Restart releases the halt, retries, then exits halted.
        self.assertEqual(len(self.engine.state["sessions"]), 2 * runner.PLAN_FAILURE_LIMIT)

    def test_recovery_live_cli_completion_drains_existing_work(self):
        self.engine.state["events"] = []
        self.engine.enqueue("hold", "research", {"instructions": "hold", "references": [], "supersedes": []}, "test")
        self.engine.enqueue("goal", "review", {"instructions": "check", "references": [], "target": {"kind": "goal"}}, "test")
        self.engine.save()
        self.until(lambda: bool(self.engine.state["complete"]))
        held_id = self.engine.state["requests"]["hold"]["session"]
        held = self.instance / "sessions" / held_id
        self.assertTrue((held / "ready").exists())
        recovered = runner.Runner(self.instance, self.skill)
        recovered.tick()
        self.assertEqual(recovered.state["sessions"][held_id]["status"], "running")
        receipt = runner.read_json(held / "process.json")
        wrong = dict(receipt["process"], birth="wrong")
        with self.assertRaises(RuntimeError):
            runner.terminate_process(wrong)
        self.assertTrue(runner.alive(receipt["process"]))
        runner.terminate_process(receipt["process"])
        old = self.engine
        self.engine = recovered
        self.engine.hosts.update(old.hosts)
        self.until(lambda: not self.engine.active())
        self.assertEqual(len(self.engine.state["sessions"]), 2)
        self.assertEqual(self.engine.state["sessions"][held_id]["status"], "integrated")
        self.assertEqual(len(list((self.instance / "knowledge").iterdir())), 2)
        # Repeated recovery cannot duplicate knowledge or its Git commits.
        runner.Runner(self.instance, self.skill).tick()
        self.assertEqual(int(runner.git(self.instance, "rev-list", "--count", "HEAD")), 3)

    def test_lock_and_pending_requests_survive_empty_plan(self):
        with runner.InstanceLock(self.instance / "runner/lock"):
            with self.assertRaises(RuntimeError):
                with runner.InstanceLock(self.instance / "runner/lock"):
                    pass
        with runner.InstanceLock(self.instance / "runner/lock"):
            pass
        self.engine.enqueue("old", "research", {"instructions": "hold", "references": [], "supersedes": []}, "old-plan")
        self.engine.state["events"] = [{"kind": "user_input", "text": "new information"}]
        self.engine.apply_output({}, "new-plan", {"category": "plan", "research": [], "reviews": [],
                                  "goal_review": None, "wait": {"needed": "old question", "reason": "old reason"}})
        self.assertEqual(self.engine.state["requests"]["old"]["status"], "pending")
        self.assertIsNone(self.engine.state["wait"])
        self.assertEqual(len(self.engine.state["events"]), 1)

    def test_recovery_after_commit_before_effects(self):
        real_git = runner.git
        interrupted = False

        def interrupt_after_commit(instance, *args):
            nonlocal interrupted
            result = real_git(instance, *args)
            if args[0] == "commit" and not interrupted:
                interrupted = True
                raise RuntimeError("Simulated runner death after Git commit")
            return result

        with patch.object(runner, "git", interrupt_after_commit):
            with self.assertRaisesRegex(RuntimeError, "Simulated runner death"):
                self.until(lambda: False)
        saved = runner.read_json(self.instance / "runner/state.json")
        self.assertEqual(next(iter(saved["sessions"].values()))["status"], "publishing")
        old = self.engine
        self.engine = runner.Runner(self.instance, self.skill)
        self.engine.hosts.update(old.hosts)
        self.until(lambda: self.engine.state["complete"] and not self.engine.active())
        self.assertEqual(len(self.engine.state["sessions"]), 5)
        self.assertEqual(int(real_git(self.instance, "rev-list", "--count", "HEAD")), 6)

    def test_detached_runner_outlives_start_command(self):
        for name in ("runner.py", "cli_adapter.py", "check.py"):
            shutil.copyfile(runner.SKILL / name, self.skill / name)
        (self.instance / "control/STOP").touch()
        launched = subprocess.run([sys.executable, "-B", str(self.skill / "runner.py"), "start", str(self.instance)],
                                  capture_output=True, text=True, encoding="utf-8", timeout=15)
        self.assertEqual(launched.returncode, 0, launched.stderr)
        paths = json.loads(launched.stdout)
        identity = runner.read_json(self.instance / "runner/process.json")["process"]
        try:
            self.assertTrue(runner.alive(identity))
            self.assertIn("started", Path(paths["stdout"]).read_text(encoding="utf-8"))
            answer = self.root / "detached-input.txt"
            answer.write_text("The launching command has now exited.\n", encoding="utf-8")
            runner.submit_input(self.instance, answer)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                state = runner.read_json(self.instance / "runner/state.json")
                if state["seen_inputs"]:
                    break
                time.sleep(0.025)
            self.assertEqual(len(state["seen_inputs"]), 1)
            self.assertFalse(state["sessions"])
        finally:
            runner.terminate_process(identity)
            deadline = time.monotonic() + 5
            while runner.alive(identity) and time.monotonic() < deadline:
                time.sleep(0.025)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fake":
        raise SystemExit(fake_session())
    unittest.main()

"""Small real-process flows with the official checker and a temporary Git repo."""

import ctypes
import errno
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tarfile
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
    if scenario == "work":
        (session / "work/nested").mkdir(parents=True)
        (session / "work/nested/scratch.txt").write_text("Private intermediate " + category + "\n", encoding="utf-8")
    output = {"category": category, "references": [], "supersedes": [],
              "overview": {"title": "Fixture " + category, "summary": "Synthetic bounded fixture, not a mathematical claim."}}
    if category == "plan" and scenario == "plan_failure":
        return 1
    if category == "plan":
        from glossary import FIELDS
        lines = ['<!-- do-math-glossary -->', '[History](glossary-history.md)',
                 '<a id="term-1"></a>', '## 1. Fixture', '| 칸 | 내용 |', '|---|---|']
        lines += [f'| {field} | Fixture |' for field in FIELDS]
        (session / 'output/glossary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        (session / 'output/glossary-history.md').write_text('No previous terms.\n', encoding='utf-8')
        (session / 'output/research-status.md').write_text('Fixture status.\n', encoding='utf-8')
        kinds = [event["kind"] for event in task["events"]]
        output.update(reason="Choose the next small step.", research=[], explorations=[], reviews=[],
                      goal_review=None, wait=None)
        if "start" in kinds and scenario == "explore":
            output["explorations"] = [{"instructions": "wander", "references": []}]
        elif "start" in kinds:
            output["research"] = [{"instructions": "fail" if scenario == "failure" else "prove",
                                   "references": [], "supersedes": [], "effort": "low",
                                   "selection_reason": "Small calculation"}]
        elif "session_failed" in kinds:
            output["wait"] = {"needed": "scope", "reason": "Need user input"}
        elif "user_input" in kinds:
            output["research"] = [{"instructions": "prove", "references": [], "supersedes": []}]
        elif "review_finished" in kinds:
            output["goal_review"] = {"instructions": "Check the goal", "references": [],
                                     "model": "claude/sonnet", "selection_reason": "Independent CLI"}
    elif category == "explore":
        (session / "output/notes.md").write_text("Unreviewed impressions.\n", encoding="utf-8")
        output.update(exposition="notes.md", questions=[])
    elif category == 'peer':
        (session / 'output/response.md').write_text('Independent mathematical response.\n', encoding='utf-8')
        output.update(target=task['target'], exposition='response.md',
                      results=[{'id': 'p1', 'exposition': 'response.md', 'verification': 'Synthetic new claim', 'lean': None}],
                      questions=[])
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
        elif task['target']['kind'] == 'bundle':
            bundle = [task['target']['work'], task['target']['peer']]
            (session / 'output/review.md').write_text('Check both original and peer claims.\n', encoding='utf-8')
            output.update(exposition='review.md', overview_assessments=[], results=[], summary='Both sides checked')
            for rid in bundle:
                source = runner.read_json(Path(data['instance']) / 'knowledge' / rid / 'output.json')
                output['overview_assessments'].append({'record': rid, 'assessment': {'verdict': 'supported', 'reason': 'Fixture'}})
                for result in source.get('results', []):
                    output['results'].append({'id': 'c' + str(len(output['results'])),
                        'source': {'record': rid, 'result': result['id']},
                        'assessment': {'verdict': 'supported', 'reason': 'Fixture'},
                        'lean': {'verdict': 'not_applicable', 'reason': 'No Lean'},
                        'alignment': {'verdict': 'not_applicable', 'reason': 'No Lean'},
                        'terminology': {'verdict': 'conforms', 'reason': 'Fixture'}})
        else:
            output["overview_assessment"] = {"verdict": "supported", "reason": "Fixture overview matches."}
            output.update(results=[{"result": "r1", "assessment": {"verdict": "supported", "reason": "Fixture"},
                                    "lean": {"verdict": "not_applicable", "reason": "No Lean"},
                                    "alignment": {"verdict": "not_applicable", "reason": "No Lean"},
                                    "terminology": {"verdict": "conforms", "reason": "Fixture"}}],
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
        for name in ("common.md", "protocol.md", "plan.md", "research.md", "explore.md", "peer.md", "review.md", "RUNTIME.md", "check.py", "glossary.py"):
            (self.skill / name).write_text("Temporary test context\n", encoding="utf-8")
        goal = self.root / "goal.md"
        goal.write_text("Synthetic goal\n", encoding="utf-8")
        settings = self.root / "settings.json"
        runner.write_json(settings, {
            "max_sessions": 2,
            "defaults": {name: {"model": "codex/gpt-6.1-sol", "effort": "high"}
                         for name in ("plan", "research", "explore", "review")},
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
        if self.engine.archiver is not None:
            self.engine.archiver.wait(timeout=60)
        self.temp.cleanup()

    def command(self, cli, model, effort, cwd):
        return Command(runner.provider_for_model(model),
                       [sys.executable, "-B", str(Path(__file__).resolve()), "--fake", self.scenario], Path(cwd))

    def until(self, condition, limit=60):
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
        self.assertEqual([s['category'] for s in sessions if s['category'] != 'plan'],
                         ['research', 'peer', 'review', 'review'])
        self.assertEqual(len(list((self.instance / 'knowledge').glob('*/output.json'))), len(sessions))
        self.assertEqual(int(runner.git(self.instance, "rev-list", "--count", "HEAD")), len(sessions) + 1)

        research = sessions[1]
        self.assertEqual((research["model"], research["effort"], research["exit_code"]), ("codex/gpt-6.1-sol", "low", 7))
        self.assertEqual((sessions[-1]["model"], sessions[-1]["effort"]), ("claude/sonnet", "high"))
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

    def test_unchanged_stopped_tick_does_not_write_state(self):
        (self.instance / "control/STOP").touch()
        with patch.object(self.engine, "save") as save:
            self.engine.tick()
            self.engine.tick()
            save.assert_not_called()
        # Input ingestion still commits a real change before returning.
        (self.instance / "control/inputs/test.txt").write_text("new input", encoding="utf-8")
        self.engine.tick()
        self.assertIn("test.txt", runner.read_json(self.engine.state_path)["seen_inputs"])

    def test_run_survives_memory_error_and_waits_before_rearming(self):
        calls = []
        def tick():
            calls.append(True)
            if len(calls) == 1:
                self.engine.state["partial_mutation"] = True
                raise MemoryError("injected tick failure")
            self.assertNotIn("partial_mutation", self.engine.state)
            self.engine.state["complete"] = "fixture-complete"
        with patch.object(self.engine, "collect"), patch.object(self.engine, "refresh_index"), \
                patch.object(self.engine, "tick", tick), \
                patch.object(runner, "available_memory", side_effect=[0, 1024**3]) as memory, \
                patch.object(runner.time, "sleep") as sleep:
            self.engine.run("memory-test")
        self.assertEqual(len(calls), 2)
        self.assertEqual(memory.call_count, 2)
        self.assertGreaterEqual(sleep.call_count, 2)
        self.assertIsNotNone(self.engine.reserve.buffer)

    def test_exploration_gets_peer_and_bundle_review(self):
        self.scenario = 'explore'
        self.until(lambda: self.engine.state['complete'] and not self.engine.active())
        state = self.engine.state
        sessions = list(state['sessions'].values())
        self.assertEqual([s['category'] for s in sessions if s['category'] != 'plan'],
                         ['explore', 'peer', 'review', 'review'])
        work = next(s for s in sessions if s['category'] == 'explore')
        peer = next(s for s in sessions if s['category'] == 'peer')
        self.assertEqual(state['requests'][work['record'] + ':automatic_peer']['status'], 'finished')
        self.assertEqual(state['requests'][peer['record'] + ':automatic_review']['status'], 'finished')
        events = [event for sid, session in state['sessions'].items() if session['category'] == 'plan'
                  for event in runner.read_json(self.instance / 'sessions' / sid / 'input.json')['task']['events']]
        self.assertIn({'kind': 'exploration_finished', 'record': work['record']}, events)
        self.assertIn({'kind': 'peer_finished', 'record': peer['record']}, events)

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
        self.assertEqual(len(list((self.instance / "knowledge").glob('*/output.json'))), 2)
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
        self.engine.apply_output({}, "new-plan", {"category": "plan", "research": [], "explorations": [], "reviews": [],
                                  "goal_review": None, "wait": {"needed": "old question", "reason": "old reason"}})
        self.assertEqual(self.engine.state["requests"]["old"]["status"], "pending")
        self.assertIsNone(self.engine.state["wait"])
        self.assertEqual(len(self.engine.state["events"]), 1)

    def test_runner_archives_work_of_finished_sessions(self):
        self.scenario = "work"
        self.until(lambda: self.engine.state["complete"] and not self.engine.active())
        sessions = [self.instance / "sessions" / sid for sid in self.engine.state["sessions"]]
        self.until(lambda: all((s / "work.tar.xz").is_file() and not (s / "work").exists() for s in sessions))
        for session in sessions:
            with tarfile.open(session / "work.tar.xz") as tar:
                text = tar.extractfile("work/nested/scratch.txt").read().decode("utf-8")
            self.assertTrue(text.startswith("Private intermediate "))

    def test_only_finished_sessions_are_archived(self):
        statuses = ("starting", "running", "publishing", "integrated", "failed")
        for status in statuses:
            work = self.instance / "sessions" / ("s-" + status) / "work"
            work.mkdir(parents=True)
            (work / "file.txt").write_text(status, encoding="utf-8")
            self.engine.state["sessions"]["s-" + status] = {"status": status}
        self.engine.save()
        self.assertEqual(runner.archive_finished(self.instance), 0)
        for status in statuses:
            session = self.instance / "sessions" / ("s-" + status)
            finished = status in ("integrated", "failed")
            self.assertEqual((session / "work.tar.xz").is_file(), finished, status)
            self.assertEqual((session / "work").is_dir(), not finished, status)

    def test_archiver_yields_to_a_running_archiver(self):
        work = self.instance / "sessions/s-done/work"
        work.mkdir(parents=True)
        self.engine.state["sessions"]["s-done"] = {"status": "integrated"}
        self.engine.save()
        with runner.InstanceLock(self.instance / "runner/archive-lock"):
            self.assertEqual(runner.archive_finished(self.instance), 0)
            self.assertTrue(work.is_dir())

    def test_missing_cli_provider_is_a_launch_failure(self):
        self.engine.state["events"] = []
        del self.engine.settings["cli"]["claude"]
        self.engine.enqueue("goal", "review", {"instructions": "check", "references": [], "target": {"kind": "goal"}},
                            "test", {"model": "claude/sonnet"})
        self.engine.tick()
        session = self.engine.state["sessions"][self.engine.state["requests"]["goal"]["session"]]
        self.assertIn("claude", session["launch_error"])
        self.engine.tick()
        self.assertEqual(self.engine.state["requests"]["goal"]["status"], "failed")

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
        self.assertEqual(sum(s['category'] == 'peer' for s in self.engine.state['sessions'].values()), 1)
        self.assertEqual(int(real_git(self.instance, "rev-list", "--count", "HEAD")), len(self.engine.state["sessions"]) + 1)

    def test_detached_runner_outlives_start_command(self):
        for name in ("runner.py", "cli_adapter.py", "check.py", "glossary.py", "knowledge_index.py"):
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


@unittest.skipUnless(os.name == "nt", "OpenProcess access denial is Windows-specific")
class AccessDeniedPidTests(unittest.TestCase):
    """A recorded PID reused by another account's process cannot be opened (WinError 5)."""

    @staticmethod
    def denied(*args):
        ctypes.set_last_error(5)  # ERROR_ACCESS_DENIED, as the real OpenProcess reports it
        return None

    def test_denied_pid_is_not_alive(self):
        with patch.object(runner.WIN, "OpenProcess", self.denied):
            self.assertFalse(runner.alive({"pid": 15260, "birth": "134371426382443405"}))

    def test_recording_an_identity_still_refuses_a_denied_pid(self):
        with patch.object(runner.WIN, "OpenProcess", self.denied):
            with self.assertRaises(PermissionError):
                runner.process_identity(15260)


def tree(root):
    """Relative POSIX path -> file bytes, or None for a directory."""
    return {p.relative_to(root).as_posix(): p.read_bytes() if p.is_file() else None for p in root.rglob("*")}


class WorkArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.session = self.root / "세션"
        work = self.session / "work"
        (work / "build/깊은/하위").mkdir(parents=True)
        (work / "empty").mkdir()
        (work / "build/깊은/하위/Module.olean").write_bytes(random.Random(0).randbytes(300_000))
        (work / "build/notes.lean").write_text("theorem t : 1 = 1 := rfl\n" * 5000, encoding="utf-8")
        (work / "zero").write_bytes(b"")
        self.original = tree(work)

    def tearDown(self):
        self.temp.cleanup()

    def leftovers(self):
        return sorted(p.name for p in self.session.iterdir() if p.name != "work")

    def archived(self):
        return (self.session / "work.tar.xz").read_bytes()

    def test_work_is_replaced_by_an_identical_archive(self):
        self.assertTrue(runner.archive_work(self.session))
        self.assertFalse((self.session / "work").exists())
        self.assertEqual(self.leftovers(), ["work.tar.xz"])
        with tarfile.open(self.session / "work.tar.xz") as tar:
            tar.extractall(self.root / "restored", filter="data")
        self.assertEqual(tree(self.root / "restored/work"), self.original)

    def test_session_without_work_is_left_alone(self):
        shutil.rmtree(self.session / "work")
        self.assertFalse(runner.archive_work(self.session))
        self.assertEqual(self.leftovers(), [])

    def test_write_failure_keeps_work_and_leaves_no_archive(self):
        def disk_full(*args, **kwargs):
            raise OSError(errno.ENOSPC, "No space left on device")
        with patch.object(tarfile.TarFile, "addfile", disk_full):
            with self.assertRaises(OSError):
                runner.archive_work(self.session)
        self.assertEqual(tree(self.session / "work"), self.original)
        self.assertEqual(self.leftovers(), [])

    def test_stale_partial_archive_is_replaced(self):
        # An archiver killed mid-write leaves its partial file behind.
        (self.session / "work.tar.xz.part").write_bytes(b"truncated")
        self.assertTrue(runner.archive_work(self.session))
        self.assertEqual(self.leftovers(), ["work.tar.xz"])

    def test_linked_directory_is_neither_followed_nor_archived(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("keep", encoding="utf-8")
        link = self.session / "work/link"
        try:
            if os.name == "nt":
                import _winapi
                _winapi.CreateJunction(str(outside), str(link))
            else:
                os.symlink(outside, link, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"cannot create a directory link: {exc}")
        with self.assertRaises(ValueError):
            runner.archive_work(self.session)
        self.assertTrue(os.path.lexists(link))
        self.assertEqual((outside / "keep.txt").read_text(encoding="utf-8"), "keep")
        self.assertEqual(self.leftovers(), [])

    def test_leftover_work_already_in_archive_is_removed(self):
        # Removal interrupted after the archive was published leaves a subset of work/.
        self.assertTrue(runner.archive_work(self.session))
        archived = self.archived()
        with tarfile.open(self.session / "work.tar.xz") as tar:
            tar.extractall(self.session, filter="data")
        shutil.rmtree(self.session / "work/build")
        self.assertTrue(runner.archive_work(self.session))
        self.assertFalse((self.session / "work").exists())
        self.assertEqual(self.archived(), archived)

    def test_work_differing_from_existing_archive_keeps_both(self):
        self.assertTrue(runner.archive_work(self.session))
        archived = self.archived()
        (self.session / "work").mkdir()
        (self.session / "work/new.txt").write_text("not archived", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            runner.archive_work(self.session)
        self.assertEqual((self.session / "work/new.txt").read_text(encoding="utf-8"), "not archived")
        self.assertEqual(self.archived(), archived)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fake":
        raise SystemExit(fake_session())
    unittest.main()

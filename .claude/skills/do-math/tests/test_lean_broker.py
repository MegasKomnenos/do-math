"""The Lean broker with a fake lean: scheduling, calibration, recovery and the client; no Lean is run."""

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lean_broker
import runner

FAKE = Path(__file__).resolve().with_name("fake_lean.py")


def source(path, imports=("Mathlib.Data.Nat.Basic",), **fake):
    """A Lean file the fake lean understands; its baseline is 8 MiB per import plus 8."""
    lines = [f"import {name}" for name in imports]
    if fake:
        lines.append("-- fake: " + " ".join(f"{k}={v}" for k, v in fake.items()))
    lines.append("theorem t : 1 = 1 := rfl")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class BrokerFixture(unittest.TestCase):
    budget = 700
    threads_budget = 4

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.instance = self.root / "instance é"  # non-ASCII on purpose: every path crosses a JSON file and an argv
        goal = self.root / "goal.md"
        goal.write_text("Synthetic goal\n", encoding="utf-8")
        self.settings_path = self.root / "settings.json"
        self.settings = {
            "max_sessions": 2,
            "defaults": {name: {"model": "codex/gpt-6.1-sol", "effort": "high"}
                         for name in ("plan", "research", "explore", "review")},
            "cli": {"codex": "codex.exe", "claude": "claude.exe"}, "limit_wait_seconds": 5,
            "lean": {"command": [sys.executable, "-B", str(FAKE)],
                     "version_command": [sys.executable, "-B", str(FAKE), "--version"], "cwd": None, "env": {},
                     "memory_budget_mb": self.budget, "min_free_memory_mb": 0, "threads": 1,
                     "cpu_threads_budget": self.threads_budget}}
        runner.write_json(self.settings_path, self.settings)
        runner.initialize(self.instance, goal, self.settings_path)
        self.paths = lean_broker.Paths(self.instance)
        self.paths.ensure()
        self.broker = None

    def write_settings(self, **lean):
        """Change the instance's settings file as an operator would, for the broker's live reload."""
        self.settings["lean"].update(lean)
        runner.write_json(self.instance / "settings.json", self.settings)

    def tearDown(self):
        # Every Lean process a job folder records is terminated, whichever broker started it (this one
        # or a detached one): on Windows a live compile holds its working folder against the cleanup.
        for directory in self.paths.jobs.iterdir() if self.paths.jobs.is_dir() else []:
            (directory / "CANCEL").touch()
            receipt = directory / "process.json"
            if receipt.exists():
                lean = runner.read_json(receipt)
                if runner.alive(lean["process"]):
                    lean_broker.terminate_tree(lean["pid"])
                    self.wait_gone(lean["process"])
        if self.broker is not None:
            for host in self.broker.hosts.values():
                host.wait(timeout=10)
        if self.paths.state.exists():  # hosts of a detached broker exit once their Lean has ended
            for job in runner.read_json(self.paths.state).get("jobs", {}).values():
                self.wait_gone(job.get("host"))
        info = lean_broker.broker_alive(self.paths)
        if info:
            runner.terminate_process(info["process"])
            while runner.alive(info["process"]):
                time.sleep(0.02)
        # A broker terminated during its startup orphans its version command for a moment; on Windows
        # that child holds the calibration folder as its working directory until it exits.
        deadline = time.monotonic() + 10
        while True:
            try:
                self.temp.cleanup()
                break
            except PermissionError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.1)

    @staticmethod
    def wait_gone(identity, limit=10):
        deadline = time.monotonic() + limit
        while runner.alive(identity) and time.monotonic() < deadline:
            time.sleep(0.02)

    def start_broker(self):
        """The broker's own startup, in this process, minus the lock and the receipt `serve` adds."""
        self.broker = lean_broker.Broker(self.instance, log_path=self.paths.log)
        self.broker.start()
        return self.broker

    def session_file(self, session, name="A.lean", **fake):
        return source(self.instance / "sessions" / session / "work" / name, **fake)

    def submit(self, path, expect_mb=200, session="s1"):
        # The broker under test runs in this process; no detached one may be launched beside it.
        with patch.object(lean_broker, "ensure_broker", return_value={}):
            return lean_broker.submit(self.paths, path, expect_mb, session)["job"]

    def build(self, root, targets, expect_mb=60, session="s1"):
        with patch.object(lean_broker, "ensure_broker", return_value={}):
            return lean_broker.build(self.paths, root, targets, expect_mb, session)["build"]

    def tree(self, session="s1", **overrides):
        """A, B and C import A, D imports B and C; `overrides` replaces a module's fake options."""
        root = self.instance / "sessions" / session / "work" / "lean"
        plan = {"A": (("Mathlib.Data.Nat.Basic",), {"sleep": 0.3}), "B": (("A",), {"sleep": 0.5}),
                "C": (("A",), {"sleep": 0.5}), "D": (("B", "C"), {"marker": "TARGET-D"})}
        for name, (imports, fake) in plan.items():
            source(root / f"{name}.lean", imports=imports, **overrides.get(name, fake))
        return root

    def build_record(self, build_id):
        return self.broker.state["builds"][build_id]

    def module_job(self, build_id, name):
        return self.broker.state["jobs"][self.build_record(build_id)["modules"][name]["job"]]

    def jobs(self, *statuses):
        return [j for j in self.broker.state["jobs"].values() if j["status"] in statuses]

    def until(self, condition, limit=60):
        deadline = time.monotonic() + limit
        while time.monotonic() < deadline:
            self.broker.tick()
            if condition():
                return
            time.sleep(0.05)
        self.fail("Broker did not reach the expected state: " + json.dumps(self.broker.state["jobs"], indent=1))

    def finished(self, job_id):
        return self.broker.state["jobs"].get(job_id, {}).get("status") in lean_broker.FINISHED


class AdmissionRuleTests(unittest.TestCase):
    def test_estimate_is_read_as_a_probable_peak_above_the_baseline(self):
        certain, mean, sd = lean_broker.reservation(1000, 400, 0.5)
        self.assertEqual(certain, 400)
        self.assertAlmostEqual(mean + lean_broker.P90 * sd, 600, places=6)
        self.assertAlmostEqual(sd / mean, 0.5)
        # The spread given is the closure's measured one or the configured default; a job below
        # its baseline reserves the baseline.
        self.assertEqual(lean_broker.reservation(100, 400, 0.5), (400.0, 0.0, 0.0))
        _, mean2, sd2 = lean_broker.reservation(1000, 400, 0.1)
        self.assertAlmostEqual(sd2 / mean2, 0.1)
        # Without a baseline (a calibration job) the whole estimate is certain and carries a spread.
        self.assertEqual(lean_broker.reservation(500, None, 0.5), (500.0, 0.0, 125.0))

    def test_running_growth_is_subtracted_from_what_is_still_owed(self):
        certain, mean, sd = lean_broker.reservation(1000, 400, 0.5)
        grown = lean_broker.reservation(1000, 400, 0.5, current_mb=500)
        self.assertEqual(grown[0], 500)
        self.assertAlmostEqual(grown[1], max(0, certain + mean - 500))
        self.assertEqual(grown[2], sd)
        beyond = lean_broker.reservation(1000, 400, 0.5, current_mb=900)
        self.assertEqual((beyond[0], beyond[1], beyond[2]), (900, 0.0, sd))

    def test_pooled_spreads_admit_what_summed_peaks_would_refuse(self):
        rows = [lean_broker.reservation(1000, 400, 0.5) for _ in range(3)]
        peak_sum = 4 * 1000
        ok, total = lean_broker.admission(rows, lean_broker.reservation(1000, 400, 0.5), 3600, 1.3)
        self.assertTrue(ok)
        self.assertLess(total, peak_sum)
        # Four spreads pooled grow like sqrt(4) = 2, not 4, so the total stays well under the peak sum.
        certain, mean, sd = rows[0]
        self.assertAlmostEqual(total, 4 * certain + 4 * mean + 1.3 * 2 * sd, places=6)
        # With no pooling (z large) or no spread to pool, the rule is a plain sum.
        self.assertFalse(lean_broker.admission(rows, rows[0], 3600, 20)[0])
        self.assertEqual(lean_broker.admission([(100, 0, 0)], (200, 0, 0), 300, 1.3), (True, 300))


class ImportClosureTests(unittest.TestCase):
    def test_imports_are_read_from_the_header_only_and_key_the_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "A.lean"
            path.write_text("/- a block\ncomment -/\n-- a line comment\nprelude\nimport B.Two\n"
                            "import A.One\nimport B.Two\n\ntheorem t : 1 = 1 := rfl\nimport C.Late\n",
                            encoding="utf-8")
            self.assertEqual(lean_broker.read_imports(path), ["A.One", "B.Two"])
            path.write_text("theorem t : 1 = 1 := rfl\n", encoding="utf-8")
            self.assertEqual(lean_broker.read_imports(path), [])
        same = lean_broker.closure_key("Lean 4.1", ["A.One", "B.Two"])
        self.assertEqual(same, lean_broker.closure_key("Lean 4.1", ["A.One", "B.Two"]))
        self.assertNotEqual(same, lean_broker.closure_key("Lean 4.2", ["A.One", "B.Two"]))
        self.assertNotEqual(same, lean_broker.closure_key("Lean 4.1", ["A.One"]))


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.instance = Path(self.temp.name)
        self.base = {"max_sessions": 3,
                     "defaults": {name: {"model": "codex/m", "effort": "high"} for name in ("plan", "research", "explore", "review")},
                     "cli": {"codex": "codex"}, "limit_wait_seconds": 1,
                     "lean": {"command": ["lean"], "version_command": ["lean", "--version"], "cwd": None, "env": {}}}

    def load(self, **lean):
        runner.write_json(self.instance / "settings.json", {**self.base, "lean": {**self.base["lean"], **lean}})
        return runner.load_settings(self.instance)

    def test_defaults_fill_in_and_derive_from_the_host(self):
        settings = self.load()
        self.assertEqual({k: settings["lean"][k] for k in runner.LEAN_DEFAULTS}, runner.LEAN_DEFAULTS)
        with patch.object(runner, "memory_status", return_value=(32 * 1024 ** 3, 8 * 1024 ** 3)), \
                patch.object(runner.os, "cpu_count", return_value=8):
            config = runner.lean_config(settings)
        self.assertEqual(config["memory_budget_mb"], 32 * 1024 - 2048 - 512 * 3)
        self.assertEqual(config["cpu_threads_budget"], 16)
        self.assertEqual(config["derived"]["logical_cores"], 8)
        explicit = runner.lean_config(self.load(memory_budget_mb=4096, cpu_threads_budget=3))
        self.assertEqual((explicit["memory_budget_mb"], explicit["cpu_threads_budget"]), (4096, 3))
        with patch.object(runner, "memory_status", return_value=(1024 ** 3, 0)):
            self.assertEqual(runner.lean_config(self.load())["memory_budget_mb"], 1024)

    def test_invalid_values_are_rejected(self):
        for bad in ({"memory_budget_mb": 0}, {"memory_budget_mb": "8192"}, {"confidence": -1},
                    {"confidence": float("nan")}, {"confidence": True}, {"min_free_memory_mb": -1},
                    {"cpu_threads_budget": 0}, {"threads": 0}, {"threads": None}, {"priority": "realtime"},
                    {"max_passes": -1}, {"max_passes": 1.5}, {"calibration_expect_mb": 0},
                    {"default_spread": -0.1}, {"default_spread": "half"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.load(**bad)


class JobHostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.job = Path(self.temp.name) / "job"
        self.job.mkdir()
        self.lean = source(Path(self.temp.name) / "A.lean", marker="MARK", stderr="WARN", exit=3)

    def launch(self, broker):
        runner.write_json(self.job / "launch.json", {
            "argv": [sys.executable, "-B", str(FAKE), "--threads=1", str(self.lean)], "cwd": str(self.job),
            "env": {"FAKE_ENV": "1"}, "priority": "below_normal", "broker": broker})
        return subprocess.Popen([sys.executable, "-B", str(lean_broker.SCRIPT), "_job", str(self.job)])

    def test_host_waits_for_go_and_records_identity_and_exit(self):
        host = self.launch(runner.process_identity(os.getpid()))
        time.sleep(0.5)
        self.assertIsNone(host.poll())
        self.assertFalse((self.job / "process.json").exists())
        (self.job / "GO").touch()
        self.assertEqual(host.wait(timeout=30), 0)
        receipt = runner.read_json(self.job / "process.json")
        self.assertFalse(runner.alive(receipt["process"]))
        self.assertEqual(runner.read_json(self.job / "exit.json")["exit_code"], 3)
        output = (self.job / "stdout.log").read_text(encoding="utf-8")
        self.assertIn("MARK", output)
        self.assertIn("threads=1", output)
        self.assertIn("FAKE_ENV=1", output)  # lean.env overrides reach the Lean process
        if hasattr(os, "nice"):
            self.assertIn(f"nice={lean_broker.NICE['below_normal']}", output)  # and so does the priority
        self.assertIn("WARN", (self.job / "stderr.log").read_text(encoding="utf-8"))

    def test_host_without_go_exits_on_cancel_or_dead_broker(self):
        host = self.launch(runner.process_identity(os.getpid()))
        (self.job / "CANCEL").touch()
        self.assertEqual(host.wait(timeout=10), 1)
        self.assertFalse((self.job / "exit.json").exists())
        (self.job / "CANCEL").unlink()
        host = self.launch({"pid": os.getpid(), "birth": "not this process"})
        self.assertEqual(host.wait(timeout=10), 1)


class BrokerTests(BrokerFixture):
    def test_first_closure_is_calibrated_then_the_job_runs_and_is_measured(self):
        self.start_broker()
        path = self.session_file("s1", alloc_mb=200, marker="OUT-A", sleep=1)
        job_id = self.submit(path, expect_mb=260)
        self.until(lambda: self.jobs("running"))
        running = self.jobs("running")
        self.assertEqual([j["kind"] for j in running], ["calibration"])
        self.assertEqual(self.broker.state["jobs"][job_id]["waiting_for"], running[0]["id"])
        self.until(lambda: self.finished(job_id))
        job = self.broker.state["jobs"][job_id]
        entry = runner.read_json(self.paths.calibration)["entries"][job["closure"]]
        self.assertEqual(entry["imports"], ["Mathlib.Data.Nat.Basic"])
        self.assertIn("4.0.0-fake", entry["version"])
        self.assertGreater(entry["baseline_mb"], 10)
        self.assertLess(entry["baseline_mb"], 60)
        self.assertEqual(job["status"], "finished")
        self.assertEqual(job["exit_code"], 0)
        self.assertGreater(job["measured"]["peak_mb"], 200)
        self.assertAlmostEqual(job["measured"]["excess_mb"], job["measured"]["peak_mb"] - entry["baseline_mb"], places=0)
        self.assertEqual(entry["excess_mb"], [job["measured"]["excess_mb"]])
        self.assertIn("OUT-A", (self.paths.job(job_id) / "stdout.log").read_text(encoding="utf-8"))
        self.assertEqual(runner.read_json(self.paths.job(job_id) / "result.json")["status"], "finished")
        self.assertAlmostEqual(job["measured"]["estimate_ratio"], job["measured"]["peak_mb"] / 260, places=1)
        # The same closure is not calibrated twice.
        second = self.submit(self.session_file("s1", "B.lean"), expect_mb=40)
        self.until(lambda: self.finished(second))
        self.assertEqual(sum(j["kind"] == "calibration" for j in self.broker.state["jobs"].values()), 1)

    def test_memory_budget_pools_spreads_and_queues_the_rest(self):
        self.start_broker()
        estimate = 360  # two summed estimates exceed the budget; two pooled reservations do not
        self.assertGreater(2 * estimate, self.budget)
        path = self.session_file("s1", alloc_mb=20, sleep=4)
        first = self.submit(path, expect_mb=estimate)
        self.until(lambda: self.broker.calibration.baseline(self.broker.state["jobs"][first]["closure"]) is not None)
        others = [self.submit(self.session_file("s1", f"{n}.lean", alloc_mb=20, sleep=4), expect_mb=estimate) for n in "BC"]
        self.until(lambda: len(self.jobs("running")) == 2)
        self.broker.tick()
        self.assertEqual(len(self.jobs("running")), 2)
        self.assertEqual(len(self.jobs("queued")), 1)
        waiting = self.jobs("queued")[0]
        self.assertGreater(waiting["reserve"]["total_mb"], self.budget)
        self.assertLess(waiting["reserve"]["total_mb"], 3 * estimate)  # still well under three summed estimates
        self.until(lambda: all(self.finished(j) for j in [first, *others]))
        self.assertTrue(all(self.broker.state["jobs"][j]["exit_code"] == 0 for j in [first, *others]))

    def serial(self, jobs):
        """Tick through the jobs and confirm that no two of them ever run at once."""
        self.until(lambda: self.jobs("running"))
        while not all(self.finished(j) for j in jobs):
            self.broker.tick()
            self.assertLessEqual(len(self.jobs("running")), 1)
            time.sleep(0.05)

    def test_thread_budget_limits_parallelism(self):
        # Memory is ample (two of these fit the 700 MiB budget easily); only the threads can serialize them.
        self.write_settings(cpu_threads_budget=2, threads=2)
        self.start_broker()
        warm = self.submit(self.session_file("s1", "warm.lean", sleep=0.2), expect_mb=30)
        self.until(lambda: self.finished(warm))
        jobs = [self.submit(self.session_file("s1", f"{n}.lean", sleep=1.5), expect_mb=30) for n in "AB"]
        self.serial(jobs)
        argv = runner.read_json(self.paths.job(jobs[0]) / "launch.json")["argv"]
        self.assertIn("--threads=2", argv)
        self.assertEqual(argv[-1], str(self.instance / "sessions/s1/work/A.lean"))
        self.write_settings(cpu_threads_budget=4)
        time.sleep(0.02)
        pair = [self.submit(self.session_file("s1", f"{n}.lean", sleep=1.5), expect_mb=30) for n in "CD"]
        self.until(lambda: len(self.jobs("running")) == 2)
        self.until(lambda: all(self.finished(j) for j in pair))

    def test_a_job_exceeding_both_budgets_alone_still_runs_alone(self):
        self.write_settings(cpu_threads_budget=1, threads=3, memory_budget_mb=50)
        self.start_broker()
        jobs = [self.submit(self.session_file("s1", f"{n}.lean", sleep=1), expect_mb=400) for n in "AB"]
        self.serial(jobs)
        self.assertTrue(all(self.broker.state["jobs"][j]["exit_code"] == 0 for j in jobs))

    def test_first_fit_lets_small_jobs_pass_and_aging_stops_starvation(self):
        self.start_broker()
        warm = self.submit(self.session_file("s1", "warm.lean", sleep=0.2), expect_mb=25)
        self.until(lambda: self.finished(warm))
        big = self.submit(self.session_file("s1", "big.lean", sleep=3), expect_mb=500)
        self.until(lambda: self.broker.state["jobs"][big]["status"] == "running")
        head = self.submit(self.session_file("s1", "head.lean", sleep=0.3), expect_mb=500)
        passes = self.broker.config["max_passes"]
        small = [self.submit(self.session_file("s1", f"small{n}.lean", sleep=0.4), expect_mb=40)
                 for n in range(passes + 2)]
        # The head cannot fit beside the big job; small jobs pass it, but only max_passes of them.
        self.until(lambda: self.broker.state["jobs"][head]["passed"] == passes)
        self.assertEqual(self.broker.state["jobs"][head]["status"], "queued")
        self.assertGreater(self.broker.state["jobs"][head]["reserve"]["total_mb"], self.budget)
        for _ in range(4):
            self.broker.tick()
            time.sleep(0.1)
        # Count the small jobs that started before the head did: under load the big job may already
        # have ended by now, letting the head start and one more small job follow it legitimately.
        head_started = self.broker.state["jobs"][head]["started_at"] or float("inf")
        started = [j for j in small if self.broker.state["jobs"][j]["started_at"]
                   and self.broker.state["jobs"][j]["started_at"] < head_started]
        self.assertEqual(len(started), passes)
        self.until(lambda: self.finished(head))
        self.assertGreaterEqual(self.broker.state["jobs"][head]["started_at"],
                                self.broker.state["jobs"][big]["finished_at"] - 0.5)
        self.until(lambda: all(self.finished(j) for j in small))
        self.assertTrue(all(self.broker.state["jobs"][j]["exit_code"] == 0 for j in small))

    def test_duplicate_submission_returns_the_running_job(self):
        self.start_broker()
        path = self.session_file("s1", sleep=2)
        first = self.submit(path, expect_mb=40)
        self.until(lambda: self.broker.state["jobs"].get(first))
        second = self.submit(path, expect_mb=40)
        self.until(lambda: (self.paths.job(second) / "result.json").exists())
        self.assertEqual(runner.read_json(self.paths.job(second) / "result.json")["duplicate_of"], first)
        self.assertNotIn(second, self.broker.state["jobs"])
        self.assertEqual(lean_broker.job_record(self.paths, second)["status"], "duplicate")
        # Another session compiling the same file is not a duplicate.
        third = self.submit(path, expect_mb=40, session="s2")
        self.until(lambda: self.broker.state["jobs"].get(third))
        self.assertEqual(self.broker.state["jobs"][third]["status"], "queued")
        self.until(lambda: self.finished(first) and self.finished(third))
        self.assertEqual(self.broker.state["jobs"][first]["exit_code"], 0)

    def test_orphaned_job_is_cancelled_and_its_process_tree_terminated(self):
        self.start_broker()
        state = runner.read_json(self.instance / "runner/state.json")
        state["sessions"]["s1"] = {"category": "research", "status": "running", "host": None, "cli": None}
        runner.write_json(self.instance / "runner/state.json", state)
        job_id = self.submit(self.session_file("s1", sleep=30), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][job_id]["status"] == "running" and self.broker.state["jobs"][job_id].get("pid"))
        pid = self.broker.state["jobs"][job_id]["pid"]
        lean = self.broker.state["jobs"][job_id]["lean"]
        self.assertTrue(runner.alive(lean))
        state["sessions"]["s1"]["status"] = "integrated"
        runner.write_json(self.instance / "runner/state.json", state)
        self.until(lambda: self.finished(job_id), limit=20)
        job = self.broker.state["jobs"][job_id]
        self.assertEqual(job["status"], "cancelled")
        self.assertIn("ended", job["reason"])
        self.assertFalse(runner.alive(lean))
        self.assertNotIn(pid, [p for p in lean_broker.process_tree(os.getpid())])
        # A cancelled job leaves no sample in the closure history.
        entry = self.broker.calibration.entry(job["closure"])
        self.assertEqual(entry["excess_mb"], [])

    def test_job_of_a_dead_session_is_cancelled_but_a_live_one_is_kept(self):
        self.start_broker()
        gone = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"], capture_output=True, text=True)
        dead = {"pid": int(gone.stdout), "birth": "a process that has exited"}
        live = runner.process_identity(os.getpid())
        state = runner.read_json(self.instance / "runner/state.json")
        state["sessions"]["s1"] = {"category": "research", "status": "running", "host": dead, "cli": live}
        state["sessions"]["s2"] = {"category": "research", "status": "running", "host": dead, "cli": dead}
        runner.write_json(self.instance / "runner/state.json", state)
        kept = self.submit(self.session_file("s1", sleep=2), expect_mb=40, session="s1")
        dropped = self.submit(self.session_file("s2", sleep=30), expect_mb=40, session="s2")
        self.until(lambda: self.finished(dropped))
        self.assertEqual(self.broker.state["jobs"][dropped]["status"], "cancelled")
        self.assertIn("no longer alive", self.broker.state["jobs"][dropped]["reason"])
        self.until(lambda: self.finished(kept))
        self.assertEqual(self.broker.state["jobs"][kept]["status"], "finished")

    def test_failed_calibration_lets_the_waiting_job_run_on_its_own_estimate(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", imports=("Missing.Module",)), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        job = self.broker.state["jobs"][job_id]
        calibration = next(j for j in self.broker.state["jobs"].values() if j["kind"] == "calibration")
        self.assertEqual((calibration["status"], calibration["exit_code"]), ("finished", 1))
        self.assertIsNone(self.broker.calibration.baseline(job["closure"]))
        self.assertEqual(self.broker.calibration.entry(job["closure"])["failed"]["exit_code"], 1)
        self.assertEqual((job["status"], job["exit_code"], job["waiting_for"]), ("finished", 1, None))
        self.assertEqual(sum(j["kind"] == "calibration" for j in self.broker.state["jobs"].values()), 1)
        self.assertEqual(job["reserve"]["certain_mb"], 40)  # no baseline: the whole estimate is reserved
        self.assertIn("unknown module", (self.paths.job(job_id) / "stdout.log").read_text(encoding="utf-8"))

    def test_failed_and_cancelled_jobs_report_their_own_exit_codes(self):
        self.start_broker()
        self.broker.config["cpu_threads_budget"] = 1
        blocker = self.submit(self.session_file("s1", "block.lean", sleep=30), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][blocker]["status"] == "running")
        vanishing = self.session_file("s1", "gone.lean")
        job_id = self.submit(vanishing, expect_mb=40)
        self.until(lambda: self.broker.state["jobs"].get(job_id, {}).get("status") == "queued")
        vanishing.unlink()
        self.broker.config["cpu_threads_budget"] = 4
        self.until(lambda: self.finished(job_id))
        self.assertEqual(self.broker.state["jobs"][job_id]["status"], "failed")
        self.assertIn("does not exist", self.broker.state["jobs"][job_id]["reason"])
        with patch.object(lean_broker, "ensure_broker", return_value={}), contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(lean_broker.wait(self.paths, job_id), 3)
        self.assertIn('"status": "failed"', err.getvalue())
        lean_broker.cancel(self.paths, blocker)
        self.until(lambda: self.finished(blocker))
        with patch.object(lean_broker, "ensure_broker", return_value={}), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lean_broker.wait(self.paths, blocker), 4)

    def test_lost_job_host_fails_the_job_with_the_reason(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", sleep=30), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][job_id]["status"] == "running" and self.broker.state["jobs"][job_id].get("pid"))
        job = self.broker.state["jobs"][job_id]
        lean_broker.terminate_tree(job["host"]["pid"])  # the host and its Lean, with no exit.json written
        self.until(lambda: self.finished(job_id))
        self.assertEqual(job["status"], "failed")
        self.assertIn("without recording an exit", job["reason"])
        self.assertFalse((self.paths.job(job_id) / "exit.json").exists())

    def test_finished_jobs_are_pruned_from_the_state_but_keep_their_results(self):
        self.start_broker()
        with patch.object(lean_broker, "KEEP_FINISHED", 1):
            first = self.submit(self.session_file("s1", "A.lean"), expect_mb=40)
            self.until(lambda: self.finished(first))
            second = self.submit(self.session_file("s1", "B.lean"), expect_mb=40)
            self.until(lambda: self.finished(second))
        self.assertNotIn(first, self.broker.state["jobs"])
        self.assertIn(second, self.broker.state["jobs"])
        self.assertEqual(lean_broker.job_record(self.paths, first)["status"], "finished")

    def test_queued_job_is_cancelled_on_request_before_it_starts(self):
        self.start_broker()
        blocker = self.submit(self.session_file("s1", "block.lean", sleep=3), expect_mb=40)
        self.until(lambda: self.jobs("running") and self.broker.calibration.baseline(self.broker.state["jobs"][blocker]["closure"]))
        self.until(lambda: self.broker.state["jobs"][blocker]["status"] == "running")
        self.write_settings(cpu_threads_budget=1)
        waiting = self.submit(self.session_file("s1", "wait.lean"), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"].get(waiting, {}).get("status") == "queued")
        lean_broker.cancel(self.paths, waiting)
        self.until(lambda: self.finished(waiting))
        self.assertEqual(self.broker.state["jobs"][waiting]["status"], "cancelled")
        self.assertEqual(lean_broker.job_record(self.paths, waiting)["status"], "cancelled")
        # Cancelled while queued: Lean was never started for it.
        self.assertIsNone(self.broker.state["jobs"][waiting]["started_at"])
        self.assertFalse((self.paths.job(waiting) / "launch.json").exists())
        self.assertEqual(self.broker.state["jobs"][blocker]["status"], "running")
        unread = self.submit(self.session_file("s1", "unread.lean"), expect_mb=40)
        self.assertIn("before the broker", lean_broker.cancel(self.paths, unread)["cancelled"])
        self.broker.tick()
        self.assertNotIn(unread, self.broker.state["jobs"])
        # A request the broker cannot accept is answered, not dropped.
        bad = "j" + "0" * 32
        runner.write_json(self.paths.queue / (bad + ".json"), {"id": bad, "source": 5, "expect_mb": 40})
        (self.paths.queue / "x..escape.json").write_text("{}", encoding="utf-8")
        self.broker.tick()
        self.assertEqual(lean_broker.job_record(self.paths, bad)["status"], "failed")
        self.assertIn("rejected", lean_broker.job_record(self.paths, bad)["reason"])
        self.assertEqual(list(self.paths.queue.glob("*.json")), [])
        self.assertFalse((self.paths.root / "escape").exists())

    def test_settings_reload_live_and_keep_the_last_good_configuration(self):
        self.start_broker()
        self.assertEqual(self.broker.config["memory_budget_mb"], self.budget)
        time.sleep(0.02)
        self.write_settings(memory_budget_mb=1234)
        self.broker.tick()
        self.assertEqual(self.broker.config["memory_budget_mb"], 1234)
        self.assertEqual(runner.read_json(self.paths.state)["config"]["memory_budget_mb"], 1234)
        time.sleep(0.02)
        (self.instance / "settings.json").write_text("{not json", encoding="utf-8")
        with patch.object(self.broker, "log") as log:
            self.broker.tick()
        self.assertEqual(self.broker.config["memory_budget_mb"], 1234)
        self.assertTrue(runner.read_json(self.paths.state)["config_error"])
        self.assertEqual(log.call_args.kwargs["event"], "settings_rejected")
        time.sleep(0.02)
        self.write_settings(memory_budget_mb=99)
        self.broker.tick()
        self.assertEqual(self.broker.config["memory_budget_mb"], 99)
        self.assertIsNone(runner.read_json(self.paths.state)["config_error"])

    def test_machine_gate_holds_every_start(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        with patch.object(lean_broker, "available_memory", return_value=10 * lean_broker.MIB):
            self.broker.config["min_free_memory_mb"] = 5000
            for _ in range(4):
                self.broker.tick()
            self.assertEqual(self.jobs("running"), [])
        self.broker.config["min_free_memory_mb"] = 0
        self.until(lambda: self.finished(job_id))

    def test_submission_requires_estimate_session_and_existing_file(self):
        with patch.object(lean_broker, "ensure_broker", return_value={}):
            path = self.session_file("s1")
            with self.assertRaisesRegex(ValueError, "expect-mb"):
                lean_broker.submit(self.paths, path, 0, "s1")
            with self.assertRaisesRegex(ValueError, "expect-mb"):
                lean_broker.submit(self.paths, path, 3.5, "s1")
            with self.assertRaisesRegex(ValueError, "does not exist"):
                lean_broker.submit(self.paths, self.root / "missing.lean", 10, "s1")
            with self.assertRaisesRegex(ValueError, "session"):
                lean_broker.submit(self.paths, path, 10, " ")
            receipt = lean_broker.submit(self.paths, source(self.root / "outside.lean"), 10, "s9")
            self.assertEqual(receipt["session"], "s9")
            self.assertEqual(len(list(self.paths.queue.glob("*.json"))), 1)
        for argv in (["run", str(self.instance), str(path), "--session", "s1"],
                     ["run", str(self.instance), str(path), "--expect-mb", "10"]):
            with self.assertRaisesRegex(SystemExit, "2"), contextlib.redirect_stderr(io.StringIO()):
                lean_broker.main(argv)

    def test_exit_rule_waits_for_sessions_and_jobs(self):
        self.start_broker()
        self.assertFalse(self.broker.should_exit())
        state = runner.read_json(self.instance / "runner/state.json")
        state["complete"] = "k1"
        state["sessions"]["s1"] = {"category": "research", "status": "running", "host": None, "cli": None}
        runner.write_json(self.instance / "runner/state.json", state)
        self.assertFalse(self.broker.should_exit())
        state["sessions"]["s1"]["status"] = "integrated"
        runner.write_json(self.instance / "runner/state.json", state)
        job_id = self.submit(self.session_file("s2", sleep=0.5), expect_mb=40, session="s2")
        self.broker.tick()
        self.assertFalse(self.broker.should_exit())
        self.until(lambda: self.finished(job_id))
        self.assertTrue(self.broker.should_exit())


class BuildTests(BrokerFixture):
    def test_build_follows_imports_caches_and_rebuilds_only_what_changed(self):
        self.start_broker()
        root = self.tree()
        first = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(first)["status"] in lean_broker.FINISHED)
        record = self.build_record(first)
        self.assertEqual(record["status"], "finished", record)
        self.assertEqual(list(record["modules"]), ["A", "B", "C", "D"])  # dependency order
        self.assertTrue(all(m["status"] == "finished" and m["exit_code"] == 0 for m in record["modules"].values()))
        a, b, c, d = (self.module_job(first, n) for n in "ABCD")
        self.assertLessEqual(a["finished_at"], min(b["started_at"], c["started_at"]))
        self.assertLess(max(b["started_at"], c["started_at"]), min(b["finished_at"], c["finished_at"]))  # side by side
        self.assertLessEqual(max(b["finished_at"], c["finished_at"]), d["started_at"])
        self.assertEqual(b["deps"], [a["id"]])
        self.assertIn("-R", runner.read_json(self.paths.job(d["id"]) / "launch.json")["argv"])
        self.assertTrue((Path(record["lib"]) / "D.olean").is_file())
        self.assertEqual(len(list(self.paths.cache.glob("*.olean"))), 4)
        # External imports alone key the calibration: B's closure is the empty one, not "A".
        self.assertEqual(b["closure"], lean_broker.closure_key(self.broker.state["version"], []))
        # The same bytes again: every module comes from the cache, no compile runs, the output is replayed.
        jobs_before = len(self.broker.state["jobs"])
        second = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(second)["status"] in lean_broker.FINISHED)
        self.assertTrue(all(m["status"] == "cached" for m in self.build_record(second)["modules"].values()))
        self.assertEqual(len(self.broker.state["jobs"]), jobs_before)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lean_broker.report_build(self.paths, self.build_record(second))
        self.assertEqual(code, 0)
        self.assertIn("TARGET-D", out.getvalue())
        summary = json.loads(err.getvalue().split("lean-broker: ", 1)[1])
        self.assertEqual(summary["status"], "finished")
        self.assertTrue(all(m["cached"] for m in summary["modules"]))
        # A change in B reaches D through the keys; A and C stay cached.
        with (root / "B.lean").open("a", encoding="utf-8") as stream:
            stream.write("-- changed\n")
        third = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(third)["status"] in lean_broker.FINISHED)
        statuses = {n: m["status"] for n, m in self.build_record(third)["modules"].items()}
        self.assertEqual(statuses, {"A": "cached", "B": "finished", "C": "cached", "D": "finished"})
        self.assertEqual(len(list(self.paths.cache.glob("*.olean"))), 6)

    def test_failed_module_fails_its_dependents_with_the_reason(self):
        self.start_broker()
        root = self.tree(A={"exit": 1})
        build_id = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        record = self.build_record(build_id)
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["modules"]["A"]["status"], "finished")
        self.assertEqual(record["modules"]["A"]["exit_code"], 1)
        for name in "BC":
            self.assertEqual(record["modules"][name]["status"], "failed")
            self.assertIn("dependency A ended with exit code 1", record["modules"][name]["reason"])
        self.assertIn("dependency", record["modules"]["D"]["reason"])
        self.assertIn("module B failed", record["reason"])
        self.assertFalse(list(self.paths.cache.glob("*.olean")))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lean_broker.report_build(self.paths, record), 3)

    def test_build_rejects_bad_targets_cycles_and_shadowing(self):
        self.start_broker()
        root = self.tree()
        with self.assertRaisesRegex(ValueError, "not in the subpath|not a module path"):
            self.build(root, [self.instance / "goal.md"])
        with self.assertRaisesRegex(ValueError, "does not exist"):
            self.build(root, [root / "Nope.lean"])
        source(root / "X.lean", imports=("Y",))
        source(root / "Y.lean", imports=("X",))
        cyclic = self.build(root, [root / "X.lean"])
        self.until(lambda: self.build_record(cyclic)["status"] in lean_broker.FINISHED)
        self.assertIn("import cycle", self.build_record(cyclic)["reason"])
        source(root / "Mathlib" / "Foo.lean", imports=())
        source(root / "Shadow.lean", imports=("Mathlib.Foo", "Mathlib.Data.Nat.Basic"))
        shadowing = self.build(root, [root / "Shadow.lean"])
        self.until(lambda: self.build_record(shadowing)["status"] in lean_broker.FINISHED)
        self.assertIn("shadow", self.build_record(shadowing)["reason"])
        self.assertFalse(self.jobs("queued", "running"))

    def test_state_written_before_builds_existed_still_accepts_a_build(self):
        runner.write_json(self.paths.state, {"jobs": {}, "version": None})  # no "builds": an older broker's state
        self.start_broker()
        root = self.tree()
        build_id = self.build(root, [root / "A.lean"])
        self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        self.assertEqual(self.build_record(build_id)["status"], "finished")

    def test_cancelling_a_build_stops_its_queue(self):
        self.start_broker()
        root = self.tree(A={"sleep": 30})
        build_id = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(build_id)["modules"]["A"]["status"] == "running")
        lean_broker.cancel(self.paths, build_id)
        self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        record = self.build_record(build_id)
        self.assertEqual(record["status"], "cancelled")
        self.assertEqual(record["modules"]["A"]["status"], "cancelled")
        self.assertTrue(all(m["status"] in ("cancelled", "failed") for m in record["modules"].values()))
        self.assertFalse(runner.alive(self.module_job(build_id, "A").get("lean")))


class LauncherTests(BrokerFixture):
    LAKE = [sys.executable, "-B", str(FAKE.with_name("fake_lake.py")), "env"]

    def test_lake_env_is_asked_once_and_lean_then_runs_directly(self):
        self.write_settings(command=self.LAKE + [sys.executable, "-B", str(FAKE)],
                            version_command=self.LAKE + [sys.executable, "-B", str(FAKE), "--version"])
        self.start_broker()
        self.assertTrue(self.broker.state["launcher"]["direct"])
        self.assertEqual(self.broker.direct["argv"], [sys.executable, "-B", str(FAKE)])
        self.assertEqual(self.broker.direct["env"]["FAKE_LAKE"], "1")
        self.assertTrue(self.broker.direct["env"]["LEAN_PATH"].startswith("fake-lake-lib"))
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        job = self.broker.state["jobs"][job_id]
        self.assertEqual(job["exit_code"], 0)
        launch = runner.read_json(self.paths.job(job_id) / "launch.json")
        self.assertEqual(launch["argv"][:3], [sys.executable, "-B", str(FAKE)])  # lean itself, no lake in front
        self.assertEqual(launch["env"]["FAKE_LAKE"], "1")
        # Baselines measured directly are keyed apart from those measured through lake.
        self.assertEqual(job["closure"], lean_broker.closure_key(self.broker.state["version"], job["imports"], True))
        self.assertNotEqual(job["closure"], lean_broker.closure_key(self.broker.state["version"], job["imports"]))
        self.assertIn("launcher", lean_broker.broker_status(self.paths))

    def test_a_lake_that_fails_leaves_the_configured_command_in_force(self):
        self.write_settings(command=self.LAKE + [sys.executable, "-B", str(FAKE)], env={"FAKE_LAKE_FAIL": "1"})
        self.start_broker()
        self.assertFalse(self.broker.state["launcher"]["direct"])
        self.assertIn("exit code 7", self.broker.state["launcher"]["reason"])
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        launch = runner.read_json(self.paths.job(job_id) / "launch.json")
        self.assertEqual(launch["argv"][:len(self.LAKE)], self.LAKE)
        self.assertEqual(self.broker.state["jobs"][job_id]["exit_code"], 7)  # what the configured lake does


class ClientAndLifecycleTests(BrokerFixture):
    def cli(self, *args, timeout=60):
        return subprocess.run([sys.executable, "-B", str(lean_broker.SCRIPT), *args],
                              capture_output=True, text=True, encoding="utf-8", timeout=timeout)

    def test_run_relays_output_exit_code_and_measurements(self):
        path = self.session_file("s1", alloc_mb=50, sleep=1, marker="RELAYED", stderr="TO-STDERR", exit=1)
        path.write_text(path.read_text(encoding="utf-8").replace("rfl", "sorry"), encoding="utf-8")
        result = self.cli("run", str(self.instance), str(path), "--session", "s1", "--expect-mb", "120")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("RELAYED", result.stdout)
        self.assertIn("warning: declaration uses 'sorry'", result.stdout)
        self.assertIn("TO-STDERR", result.stderr)
        summary = json.loads(result.stderr.strip().splitlines()[-1].split("lean-broker: ", 1)[1])
        self.assertEqual((summary["status"], summary["exit_code"], summary["expect_mb"]), ("finished", 1, 120))
        self.assertGreater(summary["measured"]["peak_mb"], 50)
        self.assertIn("baseline_mb", summary["measured"])
        record = json.loads(self.cli("result", str(self.instance), summary["job"]).stdout)
        self.assertEqual(record["session"], "s1")
        status = json.loads(self.cli("status", str(self.instance)).stdout)
        self.assertTrue(status["broker_alive"])
        self.assertEqual(status["config"]["memory_budget_mb"], self.budget)
        self.assertIn("4.0.0-fake", json.loads(self.cli("version", str(self.instance)).stdout)["version"])
        self.assertIn("4.0.0-fake", status["version"])
        self.assertEqual(runner.status(self.instance)["lean"]["version"], status["version"])

    def test_wait_timeout_returns_124_and_the_job_continues(self):
        path = self.session_file("s1", sleep=3)
        submitted = json.loads(self.cli("submit", str(self.instance), str(path), "--session", "s1", "--expect-mb", "40").stdout)
        early = self.cli("wait", str(self.instance), submitted["job"], "--timeout", "0.5")
        self.assertEqual(early.returncode, 124)
        self.assertIn(submitted["job"], early.stderr)
        late = self.cli("wait", str(self.instance), submitted["job"])
        self.assertEqual(late.returncode, 0, late.stderr)
        self.assertIn("compiled", late.stdout)
        unknown = self.cli("wait", str(self.instance), "jnobody")
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("unknown job", unknown.stderr)

    def test_second_broker_yields_to_the_lock(self):
        self.assertEqual(self.cli("version", str(self.instance)).returncode, 0)  # launches the first broker
        first = lean_broker.broker_alive(self.paths)
        self.assertTrue(first)
        second = self.cli("serve", str(self.instance), timeout=30)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("already has a running runner", second.stderr)
        self.assertTrue(runner.alive(first["process"]))
        self.cli("version", str(self.instance))  # finds the live broker; launches nothing
        self.assertEqual(lean_broker.broker_alive(self.paths)["process"], first["process"])

    def test_broker_death_mid_job_loses_neither_output_nor_exit_code(self):
        path = self.session_file("s1", sleep=4, marker="SURVIVED", exit=5)
        submitted = json.loads(self.cli("submit", str(self.instance), str(path), "--session", "s1", "--expect-mb", "40").stdout)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            record = lean_broker.job_record(self.paths, submitted["job"])
            if record and record["status"] == "running" and record.get("pid"):
                break
            time.sleep(0.05)
        else:
            self.fail("job did not start")
        broker = lean_broker.broker_alive(self.paths)
        runner.terminate_process(broker["process"])
        while runner.alive(broker["process"]):
            time.sleep(0.02)
        self.assertTrue(runner.alive(record["lean"]))
        # A client that finds no broker launches one, which adopts the running job.
        late = self.cli("wait", str(self.instance), submitted["job"])
        self.assertEqual(late.returncode, 5, late.stderr)
        self.assertIn("SURVIVED", late.stdout)
        adopted = lean_broker.job_record(self.paths, submitted["job"])
        self.assertEqual(adopted["status"], "finished")
        self.assertEqual(adopted["lean"], record["lean"])
        self.assertIn('"event": "adopted"', self.paths.log.read_text(encoding="utf-8"))

    def test_unstarted_job_is_requeued_not_failed(self):
        self.start_broker()
        self.broker.config["cpu_threads_budget"] = 1
        blocker = self.submit(self.session_file("s1", "block.lean", sleep=2), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][blocker]["status"] == "running")
        job_id = self.submit(self.session_file("s1", marker="REQUEUED"), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"].get(job_id, {}).get("status") == "queued")
        # Simulate a broker that died after recording the host but before GO.
        with patch.object(lean_broker.Path, "write_bytes", side_effect=RuntimeError("died before GO")):
            with self.assertRaises(RuntimeError):
                self.broker.launch(self.broker.state["jobs"][job_id])
        job = self.broker.state["jobs"][job_id]
        self.assertEqual(job["status"], "running")
        self.assertFalse((self.paths.job(job_id) / "GO").exists())
        self.broker.save()
        old_hosts = self.broker.hosts
        self.broker = lean_broker.Broker(self.instance, log_path=self.paths.log)
        self.broker.start()
        for host in old_hosts.values():
            host.wait(timeout=10)
        self.assertEqual(self.broker.state["jobs"][job_id]["status"], "queued")
        self.assertEqual(self.broker.state["jobs"][blocker]["status"], "running")
        self.until(lambda: self.finished(job_id) and self.finished(blocker))
        self.assertEqual(self.broker.state["jobs"][job_id]["exit_code"], 0)
        self.assertIn("REQUEUED", (self.paths.job(job_id) / "stdout.log").read_text(encoding="utf-8"))
        self.assertEqual(sum(j["kind"] == "compile" for j in self.broker.state["jobs"].values()), 2)

    def test_runner_launches_adopts_and_relaunches_the_broker(self):
        skill = runner.SKILL
        engine = runner.Runner(self.instance, skill)
        # A complete instance with nothing active is the one case where no broker is started.
        engine.state["complete"] = "k1"
        engine.ensure_broker()
        self.assertIsNone(lean_broker.broker_alive(self.paths))
        engine.state["complete"] = None
        engine.ensure_broker()  # otherwise a broker is kept alive whether or not a session exists yet
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not lean_broker.broker_alive(self.paths):
            time.sleep(0.05)
        first = lean_broker.broker_alive(self.paths)
        self.assertTrue(first)
        self.assertTrue(runner.status(self.instance)["lean"]["broker_alive"])
        other = runner.Runner(self.instance, skill)
        other.ensure_broker()
        self.assertIsNone(other.broker)
        self.assertEqual(lean_broker.broker_alive(self.paths)["process"], first["process"])
        runner.terminate_process(first["process"])
        while runner.alive(first["process"]):
            time.sleep(0.02)
        engine.ensure_broker()  # within BROKER_RETRY of the last launch: no relaunch yet
        time.sleep(0.5)
        self.assertIsNone(lean_broker.broker_alive(self.paths))
        engine.broker_attempt = float("-inf")
        engine.ensure_broker()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not lean_broker.broker_alive(self.paths):
            time.sleep(0.05)
        second = lean_broker.broker_alive(self.paths)
        self.assertNotEqual(second["process"], first["process"])
        runner.terminate_process(second["process"])
        engine.broker.wait(timeout=10)

    def test_build_command_relays_the_target_and_waits_on_a_build_id(self):
        root = self.tree()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lean_broker.main(["build", str(self.instance), str(root), "D.lean",
                                     "--session", "s1", "--expect-mb", "60"])
        self.assertEqual(code, 0, err.getvalue())
        self.assertIn("TARGET-D", out.getvalue())
        summary = json.loads(err.getvalue().strip().splitlines()[-1].split("lean-broker: ", 1)[1])
        self.assertEqual(summary["status"], "finished")
        self.assertEqual([m["module"] for m in summary["modules"]], ["A", "B", "C", "D"])
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(lean_broker.main(["build", str(self.instance), str(root), "D.lean",
                                               "--session", "s1", "--expect-mb", "60", "--no-wait"]), 0)
        build_id = json.loads(out.getvalue())["build"]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(lean_broker.main(["wait", str(self.instance), build_id, "--timeout", "60"]), 0)
        self.assertIn("TARGET-D", out.getvalue())  # replayed from the cache: nothing was compiled again
        self.assertIn('"cached": true', err.getvalue())
        with contextlib.redirect_stdout(out):
            self.assertEqual(lean_broker.main(["result", str(self.instance), build_id]), 0)
        self.assertIn("builds", json.dumps(lean_broker.broker_status(self.paths)))


if __name__ == "__main__":
    unittest.main()

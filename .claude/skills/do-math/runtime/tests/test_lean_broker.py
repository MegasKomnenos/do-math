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
import runtime_support

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
            "cli": {"codex": "codex.exe", "claude": "claude.exe"},
            "lean": {"command": [sys.executable, "-B", str(FAKE)],
                     "version_command": [sys.executable, "-B", str(FAKE), "--version"], "cwd": None, "env": {},
                     "memory_budget_mb": self.budget, "min_free_memory_mb": 0, "threads": 1,
                     "cpu_threads_budget": self.threads_budget,
                     # The stand-in compiler must not starve behind normal-priority load on the test machine.
                     "priority": "normal"}}
        runner.write_json(self.settings_path, self.settings)
        runner.initialize(self.instance, goal, self.settings_path)
        self.paths = lean_broker.Paths(self.instance)
        self.paths.ensure()
        self.broker = None
        self.previous_hosts = []

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
        hosts = self.previous_hosts + (list(self.broker.hosts.values()) if self.broker is not None else [])
        for host in hosts:
            host.wait(timeout=10)
        if self.paths.state.exists():  # hosts of a detached broker exit once their Lean has ended
            for job in runner.read_json(self.paths.state).get("jobs", {}).values():
                self.wait_gone(job.get("host"))
        self.stop_detached_broker()
        # A broker terminated during its startup orphans its version command for a moment; on Windows
        # that child holds the calibration folder as its working directory until it exits. A broker
        # that was still starting when it was looked for above holds its files as well, so each retry
        # stops any broker that has since recorded itself.
        deadline = time.monotonic() + 10
        while True:
            try:
                self.temp.cleanup()
                break
            except PermissionError:
                if time.monotonic() >= deadline:
                    raise
                self.stop_detached_broker()
                time.sleep(0.1)

    def stop_detached_broker(self):
        info = lean_broker.broker_alive(self.paths)
        if info:
            runner.terminate_process(info["process"])
            while runner.alive(info["process"]):
                time.sleep(0.02)

    @staticmethod
    def wait_gone(identity, limit=10):
        deadline = time.monotonic() + limit
        while runner.alive(identity) and time.monotonic() < deadline:
            time.sleep(0.02)

    def start_broker(self):
        """The broker's own startup, in this process, minus the lock and the receipt `serve` adds."""
        if self.broker is not None:
            self.previous_hosts.extend(self.broker.hosts.values())
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


class BuildResultTests(unittest.TestCase):
    def test_wait_preserves_nonzero_module_codes_in_the_build_aggregate(self):
        # Controlled terminal records test the real consumer, not POSIX execution. Each row is
        # a state the broker can reach. Basis is Target's import when it is cached or failed;
        # an import with a nonzero code would have failed Target, so a nonzero Basis code
        # comes from a second target compiled beside Target.
        cases = (
            ("finished", (0, 0), 0, 0),
            ("finished", (0, 1), 1, 1),
            ("finished", (0, -9), -9, -9),
            ("finished", (-9, 0), -9, -9),
            ("finished", (-15, -9), -9, -9),
            ("finished", (-9, 1), 1, 1),
            ("failed", (-9, None), 3, -9),
            ("cancelled", (0, -9), 4, -9),
            ("failed", (None, None), 3, 0),
        )
        with tempfile.TemporaryDirectory() as temporary:
            paths = lean_broker.Paths(Path(temporary))
            build_id = "b" + "1" * 32
            folder = paths.build(build_id)
            folder.mkdir(parents=True)
            for status, codes, expected_return, expected_summary in cases:
                with self.subTest(status=status, codes=codes):
                    modules = {
                        name: {"status": "finished" if code is not None else "failed",
                               "exit_code": code, "job": None}
                        for name, code in zip(("Basis", "Target"), codes)
                    }
                    if codes[0] == 0:
                        modules["Basis"]["status"] = "cached"
                    targets = ["Target"] if codes[0] in (0, None) else ["Basis", "Target"]
                    result = {"id": build_id, "status": status, "targets": targets,
                              "modules": modules, "reason": None}
                    runner.write_json(folder / "result.json", result)
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        returned = lean_broker.wait(paths, build_id, timeout=0)
                    self.assertEqual(returned, expected_return)
                    summary = json.loads(err.getvalue().split("lean-broker: ", 1)[1])
                    self.assertEqual(summary["status"], status)
                    self.assertEqual(summary["exit_code"], expected_summary)
                    self.assertEqual([(m["module"], m["exit_code"]) for m in summary["modules"]],
                                     list(zip(("Basis", "Target"), codes)))


class StatusTests(unittest.TestCase):
    def test_recently_finished_jobs_are_the_last_to_finish(self):
        # A long compile submitted before many short ones finishes after them; status must list it.
        with tempfile.TemporaryDirectory() as temporary:
            paths = lean_broker.Paths(Path(temporary))
            paths.ensure()
            late = "j" + "f" * 32
            jobs = {late: {"id": late, "status": "finished", "finished_at": 2000.0}}
            short = [f"j{n:032x}" for n in range(1, 31)]
            jobs.update({job_id: {"id": job_id, "status": "finished", "finished_at": 1000.0 + n}
                         for n, job_id in enumerate(short, 1)})
            runner.write_json(paths.state, {"jobs": jobs})
            listed = [j["id"] for j in lean_broker.broker_status(paths)["finished"]]
            self.assertEqual(listed, short[-19:] + [late])


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
    def test_comments_preserve_local_dependencies_and_cache_invalidation(self):
        headers = (
            "module\npublic import Basis\n",
            "module\n/- header -/ public import Basis\n",
            "module\n/- outer\n/- inner -/\nstill outer\n-/\npublic import Basis\n",
            "module\npublic /- interface -/ import Basis/- end -/\n",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            basis, target = root / "Basis.lean", root / "Target.lean"
            for header in headers:
                with self.subTest(header=header):
                    basis.write_text("module\npublic theorem basis : True := by trivial\n", encoding="utf-8")
                    target.write_text(header + "public theorem target : True := basis\n", encoding="utf-8")
                    modules = lean_broker.discover_modules(root, [target])
                    self.assertEqual([name for name, _ in modules], ["Basis", "Target"])
                    self.assertEqual(modules[-1][1]["local"], ["Basis"])
                    before = lean_broker.module_keys("fixture", modules)["Target"]
                    basis.write_text("module\npublic theorem basis : True := True.intro\n", encoding="utf-8")
                    after = lean_broker.module_keys("fixture", lean_broker.discover_modules(root, [target]))["Target"]
                    self.assertNotEqual(before, after)

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

    def test_module_header_import_modifiers_preserve_local_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("PublicDep", "MetaDep", "AllDep", "BothDep"):
                (root / (name + ".lean")).write_text("module\n", encoding="utf-8")
            target = root / "Target.lean"
            target.write_text("module\npublic import PublicDep\nmeta import MetaDep\n"
                              "import all AllDep\npublic meta import BothDep\n"
                              "theorem t : True := by trivial\nimport Late\n", encoding="utf-8")
            expected = ["AllDep", "BothDep", "MetaDep", "PublicDep"]
            self.assertEqual(lean_broker.read_imports(target), expected)
            modules = lean_broker.discover_modules(root, [target])
            self.assertEqual([name for name, _ in modules], expected + ["Target"])
            self.assertEqual(modules[-1][1]["local"], expected)
            self.assertEqual(modules[-1][1]["external"], [])


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.instance = Path(self.temp.name)
        self.base = {"max_sessions": 3, "cli": {"codex": "codex"},
                     "lean": {"command": ["lean"], "version_command": ["lean", "--version"], "cwd": None, "env": {}}}

    def load(self, **lean):
        runner.write_json(self.instance / "settings.json", {**self.base, "lean": {**self.base["lean"], **lean}})
        return runner.load_settings(self.instance)

    def test_defaults_fill_in_and_derive_from_the_host(self):
        settings = self.load()
        self.assertEqual({k: settings["lean"][k] for k in runtime_support.LEAN_DEFAULTS}, runtime_support.LEAN_DEFAULTS)
        with patch.object(runtime_support, "memory_status", return_value=(32 * 1024 ** 3, 8 * 1024 ** 3)), \
                patch.object(runner.os, "cpu_count", return_value=8):
            config = runtime_support.lean_config(settings)
        self.assertEqual(config["memory_budget_mb"], 32 * 1024 - 2048 - 512 * 3)
        self.assertEqual(config["cpu_threads_budget"], 16)
        self.assertEqual(config["derived"]["logical_cores"], 8)
        explicit = runtime_support.lean_config(self.load(memory_budget_mb=4096, cpu_threads_budget=3))
        self.assertEqual((explicit["memory_budget_mb"], explicit["cpu_threads_budget"]), (4096, 3))
        with patch.object(runtime_support, "memory_status", return_value=(1024 ** 3, 0)):
            self.assertEqual(runtime_support.lean_config(self.load())["memory_budget_mb"], 1024)

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

    def write_launch(self, broker):
        runner.write_json(self.job / "launch.json", {
            "argv": [sys.executable, "-B", str(FAKE), "--threads=1", str(self.lean)], "cwd": str(self.job),
            "env": {"FAKE_ENV": "1"}, "priority": "normal", "broker": broker})  # equal footing with the test machine's load

    def launch(self, broker):
        self.write_launch(broker)
        host = subprocess.Popen([sys.executable, "-B", str(lean_broker.SCRIPT), "_job", str(self.job)])
        self.addCleanup(self.stop_host, host)
        return host

    @staticmethod
    def stop_host(host):
        if host.poll() is None:
            lean_broker.terminate_tree(host.pid)
        host.wait(timeout=10)

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
            # `normal` leaves the niceness as inherited, so this shows only that the host did not change it.
            # The lowered priorities are not exercised: a below-normal stand-in starves behind normal-priority
            # research load on the test machine, which is why every fixture here runs at `normal`.
            self.assertIn(f"nice={lean_broker.NICE['normal']}", output)
        self.assertIn("WARN", (self.job / "stderr.log").read_text(encoding="utf-8"))

    def test_host_without_go_exits_on_cancel_or_dead_broker(self):
        host = self.launch(runner.process_identity(os.getpid()))
        (self.job / "CANCEL").touch()
        self.assertEqual(host.wait(timeout=10), 1)
        self.assertFalse((self.job / "exit.json").exists())
        (self.job / "CANCEL").unlink()
        host = self.launch({"pid": os.getpid(), "birth": "not this process"})
        self.assertEqual(host.wait(timeout=10), 1)

    def test_go_written_as_the_broker_dies_still_starts_lean(self):
        # The broker writes GO once this host's identity is durable and can die right after it, between the
        # host's look for GO and its look at the broker. The next broker adopts that job as started, so a host
        # that ended here without an exit.json would leave the job failed; it must run Lean instead.
        self.write_launch({"pid": os.getpid(), "birth": "a broker that has died"})
        def died_after_go(identity):
            (self.job / "GO").touch()
            return False
        with patch.object(lean_broker, "alive", side_effect=died_after_go):
            self.assertEqual(lean_broker.job_host(self.job), 0)
        self.assertEqual(runner.read_json(self.job / "exit.json")["exit_code"], 3)
        self.assertIn("MARK", (self.job / "stdout.log").read_text(encoding="utf-8"))


class BrokerTests(BrokerFixture):
    def test_edit_before_ingestion_keeps_submissions_distinct(self):
        self.start_broker()
        path = self.session_file("s1", marker="BEFORE-INGESTION")
        original_hash = lean_broker.hashlib.sha256(path.read_bytes()).hexdigest()
        first = self.submit(path)
        source(path, marker="AFTER-INGESTION")
        second = self.submit(path)
        self.broker.ingest()
        first_job = self.broker.state["jobs"][first]
        second_job = self.broker.state["jobs"][second]
        self.assertEqual(first_job["source_sha256"], original_hash)
        self.assertNotEqual(first_job["source_sha256"], second_job["source_sha256"])
        self.assertFalse((self.paths.job(second) / "result.json").exists())
        self.broker.launch(first_job)
        first_result = lean_broker.job_record(self.paths, first)
        self.assertEqual(first_result["status"], "failed")
        self.assertIn("source changed after submission", first_result["reason"])
        self.until(lambda: self.finished(second))
        self.assertEqual(lean_broker.job_record(self.paths, second)["exit_code"], 0)
        self.assertIn("AFTER-INGESTION", (self.paths.job(second) / "stdout.log").read_text(encoding="utf-8"))

    def test_ingestion_restart_preserves_registration_and_duplicate_outcomes(self):
        for kind in ("job", "build"):
            for boundary in ("registration", "duplicate"):
                with self.subTest(kind=kind, boundary=boundary):
                    self.start_broker()
                    root = self.instance / "sessions/s1/work" / f"{kind}-{boundary}"
                    target = source(root / "Target.lean", imports=(), marker=f"{kind}-{boundary}")
                    def enqueue():
                        return self.submit(target) if kind == "job" else self.build(root, [target])
                    original = enqueue()
                    identity = original
                    if boundary == "duplicate":
                        self.broker.ingest()
                        identity = enqueue()
                    request = self.paths.queue / (identity + ".json")
                    unlink = Path.unlink
                    def stop_before_ack(path, *args, **kwargs):
                        if path == request:
                            raise SystemExit("broker stopped before queue acknowledgement")
                        return unlink(path, *args, **kwargs)
                    with patch.object(Path, "unlink", stop_before_ack), self.assertRaises(SystemExit):
                        self.broker.ingest()
                    self.assertTrue(request.exists())
                    saved = runner.read_json(self.paths.state)
                    folder = self.paths.job(identity) if kind == "job" else self.paths.build(identity)
                    if boundary == "duplicate":
                        outcome = runner.read_json(folder / "result.json")
                        self.assertEqual(outcome["duplicate_of"], original)
                        # Replay must keep this receipt even when the content no
                        # longer matches the request to which it was redirected.
                        source(target, imports=(), marker=f"{kind}-{boundary}-edited")
                    self.start_broker()
                    self.broker.ingest()
                    self.assertFalse(request.exists())
                    self.assertEqual(self.broker.state["jobs"], saved["jobs"])
                    self.assertEqual(self.broker.state["builds"], saved["builds"])
                    if boundary == "duplicate":
                        self.assertEqual(lean_broker.job_record(self.paths, identity), outcome)
                    else:
                        self.assertFalse((folder / "result.json").exists())
                        self.assertEqual(lean_broker.job_record(self.paths, identity)["status"], "queued")
                        with patch.object(lean_broker, "ensure_broker", return_value={}), \
                                contextlib.redirect_stderr(io.StringIO()):
                            self.assertEqual(lean_broker.wait(self.paths, identity, timeout=0), 124)
                    self.until(lambda: lean_broker.job_record(self.paths, original)["status"] in lean_broker.FINISHED)
                    final = lean_broker.job_record(self.paths, original)
                    if boundary == "duplicate":
                        self.assertEqual(final["status"], "failed")
                        self.assertIn("source changed", final["reason"])
                    else:
                        self.assertEqual(final["status"], "finished")
                    out = io.StringIO()
                    with patch.object(lean_broker, "ensure_broker", return_value={}), \
                            contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                        self.assertEqual(lean_broker.wait(self.paths, identity, timeout=1),
                                         3 if boundary == "duplicate" else 0)
                    if boundary == "registration":
                        self.assertIn(f"{kind}-{boundary}", out.getvalue())

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
        # The entry names its environment as `status` does, so a session can tell it from one measured before a change.
        self.assertEqual((entry["environment_key"], entry["direct"]), (self.broker.state["environment_key"], False))
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
        def all_finished_serially():
            self.assertLessEqual(len(self.jobs("running")), 1)
            return all(self.finished(j) for j in jobs)
        self.until(all_finished_serially)

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
        # Establish the head's queue position before later submissions. Windows
        # can give several files the same timestamp; random request IDs then
        # legitimately decide their ingestion order within that tied batch.
        self.until(lambda: head in self.broker.state['jobs'])
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
        # broker.log records each start as the broker makes it, so its order is the order of admission.
        starts = [event["job"] for event in map(json.loads, self.paths.log.read_text(encoding="utf-8").splitlines())
                  if event["event"] == "started"]
        ahead = starts[:starts.index(head)] if head in starts else starts
        self.assertEqual(len(set(small) & set(ahead)), passes)
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
        state["sessions"]["s1"] = {"role": "attempt", "status": "running", "host": None, "cli": None}
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

    def test_every_status_of_an_ended_session_cancels_its_compiles(self):
        # The runner records a session whose CLI has ended as ended, publishing or integrated, or as failed;
        # under each status a compile has no reader. A running session with no CLI yet keeps its compile.
        self.start_broker()
        statuses = ("ended", "publishing", "integrated", "failed")
        state = runner.read_json(self.instance / "runner/state.json")
        for n, status in enumerate(statuses):
            state["sessions"][f"s{n}"] = {"role": "attempt", "status": status, "host": None, "cli": None}
        state["sessions"]["live"] = {"role": "attempt", "status": "running", "host": None, "cli": None}
        runner.write_json(self.instance / "runner/state.json", state)
        jobs = {status: self.submit(self.session_file(f"s{n}"), expect_mb=40, session=f"s{n}")
                for n, status in enumerate(statuses)}
        kept = self.submit(self.session_file("live"), expect_mb=40, session="live")
        with patch.object(lean_broker, "available_memory", return_value=0):  # the machine gate holds every start
            self.broker.tick()
        for status, job_id in jobs.items():
            with self.subTest(status=status):
                job = self.broker.state["jobs"][job_id]
                self.assertEqual(job["status"], "cancelled")
                self.assertIn(f"ended ({status})", job["reason"])
        self.assertEqual(self.broker.state["jobs"][kept]["status"], "queued")

    def test_job_of_a_dead_session_is_cancelled_but_a_live_one_is_kept(self):
        self.start_broker()
        gone = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"], capture_output=True, text=True)
        dead = {"pid": int(gone.stdout), "birth": "a process that has exited"}
        live = runner.process_identity(os.getpid())
        state = runner.read_json(self.instance / "runner/state.json")
        state["sessions"]["s1"] = {"role": "attempt", "status": "running", "host": dead, "cli": live}
        state["sessions"]["s2"] = {"role": "attempt", "status": "running", "host": dead, "cli": dead}
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

    def test_unrunnable_calibration_releases_its_waiting_job(self):
        # A Lean that cannot start gives no calibration verdict; the waiting compile must still reach its own outcome.
        self.write_settings(command=[str(self.root / "no-such-lean")])
        self.start_broker()
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        job = self.broker.state["jobs"][job_id]
        calibrations = [j for j in self.broker.state["jobs"].values() if j["kind"] == "calibration"]
        self.assertEqual([(j["status"], j["exit_code"]) for j in calibrations], [("failed", None)])
        self.assertIsNone(self.broker.calibration.entry(job["closure"]))  # nothing recorded: a later compile calibrates again
        self.assertEqual((job["status"], job["exit_code"]), ("failed", None))
        self.assertTrue(job["launch_error"])

    def test_crashed_calibration_is_not_a_verdict_on_its_imports(self):
        # Lean rejecting the imports is recorded for the closure. A calibration ended by a signal or by a
        # Windows crash code failed to execute, so the next compile with those imports calibrates again.
        self.start_broker()
        for code, verdict in ((1, True), (-9, False), (0xC0000005, False)):
            with self.subTest(code=code):
                job = self.broker.calibration_job(f"closure{code}", ["Mathlib.Data.Nat.Basic"])
                job.update(status="running", started_at=time.time())
                self.broker.finish(job, {"exit_code": code})
                self.assertEqual(job["status"], "finished")
                self.assertEqual(self.broker.calibration.known(job["closure"]), verdict)

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
        # Lean sleeps for 30 seconds: the job ends within 20 only if terminating the host reached its child.
        self.until(lambda: self.finished(job_id), limit=20)
        self.assertEqual(job["status"], "failed")
        self.assertIn("without recording an exit", job["reason"])
        self.assertFalse((self.paths.job(job_id) / "exit.json").exists())

    def test_exit_written_as_the_host_ends_is_not_lost(self):
        # The host writes exit.json and then ends. A broker that finds no exit.json and then no live host
        # may have looked between the two, so it must look for the exit once more before failing the job.
        self.start_broker()
        job_id = self.submit(self.session_file("s1", exit=5), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][job_id]["status"] == "running")
        job = self.broker.state["jobs"][job_id]
        exit_file = self.paths.job(job_id) / "exit.json"
        aside = exit_file.with_name("exit.aside")
        self.wait_gone(job["host"], limit=30)
        exit_file.replace(aside)  # the folder as the broker saw it just before the host wrote its exit
        def host_ended_meanwhile(identity):
            if identity == job["host"] and aside.exists():
                aside.replace(exit_file)
            return runner.alive(identity)
        with patch.object(lean_broker, "alive", side_effect=host_ended_meanwhile):
            self.broker.tick()
        self.assertEqual((job["status"], job["exit_code"]), ("finished", 5))

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
        self.assertEqual(lean_broker.cancel(self.paths, unread)["cancelled"], "requested")
        self.broker.tick()
        self.assertNotIn(unread, self.broker.state["jobs"])
        self.assertEqual(lean_broker.job_record(self.paths, unread)["status"], "cancelled")
        self.assertFalse((self.paths.job(unread) / "launch.json").exists())
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lean_broker.wait(self.paths, unread, timeout=0), 4)
        # A request the broker cannot accept is answered, not dropped.
        bad = "j" + "0" * 32
        runner.write_json(self.paths.queue / (bad + ".json"), {"id": bad, "source": 5, "expect_mb": 40})
        # Fields that reached the broker state unchecked would crash a later tick instead of this request.
        malformed = "j" + "2" * 32
        runner.write_json(self.paths.queue / (malformed + ".json"),
                          {"id": malformed, "source": str(self.session_file("s1", "malformed.lean")),
                           "expect_mb": 40, "session": ["s1"], "submitted_at": "now"})
        (self.paths.queue / "x..escape.json").write_text("{}", encoding="utf-8")
        if os.name != "nt":  # a POSIX file name can end in a newline, which a `$`-anchored match accepts
            (self.paths.queue / ("j" + "1" * 32 + "\n.json")).write_text("{}", encoding="utf-8")
        self.broker.tick()
        for job_id, field in ((bad, "source"), (malformed, "session")):
            self.assertEqual(lean_broker.job_record(self.paths, job_id)["status"], "failed")
            self.assertIn("rejected: " + field, lean_broker.job_record(self.paths, job_id)["reason"])
        self.assertNotIn(malformed, self.broker.state["jobs"])
        self.assertEqual(list(self.paths.queue.glob("*.json")), [])
        # Nothing under jobs/ was made for a name that is not a job ID.
        self.assertEqual([p.name for p in self.paths.jobs.iterdir() if not lean_broker.JOB_ID.fullmatch(p.name)], [])

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
        # A broker that starts on a rejected file exits at once; `status` must still say why.
        time.sleep(0.02)
        (self.instance / "settings.json").write_text("{not json", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "settings.json rejected"):
            lean_broker.Broker(self.instance, log_path=self.paths.log).start()
        self.assertTrue(lean_broker.broker_status(self.paths)["config_error"])

    def test_environment_change_fails_queued_jobs_and_calibrates_the_new_environment_anew(self):
        # An environment change reaches the broker through settings.json. A job queued under the earlier
        # identity must not start under the new one, a running compile is left alone, and the same file
        # submitted again is a job of the new environment with a calibration key of its own.
        self.write_settings(cpu_threads_budget=1)
        self.start_broker()
        before = self.broker.state["environment_key"]
        blocker = self.submit(self.session_file("s1", "block.lean", sleep=3), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][blocker]["status"] == "running")
        path = self.session_file("s1", "wait.lean", marker="NEW-EPOCH")
        waiting = self.submit(path, expect_mb=40)
        self.until(lambda: self.broker.state["jobs"].get(waiting, {}).get("status") == "queued")
        time.sleep(0.02)
        self.write_settings(cache_epoch="second")
        self.until(lambda: self.finished(waiting))
        stale = self.broker.state["jobs"][waiting]
        self.assertEqual((stale["status"], stale["exit_code"], stale["environment_key"]), ("failed", None, before))
        self.assertIn("environment changed", stale["reason"])
        self.assertFalse((self.paths.job(waiting) / "launch.json").exists())
        self.assertNotEqual(self.broker.state["environment_key"], before)
        self.assertEqual(lean_broker.broker_status(self.paths)["environment_key"], self.broker.state["environment_key"])
        again = self.submit(path, expect_mb=40)
        self.until(lambda: self.finished(again) and self.finished(blocker))
        fresh = self.broker.state["jobs"][again]
        self.assertEqual((fresh["status"], fresh["exit_code"], fresh["environment_key"]),
                         ("finished", 0, self.broker.state["environment_key"]))
        self.assertNotEqual(fresh["closure"], stale["closure"])
        self.assertEqual(self.broker.state["jobs"][blocker]["exit_code"], 0)
        calibrations = [j for j in self.broker.state["jobs"].values() if j["kind"] == "calibration"]
        self.assertEqual(sorted(j["closure"] for j in calibrations), sorted([stale["closure"], fresh["closure"]]))
        self.assertIn("NEW-EPOCH", (self.paths.job(again) / "stdout.log").read_text(encoding="utf-8"))

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

    def test_queued_compile_starts_with_the_threads_in_force(self):
        # A change of lean.threads reaches a compile that is still queued, as a change of priority does.
        self.start_broker()
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        with patch.object(lean_broker, "available_memory", return_value=0):  # the machine gate holds every start
            self.broker.tick()
            self.assertEqual(self.broker.state["jobs"][job_id]["status"], "queued")
            time.sleep(0.02)
            self.write_settings(threads=3)
            self.broker.tick()
            self.assertEqual(self.jobs("running"), [])
        self.until(lambda: self.finished(job_id))
        self.assertIn("--threads=3", runner.read_json(self.paths.job(job_id) / "launch.json")["argv"])

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
        state["complete"] = True
        state["sessions"]["s1"] = {"role": "attempt", "status": "integrated", "host": None, "cli": None}
        runner.write_json(self.instance / "runner/state.json", state)
        self.assertFalse(self.broker.should_exit())  # formal root alone does not finish pending follow-ups
        state['finished'] = True
        # The runner saves the sessions it starts in the middle of its tick and recomputes `finished`
        # at the end of it, so the broker can read `finished` beside a session that is still active.
        for status in ("starting", "running", "publishing"):
            with self.subTest(status=status):
                state["sessions"]["s1"]["status"] = status
                runner.write_json(self.instance / 'runner/state.json', state)
                self.assertFalse(self.broker.should_exit())
        state["sessions"]["s1"]["status"] = "integrated"
        runner.write_json(self.instance / 'runner/state.json', state)
        job_id = self.submit(self.session_file("s2", sleep=0.5), expect_mb=40, session="s2")
        self.broker.tick()
        self.assertFalse(self.broker.should_exit())
        self.until(lambda: self.finished(job_id))
        self.until(lambda: self.broker.should_exit())

    def test_a_replaced_broker_reports_no_version_until_it_has_read_its_own(self):
        # restart-broker returns once the new broker is alive, before that broker has run version_command.
        # A session asking for the version meanwhile must keep waiting, not receive the predecessor's.
        self.start_broker()
        state = runner.read_json(self.paths.state)
        state.update(version="Lean (version 3.9.9-replaced)", version_error=None)
        runner.write_json(self.paths.state, state)
        asked = []
        read_version = lean_broker.Broker.read_version
        def ask_before_reading(broker):
            with patch.object(lean_broker, "ensure_broker", return_value={}), \
                    patch.object(lean_broker, "READY_SECONDS", 0.5), \
                    self.assertRaisesRegex(RuntimeError, "not reported a version"):
                lean_broker.version(self.paths)
            asked.append(broker)
            read_version(broker)
        with patch.object(lean_broker.Broker, "read_version", ask_before_reading):
            self.start_broker()
        self.assertEqual(asked, [self.broker])
        with patch.object(lean_broker, "ensure_broker", return_value={}):
            self.assertIn("4.0.0-fake", lean_broker.version(self.paths)["version"])


class BuildTests(BrokerFixture):
    def test_cancellation_survives_ingestion_and_cached_completion(self):
        self.start_broker()
        cases = (("build", "before_ingest"), ("job", "after_read"),
                 ("build", "after_read"), ("job", "after_expansion"),
                 ("build", "after_expansion"), ("build", "during_restore"))
        cancelled = []
        for number, (kind, timing) in enumerate(cases):
            with self.subTest(kind=kind, timing=timing):
                root = self.instance / "sessions/s1/work" / str(number)
                target = source(root / "Target.lean", imports=())
                if timing == "during_restore":
                    warm = self.build(root, [target])
                    self.until(lambda: self.build_record(warm)["status"] in lean_broker.FINISHED)
                    self.assertEqual(self.build_record(warm)["status"], "finished")
                    self.assertEqual(self.build_record(warm)["modules"]["Target"]["exit_code"], 0)
                previous = set(self.broker.state["jobs"])
                identity = self.submit(target) if kind == "job" else self.build(root, [target])
                request = self.paths.queue / (identity + ".json")
                responses = []
                original_read = lean_broker.read_json
                original_new = self.broker.new_job
                original_restore = self.broker.restore_module

                def read_then_cancel(path, *args, **kwargs):
                    value = original_read(path, *args, **kwargs)
                    if Path(path) == request and not responses:
                        responses.append(lean_broker.cancel(self.paths, identity))
                    return value

                def expand_then_cancel(*args, **kwargs):
                    value = original_new(*args, **kwargs)
                    if not responses:
                        responses.append(lean_broker.cancel(self.paths, identity))
                    return value

                def restore_then_cancel(*args, **kwargs):
                    value = original_restore(*args, **kwargs)
                    if not responses:
                        self.assertTrue(value)
                        responses.append(lean_broker.cancel(self.paths, identity))
                    return value

                if timing == "before_ingest":
                    responses.append(lean_broker.cancel(self.paths, identity))
                    self.broker.ingest()
                elif timing == "after_read":
                    with patch.object(lean_broker, "read_json", side_effect=read_then_cancel):
                        self.broker.ingest()
                elif timing == "after_expansion":
                    with patch.object(self.broker, "new_job", side_effect=expand_then_cancel):
                        self.broker.ingest()
                else:
                    with patch.object(self.broker, "restore_module", side_effect=restore_then_cancel):
                        self.broker.ingest()
                    self.assertEqual(self.build_record(identity)["modules"]["Target"]["status"], "cached")
                    self.assertEqual(set(self.broker.state["jobs"]), previous)
                self.assertEqual(len(responses), 1)
                self.assertEqual(responses[0]["cancelled"], "requested")
                self.broker.tick()
                self.assertEqual(lean_broker.job_record(self.paths, identity)["status"], "cancelled")
                for jid in set(self.broker.state["jobs"]) - previous:
                    job = self.broker.state["jobs"][jid]
                    if job["kind"] == "compile":
                        self.assertEqual(job["status"], "cancelled")
                        self.assertFalse((self.paths.job(jid) / "launch.json").exists())
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(lean_broker.wait(self.paths, identity, timeout=0), 4)
                cancelled.append(identity)
        self.start_broker()
        for identity in cancelled:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(lean_broker.wait(self.paths, identity, timeout=0), 4)
        completed = lean_broker.job_record(self.paths, warm)
        self.assertEqual(lean_broker.cancel(self.paths, warm)["status"], "finished")
        self.broker.tick()
        self.assertEqual(lean_broker.job_record(self.paths, warm), completed)

    def test_cancelling_duplicate_ids_reaches_original_work(self):
        self.start_broker()
        for kind in ("job", "build"):
            with self.subTest(kind=kind):
                root = self.instance / "sessions/s1/work" / kind
                target = source(root / "Target.lean", imports=())
                original = self.submit(target) if kind == "job" else self.build(root, [target])
                self.broker.ingest()
                duplicate = self.submit(target) if kind == "job" else self.build(root, [target])
                self.broker.ingest()
                self.assertEqual(lean_broker.job_record(self.paths, duplicate)["duplicate_of"], original)
                self.assertEqual(lean_broker.cancel(self.paths, duplicate)["cancelled"], "requested")
                self.broker.tick()
                self.assertEqual(lean_broker.job_record(self.paths, original)["status"], "cancelled")
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(lean_broker.wait(self.paths, duplicate, timeout=0), 4)

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
        self.assertEqual(b["closure"], lean_broker.closure_key(self.broker.state['version'] + '\n' + self.broker.state['environment_key'], []))
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

    def test_fresh_review_target_recompiles_while_unchanged_dependency_is_cached(self):
        self.start_broker()
        root = self.instance / 'sessions/sreview/work/lean'
        source(root / 'Basis.lean', imports=())
        source(root / 'Target.lean', imports=('Basis',), marker='REVIEW-TARGET')
        warm = self.build(root, [root / 'Target.lean'], session='sauthor')
        self.until(lambda: self.build_record(warm)['status'] in lean_broker.FINISHED)
        self.assertEqual(self.build_record(warm)['status'], 'finished')
        self.assertTrue(all(m['exit_code'] == 0 for m in self.build_record(warm)['modules'].values()))
        original_files = {}
        for name, module in self.build_record(warm)['modules'].items():
            olean = Path(module['olean'])
            original_files[name] = {p.name: p.read_bytes()
                                    for p in olean.parent.glob(olean.stem + '.*')}
            self.assertEqual(set(original_files[name]),
                             {name + suffix for suffix in
                              ('.olean', '.olean.server', '.olean.private', '.ir')})

        cached = self.build(root, [root / 'Target.lean'], session='sauthor')
        self.until(lambda: self.build_record(cached)['status'] in lean_broker.FINISHED)
        self.assertTrue(all(m['status'] == 'cached' and m['job'] is None
                            for m in self.build_record(cached)['modules'].values()))
        for name, module in self.build_record(cached)['modules'].items():
            olean = Path(module['olean'])
            self.assertEqual({p.name: p.read_bytes()
                              for p in olean.parent.glob(olean.stem + '.*')},
                             original_files[name])
        with patch.object(lean_broker, 'ensure_broker', return_value={}):
            fresh = lean_broker.build(self.paths, root, [root / 'Target.lean'], 60,
                                      'sreview', fresh_targets=True)['build']
        self.until(lambda: self.build_record(fresh)['status'] in lean_broker.FINISHED)
        result = lean_broker.job_record(self.paths, fresh)
        self.assertEqual((result['status'], result['session']), ('finished', 'sreview'))
        basis, target = result['modules']['Basis'], result['modules']['Target']
        self.assertEqual((basis['status'], basis['job']), ('cached', None))
        restored = Path(basis['olean'])
        self.assertEqual({p.name: p.read_bytes()
                          for p in restored.parent.glob(restored.stem + '.*')},
                         original_files['Basis'])
        self.assertEqual((target['status'], target['exit_code']), ('finished', 0))
        self.assertIsNotNone(target['job'])
        compiled = lean_broker.job_record(self.paths, target['job'])
        self.assertEqual(compiled['session'], 'sreview')
        self.assertEqual(compiled['source_sha256'],
                         self.build_record(warm)['modules']['Target']['source_sha256'])
        self.assertIn('REVIEW-TARGET',
                      (self.paths.job(target['job']) / 'stdout.log').read_text(encoding='utf-8'))

        # An entry whose manifest was never published (its caching was cut short) and an entry missing an artifact are cache misses.
        for missing in ('.artifacts.json', '.olean.server'):
            with self.subTest(missing=missing):
                (self.paths.cache / (basis['key'] + missing)).unlink()
                with patch.object(lean_broker, 'ensure_broker', return_value={}):
                    rebuilt = lean_broker.build(self.paths, root, [root / 'Target.lean'], 60,
                                                'sreview', fresh_targets=True)['build']
                self.until(lambda: self.build_record(rebuilt)['status'] in lean_broker.FINISHED)
                rebuilt_record = self.build_record(rebuilt)
                self.assertEqual(rebuilt_record['status'], 'finished', rebuilt_record)
                self.assertTrue(all(m['status'] == 'finished' and m['exit_code'] == 0
                                    and m['job'] for m in rebuilt_record['modules'].values()))
                for name, module in rebuilt_record['modules'].items():
                    olean = Path(module['olean'])
                    self.assertEqual({p.name: p.read_bytes()
                                      for p in olean.parent.glob(olean.stem + '.*')},
                                     original_files[name])

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

    def test_target_compile_failure_reaches_build_wait_with_its_output_and_exit(self):
        self.start_broker()
        root = self.instance / 'sessions/s1/work/lean'
        target = source(root / 'Target.lean', imports=(), exit=1,
                        marker='TARGET-FAILED', stderr='TARGET-DIAGNOSTIC')
        build_id = self.build(root, [target])
        self.until(lambda: self.build_record(build_id)['status'] in lean_broker.FINISHED)
        result = lean_broker.job_record(self.paths, build_id)
        self.assertEqual(result['modules']['Target']['exit_code'], 1)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lean_broker.wait(self.paths, build_id)
        self.assertEqual(code, 1)
        self.assertIn('TARGET-FAILED', out.getvalue())
        self.assertIn('TARGET-DIAGNOSTIC', err.getvalue())
        summary = json.loads(err.getvalue().strip().splitlines()[-1].split('lean-broker: ', 1)[1])
        self.assertEqual(summary['exit_code'], 1)
        self.assertEqual([(m['module'], m['exit_code']) for m in summary['modules']],
                         [('Target', 1)])
        self.assertFalse(list(self.paths.cache.glob('*.olean')))

    def test_build_rejects_bad_targets_cycles_and_shadowing(self):
        self.start_broker()
        root = self.tree()
        with self.assertRaisesRegex(ValueError, "not in the subpath|not a module path"):
            self.build(root, [self.instance / "root.md"])
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

    def test_cancelling_a_build_stops_its_queue(self):
        self.start_broker()
        root = self.tree(A={"sleep": 30})
        build_id = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(build_id)["modules"]["A"]["status"] == "running")
        lean_broker.cancel(self.paths, build_id)
        # A sleeps for 30 seconds: the build ends within 20 only if the cancellation terminated A's Lean.
        self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED, limit=20)
        record = self.build_record(build_id)
        self.assertEqual(record["status"], "cancelled")
        self.assertEqual(record["modules"]["A"]["status"], "cancelled")
        self.assertTrue(all(m["status"] in ("cancelled", "failed") for m in record["modules"].values()))
        self.assertFalse(runner.alive(self.module_job(build_id, "A").get("lean")))

    def test_single_file_submission_is_not_a_duplicate_of_a_module_compile(self):
        self.start_broker()
        root = self.tree(A={"sleep": 3})
        build_id = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(build_id)["modules"]["A"]["status"] == "running")
        job_id = self.submit(root / "A.lean")
        self.broker.ingest()
        # Registered as a job of its own, not redirected to A's module compile.
        self.assertIn(job_id, self.broker.state["jobs"])
        self.assertFalse((self.paths.job(job_id) / "result.json").exists())
        self.until(lambda: self.finished(job_id))
        self.assertEqual(self.broker.state["jobs"][job_id]["exit_code"], 0)
        self.assertNotIn("-R", runner.read_json(self.paths.job(job_id) / "launch.json")["argv"])
        self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)

    def test_a_pruned_build_loses_its_lib_folder_and_keeps_its_result(self):
        # Pruning is the one place the broker deletes a folder. It takes the lib folder of the build it
        # prunes from the state and nothing else, and that build's outcome stays readable from its result.json.
        self.start_broker()
        def build_once(name):
            root = self.instance / "sessions/s1/work" / name
            build_id = self.build(root, [source(root / "Target.lean", imports=(), marker=name)])
            self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
            return build_id
        with patch.object(lean_broker, "KEEP_FINISHED", 1):
            first = build_once("first")
            first_lib = Path(self.build_record(first)["lib"])
            self.assertTrue((first_lib / "Target.olean").is_file())
            second = build_once("second")
        self.assertNotIn(first, self.broker.state["builds"])
        self.assertFalse(first_lib.exists())
        self.assertTrue((Path(self.build_record(second)["lib"]) / "Target.olean").is_file())
        self.assertEqual(lean_broker.job_record(self.paths, first)["status"], "finished")

    def test_pruning_keeps_a_finished_module_that_a_queued_module_still_imports(self):
        # A queued module learns that its imports compiled only from their records in the state. With room
        # for one finished job, B and C both finish before D starts; pruning either would fail D as unknown.
        self.start_broker()
        root = self.tree()
        with patch.object(lean_broker, "KEEP_FINISHED", 1):
            build_id = self.build(root, [root / "D.lean"])
            self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        record = self.build_record(build_id)
        self.assertEqual(record["status"], "finished", record)
        self.assertTrue(all(m["status"] == "finished" and m["exit_code"] == 0 for m in record["modules"].values()))
        self.assertEqual([j.get("module") for j in self.jobs(*lean_broker.FINISHED)], ["D"])  # pruning did run


class LauncherTests(BrokerFixture):
    LAKE = [sys.executable, "-B", str(FAKE.with_name("fake_lake.py")), "env"]

    def test_bare_executable_is_resolved_before_direct_launch(self):
        executable = Path(sys.executable)
        self.write_settings(command=self.LAKE + [executable.name, "-B", str(FAKE)],
                            env={"PATH": str(executable.parent)})
        self.start_broker()
        self.assertTrue(self.broker.state["launcher"]["direct"])
        resolved = self.broker.direct["argv"][0]
        self.assertTrue(Path(resolved).is_absolute())
        self.assertTrue(Path(resolved).samefile(executable))
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        self.assertEqual(self.broker.state["jobs"][job_id]["exit_code"], 0)

    def test_unresolved_executable_keeps_lake_fallback(self):
        self.write_settings(command=self.LAKE + ["do-math-missing-executable"])
        self.start_broker()
        self.assertFalse(self.broker.state["launcher"]["direct"])
        self.assertIn("cannot resolve executable", self.broker.state["launcher"]["reason"])
        self.assertIsNone(self.broker.direct)

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
        self.assertEqual(job["closure"], lean_broker.closure_key(self.broker.state['version'] + '\n' + self.broker.state['environment_key'], job["imports"], True))
        self.assertNotEqual(job["closure"], lean_broker.closure_key(self.broker.state['version'] + '\n' + self.broker.state['environment_key'], job["imports"]))
        self.assertTrue(self.broker.calibration.entry(job["closure"])["direct"])  # and the table says so in words
        self.assertTrue(lean_broker.broker_status(self.paths)["launcher"]["direct"])  # status names the mode in use

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

    def test_a_queued_job_is_keyed_by_the_launch_mode_it_starts_in(self):
        # An unrelated settings edit asks lake again, and its answer can switch the launch mode without
        # changing the environment key. A compile and its calibration queued in one mode and started in
        # the other must be measured and recorded under the key of the mode they ran in.
        self.write_settings(command=self.LAKE + [sys.executable, "-B", str(FAKE)])
        self.start_broker()
        self.assertTrue(self.broker.state["launcher"]["direct"])
        environment = self.broker.state["environment_key"]
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        with patch.object(lean_broker, "available_memory", return_value=0):  # the machine gate holds every start
            self.broker.tick()
            queued = self.broker.state["jobs"][job_id]["closure"]
            time.sleep(0.02)
            self.write_settings(memory_budget_mb=self.budget + 1)
            with patch.dict(os.environ, {"FAKE_LAKE_FAIL": "1"}):  # lake now fails to load its workspace
                self.broker.tick()
        self.assertFalse(self.broker.state["launcher"]["direct"])
        self.assertEqual(self.broker.state["environment_key"], environment)
        self.until(lambda: self.finished(job_id))
        job = self.broker.state["jobs"][job_id]
        through_lake = lean_broker.closure_key(self.broker.environment_identity(), job["imports"])
        self.assertNotEqual(queued, through_lake)
        self.assertEqual(job["closure"], through_lake)
        launch = runner.read_json(self.paths.job(job_id) / "launch.json")
        self.assertEqual(launch["argv"][:len(self.LAKE)], self.LAKE)
        calibrations = [j for j in self.broker.state["jobs"].values() if j["kind"] == "calibration"]
        self.assertEqual([(j["closure"], j["direct"]) for j in calibrations], [(through_lake, False)])
        self.assertEqual(self.broker.calibration.entry(through_lake)["excess_mb"], [job["measured"]["excess_mb"]])
        self.assertIsNone(self.broker.calibration.entry(queued))

    def test_a_module_build_in_direct_mode_finds_its_own_modules_and_lakes_library(self):
        # Review builds with `lake env lean` configured, so its module compiles run lean directly. Each one
        # must search the build's lib folder for the modules built before it, which the fake lean checks,
        # and then lake's LEAN_PATH for the library, which only the launch file shows here.
        self.write_settings(command=self.LAKE + [sys.executable, "-B", str(FAKE)])
        self.start_broker()
        self.assertTrue(self.broker.state["launcher"]["direct"])
        root = self.instance / "sessions/s1/work/lean"
        source(root / "Basis.lean", imports=())
        target = source(root / "Target.lean", imports=("Basis", "Mathlib.Data.Nat.Basic"))
        build_id = self.build(root, [target])
        self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        record = self.build_record(build_id)
        self.assertEqual(record["status"], "finished", record)
        self.assertTrue(all(m["exit_code"] == 0 for m in record["modules"].values()), record)
        launch = runner.read_json(self.paths.job(record["modules"]["Target"]["job"]) / "launch.json")
        self.assertEqual(launch["argv"][:3], [sys.executable, "-B", str(FAKE)])  # lean itself, no lake in front
        self.assertEqual(launch["env"]["LEAN_PATH"].split(os.pathsep)[:2], [record["lib"], "fake-lake-lib"])


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
        # The job ID comes first, before any waiting, so a session whose shell tool gave up can still wait on it.
        receipt = json.loads(result.stderr.splitlines()[0].split("lean-broker: ", 1)[1])
        self.assertEqual((receipt["job"], receipt["session"]), (summary["job"], "s1"))
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

    @unittest.skipUnless(os.name == "nt", "only Windows reports exit codes as unsigned 32-bit values")
    def test_run_relays_a_windows_crash_code_unchanged(self):
        # The stand-in exits with -1073741819, which Windows reports as 0xC0000005, the code of a
        # crashed process; the client must exit with that code and end on its summary line.
        path = self.session_file("s1", exit=-1073741819)
        result = self.cli("run", str(self.instance), str(path), "--session", "s1", "--expect-mb", "40")
        self.assertEqual(result.returncode, 0xC0000005, result.stderr)
        summary = json.loads(result.stderr.strip().splitlines()[-1].split("lean-broker: ", 1)[1])
        self.assertEqual((summary["status"], summary["exit_code"]), ("finished", 0xC0000005))

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
        self.assertIn("invalid job ID", unknown.stderr)

    def test_serve_for_a_deleted_instance_creates_nothing(self):
        gone = self.root / "deleted instance"
        result = self.cli("serve", str(gone), timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a do-math instance", result.stderr)
        self.assertFalse(gone.exists())

    def test_second_broker_yields_to_the_lock(self):
        self.assertEqual(self.cli("version", str(self.instance)).returncode, 0)  # launches the first broker
        first = lean_broker.broker_alive(self.paths)
        self.assertTrue(first)
        second = self.cli("serve", str(self.instance), timeout=30)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("already has a running Lean broker", second.stderr)
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

    def test_unstarted_job_is_requeued_unless_its_cancellation_was_requested(self):
        self.start_broker()
        self.broker.config["cpu_threads_budget"] = 1
        blocker = self.submit(self.session_file("s1", "block.lean", sleep=3), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][blocker]["status"] == "running")
        job_id = self.submit(self.session_file("s1", marker="REQUEUED"), expect_mb=40)
        dropped = self.submit(self.session_file("s1", "dropped.lean"), expect_mb=40)
        self.until(lambda: all(self.broker.state["jobs"].get(j, {}).get("status") == "queued"
                               for j in (job_id, dropped)))
        # Simulate a broker that died after recording each host but before GO.
        with patch.object(lean_broker.Path, "write_bytes", side_effect=RuntimeError("died before GO")):
            for unstarted in (job_id, dropped):
                with self.assertRaises(RuntimeError):
                    self.broker.launch(self.broker.state["jobs"][unstarted])
        job = self.broker.state["jobs"][job_id]
        self.assertEqual(job["status"], "running")
        self.assertFalse((self.paths.job(job_id) / "GO").exists())
        self.broker.save()
        # A session cancels one of them while no broker serves it; the next broker must honour that request.
        self.assertEqual(lean_broker.cancel(self.paths, dropped)["cancelled"], "requested")
        old_hosts = self.broker.hosts
        self.broker = lean_broker.Broker(self.instance, log_path=self.paths.log)
        self.broker.start()
        for host in old_hosts.values():
            host.wait(timeout=10)
        self.assertEqual(self.broker.state["jobs"][job_id]["status"], "queued")
        self.assertEqual(self.broker.state["jobs"][blocker]["status"], "running")
        cancelled = self.broker.state["jobs"][dropped]
        self.assertEqual((cancelled["status"], cancelled["started_at"]), ("cancelled", None))
        self.assertFalse((self.paths.job(dropped) / "launch.json").exists())
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lean_broker.wait(self.paths, dropped, timeout=0), 4)
        self.until(lambda: self.finished(job_id) and self.finished(blocker))
        self.assertEqual(self.broker.state["jobs"][job_id]["exit_code"], 0)
        self.assertIn("REQUEUED", (self.paths.job(job_id) / "stdout.log").read_text(encoding="utf-8"))
        self.assertEqual(sum(j["kind"] == "compile" for j in self.broker.state["jobs"].values()), 3)

    def test_runner_launches_adopts_and_relaunches_the_broker(self):
        skill = runner.SKILL
        engine = runner.Runner(self.instance, skill)
        engine.ensure_broker()  # a broker is kept alive whether or not a session exists yet
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
        engine.ensure_broker()  # within ten seconds of the last launch (runner.ensure_broker): no relaunch yet
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
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(lean_broker.main(["result", str(self.instance), build_id]), 0)
        record = json.loads(out.getvalue())
        self.assertEqual((record["id"], record["status"]), (build_id, "finished"))
        # status lists builds finished within the last ten minutes; the first build is long recorded in the state.
        listed = {b["id"]: b["status"] for b in lean_broker.broker_status(self.paths)["builds"]}
        self.assertEqual(listed.get(summary["build"]), "finished")


if __name__ == "__main__":
    unittest.main()

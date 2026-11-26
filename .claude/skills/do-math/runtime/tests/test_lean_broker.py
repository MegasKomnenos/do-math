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

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import lean_broker
import runtime_support
from settings import load_settings
from broker_fixture import FAKE, BrokerFixture, source


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
                    runtime_support.write_json(folder / "result.json", result)
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
            runtime_support.write_json(paths.state, {"jobs": jobs})
            listed = [j["id"] for j in lean_broker.broker_status(paths)["finished"]]
            self.assertEqual(listed, short[-19:] + [late])


class ProcessTreeTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "only Windows keeps the PID of a parent that has ended in its children")
    def test_a_process_created_before_its_recorded_parent_is_not_followed(self):
        # Windows keeps the PID of a parent that has ended in its children and gives that PID to a later process.
        # A cancellation terminates a compile's whole tree, so a process that only carries the compile's PID as
        # its parent, and was created before the compile, must stay out of the tree, with everything below it.
        parents = {20: 10, 30: 10, 40: 20, 50: 30, 60: 10}  # process -> the parent it records
        births = {10: 100, 20: 150, 30: 50, 40: 160, 50: 170}  # 30 is older than 10; 60 cannot be opened
        with patch.object(lean_broker, "_windows_processes", return_value=list(parents.items())), \
                patch.object(lean_broker, "_windows_birth", side_effect=births.get):
            self.assertEqual(lean_broker.process_tree(10), [10, 20, 40])

    @unittest.skipIf(os.name == "nt", "the process files of Linux")
    def test_a_process_whose_name_is_not_text_does_not_stop_the_listing(self):
        # /proc/<pid>/stat holds the name a process gave itself: up to 15 bytes that need not be UTF-8 and may hold a
        # closing parenthesis. The broker reads that file for every process of the machine.
        stats = {"10": b"10 (lean) S 1 10 10", "20": b"20 (\xff\xfe) S 10 10 10", "30": b"30 (a) b) S 20 10 10"}

        class Entry:
            def __init__(self, name):
                self.name, self.path = name, "/proc/" + name

        with patch.object(lean_broker.os, "scandir", return_value=[Entry(name) for name in stats]), \
                patch.object(Path, "read_bytes", lambda path: stats[path.parent.name]):
            self.assertEqual(lean_broker.process_tree(10), [10, 20, 30])


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
        # A larger confidence widens the pooled margin until the same four no longer fit; with no
        # spread to pool, the rule is a plain sum.
        self.assertFalse(lean_broker.admission(rows, rows[0], 3600, 20)[0])
        self.assertEqual(lean_broker.admission([(100, 0, 0)], (200, 0, 0), 300, 1.3), (True, 300))


class ImportClosureTests(unittest.TestCase):
    def test_comments_preserve_local_dependencies(self):
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
                    # Whatever is in `needs` reaches the key of Target (test_a_key_follows...): a
                    # dependency hidden by a comment would leave Target cached over a changed Basis.
                    self.assertEqual((modules[-1][1]["local"], modules[-1][1]["needs"]), (["Basis"], ["Basis"]))
                    self.assertEqual([module["reads"] for _, module in modules], ["public", "public"])

    def test_a_key_follows_the_source_and_the_output_of_every_module_the_compile_reads(self):
        key = lean_broker.module_key
        base = key("environment", "Target", "source", [("Basis", "one"), ("Middle", "two")])
        self.assertEqual(base, key("environment", "Target", "source", [("Basis", "one"), ("Middle", "two")]))
        for changed in (key("other", "Target", "source", [("Basis", "one"), ("Middle", "two")]),
                        key("environment", "Other", "source", [("Basis", "one"), ("Middle", "two")]),
                        key("environment", "Target", "edited", [("Basis", "one"), ("Middle", "two")]),
                        key("environment", "Target", "source", [("Basis", "changed"), ("Middle", "two")]),
                        key("environment", "Target", "source", [("Middle", "two")])):
            self.assertNotEqual(base, changed)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Basis.lean").write_text("module\n", encoding="utf-8")
            (root / "Middle.lean").write_text("module\npublic import Basis\n", encoding="utf-8")
            texts = {"Module": "module\npublic import Middle\n", "Plain": "import Middle\n",
                     "Prying": "module\nimport all Middle\n", "Commented": "-- first\n/- then -/ module\nimport Middle\n"}
            for name, text in texts.items():
                (root / (name + ".lean")).write_text(text, encoding="utf-8")
            modules = dict(lean_broker.discover_modules(root, [root / (name + ".lean") for name in texts]))
            # A module is keyed by the modules it reaches through others as well, in dependency order.
            self.assertTrue(all(modules[name]["needs"] == ["Basis", "Middle"] for name in texts))
            self.assertEqual(modules["Middle"]["needs"], ["Basis"])
            # A `module` file reads public output; a plain file and an `import all` read the private data too.
            self.assertEqual({name: modules[name]["reads"] for name in texts},
                             {"Module": "public", "Plain": "full", "Prying": "full", "Commented": "public"})
            self.assertEqual(modules["Plain"]["source_sha256"],
                             lean_broker.hashlib.sha256((root / "Plain.lean").read_bytes()).hexdigest())

    def test_output_identities_tell_public_files_from_the_rest(self):
        with tempfile.TemporaryDirectory() as directory:
            lib = Path(directory)
            def emit(olean, private, sibling="other"):
                for suffix, text in ((".olean", olean), (".ir", "ir"), (".olean.private", private), (".olean.server", "s")):
                    (lib / ("Foo" + suffix)).write_text(text, encoding="utf-8")
                (lib / "Foobar.olean").write_text(sibling, encoding="utf-8")  # another module's file
                files = lean_broker.emitted_files(lib / "Foo.olean")
                self.assertEqual([suffix for suffix, _ in files], [".ir", ".olean", ".olean.private", ".olean.server"])
                return lean_broker.output_identities(files)
            first = emit("statement", "proof")
            self.assertEqual(first, emit("statement", "proof", sibling="changed"))
            proof = emit("statement", "another proof")
            self.assertEqual((proof["public"] == first["public"], proof["full"] == first["full"]), (True, False))
            statement = emit("another statement", "proof")
            self.assertNotEqual(statement["public"], first["public"])
            self.assertNotEqual(statement["full"], first["full"])

    def test_the_header_gives_its_imports_whether_it_is_a_module_and_whether_it_imports_all(self):
        header = lean_broker.read_header
        text = b"-- leading\nmodule\n\npublic import A.One -- why\nimport all B.Two\r\n\r\ntheorem t : True := trivial\n"
        self.assertEqual(header(text), {"imports": ["A.One", "B.Two"], "module": True, "all": True})
        # A byte order mark hides neither the first import nor the first token.
        self.assertEqual(header(b"\xef\xbb\xbfimport A\n\n\ntheorem t : True := trivial\n"),
                         {"imports": ["A"], "module": False, "all": False})
        self.assertTrue(header(b"\xef\xbb\xbfmodule\nimport A\n")["module"])
        # `module` inside a comment, or after the header, does not make a file a module.
        self.assertEqual(header(b"/- module -/\nimport A\ndef module := 1\n"),
                         {"imports": ["A"], "module": False, "all": False})
        self.assertEqual(header(b"-- note\n\ntheorem t : True := trivial\n"),
                         {"imports": [], "module": False, "all": False})

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
        runtime_support.write_json(self.instance / "settings.json", {**self.base, "lean": {**self.base["lean"], **lean}})
        return load_settings(self.instance)

    def test_defaults_fill_in_and_derive_from_the_host(self):
        settings = self.load()
        self.assertEqual({k: settings["lean"][k] for k in runtime_support.LEAN_DEFAULTS}, runtime_support.LEAN_DEFAULTS)
        with patch.object(runtime_support, "memory_status", return_value=(32 * 1024 ** 3, 8 * 1024 ** 3)), \
                patch.object(runtime_support.os, "cpu_count", return_value=8):
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
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, next(iter(bad))):
                self.load(**bad)


class JobHostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.job = Path(self.temp.name) / "job"
        self.job.mkdir()
        self.lean = source(Path(self.temp.name) / "A.lean", marker="MARK", stderr="WARN", exit=3)

    def write_launch(self, broker, priority="normal"):  # `normal`: equal footing with the test machine's load
        runtime_support.write_json(self.job / "launch.json", {
            "argv": [sys.executable, "-B", str(FAKE), "--threads=1", str(self.lean)], "cwd": str(self.job),
            "env": {"FAKE_ENV": "1"}, "priority": priority, "broker": broker})

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
        host = self.launch(runtime_support.process_identity(os.getpid()))
        time.sleep(0.5)
        self.assertIsNone(host.poll())
        self.assertFalse((self.job / "process.json").exists())
        (self.job / "GO").touch()
        self.assertEqual(host.wait(timeout=30), 0)
        receipt = runtime_support.read_json(self.job / "process.json")
        # The identity recorded is the Lean process's own, not the host's; that process has ended by now.
        self.assertEqual(receipt["process"]["pid"], receipt["pid"])
        self.assertNotEqual(receipt["pid"], host.pid)
        self.assertFalse(runtime_support.alive(receipt["process"]))
        self.assertEqual(runtime_support.read_json(self.job / "exit.json")["exit_code"], 3)
        output = (self.job / "stdout.log").read_text(encoding="utf-8")
        self.assertIn("MARK", output)
        self.assertIn("threads=1", output)
        self.assertIn("FAKE_ENV=1", output)  # lean.env overrides reach the Lean process
        if hasattr(os, "nice"):
            # `normal` leaves the niceness as inherited, so this shows only that the host did not change it.
            # No stand-in is run at a lowered priority: a below-normal one starves behind normal-priority research
            # load on the test machine, which is why every fixture here runs at `normal`. What the host asks of the
            # system for a lowered priority is read in test_the_host_starts_lean_at_the_priority_its_launch_file_names.
            self.assertIn(f"nice={os.nice(0)}", output)
        self.assertIn("WARN", (self.job / "stderr.log").read_text(encoding="utf-8"))

    def test_host_without_go_exits_on_cancel_or_dead_broker(self):
        host = self.launch(runtime_support.process_identity(os.getpid()))
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
        with patch.object(runtime_support, "alive", side_effect=died_after_go):
            self.assertEqual(lean_broker.job_host(self.job), 0)
        self.assertEqual(runtime_support.read_json(self.job / "exit.json")["exit_code"], 3)
        self.assertIn("MARK", (self.job / "stdout.log").read_text(encoding="utf-8"))

    def test_a_host_that_ends_on_a_defect_of_the_program_leaves_a_traceback(self):
        # A job host is detached, and its output, kept in host.log, is all that says why it ended. A launch file
        # without the broker's identity ends the host; the name of the missing key alone would not say where.
        self.write_launch(runtime_support.process_identity(os.getpid()))
        launch = runtime_support.read_json(self.job / "launch.json")
        del launch["broker"]
        runtime_support.write_json(self.job / "launch.json", launch)
        host = subprocess.run([sys.executable, "-B", str(lean_broker.SCRIPT), "_job", str(self.job)],
                              capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(host.returncode, 1)
        self.assertIn("Traceback", host.stderr)
        self.assertIn("KeyError: 'broker'", host.stderr)
        self.assertFalse((self.job / "exit.json").exists())

    def test_the_host_starts_lean_at_the_priority_its_launch_file_names(self):
        # lean.priority is below_normal unless an instance sets another, and every fixture here runs at `normal`. A
        # stand-in started at a lowered priority starves behind the test machine's load, so none is started here: this
        # process answers the call that would start Lean, and what the host asked of the system is read from it.
        lowered = {"below_normal": ("BELOW_NORMAL_PRIORITY_CLASS", 10), "idle": ("IDLE_PRIORITY_CLASS", 19)}
        (self.job / "GO").touch()

        class Started:
            pid = os.getpid()

            def wait(self):
                return 0

        for priority, (priority_class, niceness) in lowered.items():
            with self.subTest(priority=priority):
                self.write_launch(runtime_support.process_identity(os.getpid()), priority)
                asked = {}

                def start(argv, **options):
                    asked.update(options)
                    return Started()

                with patch.object(lean_broker.subprocess, "Popen", side_effect=start):
                    self.assertEqual(lean_broker.job_host(self.job), 0)
                if os.name == "nt":
                    every = (subprocess.NORMAL_PRIORITY_CLASS | subprocess.BELOW_NORMAL_PRIORITY_CLASS
                             | subprocess.IDLE_PRIORITY_CLASS)
                    self.assertEqual(asked["creationflags"] & every, getattr(subprocess, priority_class))
                else:
                    with patch.object(lean_broker.os, "nice") as nice:
                        asked["preexec_fn"]()  # what the host has the new process run before it becomes Lean
                    nice.assert_called_once_with(niceness)
                self.assertEqual(runtime_support.read_json(self.job / "exit.json")["exit_code"], 0)


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
        # A request leaves the queue once a client can find it elsewhere: at once when it is answered
        # with a result, and otherwise when a state that holds it has been written. The broker is
        # stopped at each point at which a request is still in the queue; the next broker must lose
        # nothing, register nothing twice, and keep an answer that was given.
        #   unwritten: the request is registered, and no state that holds it has been written
        #   written:   that state has been written, and the request has not left the queue
        #   duplicate: the request has been answered as a duplicate, and has not left the queue
        for kind in ("job", "build"):
            for boundary in ("unwritten", "written", "duplicate"):
                with self.subTest(kind=kind, boundary=boundary), patch.object(lean_broker, "STATE_SECONDS", 3600):
                    self.start_broker()
                    root = self.instance / "sessions/s1/work" / f"{kind}-{boundary}"
                    target = source(root / "Target.lean", imports=(), marker=f"{kind}-{boundary}")
                    def enqueue():
                        return self.submit(target) if kind == "job" else self.build(root, [target])
                    original = enqueue()
                    identity = original
                    if boundary == "duplicate":
                        self.broker.ingest()
                        self.broker.save(now=True)  # the request it will be redirected to is registered and written
                        identity = enqueue()
                    request = self.paths.queue / (identity + ".json")
                    unlink = Path.unlink
                    def stop_before_ack(path, *args, **kwargs):
                        if path == request:
                            raise SystemExit("broker stopped before queue acknowledgement")
                        return unlink(path, *args, **kwargs)
                    if boundary == "unwritten":
                        self.broker.ingest()
                        self.broker.save()  # within the interval: nothing is written, and the request stays
                    else:
                        with patch.object(Path, "unlink", stop_before_ack), self.assertRaises(SystemExit):
                            self.broker.ingest()
                            self.broker.save(now=True)
                    self.assertTrue(request.exists())
                    saved = self.on_disk()
                    kept = "jobs" if kind == "job" else "builds"
                    folder = self.paths.job(identity) if kind == "job" else self.paths.build(identity)
                    self.assertEqual(identity in saved[kept], boundary == "written")
                    self.assertEqual(original in saved[kept], boundary != "unwritten")
                    if boundary == "duplicate":
                        outcome = runtime_support.read_json(folder / "result.json")
                        self.assertEqual(outcome["duplicate_of"], original)
                        # Replay must keep this receipt even when the content no
                        # longer matches the request to which it was redirected.
                        source(target, imports=(), marker=f"{kind}-{boundary}-edited")
                    if boundary == "unwritten":
                        # What a client sees of a job that only the stopped broker knew: it is not unknown.
                        self.assertEqual(lean_broker.job_record(self.paths, identity),
                                         {"id": identity, "status": "submitted"})
                    self.start_broker()
                    self.broker.ingest()
                    if boundary == "unwritten":
                        # Registered again from the request, which stays until this broker has written it.
                        self.assertTrue(request.exists())
                        self.assertEqual(self.broker.state[kept][identity]["status"], "queued")
                        self.assertFalse((folder / "result.json").exists())
                        self.assertEqual(lean_broker.job_record(self.paths, identity)["status"], "submitted")
                        self.broker.save(now=True)
                    else:
                        self.assertEqual(self.broker.state["jobs"], saved["jobs"])
                        self.assertEqual(self.broker.state["builds"], saved["builds"])
                    self.assertFalse(request.exists())
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
                    if boundary != "duplicate":
                        self.assertIn(f"{kind}-{boundary}", out.getvalue())

    def test_a_request_registered_while_its_record_is_read_is_not_unknown(self):
        # The broker writes a state that holds a request and then removes the request from the queue. A
        # client that read the state just before that write and looks at the queue just after the removal
        # must still find the job; `wait` would otherwise end with "unknown job" for a job that is queued.
        self.start_broker()
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        original_read = lean_broker.read_json
        registered = []
        def register_after_the_read(path, *args, **kwargs):
            value = original_read(path, *args, **kwargs)
            if Path(path) == self.paths.state and not registered:
                registered.append(job_id)
                self.broker.ingest()
                self.broker.save(now=True)
            return value
        with patch.object(lean_broker, "read_json", side_effect=register_after_the_read):
            record = lean_broker.job_record(self.paths, job_id)
        self.assertEqual(registered, [job_id])
        self.assertFalse((self.paths.queue / (job_id + ".json")).exists())
        self.assertEqual(record, {"id": job_id, "status": "submitted"})
        self.assertEqual(lean_broker.job_record(self.paths, job_id)["status"], "queued")

    def test_a_request_whose_removal_is_refused_keeps_its_answer_and_leaves_at_the_next_poll(self):
        # On Windows a file that another process has open can refuse removal for a moment. A request that
        # was answered with a result then stays in the queue until the next poll. The refusal is no fault
        # of the request, so the answer stands and the broker goes on.
        self.start_broker()
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        lean_broker.cancel(self.paths, job_id)  # before registration: the request is answered with a result
        request = self.paths.queue / (job_id + ".json")
        unlink = Path.unlink
        def refused(path, *args, **kwargs):
            if path == request:
                raise PermissionError("the file is in use by another process")
            return unlink(path, *args, **kwargs)
        with patch.object(Path, "unlink", refused):
            self.broker.ingest()
        self.assertTrue(request.exists())
        self.assertEqual(lean_broker.job_record(self.paths, job_id)["status"], "cancelled")
        self.broker.ingest()
        self.assertFalse(request.exists())
        self.assertEqual(lean_broker.job_record(self.paths, job_id)["status"], "cancelled")
        self.assertNotIn(job_id, self.broker.state["jobs"])

    def test_a_request_the_broker_cannot_take_is_answered_as_failed_and_leaves_the_queue(self):
        # A request is a file that a client wrote into the queue. One that lacks what a request holds, or
        # whose name is no job ID, must not end the broker: where it names a job it is answered with a
        # failed result that says why, and it leaves the queue either way.
        self.start_broker()
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        request = self.paths.queue / (job_id + ".json")
        content = runtime_support.read_json(request)
        del content["expect_mb"]
        runtime_support.write_json(request, content)
        runtime_support.write_json(self.paths.queue / "not-a-job.json", content)
        self.broker.ingest()
        self.assertEqual(list(self.paths.queue.glob("*.json")), [])
        self.assertNotIn(job_id, self.broker.state["jobs"])
        record = lean_broker.job_record(self.paths, job_id)
        self.assertEqual(record["status"], "failed")
        self.assertIn("request rejected", record["reason"])
        self.assertIn("expect_mb", record["reason"])
        self.assertEqual([p.name for p in self.paths.jobs.iterdir()], [job_id])  # no folder for a name that is no job ID
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(lean_broker.wait(self.paths, job_id, timeout=0), 3)
        self.assertIn("request rejected", err.getvalue())

    def test_first_closure_is_calibrated_then_the_job_runs_and_is_measured(self):
        self.write_settings(calibration_expect_mb=300, threads=2)
        self.start_broker()
        path = self.session_file("s1", alloc_mb=200, marker="OUT-A", sleep=1)
        job_id = self.submit(path, expect_mb=260)
        self.until(lambda: self.jobs("running"))
        running = self.jobs("running")
        self.assertEqual([j["kind"] for j in running], ["calibration"])
        # The calibration compile is reserved at calibration_expect_mb and with one thread, whatever lean.threads is.
        self.assertEqual((running[0]["expect_mb"], running[0]["reserve"]["certain_mb"], running[0]["threads"]), (300, 300, 1))
        self.assertEqual(self.broker.state["jobs"][job_id]["waiting_for"], running[0]["id"])
        self.until(lambda: self.finished(job_id))
        job = self.broker.state["jobs"][job_id]
        entry = runtime_support.read_json(self.paths.calibration)["entries"][job["closure"]]
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
        self.assertEqual(runtime_support.read_json(self.paths.job(job_id) / "result.json")["status"], "finished")
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

    def test_a_closure_reserves_with_its_measured_spread_once_two_excesses_differ(self):
        # The memory rule takes the spread the broker has observed for a closure's excess (reference/lean-broker.md);
        # default_spread stands in until two excesses are recorded and while they do not differ.
        self.start_broker()
        calibration, default = self.broker.calibration, self.broker.config["default_spread"]
        calibration.record_baseline("closure", {"imports": []}, 400, 1)
        job = {"kind": "compile", "closure": "closure", "expect_mb": 1000, "status": "queued", "measured": None}
        def reserves_with(spread):
            for reserved, expected in zip(self.broker.reserve(job), lean_broker.reservation(1000, 400, spread)):
                self.assertAlmostEqual(reserved, expected)
        reserves_with(default)
        calibration.record_job("closure", 100, 1)
        reserves_with(default)
        calibration.record_job("closure", 100, 1)
        reserves_with(default)
        calibration.record_job("closure", 200, 1)
        reserves_with(2 ** 0.5 / 4)  # excesses 100, 100 and 200: a deviation of 47.1 over a mean of 133.3

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
        argv = runtime_support.read_json(self.paths.job(jobs[0]) / "launch.json")["argv"]
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
        self.assertEqual(runtime_support.read_json(self.paths.job(second) / "result.json")["duplicate_of"], first)
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
        state = runtime_support.read_json(self.instance / "runner/state.json")
        state["sessions"]["s1"] = {"role": "attempt", "status": "running", "host": None, "cli": None}
        runtime_support.write_json(self.instance / "runner/state.json", state)
        job_id = self.submit(self.session_file("s1", sleep=30), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][job_id]["status"] == "running" and self.broker.state["jobs"][job_id].get("pid"))
        pid = self.broker.state["jobs"][job_id]["pid"]
        lean = self.broker.state["jobs"][job_id]["lean"]
        self.assertTrue(runtime_support.alive(lean))
        state["sessions"]["s1"]["status"] = "integrated"
        runtime_support.write_json(self.instance / "runner/state.json", state)
        self.until(lambda: self.finished(job_id), limit=20)
        job = self.broker.state["jobs"][job_id]
        self.assertEqual(job["status"], "cancelled")
        self.assertIn("ended", job["reason"])
        self.assertFalse(runtime_support.alive(lean))
        self.assertNotIn(pid, [p for p in lean_broker.process_tree(os.getpid())])
        # A cancelled job leaves no sample in the closure history.
        entry = self.broker.calibration.entry(job["closure"])
        self.assertEqual(entry["excess_mb"], [])

    def test_every_status_of_an_ended_session_cancels_its_compiles(self):
        # The runner records a session whose CLI has ended as ended, publishing or integrated, or as failed;
        # under each status a compile has no reader. A running session with no CLI yet keeps its compile.
        self.start_broker()
        statuses = ("ended", "publishing", "integrated", "failed")
        state = runtime_support.read_json(self.instance / "runner/state.json")
        for n, status in enumerate(statuses):
            state["sessions"][f"s{n}"] = {"role": "attempt", "status": status, "host": None, "cli": None}
        state["sessions"]["live"] = {"role": "attempt", "status": "running", "host": None, "cli": None}
        runtime_support.write_json(self.instance / "runner/state.json", state)
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
        live = runtime_support.process_identity(os.getpid())
        state = runtime_support.read_json(self.instance / "runner/state.json")
        state["sessions"]["s1"] = {"role": "attempt", "status": "running", "host": dead, "cli": live}
        state["sessions"]["s2"] = {"role": "attempt", "status": "running", "host": dead, "cli": dead}
        runtime_support.write_json(self.instance / "runner/state.json", state)
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
            return runtime_support.alive(identity)
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

    def test_settings_reload_live_and_keep_the_last_good_configuration(self):
        self.start_broker()
        self.assertEqual(self.broker.config["memory_budget_mb"], self.budget)
        time.sleep(0.02)
        self.write_settings(memory_budget_mb=1234)
        self.broker.tick()
        self.assertEqual(self.broker.config["memory_budget_mb"], 1234)
        self.assertEqual(self.status()["config"]["memory_budget_mb"], 1234)
        time.sleep(0.02)
        (self.instance / "settings.json").write_text("{not json", encoding="utf-8")
        with patch.object(self.broker, "log") as log:
            self.broker.tick()
        self.assertEqual(self.broker.config["memory_budget_mb"], 1234)
        self.assertTrue(self.status()["config_error"])
        self.assertEqual(log.call_args.kwargs["event"], "settings_rejected")
        time.sleep(0.02)
        self.write_settings(memory_budget_mb=99)
        self.broker.tick()
        self.assertEqual(self.broker.config["memory_budget_mb"], 99)
        self.assertIsNone(self.status()["config_error"])
        # A broker that starts on a rejected file exits at once; `status` must still say why.
        time.sleep(0.02)
        (self.instance / "settings.json").write_text("{not json", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "settings.json rejected"):
            lean_broker.Broker(self.instance, log_path=self.paths.log).start()
        self.assertTrue(lean_broker.broker_status(self.paths)["config_error"])
        # A file that is missing when the broker starts is a rejection with its own reason, too.
        (self.instance / "settings.json").unlink()
        with self.assertRaisesRegex(ValueError, r"settings.json rejected: .*settings\.json"):
            lean_broker.Broker(self.instance, log_path=self.paths.log).start()
        self.assertIn("settings.json", lean_broker.broker_status(self.paths)["config_error"])

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
        self.assertEqual(self.status()["environment_key"], self.broker.state["environment_key"])
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

    def test_machine_gate_counts_what_running_compiles_have_still_to_take(self):
        # Free memory shows what a running compile has taken so far. One started a tick ago is still
        # loading its imports, so the gate counts the rest of its certain part as taken already.
        self.start_broker()
        self.broker.config.update(memory_budget_mb=100000, min_free_memory_mb=100)
        self.broker.calibration.record_baseline("closure", {"imports": []}, 400, 1)
        def job(status, current_mb=None):
            return {"kind": "compile", "closure": "closure", "expect_mb": 400, "threads": 1, "status": status,
                    "measured": None if current_mb is None else {"current_mb": current_mb}}
        candidate = job("queued")
        # 550 MiB free leaves 150 after the candidate's 400, above the gate's 100.
        self.assertTrue(self.broker.fits(candidate, [job("running", current_mb=400)], 550))
        # A running compile that has taken 50 of its 400 still owes 350 of them.
        self.assertFalse(self.broker.fits(candidate, [job("running", current_mb=50)], 550))
        self.assertTrue(self.broker.fits(candidate, [job("running", current_mb=50)], 900))

    def test_the_margin_for_the_pooled_spread_is_the_configured_confidence(self):
        # reference/lean-broker.md: `confidence` multiplies the pooled spread in the memory rule. Two compiles of
        # one closure, each with 100 MiB certain, 121.9 expected above it and a spread of 60.9, come to 555.8 MiB
        # at a confidence of 1.3 and to 616.2 MiB at 2.
        self.start_broker()
        self.broker.config.update(memory_budget_mb=580, default_spread=0.5)
        self.broker.calibration.record_baseline("closure", {"imports": []}, 100, 1)
        def job(status):
            return {"kind": "compile", "closure": "closure", "expect_mb": 300, "threads": 1, "status": status,
                    "measured": {"current_mb": 100} if status == "running" else None}
        self.broker.config["confidence"] = 1.3
        self.assertTrue(self.broker.fits(job("queued"), [job("running")], 100000))
        self.broker.config["confidence"] = 2
        self.assertFalse(self.broker.fits(job("queued"), [job("running")], 100000))

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
        self.assertIn("--threads=3", runtime_support.read_json(self.paths.job(job_id) / "launch.json")["argv"])

    def test_a_compile_runs_in_lean_cwd_or_else_in_the_folder_of_its_session(self):
        # What reference/lean.md tells a session of the working directory: lean.cwd from the settings, or the
        # session's folder when that is null. With a library configured, lean.cwd is the project in which
        # `lake env lean` has to run, and the broker's own calibration compile, which has no session, runs there too.
        self.start_broker()
        first = self.compiled(self.session_file("s1"))
        launch = runtime_support.read_json(self.paths.job(first["id"]) / "launch.json")
        self.assertEqual(launch["cwd"], str(self.paths.instance / "sessions" / "s1"))
        project = self.root / "project"
        project.mkdir()
        time.sleep(0.02)
        self.write_settings(cwd=str(project))
        second = self.compiled(self.session_file("s1", "B.lean"))
        configured = [j for j in self.broker.state["jobs"].values() if j["environment_key"] == second["environment_key"]]
        self.assertEqual(sorted(j["kind"] for j in configured), ["calibration", "compile"])
        for job in configured:
            self.assertEqual(runtime_support.read_json(self.paths.job(job["id"]) / "launch.json")["cwd"], str(project))

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
        state = runtime_support.read_json(self.instance / "runner/state.json")
        state["complete"] = True
        state["sessions"]["s1"] = {"role": "attempt", "status": "integrated", "host": None, "cli": None}
        runtime_support.write_json(self.instance / "runner/state.json", state)
        self.assertFalse(self.broker.should_exit())  # formal root alone does not finish pending follow-ups
        state['finished'] = True
        # The runner saves the sessions it starts in the middle of its tick and recomputes `finished`
        # at the end of it, so the broker can read `finished` beside a session that is still active.
        for status in ("starting", "running", "publishing"):
            with self.subTest(status=status):
                state["sessions"]["s1"]["status"] = status
                runtime_support.write_json(self.instance / 'runner/state.json', state)
                self.assertFalse(self.broker.should_exit())
        state["sessions"]["s1"]["status"] = "integrated"
        runtime_support.write_json(self.instance / 'runner/state.json', state)
        job_id = self.submit(self.session_file("s2", sleep=0.5), expect_mb=40, session="s2")
        self.broker.tick()
        self.assertFalse(self.broker.should_exit())
        self.until(lambda: self.finished(job_id))
        self.until(lambda: self.broker.should_exit())

    def test_a_replaced_broker_reports_no_version_until_it_has_read_its_own(self):
        # restart-broker returns once the new broker is alive, before that broker has run version_command.
        # A session asking for the version meanwhile must keep waiting, not receive the predecessor's.
        self.start_broker()
        state = runtime_support.read_json(self.paths.state)
        state.update(version="Lean (version 3.9.9-replaced)", version_error=None)
        runtime_support.write_json(self.paths.state, state)
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

    def test_a_version_command_that_fails_is_reported_rather_than_waited_for(self):
        # A Lean whose version cannot be read leaves nothing to wait for: `version` answers with the error,
        # and `status` reports it beside the missing version.
        self.write_settings(version_command=[str(self.root / "no-such-lean"), "--version"])
        self.start_broker()
        with patch.object(lean_broker, "ensure_broker", return_value={}), \
                patch.object(lean_broker, "READY_SECONDS", 0.5):
            reported = lean_broker.version(self.paths)
        self.assertIsNone(reported["version"])
        self.assertTrue(reported["error"])
        status = lean_broker.broker_status(self.paths)
        self.assertEqual((status["version"], status["version_error"]), (None, reported["error"]))


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

    def test_resubmission_after_a_cancellation_is_new_work(self):
        # A session that cancels running work and submits the same bytes again asks for that work anew.
        # Redirected to the work whose cancellation it requested, the new ID would end cancelled as well.
        self.start_broker()
        for kind in ("job", "build"):
            with self.subTest(kind=kind):
                root = self.instance / "sessions/s1/work" / f"resubmitted-{kind}"
                target = source(root / "Target.lean", imports=(), sleep=30)
                def enqueue():
                    return self.submit(target) if kind == "job" else self.build(root, [target])
                original = enqueue()
                self.until(lambda: lean_broker.job_record(self.paths, original)["status"] == "running")
                lean_broker.cancel(self.paths, original)
                again = enqueue()
                self.broker.tick()  # takes up the cancellation, then reads the new request
                self.assertIn(lean_broker.job_record(self.paths, again)["status"], lean_broker.ACTIVE)
                lean_broker.cancel(self.paths, again)
                # Each Lean sleeps for 30 seconds: both end within 20 only if each cancellation reached its own work.
                self.until(lambda: all(lean_broker.job_record(self.paths, i)["status"] in lean_broker.FINISHED
                                       for i in (original, again)), limit=20)
                self.assertEqual([lean_broker.job_record(self.paths, i)["status"] for i in (original, again)],
                                 ["cancelled", "cancelled"])

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
        self.assertIn("-R", runtime_support.read_json(self.paths.job(d["id"]) / "launch.json")["argv"])
        self.assertTrue((Path(record["lib"]) / "D.olean").is_file())
        self.assertEqual(len(list(self.paths.cache.glob("*.olean"))), 4)
        # External imports alone key the calibration: B's closure is the empty one, not "A".
        self.assertEqual(b["closure"], lean_broker.closure_key(self.broker.environment_identity(), []))
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
        # A change in B reaches D, a plain file that reads all of B's output; A and C stay cached.
        with (root / "B.lean").open("a", encoding="utf-8") as stream:
            stream.write("-- changed\n")
        third = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(third)["status"] in lean_broker.FINISHED)
        statuses = {n: m["status"] for n, m in self.build_record(third)["modules"].items()}
        self.assertEqual(statuses, {"A": "cached", "B": "finished", "C": "cached", "D": "finished"})
        self.assertEqual(len(list(self.paths.cache.glob("*.olean"))), 6)
        # The environment identity is part of every module key. After a change of cache_epoch, which the
        # operator makes when the libraries change in place, no module compiled before it is reused.
        time.sleep(0.02)
        self.write_settings(cache_epoch="second")
        fourth = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(fourth)["status"] in lean_broker.FINISHED)
        modules = self.build_record(fourth)["modules"]
        self.assertEqual({n: (m["status"], m["exit_code"]) for n, m in modules.items()},
                         {n: ("finished", 0) for n in "ABCD"})

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

    def need_hard_links(self):
        probe = self.root / "probe"
        probe.write_bytes(b"")
        try:
            os.link(probe, self.root / "probe-link")
        except OSError:
            self.skipTest("the file system of the temporary folder makes no hard links")

    def emitted(self, record):
        """(the lib's file, the cache's file) for each emitted file of each module of a build."""
        pairs = []
        for module in record["modules"].values():
            olean = Path(module["olean"])
            for suffix in (".olean", ".olean.private", ".olean.server", ".ir"):
                pairs.append((olean.with_name(olean.stem + suffix), self.paths.cache / (module["key"] + suffix)))
        return pairs

    def test_a_cached_module_is_linked_into_the_lib_and_copied_where_no_link_can_be_made(self):
        # A build's lib names the cache's own file for each module it takes from the cache, so the lib
        # holds no second copy of that module. Where the file system makes no link, the file is copied.
        self.need_hard_links()
        self.start_broker()
        root = self.tree()
        warm = self.built(root, [root / "D.lean"])
        self.assertEqual(warm["status"], "finished", warm)
        linked = self.built(root, [root / "D.lean"])
        self.assertTrue(all(m["status"] == "cached" for m in linked["modules"].values()))
        for in_lib, in_cache in self.emitted(linked):
            self.assertTrue(os.path.samefile(in_lib, in_cache), in_lib)
        with patch.object(lean_broker.os, "link", side_effect=OSError("no link can be made")):
            copied = self.built(root, [root / "D.lean"])
        self.assertTrue(all(m["status"] == "cached" for m in copied["modules"].values()))
        for in_lib, in_cache in self.emitted(copied):
            self.assertFalse(os.path.samefile(in_lib, in_cache), in_lib)
            self.assertEqual(in_lib.read_bytes(), in_cache.read_bytes())

    def test_a_restore_cut_short_takes_back_its_files_and_the_module_is_compiled(self):
        self.start_broker()
        root = self.instance / "sessions/s1/work/lean"
        target = source(root / "Target.lean", imports=())
        warm = self.built(root, [target])
        self.assertEqual(warm["status"], "finished", warm)
        key = warm["modules"]["Target"]["key"]
        cached = {p.name: p.read_bytes() for p in self.paths.cache.glob(key + ".*")}
        original, placed = lean_broker.link_or_copy, []

        def fail_on_the_third(source_file, target_file):
            if len(placed) == 2:
                raise OSError("the third file could not be placed")
            original(source_file, target_file)
            placed.append(Path(target_file))

        # The restore alone: the two files placed before the failure are gone again.
        olean = self.root / "a lib" / "Target.olean"
        with patch.object(lean_broker, "link_or_copy", side_effect=fail_on_the_third):
            with self.assertRaises(OSError):
                self.broker.restore_module(key, olean)
        self.assertEqual(len(placed), 2)
        self.assertEqual(list(olean.parent.iterdir()), [])
        # In a build: the module is compiled instead, and the cache's entry is as it was.
        placed.clear()
        with patch.object(lean_broker, "link_or_copy", side_effect=fail_on_the_third):
            rebuilt = self.built(root, [target])
        module = rebuilt["modules"]["Target"]
        self.assertEqual((rebuilt["status"], module["status"], module["exit_code"]), ("finished", "finished", 0))
        self.assertIsNotNone(module["job"])
        self.assertEqual({p.name: p.read_bytes() for p in self.paths.cache.glob(key + ".*")}, cached)
        for in_lib, in_cache in self.emitted(rebuilt):
            self.assertFalse(os.path.samefile(in_lib, in_cache), in_lib)

    def test_a_compile_does_not_write_into_a_file_left_at_its_output(self):
        # Lean writes into the file that stands at its output path. A file left there can be a link to
        # the cache's file, and a compile must leave the cache's entry as it was.
        self.need_hard_links()
        self.start_broker()
        root = self.instance / "sessions/s1/work/lean"
        target = source(root / "Target.lean", imports=(), marker="FIRST")
        warm = self.built(root, [target])
        self.assertEqual(warm["status"], "finished", warm)
        key = warm["modules"]["Target"]["key"]
        cached = {p.name: p.read_bytes() for p in self.paths.cache.glob(key + ".*")}
        source(root / "Target.lean", imports=(), marker="SECOND")
        build_id = self.build(root, [target])
        self.broker.ingest()  # the build is registered and its compile queued; no Lean has started
        module = self.build_record(build_id)["modules"]["Target"]
        self.assertNotEqual(module["key"], key)
        olean = Path(module["olean"])
        olean.parent.mkdir(parents=True, exist_ok=True)
        for suffix in (".olean", ".olean.private", ".olean.server", ".ir"):
            os.link(self.paths.cache / (key + suffix), olean.with_name(olean.stem + suffix))
        self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        module = self.build_record(build_id)["modules"]["Target"]
        self.assertEqual((module["status"], module["exit_code"]), ("finished", 0))
        self.assertEqual({p.name: p.read_bytes() for p in self.paths.cache.glob(key + ".*")}, cached)
        self.assertFalse(os.path.samefile(olean, self.paths.cache / (key + ".olean")))
        self.assertIn("SECOND", olean.with_name("Target.olean.private").read_text(encoding="utf-8"))

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

    def test_a_module_that_exits_with_code_0_and_wrote_no_olean_fails_and_is_not_cached(self):
        # An exit code of 0 counts as a compiled module only together with the .olean that the modules
        # above it read. Kept in the cache without it, the module would be an entry with no files, and
        # every later build with the same key would take nothing from it and report the module as cached.
        self.start_broker()
        root = self.instance / "sessions/s1/work/lean"
        record = self.built(root, [source(root / "Target.lean", imports=(), emit=0)])
        module = record["modules"]["Target"]
        self.assertEqual((record["status"], module["status"], module["exit_code"]), ("failed", "failed", 0))
        self.assertIn("wrote no .olean", module["reason"])
        self.assertIn("module Target failed", record["reason"])
        self.assertEqual(list(self.paths.cache.iterdir()), [])

    def test_build_rejects_bad_targets_cycles_and_shadowing(self):
        self.start_broker()
        root = self.tree()
        with self.assertRaisesRegex(ValueError, "not in the subpath|not a module path"):
            self.build(root, [self.instance / "settings.json"])  # a file that exists, outside the root
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
        # A module of yours under a toolchain root is refused even when no library import shares that root.
        source(root / "Std" / "Extra.lean", imports=())
        source(root / "UsesStd.lean", imports=("Std.Extra",))
        toolchain = self.build(root, [root / "UsesStd.lean"])
        self.until(lambda: self.build_record(toolchain)["status"] in lean_broker.FINISHED)
        self.assertIn("shadow the toolchain", self.build_record(toolchain)["reason"])
        # An import with no file under the root is read as the library's; the reason also names a missing file.
        source(root / "Notes" / "Main.lean", imports=("Notes.Lemma",))
        missing = self.build(root, [root / "Notes" / "Main.lean"])
        self.until(lambda: self.build_record(missing)["status"] in lean_broker.FINISHED)
        self.assertIn("Notes.Lemma", self.build_record(missing)["reason"])
        self.assertIn("file is missing", self.build_record(missing)["reason"])
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
        self.assertFalse(runtime_support.alive(self.module_job(build_id, "A").get("lean")))

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
        self.assertNotIn("-R", runtime_support.read_json(self.paths.job(job_id) / "launch.json")["argv"])
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

    def test_pruning_finished_jobs_leaves_a_waiting_module_what_it_needs(self):
        # A waiting module learns that its imports compiled, and what they emitted, from the build's own
        # record. With room for one finished job, the jobs of A, B and C are pruned before D is keyed.
        self.start_broker()
        root = self.tree()
        with patch.object(lean_broker, "KEEP_FINISHED", 1):
            build_id = self.build(root, [root / "D.lean"])
            self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        record = self.build_record(build_id)
        self.assertEqual(record["status"], "finished", record)
        self.assertTrue(all(m["status"] == "finished" and m["exit_code"] == 0 for m in record["modules"].values()))
        self.assertEqual([j.get("module") for j in self.jobs(*lean_broker.FINISHED)], ["D"])  # pruning did run


class OutputKeyTests(BrokerFixture):
    """A module's cache key follows the compiled output of the modules its compile reads, not their sources."""

    def library(self, **basis):
        """Basis is a `module`; Uses is a module that imports it; Top is a module that imports Uses alone;
        Plain is a plain file that imports Basis; Prying is a module that imports all of Basis."""
        root = self.instance / "sessions/s1/work/lean"
        source(root / "Basis.lean", imports=(), module=True, **{"proof": "first", **basis})
        source(root / "Uses.lean", imports=("Basis",), module=True, marker="USES-OUTPUT")
        source(root / "Top.lean", imports=("Uses",), module=True)
        source(root / "Plain.lean", imports=("Basis",))
        source(root / "Prying.lean", imports=("all Basis",), module=True)
        return root, [root / f"{name}.lean" for name in ("Top", "Plain", "Prying")]

    @staticmethod
    def statuses(record):
        return {name: module["status"] for name, module in record["modules"].items()}

    def test_a_replaced_proof_recompiles_only_what_reads_proofs(self):
        self.start_broker()
        root, targets = self.library()
        first = self.built(root, targets)
        self.assertEqual(first["status"], "finished", first)
        self.assertEqual(self.statuses(first), dict.fromkeys(("Basis", "Uses", "Top", "Plain", "Prying"), "finished"))
        # The proof in Basis is replaced. Its public files are the same bytes, so the modules that read
        # only those keep their keys and come from the cache; the plain file and the `import all` do not.
        root, targets = self.library(proof="second")
        second = self.built(root, targets)
        self.assertEqual(second["status"], "finished", second)
        self.assertEqual(self.statuses(second), {"Basis": "finished", "Uses": "cached", "Top": "cached",
                                                 "Plain": "finished", "Prying": "finished"})
        before, after = first["modules"], second["modules"]
        self.assertEqual(after["Basis"]["public"], before["Basis"]["public"])
        self.assertNotEqual(after["Basis"]["full"], before["Basis"]["full"])
        self.assertNotEqual(after["Basis"]["key"], before["Basis"]["key"])
        for name in ("Uses", "Top"):
            self.assertEqual(after[name]["key"], before[name]["key"])
            self.assertEqual((after[name]["job"], after[name]["exit_code"]), (None, 0))
            self.assertEqual((after[name]["public"], after[name]["full"]), (before[name]["public"], before[name]["full"]))
        for name in ("Plain", "Prying"):
            self.assertNotEqual(after[name]["key"], before[name]["key"])
        jobs_before = len(self.broker.state["jobs"])
        # A cached target reports its key and replays what its compile printed, from the cache entry
        # under that key; its files are in the build's lib folder.
        third = self.built(root, [root / "Uses.lean"])
        self.assertEqual(self.statuses(third), {"Basis": "cached", "Uses": "cached"})
        self.assertEqual(len(self.broker.state["jobs"]), jobs_before)
        self.assertEqual(third["modules"]["Uses"]["key"], before["Uses"]["key"])
        self.assertIn("USES-OUTPUT", (self.paths.cache / (third["modules"]["Uses"]["key"] + ".stdout.log"))
                      .read_text(encoding="utf-8"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lean_broker.report_build(self.paths, lean_broker.job_record(self.paths, third["id"])), 0)
        self.assertIn("USES-OUTPUT", out.getvalue())
        self.assertEqual({p.name for p in Path(third["lib"]).iterdir()},
                         {name + suffix for name in ("Basis", "Uses")
                          for suffix in (".olean", ".olean.private", ".olean.server", ".ir")})
        # --fresh-targets compiles the target although an entry with its key exists, and leaves that entry as it is.
        manifest = self.paths.cache / (before["Uses"]["key"] + ".artifacts.json")
        stored = manifest.read_bytes()
        with patch.object(lean_broker, "ensure_broker", return_value={}):
            fresh_id = lean_broker.build(self.paths, root, [root / "Uses.lean"], 60, "s1", fresh_targets=True)["build"]
        self.until(lambda: self.build_record(fresh_id)["status"] in lean_broker.FINISHED)
        fresh = self.build_record(fresh_id)
        self.assertEqual(self.statuses(fresh), {"Basis": "cached", "Uses": "finished"})
        self.assertIsNotNone(fresh["modules"]["Uses"]["job"])
        self.assertEqual(fresh["modules"]["Uses"]["key"], before["Uses"]["key"])
        self.assertEqual(manifest.read_bytes(), stored)

    def test_a_changed_statement_recompiles_everything_that_reaches_it(self):
        self.start_broker()
        root, targets = self.library()
        first = self.built(root, targets)
        self.assertEqual(first["status"], "finished", first)
        root, targets = self.library(marker="ANOTHER-STATEMENT")  # a line of Basis that is in its public files
        second = self.built(root, targets)
        self.assertEqual(second["status"], "finished", second)
        self.assertEqual(self.statuses(second), dict.fromkeys(("Basis", "Uses", "Top", "Plain", "Prying"), "finished"))
        before, after = first["modules"], second["modules"]
        self.assertNotEqual(after["Basis"]["public"], before["Basis"]["public"])
        # Uses was compiled again from the same source and emitted the same files. Top imports Uses
        # alone and still has another key, because its compile reads Basis through Uses.
        self.assertEqual((after["Uses"]["public"], after["Uses"]["full"]), (before["Uses"]["public"], before["Uses"]["full"]))
        self.assertNotEqual(after["Top"]["key"], before["Top"]["key"])

    def test_an_environment_change_fails_the_modules_still_waiting(self):
        # A waiting module's key would name the new environment while its imports were compiled in the old one.
        self.start_broker()
        root, _ = self.library(sleep=3)
        build_id = self.build(root, [root / "Uses.lean"])
        self.until(lambda: self.build_record(build_id)["modules"]["Basis"]["status"] == "running")
        time.sleep(0.02)
        self.write_settings(cache_epoch="second")
        self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        record = self.build_record(build_id)
        self.assertEqual((record["modules"]["Basis"]["status"], record["modules"]["Basis"]["exit_code"]), ("finished", 0))
        uses = record["modules"]["Uses"]
        self.assertEqual((uses["status"], uses["job"], uses["key"]), ("failed", None, None))
        self.assertIn("environment changed", uses["reason"])
        self.assertEqual(record["status"], "failed")


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
        launch = runtime_support.read_json(self.paths.job(job_id) / "launch.json")
        self.assertEqual(launch["argv"][:3], [sys.executable, "-B", str(FAKE)])  # lean itself, no lake in front
        self.assertEqual(launch["env"]["FAKE_LAKE"], "1")
        # Baselines measured directly are keyed apart from those measured through lake.
        self.assertEqual(job["closure"], lean_broker.closure_key(self.broker.environment_identity(), job["imports"], True))
        self.assertNotEqual(job["closure"], lean_broker.closure_key(self.broker.environment_identity(), job["imports"]))
        self.assertTrue(self.broker.calibration.entry(job["closure"])["direct"])  # and the table says so in words
        self.assertTrue(lean_broker.broker_status(self.paths)["launcher"]["direct"])  # status names the mode in use

    def test_a_lake_that_fails_leaves_the_configured_command_in_force(self):
        self.write_settings(command=self.LAKE + [sys.executable, "-B", str(FAKE)], env={"FAKE_LAKE_FAIL": "1"})
        self.start_broker()
        self.assertFalse(self.broker.state["launcher"]["direct"])
        self.assertIn("exit code 7", self.broker.state["launcher"]["reason"])
        job_id = self.submit(self.session_file("s1"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        launch = runtime_support.read_json(self.paths.job(job_id) / "launch.json")
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
        launch = runtime_support.read_json(self.paths.job(job_id) / "launch.json")
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
        launch = runtime_support.read_json(self.paths.job(record["modules"]["Target"]["job"]) / "launch.json")
        self.assertEqual(launch["argv"][:3], [sys.executable, "-B", str(FAKE)])  # lean itself, no lake in front
        self.assertEqual(launch["env"]["LEAN_PATH"].split(os.pathsep)[:2], [record["lib"], "fake-lake-lib"])


class ClientAndLifecycleTests(BrokerFixture):
    def cli(self, *args, timeout=60):
        return subprocess.run([sys.executable, "-B", str(lean_broker.SCRIPT), *args],
                              capture_output=True, text=True, encoding="utf-8", timeout=timeout)

    def test_run_relays_output_exit_code_and_measurements(self):
        path = self.session_file("s1", alloc_mb=50, sleep=1, marker="RELAYED", stderr="TO-STDERR", exit=1)
        result = self.cli("run", str(self.instance), str(path), "--session", "s1", "--expect-mb", "120")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("RELAYED", result.stdout)
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
        # The runner's `status` carries this same object as its `lean` entry.
        self.assertEqual(lean_broker.broker_status(self.paths)["version"], status["version"])
        # `cancel` answers through the command line too. The job has ended, so it is reported as it ended;
        # an ID that names no job is refused.
        cancelled = self.cli("cancel", str(self.instance), summary["job"])
        self.assertEqual(cancelled.returncode, 0, cancelled.stderr)
        self.assertEqual(json.loads(cancelled.stdout),
                         {"job": summary["job"], "status": "finished", "cancelled": "already completed"})
        unknown = self.cli("cancel", str(self.instance), "j" + "0" * 32)
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("unknown job", unknown.stderr)

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
        # A well-formed ID that names no job is answered at once rather than waited on; a malformed one is refused.
        unknown = self.cli("wait", str(self.instance), "j" + "0" * 32)
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("unknown job", unknown.stderr)
        invalid = self.cli("wait", str(self.instance), "jnobody")
        self.assertEqual(invalid.returncode, 1)
        self.assertIn("invalid job ID", invalid.stderr)

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
        # The receipt says that this broker writes its state on request; a client asks only such a broker.
        self.assertEqual(first["state_seconds"], lean_broker.STATE_SECONDS)
        second = self.cli("serve", str(self.instance), timeout=30)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("already has a running Lean broker", second.stderr)
        self.assertTrue(runtime_support.alive(first["process"]))
        self.cli("version", str(self.instance))  # finds the live broker; launches nothing
        self.assertEqual(lean_broker.broker_alive(self.paths)["process"], first["process"])

    def test_broker_death_mid_job_loses_neither_output_nor_exit_code(self):
        path = self.session_file("s1", sleep=4, marker="SURVIVED", exit=5)
        submitted = json.loads(self.cli("submit", str(self.instance), str(path), "--session", "s1", "--expect-mb", "40").stdout)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            # As `result` reads it: the Lean's identity is in the state file once the broker has been asked.
            record = lean_broker.job_record(self.paths, submitted["job"], current=True)
            if record and record["status"] == "running" and record.get("pid"):
                break
            time.sleep(0.05)
        else:
            self.fail("job did not start")
        broker = lean_broker.broker_alive(self.paths)
        runtime_support.terminate_process(broker["process"])
        while runtime_support.alive(broker["process"]):
            time.sleep(0.02)
        self.assertTrue(runtime_support.alive(record["lean"]))
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
        # Runner.ensure_broker alone is under test. A Runner is built around an initialized instance with
        # its compiled canon; ensure_broker reads only the instance's path and the two fields set here.
        import runner
        def bare_runner():
            engine = runner.Runner.__new__(runner.Runner)
            engine.instance, engine.broker, engine.broker_attempt = self.instance, None, 0
            return engine
        engine = bare_runner()
        before = time.monotonic()
        engine.ensure_broker()  # a broker is kept alive whether or not a session exists yet
        self.assertGreaterEqual(engine.broker_attempt, before)  # the launch records its moment for the ten seconds below
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not lean_broker.broker_alive(self.paths):
            time.sleep(0.05)
        first = lean_broker.broker_alive(self.paths)
        self.assertTrue(first)
        self.assertTrue(lean_broker.broker_status(self.paths)["broker_alive"])
        other = bare_runner()
        other.ensure_broker()
        self.assertIsNone(other.broker)
        self.assertEqual(lean_broker.broker_alive(self.paths)["process"], first["process"])
        runtime_support.terminate_process(first["process"])
        while runtime_support.alive(first["process"]):
            time.sleep(0.02)
        # Within ten seconds of the last launch no relaunch is made (runner.ensure_broker). The moment of that
        # launch is set here, so that a machine slow enough to spend those seconds above changes nothing, and the
        # launch itself is watched, because a relaunched broker writes its receipt only seconds later.
        engine.broker_attempt = time.monotonic()
        with patch.object(lean_broker, "launch_broker") as relaunch:
            engine.ensure_broker()
        relaunch.assert_not_called()
        self.assertIsNone(lean_broker.broker_alive(self.paths))
        engine.broker_attempt = float("-inf")
        engine.ensure_broker()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not lean_broker.broker_alive(self.paths):
            time.sleep(0.05)
        second = lean_broker.broker_alive(self.paths)
        self.assertNotEqual(second["process"], first["process"])
        runtime_support.terminate_process(second["process"])
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
        # `cancel` through the command line; work that has already completed keeps its outcome.
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(lean_broker.main(["cancel", str(self.instance), build_id]), 0)
        self.assertEqual(json.loads(out.getvalue()),
                         {"build": build_id, "status": "finished", "cancelled": "already completed"})
        # status lists builds finished within the last ten minutes; the first build is long recorded in the state.
        listed = {b["id"]: b["status"] for b in lean_broker.broker_status(self.paths)["builds"]}
        self.assertEqual(listed.get(summary["build"]), "finished")


if __name__ == "__main__":
    unittest.main()

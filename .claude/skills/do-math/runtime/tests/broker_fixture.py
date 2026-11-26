"""The fixture that runs a Lean broker inside the test process, shared by the test modules of the broker and by
test_resilience, whose test of the runner's broker start stands on the same bare instance."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lean_broker
import runtime_support

FAKE = Path(__file__).resolve().with_name("fake_lean.py")


def source(path, imports=("Mathlib.Data.Nat.Basic",), module=False, proof=None, **fake):
    """A Lean file the fake lean understands; its baseline is 8 MiB per import plus 8.

    `module` writes it as a file of Lean's module system. `proof` adds a line that the fake lean
    keeps out of the public files it emits, as Lean keeps a proof out of them."""
    lines = (["module"] if module else []) + [f"import {name}" for name in imports]
    if fake:
        lines.append("-- fake: " + " ".join(f"{k}={v}" for k, v in fake.items()))
    if proof is not None:
        lines.append(f"-- proof: {proof}")
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
        self.settings = {
            "max_sessions": 2,
            "cli": {"codex": "codex.exe", "claude": "claude.exe"},
            "lean": {"command": [sys.executable, "-B", str(FAKE)],
                     "version_command": [sys.executable, "-B", str(FAKE), "--version"], "cwd": None, "env": {},
                     "memory_budget_mb": self.budget, "min_free_memory_mb": 0, "threads": 1,
                     "cpu_threads_budget": self.threads_budget,
                     # A calibration compile reserves all of calibration_expect_mb as certain, and the machine gate
                     # holds it until the test machine has that much memory free. The stand-in takes a few dozen MiB.
                     "calibration_expect_mb": 64,
                     # The stand-in compiler must not starve behind normal-priority load on the test machine.
                     "priority": "normal"}}
        # What the broker reads of an instance: its settings, the runner's folder, and in the runner's
        # state the sessions and whether the instance has finished. The runner creates a real instance
        # around a compiled canon, which no test of the broker needs.
        for folder in ("runner", "sessions"):
            (self.instance / folder).mkdir(parents=True)
        runtime_support.write_json(self.instance / "settings.json", self.settings)
        runtime_support.write_json(self.instance / "runner/state.json", {"sessions": {}, "finished": False})
        self.paths = lean_broker.Paths(self.instance)
        self.paths.ensure()
        self.broker = None
        self.previous_hosts = []

    def write_settings(self, **lean):
        """Change the instance's settings file as an operator would, for the broker's live reload."""
        self.settings["lean"].update(lean)
        runtime_support.write_json(self.instance / "settings.json", self.settings)

    def tearDown(self):
        # Every Lean process a job folder records is terminated, whichever broker started it (this one
        # or a detached one): on Windows a live compile holds its working folder against the cleanup.
        for directory in self.paths.jobs.iterdir() if self.paths.jobs.is_dir() else []:
            (directory / "CANCEL").touch()
            receipt = directory / "process.json"
            if receipt.exists():
                lean = runtime_support.read_json(receipt)
                if runtime_support.alive(lean["process"]):
                    lean_broker.terminate_tree(lean["pid"])
                    self.wait_gone(lean["process"])
        hosts = self.previous_hosts + (list(self.broker.hosts.values()) if self.broker is not None else [])
        for host in hosts:
            host.wait(timeout=10)
        if self.paths.state.exists():  # hosts of a detached broker exit once their Lean has ended
            for job in runtime_support.read_json(self.paths.state).get("jobs", {}).values():
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
            runtime_support.terminate_process(info["process"])
            while runtime_support.alive(info["process"]):
                time.sleep(0.02)

    @staticmethod
    def wait_gone(identity, limit=10):
        deadline = time.monotonic() + limit
        while runtime_support.alive(identity) and time.monotonic() < deadline:
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

    def build(self, root, targets, session="s1"):
        with patch.object(lean_broker, "ensure_broker", return_value={}):
            return lean_broker.build(self.paths, root, targets, 60, session)["build"]

    def built(self, root, targets):
        """A build carried to its end; its record."""
        build_id = self.build(root, targets)
        self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        return self.build_record(build_id)

    def compiled(self, path):
        """A single-file compile carried to its end; its job record."""
        job_id = self.submit(path, expect_mb=40)
        self.until(lambda: self.finished(job_id))
        return self.broker.state["jobs"][job_id]

    def tree(self, **overrides):
        """A imports the library, B and C import A, D imports B and C; `overrides` replaces a module's fake options."""
        root = self.instance / "sessions" / "s1" / "work" / "lean"
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

    def on_disk(self):
        """The broker's state as its file holds it, which can be behind the broker under test."""
        return runtime_support.read_json(self.paths.state)

    def asking(self, call):
        """What a client's call returns when the broker under test is a live broker that writes on request.

        The broker runs in this process and has written no receipt, so the client is given the
        receipt that a served broker writes. The client runs in a thread while this thread makes the
        broker's polls."""
        receipt = {"process": runtime_support.process_identity(os.getpid()), "state_seconds": lean_broker.STATE_SECONDS}
        outcome = []

        def client():
            try:
                outcome.append((call(), None))
            except BaseException as exc:  # raised again in the test's thread, below
                outcome.append((None, exc))

        with patch.object(lean_broker, "broker_alive", return_value=receipt):
            thread = threading.Thread(target=client)
            thread.start()
            deadline = time.monotonic() + 30
            while thread.is_alive() and time.monotonic() < deadline:
                self.broker.tick()
                time.sleep(0.02)
            thread.join(timeout=lean_broker.READY_SECONDS + 5)
        self.assertFalse(thread.is_alive(), "the client did not return")
        value, error = outcome[0]
        if error is not None:
            raise error
        return value

    def status(self):
        """`status` of the broker under test, asked of it as a client asks a live broker."""
        return self.asking(lambda: lean_broker.broker_status(self.paths))

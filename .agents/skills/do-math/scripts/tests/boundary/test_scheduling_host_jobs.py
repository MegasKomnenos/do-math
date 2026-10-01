"""Host resource limits on real Windows Jobs: the kernel's enforcement, setting failures, and the reservations they settle.

``WindowsJob`` sets a Job's commit-memory and CPU-rate limits before it creates
the suspended root, so a refused setting creates no process. The kernel refuses
a Job memory limit below its minimum (one byte here) with
``ERROR_INVALID_PARAMETER``, which the adapter reports as the missing
``local_job_resources`` capability; these cases use that real refusal. The
model runner and the slots ledger run with the real Jobs port and clock. All
numbers are disposable test budgets, never product defaults.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

from do_math import execution_profiles as profiles
from do_math.activities import assign_execution, open_activity
from do_math.canonical import canonical_json
from do_math.execution_lifecycle import create_execution, transition_execution
from do_math.model_runner import ModelRunner
from do_math.repository import ResearchRepository
from do_math.session_slots import SessionSlots
from do_math.system_clock import SystemClock
from do_math.windows_job import WindowsJob, WindowsJobs, process_identity
from support.provider_inputs import host_capacity_fixture
from support.state_builders import current_state
from support.fakes.git_backend import make_repository
from support.provider_probes import ObservedCalls
from support.scheduling_hosts import dispatched
from test_categories import test_group as category

MiB = 1024 ** 2
# A Job memory limit the kernel refuses (below its minimum): a real setting failure.
REFUSED = {"memory_bytes": 1, "cpu_rate_basis_points": 2000}


def emptied(job, timeout=10):
    """Poll until the Job has no active process or ``timeout`` seconds pass; whether it emptied."""
    deadline = time.monotonic() + timeout
    pause = threading.Event()
    while job.inspect().active_processes and time.monotonic() < deadline:
        pause.wait(0.02)
    return job.inspect().active_processes == 0


def real_slots(runtime, instance):
    from support.entry import entry
    _entry = entry()
    return SessionSlots(runtime, instance, clock=SystemClock(), jobs=WindowsJobs(), host_id=_entry.host_id)


@category('resource')
@unittest.skipUnless(os.name == "nt", "Windows kernel required")
class HostJobTests(unittest.TestCase):
    def test_resource_setting_failure_is_distinct_capability_and_starts_nothing(self):
        from support.entry import entry
        _entry = entry()
        _, selected, constraint = host_capacity_fixture()
        p = profiles.with_host_resources(selected["research_work"], constraint, {"jobs": 1, **REFUSED})
        jobs, clock = WindowsJobs(), SystemClock()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "work"
            workspace.mkdir()
            prompt = profiles.prepare_prompt("temporary failure probe", p)
            with ObservedCalls(create=WindowsJob._create_suspended_root) as observed:
                result = ModelRunner(codex_path=sys.executable, jobs=jobs, clock=clock, environment=_entry.environment, host_id=_entry.host_id).run(
                    prompt=prompt, input_seal=profiles.prompt_seal(prompt), output_schema={}, workspace=workspace,
                    evidence_dir=root / "evidence", model=p["ai"]["model"], effort=p["ai"]["effort"],
                    timeout_seconds=15, execution_id="EX-setting-failure", profile=p,
                    launch_ticket=dispatched('EX-setting-failure', p, jobs=jobs, clock=clock),
                    on_started=lambda identity: self.fail("setting failure cannot publish a live process"))
            self.assertEqual(observed.count("create"), 0)
            self.assertEqual(result["error_kind"], "profile_unsupported")
            self.assertEqual(result["capability_failure"]["capability"], "local_job_resources")
            self.assertEqual(result["capability_evidence"]["execution_profile_ref"], profiles.profile_ref(p))
            self.assertEqual(result["capability_evidence"]["capabilities"]["local_job_resources"]["status"], "unsupported")
            self.assertNotIn("atomic_local_job", result["capability_evidence"]["capabilities"])

    def test_both_real_adapters_receive_limits_before_user_code_or_model_call(self):
        from support.entry import entry
        _entry = entry()
        _, selected, _ = host_capacity_fixture()
        jobs, clock = WindowsJobs(), SystemClock()
        for provider in ("codex", "claude"):
            p = deepcopy(selected["research_work"])
            if provider == "claude":
                p["ai"].update(provider="claude", model="claude-test")
                p = profiles.seal_profile(p)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                workspace = root / "work"
                workspace.mkdir()
                prompt = profiles.prepare_prompt("temporary binding probe", p)
                started = []
                result = ModelRunner(**{provider + "_path": sys.executable}, jobs=jobs, clock=clock, environment=_entry.environment, host_id=_entry.host_id).run(
                    prompt=prompt, input_seal=profiles.prompt_seal(prompt), output_schema={}, workspace=workspace,
                    evidence_dir=root / "evidence", model=p["ai"]["model"], effort=p["ai"]["effort"],
                    timeout_seconds=15, execution_id="EX-" + provider, profile=p, should_stop=lambda: True,
                    on_started=started.append, launch_ticket=dispatched('EX-' + provider, p, jobs=jobs, clock=clock))
                self.assertEqual(result["status"], "stopped")
                self.assertEqual(started[0]["host_resources"]["limits"], profiles.job_resource_limits(p, host_id=_entry.host_id))
                request = json.loads((root / "evidence" / "request.json").read_text(encoding="utf-8"))
                self.assertEqual(request["resource_limits"], profiles.job_resource_limits(p, host_id=_entry.host_id))
                self.assertEqual(request["profile_ref"], profiles.profile_ref(p))
                self.assertTrue(result["execution"]["collect"]["termination_barrier"]["confirmed"])
                self.assertIsNone(result["execution"]["collect"]["worker_status"])

    def test_real_creation_failure_and_normal_abnormal_termination_return_once(self):
        from support.entry import entry
        _entry = entry()
        for outcome in ("creation_failure", "normal", "nonzero", "terminated", "setting_failure"):
            instance, selected, _ = host_capacity_fixture()
            runtime = {"executions": {}, "reservations": {}}
            slots = real_slots(runtime, instance)
            p = selected["formal_check"]
            e = {"id": "EX-" + outcome, "role": p["role"], "status": "queued"}
            self.assertTrue(slots.acquire(e["id"], profile=p, execution=e))
            with tempfile.TemporaryDirectory() as directory:
                marker = Path(directory) / "started"
                code = f"from pathlib import Path; import sys,time; Path({str(marker)!r}).write_text('started'); "
                code += "time.sleep(30)" if outcome == "terminated" else "sys.exit(7)" if outcome == "nonzero" else "pass"
                argv = [str(Path(directory) / "absent.exe")] if outcome == "creation_failure" else [sys.executable, "-c", code]
                kwargs = {"resource_limits": profiles.job_resource_limits(p, host_id=_entry.host_id), "name": e['launch_ticket']['job_name']}
                if outcome == "setting_failure":
                    with self.assertRaisesRegex(OSError, "SetInformationJobObject"):
                        WindowsJob(argv, **{**kwargs, "resource_limits": REFUSED})
                    self.assertFalse(marker.exists())
                elif outcome == "creation_failure":
                    with self.assertRaisesRegex(OSError, "CreateProcessW failed"):
                        WindowsJob(argv, **kwargs)
                    self.assertFalse(marker.exists())
                else:
                    with WindowsJob(argv, **kwargs) as job:
                        slots.started(e["id"], {**process_identity(job), "job_name": job.name}, at="2026-09-20T00:00:00Z")
                        self.assertFalse(slots.release(e["id"]), "a suspended but live Job must retain capacity")
                        job.resume()
                        if outcome == "terminated":
                            job.terminate()
                        self.assertTrue(job.wait(15))
                        emptied(job)
                        self.assertEqual(job.inspect().active_processes, 0)
                        self.assertTrue(slots.release(e["id"]))
                self.assertTrue(slots.release(e["id"], reason=outcome))
                once = deepcopy(runtime)
                self.assertTrue(slots.release(e["id"], reason="replayed return"))
                self.assertEqual(runtime, once)
                self.assertTrue(all(r["reserved"] == r["returned"] and r["state"] == "settled"
                                    for r in runtime["reservations"].values()))

    def test_native_process_identity_round_trips_without_integer_precision_loss(self):
        with WindowsJob([sys.executable, "-c", "pass"]) as job:
            value = process_identity(job)
            self.assertIsInstance(value["creation_filetime"], str)
            self.assertEqual(int(value["creation_filetime"]), job.creation_filetime)
            self.assertEqual(json.loads(canonical_json(value)), value)

    @category('resource')
    def test_commit_limit_is_applied_before_resume_and_denies_child_allocation(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "memory.json"
            code = "\n".join([
                "import ctypes,json", "from pathlib import Path", "k=ctypes.WinDLL('kernel32',use_last_error=True)",
                "k.VirtualAlloc.restype=ctypes.c_void_p",
                "p=k.VirtualAlloc(None,256*1024**2,0x3000,4)",
                f"Path({str(output)!r}).write_text(json.dumps({{'allocated':bool(p),'winerror':ctypes.get_last_error()}}))"])
            limits = {"memory_bytes": 128 * MiB, "cpu_rate_basis_points": 2000}
            with WindowsJob([sys.executable, "-c", code], resource_limits=limits) as job:
                before = job.resource_usage()
                self.assertEqual(before["limits"], limits)
                self.assertFalse(output.exists())
                job.resume()
                self.assertTrue(job.wait(15))
                observed = json.loads(output.read_text())
                self.assertFalse(observed["allocated"])
                self.assertNotEqual(observed["winerror"], 0)
                # Windows can include a rejected commit attempt in PeakJobMemoryUsed.
                # Allocation success is the enforcement oracle, not peak <= cap.
                self.assertGreater(job.resource_usage()["peak_job_memory_bytes"], 0)
            output.unlink()
            with WindowsJob([sys.executable, "-c", code]) as control:
                control.resume()
                self.assertTrue(control.wait(15))
                self.assertTrue(json.loads(output.read_text())["allocated"])

    @category('resource')
    def test_cpu_hard_cap_reduces_local_cpu_time_in_isolated_busy_child(self):
        """About 30 s: the capped child starts its interpreter at 0.1 % CPU; the cap's effect is what is measured."""
        samples = []
        with tempfile.TemporaryDirectory() as directory:
            for cap in (None, 10):
                output = Path(directory) / (str(cap) + ".json")
                code = "\n".join(["import time,json", "from pathlib import Path",
                                  "wall=time.monotonic(); cpu=time.process_time()", "while time.monotonic()-wall<3: pass",
                                  f"Path({str(output)!r}).write_text(json.dumps({{'wall':time.monotonic()-wall,'cpu':time.process_time()-cpu}}))"])
                limits = None if cap is None else {"memory_bytes": 128 * MiB, "cpu_rate_basis_points": cap}
                with WindowsJob([sys.executable, "-c", code], resource_limits=limits) as job:
                    job.resume()
                    self.assertTrue(job.wait(45))
                    samples.append(json.loads(output.read_text()))
                    samples[-1].update(cap_basis_points=cap, job=job.resource_usage())
                    if cap is not None:
                        self.assertEqual(job.resource_usage()["limits"], limits)
        self.assertGreater(samples[0]["cpu"], .1, "control child got too little CPU for a meaningful comparison")
        self.assertLess(samples[1]["cpu"], samples[0]["cpu"] * .6, samples)

    def test_invalid_limits_or_setting_failure_never_create_root(self):
        with ObservedCalls(create=WindowsJob._create_suspended_root) as observed:
            with self.assertRaisesRegex(ValueError, "Job limits need positive commit bytes"):
                WindowsJob([sys.executable, "-c", "pass"], resource_limits={"memory_bytes": 0, "cpu_rate_basis_points": 0})
        self.assertEqual(observed.count("create"), 0)
        with ObservedCalls(create=WindowsJob._create_suspended_root) as observed:
            with self.assertRaisesRegex(OSError, "SetInformationJobObject"):
                WindowsJob([sys.executable, "-c", "pass"], resource_limits=REFUSED)
        self.assertEqual(observed.count("create"), 0)


@category('resource')
@unittest.skipUnless(os.name == "nt", "Windows kernel required")
class HostRepositoryJobTests(unittest.TestCase):
    def test_positive_host_records_round_trip_with_a_real_windows_job(self):
        """The real Git repository and a real limited Job: user code waits for the published identity; settlement is once."""
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        instance, selected, _ = host_capacity_fixture()
        with tempfile.TemporaryDirectory() as directory:
            make_repository(directory)
            iid = "RI-00000000000000000000000000"
            instance.update(id=iid, workspace=directory, config={})
            instance, runtime = current_state(instance, {"status": "ready", "executions": {}, "reservations": {},
                                                         "provider_waits": {}})
            repo = ResearchRepository(Path(directory), iid, backend=_entry.ports.git_backend, clock=_entry.ports.clock)
            head = repo.initialize(instance, runtime)
            p = selected["formal_check"]
            open_activity(runtime, activity_id="AT-host", activity_kind="formal_check", owner_ref="engine",
                          input_refs=[], opened_at="2026-09-20T00:00:00Z")
            e = create_execution(execution_id="EX-host-roundtrip", owner_activity_id="AT-host", actor_kind="machine",
                                 input_manifest={}, profile_ref=profiles.profile_ref(p), created_at="2026-09-20T00:00:00Z")
            e["role"] = p["role"]
            assign_execution(runtime, "AT-host", e)
            slots = real_slots(runtime, instance)
            with repo.writer_lock():
                self.assertTrue(slots.acquire(e["id"], profile=p, execution=e))
                head = repo.save_with_state(head, instance, runtime)[0]
            loaded_head, _, loaded = repo.load()
            self.assertEqual(loaded_head, head)
            self.assertEqual(loaded["executions"][e["id"]]["status"], "starting")
            self.assertEqual(len(loaded["executions"][e["id"]]["capacity"]["reservation_ids"]), 3)
            marker = Path(directory) / "user-started"
            code = f"from pathlib import Path; Path({str(marker)!r}).write_text('ok')"
            with WindowsJob([sys.executable, "-c", code], resource_limits=profiles.job_resource_limits(p, host_id=_entry.host_id),
                            name=e['launch_ticket']['job_name']) as job:
                with repo.writer_lock():
                    slots.started(e["id"], {**process_identity(job), "job_name": job.name,
                                           "host_resources": job.resource_usage()}, at="2026-09-20T00:00:30Z")
                    head = repo.save_with_state(head, instance, runtime)[0]
                self.assertFalse(marker.exists(), "user code must wait for the published identity")
                job.resume()
                self.assertTrue(job.wait(15))
                emptied(job)
                with repo.writer_lock():
                    self.assertTrue(slots.release(e["id"]))
                    transition_execution(e, "stopping", at="2026-09-20T00:01:00Z")
                    transition_execution(e, "ended", at="2026-09-20T00:01:01Z", outcome="execution_incomplete")
                    head = repo.save_with_state(head, instance, runtime)[0]
                    self.assertTrue(slots.release(e["id"], reason="repeat settlement"))
                    self.assertEqual(repo.save_with_state(head, instance, runtime)[0], head)
                _, _, after = repo.load()
                self.assertTrue(all(row["reserved"] == row["returned"] for row in after["reservations"].values()))


if __name__ == "__main__":
    unittest.main()

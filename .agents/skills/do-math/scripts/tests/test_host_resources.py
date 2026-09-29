"""Local instance reservations and real Windows Job resource enforcement.

All numbers here are disposable test budgets, never product defaults.
"""
import json
import os
import platform
import sys
import tempfile
import time
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles, execution_profiles as profiles
from do_math.session_slots import SessionSlots
from do_math.windows_job import WindowsJob
from provider_fixtures import host_capacity_fixture, PROFILE_CONFIG
from research_fixtures import current_state, dispatched_launch, git_init
from test_categories import test_group as category


class HostReservations(unittest.TestCase):
    def admit(self, slots, eid, profile):
        execution = {"id": eid, "role": profile["role"], "status": "queued"}
        accepted = slots.acquire(eid, profile=profile, execution=execution)
        return accepted, execution

    def test_work_operations_machine_share_capacity_and_preserve_control(self):
        instance, selected, constraint = host_capacity_fixture()
        runtime = {"executions": {}, "reservations": {}}
        slots = SessionSlots(runtime, instance)
        for n, role in enumerate(selected):
            accepted, execution = self.admit(slots, "EX-" + str(n), selected[role])
            self.assertTrue(accepted)
            self.assertEqual(execution["status"], "starting")
        before = deepcopy(runtime)
        self.assertFalse(self.admit(slots, "EX-extra", selected["formal_check"])[0])
        self.assertEqual(runtime, before)
        units = lambda eid: {r["unit"] for r in runtime["reservations"].values() if r["owner_id"] == eid}
        host_units = {"jobs", "memory_bytes", "cpu_rate_basis_points"}
        self.assertEqual(units("EX-0"), host_units | {"execution"})
        self.assertEqual(units("EX-1"), host_units, "an operational role reserves no model slot")
        machine_rows = [r for r in runtime["reservations"].values() if r["owner_id"] == "EX-2"]
        self.assertEqual({r["unit"] for r in machine_rows}, {"jobs", "memory_bytes", "cpu_rate_basis_points"})
        self.assertTrue(all(r["constraint_id"] == constraint["id"] for r in machine_rows))
        self.assertIsNone(runtime["executions"]["EX-2"]["capacity"]["provider"])
        self.assertTrue(slots.release("EX-2", reason="creation failed before resume"))
        once = deepcopy(runtime)
        self.assertTrue(slots.release("EX-2", reason="repeat return"))
        self.assertEqual(runtime, once)
        self.assertTrue(self.admit(slots, "EX-next", selected["formal_check"])[0])

    def test_each_constraint_refuses_without_partial_ai_or_host_records(self):
        for unit, amount in (("jobs", 0), ("memory_bytes", 1), ("cpu_rate_basis_points", 1)):
            with self.subTest(unit=unit):
                instance, selected, constraint = host_capacity_fixture()
                key = "max_jobs" if unit == "jobs" else unit
                # Author a new approval, rather than mutate a content-addressed row.
                limits = {"jobs": constraint["max_jobs"], "memory_bytes": constraint["memory_bytes"],
                          "cpu_rate_basis_points": constraint["cpu_rate_basis_points"]}
                limits[unit] = amount
                reserve = {k: 0 for k in limits}
                limited = profiles.host_constraint(host_id=platform.node(), limits=limits,
                    control_reserve=reserve, authority_refs=["GS-host-refusal-test"])
                instance["capacity_constraints"][limited["id"]] = limited
                instance["host_capacity_ref"] = limited["id"]
                p = profiles.with_host_resources(selected["research_work"], limited,
                    {"jobs": 1, "memory_bytes": 128 * 1024**2, "cpu_rate_basis_points": 2000})
                instance["execution_profiles"][p["id"]] = p
                runtime = {"executions": {}, "reservations": {}}
                slots = SessionSlots(runtime, instance)
                before = deepcopy(runtime)
                self.assertFalse(self.admit(slots, "EX-refused", p)[0])
                self.assertEqual(runtime, before)

    def test_no_approval_stays_unmeasured_machine_has_no_ai_budget(self):
        instance = profiles.build_profiles(PROFILE_CONFIG)
        p = next(p for p in instance["execution_profiles"].values() if p["role"] == "formal_check")
        self.assertIsNone(profiles.job_resource_limits(p))
        self.assertEqual(p["host_capacity_status"], "unmeasured_not_enforced")
        runtime = {"executions": {}, "reservations": {}}
        self.assertTrue(self.admit(SessionSlots(runtime, instance), "EX-machine", p)[0])
        self.assertEqual(runtime["reservations"], {})

    def test_other_host_refused_and_unknown_termination_retains_reservations(self):
        instance, selected, _ = host_capacity_fixture()
        runtime = {"executions": {}, "reservations": {}}
        slots = SessionSlots(runtime, instance)
        with patch("platform.node", return_value="different-host"):
            with self.assertRaisesRegex(ValueError, "host"):
                self.admit(slots, "EX-wrong", selected["formal_check"])
        self.assertEqual(runtime["executions"], {})
        self.assertTrue(self.admit(slots, "EX-unknown", selected["formal_check"])[0])
        slots.started("EX-unknown", {"job_name": runtime['executions']['EX-unknown']['launch_ticket']['job_name']},
                      at="2026-09-20T00:00:00Z")
        with patch("do_math.windows_job.named_job_empty", return_value=None):
            self.assertFalse(slots.release("EX-unknown"))
        self.assertTrue(all(r["state"] == "held" for r in runtime["reservations"].values()))

    def test_actual_git_cas_publishes_start_and_all_demands_together(self):
        # Exercise the real Git publication primitive. Repository schema
        # integration is separately tested below; this is no schema assurance.
        from do_math.git_store import GitStateStore, GitStateStoreConflict
        from do_math.canonical import canonical_json
        instance, selected, _ = host_capacity_fixture()
        runtime = {"executions": {}, "reservations": {}}
        with tempfile.TemporaryDirectory() as directory:
            git_init(directory)
            store = GitStateStore(directory, "RI-00000000000000000000000000")
            head = store.publish(None, {"research/approval.json": canonical_json(instance),
                "runtime/initial.json": b"{}"}).head
            slots = SessionSlots(runtime, instance)
            for index, role in enumerate(selected):
                eid = "EX-" + str(index)
                self.assertTrue(self.admit(slots, eid, selected[role])[0])
                changes = {"runtime/executions/" + eid + ".json": canonical_json(runtime["executions"][eid])}
                changes.update({"runtime/reservations/" + rid + ".json": canonical_json(row)
                    for rid, row in runtime["reservations"].items() if row["owner_id"] == eid})
                stale = head
                with store.writer_lock():
                    head = store.publish(head, changes).head
                published = json.loads(store.read_bytes(head, "runtime/executions/" + eid + ".json"))
                self.assertEqual(published["status"], "starting")
                for rid in published["capacity"]["reservation_ids"]:
                    self.assertEqual(json.loads(store.read_bytes(head, "runtime/reservations/" + rid + ".json"))["state"], "held")
            before = deepcopy(runtime)
            self.assertFalse(self.admit(slots, "EX-denied", selected["formal_check"])[0])
            self.assertEqual(runtime, before)
            self.assertEqual(store.read_snapshot().head, head)
            with self.assertRaises(GitStateStoreConflict):
                store.publish(stale, {"runtime/stale.json": b"{}"})
            self.assertEqual(store.read_snapshot().head, head)

    def test_old_profile_editions_do_not_open_an_independent_host_pool(self):
        instance, selected, constraint = host_capacity_fixture()
        runtime = {"executions": {}, "reservations": {}}
        slots = SessionSlots(runtime, instance)
        for n in range(3):
            self.assertTrue(self.admit(slots, "EX-" + str(n), selected["formal_check"])[0])
        changed = profiles.host_constraint(host_id=constraint["host_id"],
            limits={"jobs": 4, "memory_bytes": 512*1024**2, "cpu_rate_basis_points": 8000},
            control_reserve=constraint["control_reserve"], authority_refs=["GS-host-next-test"])
        instance["capacity_constraints"][changed["id"]] = changed
        instance["host_capacity_ref"] = changed["id"]
        p = profiles.with_host_resources(selected["formal_check"], changed, selected["formal_check"]["host_resources"]["demands"])
        instance["execution_profiles"][p["id"]] = p
        self.assertFalse(self.admit(slots, "EX-escape", p)[0])

    def test_unbound_profiles_cannot_bypass_shared_approval(self):
        instance, _, _ = host_capacity_fixture()
        unbound = next(p for p in instance["execution_profiles"].values() if not p.get("host_capacity_refs"))
        runtime = {"executions": {}, "reservations": {}}
        with self.assertRaisesRegex(ValueError, "current adopted host"):
            self.admit(SessionSlots(runtime, instance), "EX-bypass", unbound)
        self.assertEqual(runtime, {"executions": {}, "reservations": {}})

    def test_explicit_authoring_covers_every_capped_role(self):
        _, selected, constraint = host_capacity_fixture()
        bare = profiles.build_profiles(PROFILE_CONFIG)
        demands = {p["role"]: {"jobs": 1, "memory_bytes": 128*1024**2, "cpu_rate_basis_points": 1000}
                   for p in bare["execution_profiles"].values() if p["role"] in profiles.HOST_ROLES}
        config = {**PROFILE_CONFIG,
                  "host_resources": {"constraint": constraint, "demands_by_role": demands}}
        instance = profiles.build_profiles(config)
        self.assertEqual(instance["host_capacity_ref"], constraint["id"])
        self.assertTrue(all(p["host_capacity_refs"] == ([] if p['role'] in {'formal_check','trust_check','trust_activate'}
                            else [constraint["id"]]) for p in instance["execution_profiles"].values()))
        p = next(p for p in instance["execution_profiles"].values() if p["role"] == "research_work")
        runtime = {"executions": {}, "reservations": {}}
        slots = SessionSlots(runtime, instance)
        for n in range(2):
            self.assertTrue(self.admit(slots, "EX-call-" + str(n), p)[0])
            self.assertTrue(slots.release("EX-call-" + str(n)))
        self.assertTrue(self.admit(slots, "EX-call-extra", p)[0])
        machine = next(p for p in instance["execution_profiles"].values() if p["role"] == "formal_check")
        self.assertTrue(self.admit(slots, "EX-machine", machine)[0])
        self.assertEqual({r["unit"] for r in runtime["reservations"].values() if r["owner_id"] == "EX-machine"},
                         set())
        bad = deepcopy(config)
        del bad["host_resources"]["demands_by_role"]["research_work"]
        with self.assertRaisesRegex(ValueError, "every capped role"):
            profiles.build_profiles(bad)

    def test_legacy_host_capped_lean_profile_requires_replacement(self):
        _, _, constraint = host_capacity_fixture()
        authored = profiles.build_profiles({**PROFILE_CONFIG, "lean_command": [sys.executable]})
        p = next(p for p in authored["execution_profiles"].values() if p["role"] == "formal_check")
        p = profiles.with_host_resources(p, constraint,
            {"jobs": 1, "memory_bytes": 128*1024**2, "cpu_rate_basis_points": 2000})
        environment = {"toolchain": {"configured_command": [sys.executable]}}
        with self.assertRaisesRegex(ValueError, "uncapped profile"):
            profiles.machine_invocation(p, trust_environment=environment)
        callback = lambda identity: None
        with self.assertRaisesRegex(ValueError, "uncapped profile"):
            profiles.machine_invocation(p, trust_environment=environment, on_started=callback)


class HostRepositoryContract(unittest.TestCase):
    def test_positive_host_records_pass_real_repository_and_round_trip(self):
        from do_math.repository import ResearchRepository
        instance, selected, _ = host_capacity_fixture()
        with tempfile.TemporaryDirectory() as directory:
            git_init(directory)
            iid = "RI-00000000000000000000000000"
            instance.update(id=iid, workspace=directory, config={})
            instance, runtime = current_state(instance, {"status": "ready", "executions": {}, "reservations": {},
                                                         "provider_waits": {}})
            repo = ResearchRepository(Path(directory), iid)
            head = repo.initialize(instance, runtime)
            p = selected["formal_check"]
            from do_math.activities import open_activity, assign_execution
            from do_math.execution_lifecycle import create_execution
            open_activity(runtime, activity_id="AT-host", activity_kind="formal_check", owner_ref="engine",
                input_refs=[], opened_at="2026-09-20T00:00:00Z")
            e = create_execution(execution_id="EX-host-roundtrip", owner_activity_id="AT-host", actor_kind="machine",
                input_manifest={}, profile_ref=profiles.profile_ref(p), created_at="2026-09-20T00:00:00Z")
            e["role"] = p["role"]
            assign_execution(runtime, "AT-host", e)
            with repo.writer_lock():
                self.assertTrue(SessionSlots(runtime, instance).acquire(e["id"], profile=p, execution=e))
                head = repo.save_with_state(head, instance, runtime)[0]
            loaded_head, _, loaded = repo.load()
            self.assertEqual(loaded_head, head)
            self.assertEqual(loaded["executions"][e["id"]]["status"], "starting")
            self.assertEqual(len(loaded["executions"][e["id"]]["capacity"]["reservation_ids"]), 3)
            if os.name == "nt":
                from do_math.windows_job import process_identity
                from do_math.execution_lifecycle import transition_execution
                marker = Path(directory) / "user-started"
                code = f"from pathlib import Path; Path({str(marker)!r}).write_text('ok')"
                slots = SessionSlots(runtime, instance)
                with WindowsJob([sys.executable, "-c", code], resource_limits=profiles.job_resource_limits(p),
                                name=e['launch_ticket']['job_name']) as job:
                    with repo.writer_lock():
                        slots.started(e["id"], {**process_identity(job), "job_name": job.name,
                                               "host_resources": job.resource_usage()},
                                      at="2026-09-20T00:00:30Z")
                        head = repo.save_with_state(head, instance, runtime)[0]
                    self.assertFalse(marker.exists(), "user code must wait for the published identity")
                    job.resume()
                    self.assertTrue(job.wait(15))
                    deadline = time.monotonic() + 10
                    while job.inspect().active_processes and time.monotonic() < deadline: time.sleep(.02)
                    with repo.writer_lock():
                        self.assertTrue(slots.release(e["id"]))
                        transition_execution(e, "stopping", at="2026-09-20T00:01:00Z")
                        transition_execution(e, "ended", at="2026-09-20T00:01:01Z", outcome="execution_incomplete")
                        head = repo.save_with_state(head, instance, runtime)[0]
                        self.assertTrue(slots.release(e["id"], reason="repeat settlement"))
                        self.assertEqual(repo.save_with_state(head, instance, runtime)[0], head)
                    _, _, after = repo.load()
                    self.assertTrue(all(row["reserved"] == row["returned"] for row in after["reservations"].values()))


@unittest.skipUnless(os.name == "nt", "Windows kernel required")
class HostJobTests(unittest.TestCase):
    def test_transient_resource_exhaustion_is_not_a_structural_unsupported_fact(self):
        import ctypes
        from do_math.windows_job import WindowsJobUnsupportedError
        def exhausted(*args):
            ctypes.set_last_error(8)  # ERROR_NOT_ENOUGH_MEMORY; not a capability result.
            return 0
        with patch("do_math.windows_job._kernel32.SetInformationJobObject", side_effect=exhausted):
            with self.assertRaises(OSError) as caught:
                WindowsJob([sys.executable, "-c", "pass"],
                    resource_limits={"memory_bytes": 128*1024**2, "cpu_rate_basis_points": 1000})
        self.assertNotIsInstance(caught.exception, WindowsJobUnsupportedError)

    def test_host_bound_runner_requires_start_publication_callback(self):
        from do_math.model_runner import ModelRunner
        _, selected, _ = host_capacity_fixture()
        p = selected["research_work"]
        prompt = profiles.prepare_prompt("test", p)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "work"; workspace.mkdir()
            with self.assertRaisesRegex(ValueError, "on_started"):
                ModelRunner(codex_path=sys.executable).run(prompt=prompt, input_seal=profiles.prompt_seal(prompt),
                    output_schema={}, workspace=workspace, evidence_dir=root / "evidence", model=p["ai"]["model"],
                    effort=p["ai"]["effort"], timeout_seconds=15, execution_id="EX-no-callback", profile=p,
                    launch_ticket=dispatched_launch('EX-no-callback',p))
            self.assertFalse((root / "evidence").exists())

    def test_resource_setting_failure_is_distinct_capability_and_starts_nothing(self):
        import ctypes
        from do_math.model_runner import ModelRunner
        _, selected, _ = host_capacity_fixture()
        p = selected["research_work"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); workspace = root / "work"; workspace.mkdir()
            prompt = profiles.prepare_prompt("temporary failure probe", p)
            def unsupported(*args):
                ctypes.set_last_error(50)  # Explicit API double: ERROR_NOT_SUPPORTED.
                return 0
            with patch("do_math.windows_job._kernel32.SetInformationJobObject", side_effect=unsupported), \
                 patch.object(WindowsJob, "_create_suspended_root") as create:
                result = ModelRunner(codex_path=sys.executable).run(prompt=prompt, input_seal=profiles.prompt_seal(prompt),
                    output_schema={}, workspace=workspace, evidence_dir=root / "evidence", model=p["ai"]["model"],
                    effort=p["ai"]["effort"], timeout_seconds=15, execution_id="EX-setting-failure", profile=p,
                    launch_ticket=dispatched_launch('EX-setting-failure',p),
                    on_started=lambda identity: self.fail("setting failure cannot publish a live process"))
            create.assert_not_called()
            self.assertEqual(result["error_kind"], "profile_unsupported")
            self.assertEqual(result["capability_failure"]["capability"], "local_job_resources")
            self.assertEqual(result["capability_evidence"]["execution_profile_ref"], profiles.profile_ref(p))
            self.assertEqual(result["capability_evidence"]["capabilities"]["local_job_resources"]["status"], "unsupported")
            self.assertNotIn("atomic_local_job", result["capability_evidence"]["capabilities"])

    def test_both_real_adapters_receive_limits_before_user_code_or_model_call(self):
        from do_math.model_runner import ModelRunner
        _, selected, _ = host_capacity_fixture()
        for provider in ("codex", "claude"):
            p = deepcopy(selected["research_work"])
            if provider == "claude":
                p["ai"].update(provider="claude", model="claude-test")
                p = profiles.seal_profile(p)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                workspace = root / "work"; workspace.mkdir()
                prompt = profiles.prepare_prompt("temporary binding probe", p)
                started = []
                result = ModelRunner(**{provider + "_path": sys.executable}).run(prompt=prompt, input_seal=profiles.prompt_seal(prompt),
                    output_schema={}, workspace=workspace, evidence_dir=root / "evidence", model=p["ai"]["model"],
                    effort=p["ai"]["effort"], timeout_seconds=15, execution_id="EX-" + provider,
                    profile=p, should_stop=lambda: True, on_started=started.append,
                    launch_ticket=dispatched_launch('EX-'+provider,p))
                self.assertEqual(result["status"], "stopped")
                self.assertEqual(started[0]["host_resources"]["limits"], profiles.job_resource_limits(p))
                request = json.loads((root / "evidence" / "request.json").read_text(encoding="utf-8"))
                self.assertEqual(request["resource_limits"], profiles.job_resource_limits(p))
                self.assertEqual(request["profile_ref"], profiles.profile_ref(p))
                self.assertTrue(result["execution"]["collect"]["termination_barrier"]["confirmed"])
                self.assertIsNone(result["execution"]["collect"]["worker_status"])

    def test_real_creation_failure_and_normal_abnormal_termination_return_once(self):
        from do_math.windows_job import process_identity
        for outcome in ("creation_failure", "normal", "nonzero", "terminated", "setting_failure"):
            instance, selected, _ = host_capacity_fixture()
            runtime = {"executions": {}, "reservations": {}}
            slots = SessionSlots(runtime, instance)
            p = selected["formal_check"]
            e = {"id": "EX-" + outcome, "role": p["role"], "status": "queued"}
            self.assertTrue(slots.acquire(e["id"], profile=p, execution=e))
            with tempfile.TemporaryDirectory() as directory:
                marker = Path(directory) / "started"
                code = f"from pathlib import Path; import sys,time; Path({str(marker)!r}).write_text('started'); "
                code += "time.sleep(30)" if outcome == "terminated" else "sys.exit(7)" if outcome == "nonzero" else "pass"
                argv = [str(Path(directory) / "absent.exe")] if outcome == "creation_failure" else [sys.executable, "-c", code]
                kwargs = {"resource_limits": profiles.job_resource_limits(p), "name": e['launch_ticket']['job_name']}
                if outcome == "setting_failure":
                    with patch("do_math.windows_job._kernel32.SetInformationJobObject", return_value=0):
                        with self.assertRaises(OSError): WindowsJob(argv, **kwargs)
                    self.assertFalse(marker.exists())
                elif outcome == "creation_failure":
                    with self.assertRaises(OSError): WindowsJob(argv, **kwargs)
                    self.assertFalse(marker.exists())
                else:
                    with WindowsJob(argv, **kwargs) as job:
                        slots.started(e["id"], {**process_identity(job), "job_name": job.name},
                                      at="2026-09-20T00:00:00Z")
                        self.assertFalse(slots.release(e["id"]), "a suspended but live Job must retain capacity")
                        job.resume()
                        if outcome == "terminated": job.terminate()
                        self.assertTrue(job.wait(15))
                        deadline = time.monotonic() + 10
                        while job.inspect().active_processes and time.monotonic() < deadline: time.sleep(.02)
                        self.assertEqual(job.inspect().active_processes, 0)
                        self.assertTrue(slots.release(e["id"]))
                self.assertTrue(slots.release(e["id"], reason=outcome))
                once = deepcopy(runtime)
                self.assertTrue(slots.release(e["id"], reason="replayed return"))
                self.assertEqual(runtime, once)
                self.assertTrue(all(r["reserved"] == r["returned"] and r["state"] == "settled"
                                    for r in runtime["reservations"].values()))

    def test_native_process_identity_round_trips_without_integer_precision_loss(self):
        from do_math.canonical import canonical_json
        from do_math.windows_job import process_identity
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
            limits = {"memory_bytes": 128 * 1024**2, "cpu_rate_basis_points": 2000}
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
        samples = []
        with tempfile.TemporaryDirectory() as directory:
            for cap in (None, 10):
                output = Path(directory) / (str(cap) + ".json")
                code = "\n".join(["import time,json", "from pathlib import Path",
                    "wall=time.monotonic(); cpu=time.process_time()", "while time.monotonic()-wall<3: pass",
                    f"Path({str(output)!r}).write_text(json.dumps({{'wall':time.monotonic()-wall,'cpu':time.process_time()-cpu}}))"])
                limits = None if cap is None else {"memory_bytes": 128 * 1024**2, "cpu_rate_basis_points": cap}
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
        with patch.object(WindowsJob, "_create_suspended_root") as create:
            with self.assertRaises(ValueError):
                WindowsJob([sys.executable, "-c", "pass"],
                    resource_limits={"memory_bytes": 0, "cpu_rate_basis_points": 0})
            create.assert_not_called()
        with patch("do_math.windows_job._kernel32.SetInformationJobObject", return_value=0), \
             patch.object(WindowsJob, "_create_suspended_root") as create:
            with self.assertRaises(OSError):
                WindowsJob([sys.executable, "-c", "pass"],
                    resource_limits={"memory_bytes": 128 * 1024**2, "cpu_rate_basis_points": 1000})
            create.assert_not_called()


class HostConfigurationTests(unittest.TestCase):
    def test_host_demands_accept_only_capped_roles(self):
        from do_math.configuration import validate_config
        config = self.configuration()
        validate_config(config)
        profiles = execution_profiles.build_profiles(config)['execution_profiles']
        self.assertTrue(all('host_resources' not in p for p in profiles.values()
            if p['role'] in {'formal_check','trust_check','trust_activate'}))
        invalid = deepcopy(config)
        invalid['host_resources']['demands_by_role']['formal_check'] = {'jobs': 1, 'memory_bytes': 100, 'cpu_rate_basis_points': 100}
        with self.assertRaisesRegex(ValueError, 'capped roles only'):
            validate_config(invalid)
        config['host_resources']['demands_by_role'].pop('research_work')
        with self.assertRaisesRegex(ValueError, 'capped role'):
            validate_config(config)

    def test_unstarted_role_defaults_refresh_while_task_profiles_require_preparation(self):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.initialization import initialize_state
        from do_math.contracts import task_candidate_record
        from research_fixtures import bare_engine, candidate
        with tempfile.TemporaryDirectory() as directory:
            config = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}
            instance, runtime = initialize_state(instance_id='RI-host-change', goal='Test profiles', workspace=Path(directory), config=config, source_input='Test profiles', created_at='2026-09-23T00:00:00Z')
            instance.update(execution_profiles.build_profiles(config))
            old = deepcopy(instance['role_profile_refs']['maintenance'][0])
            wire = candidate()
            wire['profile_refs'] = [deepcopy(instance['role_profile_refs']['research_work'][0])]
            task = task_candidate_record(wire, task_id='TK-pinned')
            task.update(status='planned', results=[], reviews=[])
            runtime['tasks'][task['id']] = task
            runtime['queue'] = [{'id':'AC-default','role':'maintenance','profile_ref':old}]
            changed, state = bare_engine()._configure_candidate(instance, runtime,
                {'config':{'host_resources':self.configuration()['host_resources']}})
            pending = next(a for a in state['queue'] if a['id']=='AC-default')
            self.assertNotEqual(pending['profile_ref'], old)
            self.assertEqual(state['tasks'][task['id']]['profile_refs'], task['profile_refs'])
            self.assertTrue(any(task['id'] in a.get('revision_targets', {}) for a in state['queue']))

    def configuration(self):
        import platform
        from do_math.configuration import DEFAULT_CONFIG
        settings = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}
        roles = execution_profiles.build_profiles(settings)['role_profile_refs']
        host = execution_profiles.host_constraint(host_id=platform.node(),
            limits={'jobs': 4, 'memory_bytes': 536870912, 'cpu_rate_basis_points': 8000},
            control_reserve={'jobs': 1, 'memory_bytes': 134217728, 'cpu_rate_basis_points': 2000},
            authority_refs=['configuration:request'])
        settings['host_resources'] = {'constraint': host, 'demands_by_role': {role:
            {'jobs': 1, 'memory_bytes': 134217728, 'cpu_rate_basis_points': 2000} for role in roles if role in execution_profiles.HOST_ROLES}}
        return settings

    def test_public_init_configure_and_removal(self):
        from do_math.repository import ResearchRepository
        from research_fixtures import bare_engine, new_instance
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = self.configuration()
            instance_id = new_instance(root, goal='Temporary configuration test', workspace=root/'workspace', config=settings)
            store = ResearchRepository(root, instance_id)
            head, instance, runtime = store.load()
            host_id = instance['host_capacity_ref']
            approval = instance['capacity_constraints'][host_id]['authority_refs'][0]
            self.assertEqual(instance['governance_sources'][approval]['origin'], 'user')
            self.assertNotEqual(approval, 'configuration:request')
            host = bare_engine()
            same, state = host._configure_candidate(instance, runtime, {'config': {'host_resources': settings['host_resources']}})
            self.assertEqual(same['host_capacity_ref'], host_id)
            with self.assertRaisesRegex(ValueError, 'user'):
                host._configure_candidate(instance, runtime, {'origin': 'operator', 'config': {'host_resources': None}})
            # Public admission refuses the same operator change instead of queueing a request application rejects.
            from do_math.engine import control
            with self.assertRaisesRegex(ValueError, 'user decision'):
                control(root, instance_id, 'configure', config={'host_resources': None}, origin='operator')
            held = deepcopy(runtime)
            held['executions']['EX-live'] = {'id': 'EX-live', 'status': 'queued'}
            with self.assertRaisesRegex(ValueError, 'stopped'):
                host._configure_candidate(instance, held, {'config': {'host_resources': None}})
            removed, state = host._configure_candidate(instance, runtime, {'config': {'host_resources': None}})
            self.assertNotIn('host_capacity_ref', removed)
            self.assertIn(host_id, removed['capacity_constraints'])
            saved = store.save_with_state(head, removed, state)[0]
            self.assertIsNone(store.load(saved)[1]['config']['host_resources'])
            for profile in same['execution_profiles'].values():
                if profile['role'] in {'formal_check', 'trust_check', 'trust_activate'}:
                    self.assertNotIn('host_resources', profile)

    def test_host_configuration_builds_profiles_once_per_step(self):
        # Admission only checks the host section; initialization and application each author the editions once.
        from do_math.engine import control
        from do_math.repository import ResearchRepository
        from research_fixtures import bare_engine, new_instance
        build = execution_profiles.build_profiles
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = self.configuration()
            request = {'host_resources': settings['host_resources']}
            with patch.object(execution_profiles, 'build_profiles', wraps=build) as built:
                instance_id = new_instance(root, goal='Profile count test', workspace=root/'workspace', config=settings)
            self.assertEqual(built.call_count, 1)
            head, instance, runtime = ResearchRepository(root, instance_id).load()
            with patch.object(execution_profiles, 'build_profiles', wraps=build) as built:
                control(root, instance_id, 'configure', config=request)
            self.assertEqual(built.call_count, 0)
            with patch.object(execution_profiles, 'build_profiles', wraps=build) as built:
                bare_engine()._configure_candidate(instance, runtime, {'config': request})
            self.assertEqual(built.call_count, 1)


if __name__ == "__main__":
    unittest.main()

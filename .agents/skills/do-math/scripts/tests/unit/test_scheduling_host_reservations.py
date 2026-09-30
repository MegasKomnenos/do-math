"""Local instance reservations under an approved host constraint (``session_slots``, ``execution_profiles``, layer 2).

A host approval (jobs, commit memory, CPU rate and the controller's reserve)
is adopted as the instance's ``host_capacity_ref``; capped roles bind their
demands to it. ``SessionSlots.acquire`` reserves the model slot and the host
units of one execution at once, and ``release`` settles them exactly once and
only after the local Job's end is confirmed. The slots run on the clock and
Jobs port fakes (``scheduling_hosts``); the storage cases run the real stores
on the in-process Git backend. All numbers are disposable test budgets, never
product defaults.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

from do_math import execution_profiles as profiles
from do_math.activities import assign_execution, open_activity
from do_math.canonical import canonical_json
from do_math.configuration import validate_config
from do_math.execution_lifecycle import create_execution, transition_execution
from do_math.git_store import GitStateStore, GitStateStoreConflict
from do_math.repository import ResearchRepository
from do_math.windows_job import process_identity
from provider_fixtures import PROFILE_CONFIG, host_capacity_fixture
from research_fixtures import current_state
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit, make_repository
from support.fakes.jobs import FakeJobs
from support.scheduling_hosts import UnknownJobs, admit, host_configuration, host_slots

INSTANCE_ID = "RI-00000000000000000000000000"
HOST_UNITS = {"jobs", "memory_bytes", "cpu_rate_basis_points"}


class HostReservations(unittest.TestCase):
    def test_work_operations_machine_share_capacity_and_preserve_control(self):
        instance, selected, constraint = host_capacity_fixture()
        runtime = {"executions": {}, "reservations": {}}
        slots = host_slots(runtime, instance)
        for n, role in enumerate(selected):
            accepted, execution = admit(slots, "EX-" + str(n), selected[role])
            self.assertTrue(accepted)
            self.assertEqual(execution["status"], "starting")
        before = deepcopy(runtime)
        self.assertFalse(admit(slots, "EX-extra", selected["formal_check"])[0])
        self.assertEqual(runtime, before)

        def units(eid):
            return {r["unit"] for r in runtime["reservations"].values() if r["owner_id"] == eid}
        self.assertEqual(units("EX-0"), HOST_UNITS | {"execution"})
        self.assertEqual(units("EX-1"), HOST_UNITS, "an operational role reserves no model slot")
        machine_rows = [r for r in runtime["reservations"].values() if r["owner_id"] == "EX-2"]
        self.assertEqual({r["unit"] for r in machine_rows}, HOST_UNITS)
        self.assertTrue(all(r["constraint_id"] == constraint["id"] for r in machine_rows))
        self.assertIsNone(runtime["executions"]["EX-2"]["capacity"]["provider"])
        self.assertTrue(slots.release("EX-2", reason="creation failed before resume"))
        once = deepcopy(runtime)
        self.assertTrue(slots.release("EX-2", reason="repeat return"))
        self.assertEqual(runtime, once)
        self.assertTrue(admit(slots, "EX-next", selected["formal_check"])[0])

    def test_each_constraint_refuses_without_partial_ai_or_host_records(self):
        for unit, amount in (("jobs", 0), ("memory_bytes", 1), ("cpu_rate_basis_points", 1)):
            with self.subTest(unit=unit):
                instance, selected, constraint = host_capacity_fixture()
                # Author a new approval, rather than mutate a content-addressed row.
                limits = {"jobs": constraint["max_jobs"], "memory_bytes": constraint["memory_bytes"],
                          "cpu_rate_basis_points": constraint["cpu_rate_basis_points"]}
                limits[unit] = amount
                limited = profiles.host_constraint(host_id=constraint["host_id"], limits=limits,
                                                   control_reserve={k: 0 for k in limits},
                                                   authority_refs=["GS-host-refusal-test"])
                instance["capacity_constraints"][limited["id"]] = limited
                instance["host_capacity_ref"] = limited["id"]
                p = profiles.with_host_resources(selected["research_work"], limited,
                                                 {"jobs": 1, "memory_bytes": 128 * 1024**2, "cpu_rate_basis_points": 2000})
                instance["execution_profiles"][p["id"]] = p
                runtime = {"executions": {}, "reservations": {}}
                slots = host_slots(runtime, instance)
                before = deepcopy(runtime)
                self.assertFalse(admit(slots, "EX-refused", p)[0])
                self.assertEqual(runtime, before)

    def test_no_approval_stays_unmeasured_machine_has_no_ai_budget(self):
        instance = profiles.build_profiles(PROFILE_CONFIG)
        p = next(p for p in instance["execution_profiles"].values() if p["role"] == "formal_check")
        self.assertIsNone(profiles.job_resource_limits(p))
        self.assertEqual(p["host_capacity_status"], "unmeasured_not_enforced")
        runtime = {"executions": {}, "reservations": {}}
        self.assertTrue(admit(host_slots(runtime, instance), "EX-machine", p)[0])
        self.assertEqual(runtime["reservations"], {})

    def test_other_host_refused_and_unknown_termination_retains_reservations(self):
        instance, selected, constraint = host_capacity_fixture()
        runtime = {"executions": {}, "reservations": {}}
        # An approval adopted for another host: its bound profile names that host, not this one.
        elsewhere = deepcopy(instance)
        foreign = profiles.host_constraint(host_id="different-host",
            limits={"jobs": constraint["max_jobs"], "memory_bytes": constraint["memory_bytes"],
                    "cpu_rate_basis_points": constraint["cpu_rate_basis_points"]},
            control_reserve=constraint["control_reserve"], authority_refs=constraint["authority_refs"])
        elsewhere["capacity_constraints"][foreign["id"]] = foreign
        elsewhere["host_capacity_ref"] = foreign["id"]
        wrong = profiles.with_host_resources(selected["formal_check"], foreign,
                                             selected["formal_check"]["host_resources"]["demands"])
        elsewhere["execution_profiles"][wrong["id"]] = wrong
        with self.assertRaisesRegex(ValueError, "profile host differs from this local host"):
            admit(host_slots(runtime, elsewhere), "EX-wrong", wrong)
        self.assertEqual(runtime["executions"], {})
        slots = host_slots(runtime, instance, jobs=UnknownJobs())
        self.assertTrue(admit(slots, "EX-unknown", selected["formal_check"])[0])
        slots.started("EX-unknown", {"job_name": runtime['executions']['EX-unknown']['launch_ticket']['job_name']},
                      at="2026-09-20T00:00:00Z")
        self.assertFalse(slots.release("EX-unknown"))
        self.assertEqual(runtime["executions"]["EX-unknown"]["capacity"]["local_termination"], "unknown")
        self.assertTrue(runtime["reservations"])
        self.assertTrue(all(r["state"] == "held" for r in runtime["reservations"].values()))

    def test_actual_git_cas_publishes_start_and_all_demands_together(self):
        # The store's publication (one commit, one compare-and-swap of the ref) on the
        # Git port fake; repository schema integration is the round trip below.
        instance, selected, _ = host_capacity_fixture()
        runtime = {"executions": {}, "reservations": {}}
        with tempfile.TemporaryDirectory() as directory:
            store = GitStateStore(make_repository(Path(directory) / "repository"), INSTANCE_ID,
                                  backend=InProcessGit(), clock=FakeClock())
            head = store.publish(None, {"research/approval.json": canonical_json(instance),
                                        "runtime/initial.json": b"{}"}).head
            slots = host_slots(runtime, instance)
            stale = head
            for index, role in enumerate(selected):
                eid = "EX-" + str(index)
                self.assertTrue(admit(slots, eid, selected[role])[0])
                changes = {"runtime/executions/" + eid + ".json": canonical_json(runtime["executions"][eid])}
                changes.update({"runtime/reservations/" + rid + ".json": canonical_json(row)
                                for rid, row in runtime["reservations"].items() if row["owner_id"] == eid})
                stale = head
                with store.writer_lock():
                    head = store.publish(head, changes).head
                published = json.loads(store.read_bytes(head, "runtime/executions/" + eid + ".json"))
                self.assertEqual(published["status"], "starting")
                self.assertEqual(len(published["capacity"]["reservation_ids"]), len(changes) - 1)
                for rid in published["capacity"]["reservation_ids"]:
                    self.assertEqual(json.loads(store.read_bytes(head, "runtime/reservations/" + rid + ".json"))["state"],
                                     "held")
            before = deepcopy(runtime)
            self.assertFalse(admit(slots, "EX-denied", selected["formal_check"])[0])
            self.assertEqual(runtime, before)
            self.assertEqual(store.read_snapshot().head, head)
            with self.assertRaisesRegex(GitStateStoreConflict, "compare-and-swap"):
                store.publish(stale, {"runtime/stale.json": b"{}"})
            self.assertEqual(store.read_snapshot().head, head)

    def test_old_profile_editions_do_not_open_an_independent_host_pool(self):
        instance, selected, constraint = host_capacity_fixture()
        runtime = {"executions": {}, "reservations": {}}
        slots = host_slots(runtime, instance)
        for n in range(3):
            self.assertTrue(admit(slots, "EX-" + str(n), selected["formal_check"])[0])
        changed = profiles.host_constraint(host_id=constraint["host_id"],
            limits={"jobs": 4, "memory_bytes": 512 * 1024**2, "cpu_rate_basis_points": 8000},
            control_reserve=constraint["control_reserve"], authority_refs=["GS-host-next-test"])
        instance["capacity_constraints"][changed["id"]] = changed
        instance["host_capacity_ref"] = changed["id"]
        p = profiles.with_host_resources(selected["formal_check"], changed,
                                         selected["formal_check"]["host_resources"]["demands"])
        instance["execution_profiles"][p["id"]] = p
        self.assertFalse(admit(slots, "EX-escape", p)[0])

    def test_unbound_profiles_cannot_bypass_shared_approval(self):
        instance, _, _ = host_capacity_fixture()
        unbound = next(p for p in instance["execution_profiles"].values() if not p.get("host_capacity_refs"))
        runtime = {"executions": {}, "reservations": {}}
        with self.assertRaisesRegex(ValueError, "current adopted host"):
            admit(host_slots(runtime, instance), "EX-bypass", unbound)
        self.assertEqual(runtime, {"executions": {}, "reservations": {}})

    def test_explicit_authoring_covers_every_capped_role(self):
        _, _, constraint = host_capacity_fixture()
        bare = profiles.build_profiles(PROFILE_CONFIG)
        demands = {p["role"]: {"jobs": 1, "memory_bytes": 128 * 1024**2, "cpu_rate_basis_points": 1000}
                   for p in bare["execution_profiles"].values() if p["role"] in profiles.HOST_ROLES}
        config = {**PROFILE_CONFIG, "host_resources": {"constraint": constraint, "demands_by_role": demands}}
        instance = profiles.build_profiles(config)
        self.assertEqual(instance["host_capacity_ref"], constraint["id"])
        self.assertTrue(all(p["host_capacity_refs"] == ([] if p['role'] in {'formal_check', 'trust_check', 'trust_activate'}
                                                        else [constraint["id"]])
                            for p in instance["execution_profiles"].values()))
        p = next(p for p in instance["execution_profiles"].values() if p["role"] == "research_work")
        runtime = {"executions": {}, "reservations": {}}
        slots = host_slots(runtime, instance)
        for n in range(2):
            self.assertTrue(admit(slots, "EX-call-" + str(n), p)[0])
            self.assertTrue(slots.release("EX-call-" + str(n)))
        self.assertTrue(admit(slots, "EX-call-extra", p)[0])
        machine = next(p for p in instance["execution_profiles"].values() if p["role"] == "formal_check")
        self.assertTrue(admit(slots, "EX-machine", machine)[0])
        self.assertEqual({r["unit"] for r in runtime["reservations"].values() if r["owner_id"] == "EX-machine"}, set())
        bad = deepcopy(config)
        del bad["host_resources"]["demands_by_role"]["research_work"]
        with self.assertRaisesRegex(ValueError, "every capped role"):
            profiles.build_profiles(bad)

    def test_legacy_host_capped_lean_profile_requires_replacement(self):
        _, _, constraint = host_capacity_fixture()
        authored = profiles.build_profiles({**PROFILE_CONFIG, "lean_command": [sys.executable]})
        p = next(p for p in authored["execution_profiles"].values() if p["role"] == "formal_check")
        p = profiles.with_host_resources(p, constraint, {"jobs": 1, "memory_bytes": 128 * 1024**2,
                                                         "cpu_rate_basis_points": 2000})
        environment = {"toolchain": {"configured_command": [sys.executable]}}
        with self.assertRaisesRegex(ValueError, "uncapped profile"):
            profiles.machine_invocation(p, trust_environment=environment)
        with self.assertRaisesRegex(ValueError, "uncapped profile"):
            profiles.machine_invocation(p, trust_environment=environment, on_started=lambda identity: None)


def marker_program(argv, cwd, env):
    """The Job's user code: it writes the marker its argv names."""
    Path(argv[-1]).write_text('ok')
    return 0


class HostRepositoryContract(unittest.TestCase):
    def test_positive_host_records_pass_real_repository_and_round_trip(self):
        """The host reservation records pass the storage contract, the Job's identity is published before it resumes, and settlement is once.

        About 0.2 s, at the 0.2 s unit budget: five publications of a full state through the storage contract are the case.
        """
        instance, selected, _ = host_capacity_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            instance.update(id=INSTANCE_ID, workspace=directory, config={})
            instance, runtime = current_state(instance, {"status": "ready", "executions": {}, "reservations": {},
                                                         "provider_waits": {}})
            repo = ResearchRepository(make_repository(root / "repository"), INSTANCE_ID, backend=InProcessGit(),
                                      clock=FakeClock())
            head = repo.initialize(instance, runtime)
            p = selected["formal_check"]
            open_activity(runtime, activity_id="AT-host", activity_kind="formal_check", owner_ref="engine",
                          input_refs=[], opened_at="2026-09-20T00:00:00Z")
            e = create_execution(execution_id="EX-host-roundtrip", owner_activity_id="AT-host", actor_kind="machine",
                                 input_manifest={}, profile_ref=profiles.profile_ref(p), created_at="2026-09-20T00:00:00Z")
            e["role"] = p["role"]
            assign_execution(runtime, "AT-host", e)
            jobs = FakeJobs([(lambda argv: argv[:1] == ['user-code'], marker_program)])
            slots = host_slots(runtime, instance, jobs=jobs)
            with repo.writer_lock():
                self.assertTrue(slots.acquire(e["id"], profile=p, execution=e))
                head = repo.save_with_state(head, instance, runtime)[0]
            loaded_head, _, loaded = repo.load()
            self.assertEqual(loaded_head, head)
            self.assertEqual(loaded["executions"][e["id"]]["status"], "starting")
            self.assertEqual(len(loaded["executions"][e["id"]]["capacity"]["reservation_ids"]), 3)
            marker = root / "user-started"
            with jobs.launch(['user-code', str(marker)], resource_limits=profiles.job_resource_limits(p),
                             name=e['launch_ticket']['job_name']) as job:
                with repo.writer_lock():
                    slots.started(e["id"], {**process_identity(job), "job_name": job.name,
                                            "host_resources": job.resource_usage()}, at="2026-09-20T00:00:30Z")
                    head = repo.save_with_state(head, instance, runtime)[0]
                self.assertFalse(marker.exists(), "user code must wait for the published identity")
                self.assertEqual(repo.load()[2]["executions"][e["id"]]["capacity"]["process"]["job_name"], job.name)
                self.assertFalse(slots.release(e["id"]), "a suspended but live Job must retain capacity")
                job.resume()
                self.assertTrue(job.wait(15))
                self.assertTrue(marker.exists())
                with repo.writer_lock():
                    self.assertTrue(slots.release(e["id"]))
                    transition_execution(e, "stopping", at="2026-09-20T00:01:00Z")
                    transition_execution(e, "ended", at="2026-09-20T00:01:01Z", outcome="execution_incomplete")
                    head = repo.save_with_state(head, instance, runtime)[0]
                    self.assertTrue(slots.release(e["id"], reason="repeat settlement"))
                    self.assertEqual(repo.save_with_state(head, instance, runtime)[0], head)
                _, _, after = repo.load()
                self.assertEqual(len(after["reservations"]), 3)
                self.assertTrue(all(row["reserved"] == row["returned"] for row in after["reservations"].values()))


class AdmissionClockTests(unittest.TestCase):
    def test_admission_transition_preserves_native_utc_precision(self):
        from datetime import datetime, timezone
        from types import SimpleNamespace
        from do_math.configuration import DEFAULT_CONFIG
        instant = datetime(2026, 9, 23, 0, 0, 0, 997259, tzinfo=timezone.utc)
        instance = profiles.build_profiles(DEFAULT_CONFIG)
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'formal_check')
        runtime = {'executions': {}, 'reservations': {}}
        execution = create_execution(execution_id='EX-precision', owner_activity_id='AY-precision', actor_kind='machine',
                                     input_manifest=[], profile_ref=profiles.profile_ref(profile),
                                     created_at=instant.isoformat())
        execution['role'] = 'formal_check'
        # The clock port's wall time and its nanoseconds disagree by one microsecond:
        # the transition must record the wall time itself, not a value rebuilt from nanoseconds.
        clock = SimpleNamespace(wall=lambda: instant, wall_ns=lambda: int((instant.timestamp() - .000001) * 10**9),
                                random_hex=lambda nbytes: '0f' * nbytes)
        from do_math.session_slots import SessionSlots
        slots = SessionSlots(runtime, instance, clock=clock, jobs=FakeJobs())
        self.assertTrue(slots.acquire(execution['id'], profile=profile, execution=execution))
        self.assertEqual(execution['transitions'][-1]['at'], instant.isoformat())


class HostConfigurationTests(unittest.TestCase):
    def test_host_demands_accept_only_capped_roles(self):
        config = host_configuration()
        validate_config(config)
        built = profiles.build_profiles(config)['execution_profiles']
        self.assertTrue(all('host_resources' not in p for p in built.values()
                            if p['role'] in {'formal_check', 'trust_check', 'trust_activate'}))
        invalid = deepcopy(config)
        invalid['host_resources']['demands_by_role']['formal_check'] = {'jobs': 1, 'memory_bytes': 100,
                                                                       'cpu_rate_basis_points': 100}
        with self.assertRaisesRegex(ValueError, 'capped roles only'):
            validate_config(invalid)
        config['host_resources']['demands_by_role'].pop('research_work')
        with self.assertRaisesRegex(ValueError, 'capped role'):
            validate_config(config)


if __name__ == "__main__":
    unittest.main()

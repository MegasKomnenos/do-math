"""Git-backed local execution reservations shared by engine and recovery.

The repository writer lock and single CAS own admission. Local Job evidence
settles local capacity; it proves neither remote termination nor provider use.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import time


def _lock(path: Path):
    stream = path.open("a+b")
    if path.stat().st_size == 0:
        stream.write(b"0"); stream.flush()
    stream.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        stream.close()
        return None
    return stream


def _unlock(stream):
    if stream is None:
        return
    stream.seek(0)
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    stream.close()


class GitSessionSlots:
    """A working view of the Git execution/reservation families.

    The caller holds ResearchRepository.writer_lock for every mutation and
    publishes the candidate runtime through one save/CAS before starting a Job.
    Read-only views never reconcile or create files. No counter or local SQL
    database is authoritative for this path.
    """

    def __init__(self, runtime: dict, instance: dict, *, observer=False):
        self.runtime, self.instance, self.observer = runtime, instance, observer
        self.admission_reason = None

    def _writable(self):
        if self.observer:
            raise ValueError("a read-only slot observer cannot mutate reservations")

    def admission_available(self, profile):
        """Evaluate the actual admission calculation on detached ledger data.

        A ready result is not a reservation. The real acquire repeats the check
        while publishing its execution and reservations under the writer lock.
        """
        from copy import deepcopy
        from .repository import new_id
        runtime = {"executions": {},
                   "reservations": deepcopy(self.runtime.get("reservations", {})),
                   "provider_waits": deepcopy(self.runtime.get("provider_waits", {}))}
        candidate = {"id": new_id("EX"), "role": profile["role"], "status": "queued"}
        return GitSessionSlots(runtime, self.instance).acquire(
            candidate["id"], profile["budget_kind"], profile.get("ai", {}).get("model"),
            profile=profile, execution=candidate)

    def configure(self, limits):
        self._writable()
        from .execution_profiles import build_profiles
        authored = build_profiles({**self.instance["config"], "session_limits": limits})
        if self.instance.get("host_capacity_ref") and authored.get("host_capacity_ref") != self.instance["host_capacity_ref"]:
            raise ValueError("session reconfiguration cannot drop or change the adopted host constraint")
        # Old immutable profiles remain available to already admitted executions.
        self.instance.setdefault("execution_profiles", {}).update(authored["execution_profiles"])
        self.instance.setdefault("capacity_constraints", {}).update(authored["capacity_constraints"])
        self.instance["role_profile_refs"] = authored["role_profile_refs"]
        if authored.get("host_capacity_ref"):
            self.instance["host_capacity_ref"] = authored["host_capacity_ref"]
        else:
            self.instance.pop('host_capacity_ref', None)

    def acquire(self, execution_id, pool, model, *, profile=None, execution=None, provider=None,
                enforce_capacity=True, current_time=None):
        self._writable()
        from copy import deepcopy
        from .execution_profiles import (bind_execution, resolve_profile, profile_ref,
                                         job_resource_limits, validate_host_constraint)
        from .budget import plan_reservations, BudgetConflict, ReservationPlan
        if profile is None or execution is None:
            raise ValueError("Git admission requires the selected profile and starting execution")
        profile = resolve_profile(self.instance["execution_profiles"], profile_ref(profile))
        approved_host = self.instance.get("host_capacity_ref")
        uncapped_lean = (profile['actor_kind']=='machine'
                        and profile['role'] in {'formal_check','trust_check','trust_activate'}
                        and profile.get('host_resources') is None)
        if profile.get("host_capacity_refs", []) != ([approved_host] if approved_host and not uncapped_lean else []):
            raise ValueError("execution profile must bind the instance's current adopted host constraint")
        if profile["budget_kind"] != pool or profile.get("ai", {}).get("model") != model:
            raise ValueError("admission differs from the pinned profile")
        if execution.get("id") != execution_id:
            raise ValueError("execution identity differs from admission")
        existing = self.runtime.get("executions", {}).get(execution_id)
        if existing is not None and (existing is not execution or "capacity" in existing
                                     or existing.get("status") not in {"queued", "starting"}):
            raise ValueError("execution IDs are single-use; only the registered unreserved execution can be admitted")
        current = time.time() if current_time is None else current_time
        job_resource_limits(profile)  # Reject a profile bound to another host before any mutation.
        ai = profile.get("ai", {})
        expected_provider = ai.get("provider")
        if provider is not None and provider != expected_provider:
            raise ValueError("provider differs from profile")
        provider = expected_provider
        gate = self.runtime.get("provider_waits", {}).get("PW-" + provider) if provider else None
        if gate and (gate["state"] == "checking" or gate["state"] == "waiting" and gate["retry_at"] > current):
            self.admission_reason = "provider_limit"
            return False
        # A new capacity edition must still count executions reserved under older
        # editions of the same model. Limits are not independent resource pools.
        constraints = self.instance["capacity_constraints"]
        reservations = deepcopy(self.runtime.get("reservations", {}))
        refs = ai.get("capacity_refs", []) + ai.get("usage_constraint_ids", [])
        host_refs = profile.get("host_capacity_refs", [])
        for ref in host_refs:
            validate_host_constraint(constraints[ref])
            if any(profile["host_resources"][k] != constraints[ref][k] for k in ("scope", "host_id")):
                raise ValueError("profile and approved host scope differ")
        for row in reservations.values():
            previous = constraints.get(row["constraint_id"], {})
            for ref in refs + host_refs:
                constraint = constraints[ref]
                same_pool = (previous.get("kind") == constraint["kind"] == "cumulative"
                             and previous.get("budget_kind") == constraint["budget_kind"]
                             and previous.get("unit") == constraint["unit"])
                same_model = (previous.get("kind") == constraint["kind"] == "concurrency"
                              and previous.get("model") == constraint["model"])
                same_host = (previous.get("kind") == constraint["kind"] == "host"
                             and previous.get("scope") == constraint.get("scope") == "instance_on_host"
                             and previous.get("host_id") == constraint.get("host_id"))
                if same_pool or same_model or same_host:
                    row["constraint_id"] = ref
        demands = [{"id": "RS-" + execution_id + "-" + str(i), "constraint_id": ref,
                    "unit": constraints[ref].get("accounting_unit", constraints[ref].get("unit")), "amount": 1}
                   for i, ref in enumerate(refs)]
        for ref in host_refs:
            demands.extend({"id": "RS-" + execution_id + "-host-" + unit,
                "constraint_id": ref, "unit": unit, "amount": amount}
                for unit, amount in profile["host_resources"]["demands"].items())
        request = {"budget_kind": pool, "owner_kind": "execution", "owner_id": execution_id,
                   "purpose": "normal", "authority_refs": [profile_ref(profile)],
                   "reobserve": {"on": "local_termination_barrier"}, "demands": demands}
        try:
            plan = (plan_reservations({"reservations": reservations},
                                     {"constraints": list(constraints.values())}, profile, request)
                    if demands else ReservationPlan((), False, ()))
        except BudgetConflict:
            self.admission_reason = "capacity"
            return False
        candidate = deepcopy(execution)
        bind_execution(candidate, profile)
        if "actor_kind" in candidate:
            from .execution_lifecycle import transition_execution
            from datetime import datetime, timezone
            admitted_at = (datetime.now(timezone.utc) if current_time is None
                           else datetime.fromtimestamp(current, timezone.utc))
            transition_execution(candidate, "starting", at=admitted_at.isoformat())
        else:
            candidate["status"] = "starting"
        candidate["capacity"] = {"reservation_ids": [r["id"] for r in plan.records],
                                 "provider": provider, "process": None, "local_termination": "unknown"}
        self.runtime.setdefault("reservations", {}).update({r["id"]: r for r in plan.records})
        self.runtime.setdefault("executions", {})[execution_id] = candidate
        if gate and gate["state"] == "waiting":
            gate.update(state="checking", probe_owner=execution_id, probe_started_at=int(current))
        execution.clear()
        execution.update(candidate)
        self.runtime["executions"][execution_id] = execution
        self.admission_reason = None
        return True

    def started(self, execution_id, identity):
        self._writable()
        from copy import deepcopy
        execution = self.runtime["executions"][execution_id]
        capacity = execution["capacity"]
        if capacity["process"] is not None:
            if capacity["process"] == identity:
                return
            raise ValueError("execution process identity is already fixed")
        if not identity.get("job_name"):
            raise ValueError("started execution requires the named local Job")
        capacity["process"] = deepcopy(identity)

    def release(self, execution_id, *, reason="local runner returned after termination"):
        self._writable()
        from .budget import settle_reservation
        execution = self.runtime.get("executions", {}).get(execution_id)
        if not execution or "capacity" not in execution:
            return False
        capacity = execution["capacity"]
        if capacity["local_termination"] == "confirmed":
            return True
        identity = capacity["process"]
        if identity:
            from .windows_job import named_job_empty
            if named_job_empty(identity["job_name"]) is not True:
                capacity["local_termination"] = "unknown"
                return False
        # No process means on_started was never acknowledged; the suspended Job
        # cannot have resumed. The engine must preserve that ordering.
        evidence = [{"execution_id": execution_id, "job_name": identity.get("job_name") if identity else None,
                     "kind": "local_job_empty" if identity else "never_resumed", "reason": reason}]
        updates = {}
        for rid in capacity["reservation_ids"]:
            record = self.runtime["reservations"][rid]
            # The approved call mode counts admitted local attempts, including
            # unsuccessful starts. Returning a concurrency slot does not refund it.
            consumed = record["reserved"] if record["unit"] == "local_execution_attempt" else 0
            updates[rid] = settle_reservation({"reservations": self.runtime["reservations"]}, rid,
                confirmed_consumed=consumed, returned=record["reserved"] - consumed, evidence_refs=evidence).record
        self.runtime["reservations"].update(updates)
        capacity["local_termination"] = "confirmed"
        for gate in self.runtime.get("provider_waits", {}).values():
            if gate["state"] == "checking" and gate["probe_owner"] == execution_id:
                # Releasing a local slot is no evidence that a provider recovered.
                gate.update(state="waiting", probe_owner=None, probe_started_at=None)
        return True

    def provider_result(self, execution_id, provider, *, failure=None, response_observed=True,
                        current_time=None, initial_seconds=300, maximum_seconds=7200):
        self._writable()
        from .provider_wait import retry_time
        import math
        current = time.time() if current_time is None else current_time
        execution = self.runtime.get("executions", {}).get(execution_id, {})
        if execution.get("capacity", {}).get("provider") != provider:
            raise ValueError("provider result has no matching admitted execution")
        rows = self.runtime.setdefault("provider_waits", {})
        row = rows.get("PW-" + provider)
        if failure is not None:
            if failure.get("kind") != "provider_limit" or failure.get("provider") != provider:
                raise ValueError("provider failure differs from admission")
            attempts = 1 if not row or row["state"] == "available" else row["attempts"] + int(
                row["state"] == "checking" and row["probe_owner"] == execution_id)
            retry_at = math.ceil(retry_time(failure, attempts, current, initial_seconds, maximum_seconds))
            if row and row["state"] == "waiting":
                retry_at = max(retry_at, row["retry_at"])
            rows["PW-" + provider] = {"id": "PW-" + provider, "provider": provider, "generation": row["generation"] + 1 if row else 1,
                "state": "waiting", "retry_at": retry_at, "evidence": {
                    "execution_id": execution_id, "kind": failure["kind"], "provider": provider,
                    "evidence_ref": failure.get("evidence_ref"),
                    "reported_fields_json": json.dumps(failure, ensure_ascii=False, allow_nan=False)},
                "probe_owner": None, "probe_started_at": None, "attempts": attempts}
        elif row and row["state"] == "checking" and row["probe_owner"] == execution_id:
            if response_observed:
                row.update(state="available", retry_at=None, attempts=0, probe_owner=None, probe_started_at=None)
            else:
                retry_at = math.ceil(retry_time({}, row["attempts"] + 1, current, initial_seconds, maximum_seconds))
                row.update(state="waiting", retry_at=retry_at, attempts=row["attempts"] + 1,
                           probe_owner=None, probe_started_at=None)
        return self.provider_snapshot(current_time=current)["providers"].get(provider,
                    {"provider": provider, "state": "available", "generation": 0})

    def provider_snapshot(self, *, current_time=None):
        from copy import deepcopy
        from .provider_wait import utc
        current = time.time() if current_time is None else current_time
        rows = deepcopy(self.runtime.get("provider_waits", {}))
        for row in rows.values():
            row["due"] = row["state"] == "waiting" and row["retry_at"] <= current
            row["retry_at"] = utc(row["retry_at"])
            row["probe_started_at"] = utc(row["probe_started_at"])
        return {"observed_at": utc(current), "source": "git_runtime", "providers": {row["provider"]: row for row in rows.values()}}

    def snapshot(self):
        constraints = self.instance["capacity_constraints"]
        active_refs = {ref["id"] for refs in self.instance.get("role_profile_refs", {}).values() for ref in refs}
        active_constraints = {ref for pid in active_refs for ref in self.instance["execution_profiles"][pid].get("ai", {}).get("capacity_refs", [])}
        result = {"work": {}, "operations": {}}
        for cid in active_constraints:
            constraint = constraints[cid]
            for pool in result:
                result[pool][constraint["model"]] = {"limit": constraint[pool + "_slots"], "used": 0, "execution_ids": []}
        for row in self.runtime.get("reservations", {}).values():
            if row["state"] != "held" or row["unit"] != "execution":
                continue
            model = constraints[row["constraint_id"]]["model"]
            cell = result[row["budget_kind"]].setdefault(model, {"limit": 0, "used": 0, "execution_ids": []})
            cell["used"] += row["reserved"]
            cell["execution_ids"].append(row["owner_id"])
        for pool in result.values():
            for cell in pool.values():
                cell["available"] = max(0, cell["limit"] - cell["used"])
        return result

    def usage_snapshot(self):
        """Project adopted cumulative call limits from the same reservation ledger."""
        constraints = self.instance["capacity_constraints"]
        active_profiles = {ref["id"] for refs in self.instance.get("role_profile_refs", {}).values() for ref in refs}
        usage_ids = {cid for pid in active_profiles for cid in
                     self.instance["execution_profiles"][pid].get("ai", {}).get("usage_constraint_ids", [])}
        result = {}
        for cid in usage_ids:
            constraint = constraints[cid]
            pool = constraint["budget_kind"]
            used = sum(row["reserved"] - row["returned"] for row in self.runtime.get("reservations", {}).values()
                       if constraints[row["constraint_id"]].get("kind") == "cumulative"
                       and constraints[row["constraint_id"]].get("unit") == constraint["unit"]
                       and row["budget_kind"] == pool)
            maximum = constraint["limit"].get("value") if constraint["limit"]["kind"] == "bounded" else None
            result[pool] = {"limit": maximum, "used": used,
                            "available": None if maximum is None else max(0, maximum - used),
                            "unit": constraint["unit"], "source": "git_reservations"}
        return result

    def close(self):
        pass  # The repository owns the writer lock and CAS; this view owns neither.


def SessionSlots(workspace, instance_id, *, runtime, instance, observer=False):
    """Keep caller argument shape while requiring the sole Git working set."""
    return GitSessionSlots(runtime, instance, observer=observer)

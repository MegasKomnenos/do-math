"""Git-backed local execution reservations shared by engine and recovery.

The repository writer lock and single CAS own admission. Local Job evidence
settles local capacity; it proves neither remote termination nor provider use.
Only work roles reserve a model slot. Operational AI roles are admitted on
their pinned model without a slot; host limits still bound every capped role.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math

# Admission wait kinds recorded in a queued request's ``dispatch_wait``.
PROVIDER_WAIT = 'provider_limit'
# Slot waits: the instance is capacity_waiting when every queued request has one.
SLOT_WAITS = frozenset({'capacity', 'host_capacity'})
# Resource waits: a changed resource configuration may release them.
RESOURCE_WAITS = SLOT_WAITS | {'resource_unclassified'}
# Every admission wait, as status reports show scheduling waits.
ADMISSION_WAITS = RESOURCE_WAITS | {PROVIDER_WAIT}


def held_reservations(runtime: dict, owner_ids=None) -> list:
    """Reservations still held, optionally only those owned by ``owner_ids``."""
    return [row for row in runtime.get('reservations', {}).values()
            if row['state'] == 'held' and (owner_ids is None or row['owner_id'] in owner_ids)]


def local_termination_confirmed(execution: dict) -> bool:
    """The execution's admitted capacity was returned after its local termination was confirmed."""
    return execution.get('capacity', {}).get('local_termination') == 'confirmed'


def quiescence(runtime: dict) -> dict:
    """Unended executions and held reservations; an instance is quiescent when both are empty."""
    return {'pending_executions': [e['id'] for e in runtime.get('executions', {}).values() if e['status'] != 'ended'],
            'held_reservations': [row['id'] for row in held_reservations(runtime)]}


def live_action_ids(runtime: dict) -> set:
    """IDs of the actions whose executions have not ended."""
    return {e.get('action', {}).get('id') for e in runtime.get('executions', {}).values()
            if e.get('status') != 'ended'}


class SessionSlots:
    """A working view of the Git execution/reservation families.

    The caller holds ResearchRepository.writer_lock for every mutation and
    publishes the candidate runtime through one save/CAS before starting a Job.
    Read-only views never reconcile or create files. No counter or local SQL
    database is authoritative for this path.
    """

    def __init__(self, runtime: dict, instance: dict, *, observer=False, clock, jobs, host_id):
        self.clock = clock
        self.host_id = host_id
        self.jobs = jobs
        self.runtime, self.instance, self.observer = runtime, instance, observer
        self.admission_wait = None

    @property
    def admission_reason(self):
        return (self.admission_wait or {}).get('kind')

    def _writable(self):
        if self.observer:
            raise ValueError("a read-only slot observer cannot mutate reservations")

    def _gate(self, provider):
        return self.runtime.get("provider_waits", {}).get("PW-" + provider) if provider else None

    def provider_wait(self, profile, *, current_time=None):
        """The admission wait while this profile's provider gate is closed, else None."""
        from .execution_profiles import profile_ref
        from .provider_wait import gate_open, utc
        current = self.clock.wall_ns() / 1_000_000_000 if current_time is None else current_time
        ai = profile.get("ai", {})
        gate = self._gate(ai.get("provider"))
        if gate is None or gate_open(gate, current):
            return None
        return {'kind': PROVIDER_WAIT, 'model': ai["model"], 'profile_ref': profile_ref(profile),
                'provider': ai["provider"], 'retry_at': utc(gate['retry_at']),
                'reason': 'provider admission is waiting for reobservation', 'next_owner': 'scheduler'}

    def _admission(self, profile, execution_id, current):
        """The one admission calculation shared by the check and the real acquire.

        Returns the registered profile and the reservation records to publish,
        or None after recording ``admission_wait``. Nothing is written.
        """
        from .execution_profiles import (match_profile_ref, profile_ref, job_resource_limits,
                                         validate_host_constraint, UNCAPPED_ROLES)
        from .budget import plan_reservations, BudgetConflict
        self.admission_wait = None
        profile = match_profile_ref(self.instance["execution_profiles"], profile_ref(profile))
        approved_host = self.instance.get("host_capacity_ref")
        uncapped_lean = (profile['actor_kind']=='machine'
                        and profile['role'] in UNCAPPED_ROLES
                        and profile.get('host_resources') is None)
        if profile.get("host_capacity_refs", []) != ([approved_host] if approved_host and not uncapped_lean else []):
            raise ValueError("execution profile must bind the instance's current adopted host constraint")
        job_resource_limits(profile, host_id=self.host_id)  # Reject a profile bound to another host before any mutation.
        ai = profile.get("ai", {})
        model = ai.get("model")
        self.admission_wait = self.provider_wait(profile, current_time=current)
        if self.admission_wait is not None:
            return None
        # A new capacity edition must still count executions reserved under older
        # editions of the same model. Limits are not independent resource pools.
        constraints = self.instance["capacity_constraints"]
        # Rebase only each held row's constraint ID; nested evidence stays read-only.
        held = [dict(row) for row in held_reservations(self.runtime)]
        capacity_refs = list(ai.get("capacity_refs", []))
        adopted = self.instance.get("role_profile_refs")
        if adopted and capacity_refs:
            # An execution keeps its immutable profile, but a new reservation
            # must obey the currently adopted limit for the same resource.
            active_constraints = set()
            for role_refs in adopted.values():
                for reference in role_refs:
                    active_profile = self.instance["execution_profiles"][reference["id"]]
                    active_ai = active_profile.get("ai", {})
                    active_constraints.update(active_ai.get("capacity_refs", []))

            def current_ref(reference):
                previous = constraints[reference]
                matches = [cid for cid in active_constraints if constraints[cid]["kind"] == "concurrency"
                           and constraints[cid]["model"] == previous["model"]]
                return matches[0] if len(matches) == 1 else None

            capacity_refs = [current_ref(ref) for ref in capacity_refs]
            if None in capacity_refs:
                self.admission_wait = {"kind": "capacity", "model": model,
                    "profile_ref": profile_ref(profile), "reason": "pinned profile has no current adopted accounting constraint",
                    "next_owner": "user"}
                return None
        refs = capacity_refs
        accounting_profile = {**profile, "ai": {**ai, "capacity_refs": capacity_refs}} if ai else profile
        host_refs = profile.get("host_capacity_refs", [])
        for ref in host_refs:
            validate_host_constraint(constraints[ref])
            if any(profile["host_resources"][k] != constraints[ref][k] for k in ("scope", "host_id")):
                raise ValueError("profile and approved host scope differ")
        for row in held:
            previous = constraints.get(row["constraint_id"], {})
            for ref in refs + host_refs:
                constraint = constraints[ref]
                same_model = (previous.get("kind") == constraint["kind"] == "concurrency"
                              and previous.get("model") == constraint["model"])
                same_host = (previous.get("kind") == constraint["kind"] == "host"
                             and previous.get("scope") == constraint.get("scope") == "instance_on_host"
                             and previous.get("host_id") == constraint.get("host_id"))
                if same_model or same_host:
                    row["constraint_id"] = ref
        try:
            records = plan_reservations(held, constraints, accounting_profile, owner_id=execution_id)
        except BudgetConflict as error:
            kind, owner = {'concurrency': ('capacity', 'scheduler'),
                           'host': ('host_capacity', 'operations')}.get(
                               error.constraint_kind, ('resource_unclassified', 'operations'))
            constraint = constraints.get(error.constraint_id, {})
            if error.constraint_kind == 'concurrency' and constraint.get('work_slots') == 0:
                owner = 'user'
            self.admission_wait = {'kind': kind, 'model': model,
                'profile_ref': profile_ref(profile), 'constraint_id': error.constraint_id,
                'constraint_kind': error.constraint_kind, 'reason': str(error), 'next_owner': owner}
            return None
        return profile, records

    def admission_check(self, profile, *, current_time=None):
        """Evaluate the admission calculation without writing the ledger.

        A ready result is not a reservation. The real acquire repeats the check
        while publishing its execution and reservations under the writer lock.
        """
        current = self.clock.wall_ns() / 1_000_000_000 if current_time is None else current_time
        allowed = self._admission(profile, "EX-admission-check", current) is not None
        return {'allowed': allowed, 'wait': deepcopy(self.admission_wait)}

    def acquire(self, execution_id, *, profile, execution, current_time=None):
        """Admit one registered execution on its pinned profile, or record the wait."""
        self._writable()
        from .execution_profiles import bind_execution
        from .execution_lifecycle import transition_execution
        from .launch import ticket
        from datetime import datetime, timezone
        if execution.get("id") != execution_id:
            raise ValueError("execution identity differs from admission")
        existing = self.runtime.get("executions", {}).get(execution_id)
        if existing is not None and (existing is not execution or "capacity" in existing
                                     or existing.get("status") not in {"queued", "starting"}):
            raise ValueError("execution IDs are single-use; only the registered unreserved execution can be admitted")
        current = self.clock.wall_ns() / 1_000_000_000 if current_time is None else current_time
        admitted = self._admission(profile, execution_id, current)
        if admitted is None:
            return False
        profile, records = admitted
        candidate = deepcopy(execution)
        bind_execution(candidate, profile)
        candidate['launch_ticket'] = ticket(execution_id, profile, jobs=self.jobs, clock=self.clock)
        admitted_at = (self.clock.wall() if current_time is None
                       else datetime.fromtimestamp(current, timezone.utc))
        transition_execution(candidate, "starting", at=admitted_at.isoformat())
        provider = profile.get("ai", {}).get("provider")
        candidate["capacity"] = {"reservation_ids": [r["id"] for r in records],
                                 "provider": provider, "process": None, "local_termination": "unknown"}
        self.runtime.setdefault("reservations", {}).update({r["id"]: r for r in records})
        self.runtime.setdefault("executions", {})[execution_id] = candidate
        gate = self._gate(provider)
        if gate and gate["state"] == "waiting":
            gate.update(state="checking", probe_owner=execution_id, probe_started_at=int(current))
        execution.clear()
        execution.update(candidate)
        self.runtime["executions"][execution_id] = execution
        return True

    def started(self, execution_id, identity, *, at):
        """Record the started named Job, its running transition and start time."""
        self._writable()
        from .execution_lifecycle import transition_execution
        execution = self.runtime["executions"][execution_id]
        capacity = execution["capacity"]
        launch = execution['launch_ticket']
        if launch['kind'] != 'native_job' or identity.get('job_name') != launch['job_name']:
            raise ValueError('started Job differs from the published launch ticket')
        if capacity["process"] is not None:
            if capacity["process"] == identity:
                return execution
            raise ValueError("execution process identity is already fixed")
        capacity["process"] = deepcopy(identity)
        transition_execution(execution, "running", at=at)
        execution["started_at"] = at
        return execution

    def release(self, execution_id, *, reason="local runner returned after termination"):
        self._writable()
        from .budget import settle_reservation
        from .launch import termination_confirmed
        execution = self.runtime.get("executions", {}).get(execution_id)
        if not execution or "capacity" not in execution:
            return False
        capacity = execution["capacity"]
        if capacity["local_termination"] == "confirmed":
            return True
        identity = capacity["process"]
        # The launch ticket, not missing process metadata, establishes the
        # barrier; for a native Job it already requires the named Job empty.
        # A suspended root may exist before on_started is saved.
        if not execution.get('launch_ticket') or not termination_confirmed(execution['launch_ticket'], jobs=self.jobs):
            capacity['local_termination'] = 'unknown'
            return False
        evidence = [{"execution_id": execution_id, "job_name": identity.get("job_name") if identity else None,
                     "kind": "local_job_empty" if identity else "never_resumed", "reason": reason}]
        updates = {}
        for rid in capacity["reservation_ids"]:
            record = self.runtime["reservations"][rid]
            updates[rid] = settle_reservation(record, confirmed_consumed=0, returned=record["reserved"],
                                              evidence_refs=evidence)
        self.runtime["reservations"].update(updates)
        capacity["local_termination"] = "confirmed"
        for gate in self.runtime.get("provider_waits", {}).values():
            if gate["state"] == "checking" and gate["probe_owner"] == execution_id:
                # Releasing a local slot is no evidence that a provider recovered.
                gate.update(state="waiting", probe_owner=None, probe_started_at=None)
        return True

    def provider_result_from_run(self, execution_id, result, config, *, current_time=None):
        """Apply one runner result to the gate of the execution's admitted provider.

        Only a provider_limit failure closes the gate. The probe owner reopens
        it when the provider answered at all: a completed call, or a reported
        failed or completed turn.
        """
        self._writable()
        from .provider_wait import retry_time
        current = self.clock.wall_ns() / 1_000_000_000 if current_time is None else current_time
        initial_seconds = config["provider_retry_initial_seconds"]
        maximum_seconds = config["provider_retry_max_seconds"]
        execution = self.runtime.get("executions", {}).get(execution_id, {})
        provider = execution.get("capacity", {}).get("provider")
        if provider is None:
            raise ValueError("provider result has no matching admitted execution")
        parsed = result.get("execution", {}).get("collect", {}).get("jsonl", {})
        failure = result.get("failure") if result.get("error_kind") == "provider_limit" else None
        response_observed = result.get("status") == "completed" or bool(
            parsed.get("turn_failed") or parsed.get("turn_completed"))
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
        from .provider_wait import gate_open, utc
        current = self.clock.wall_ns() / 1_000_000_000 if current_time is None else current_time
        rows = deepcopy(self.runtime.get("provider_waits", {}))
        for row in rows.values():
            row["open"] = gate_open(row, current)
            row["retry_at"] = utc(row["retry_at"])
            row["probe_started_at"] = utc(row["probe_started_at"])
        return {"observed_at": utc(current), "providers": {row["provider"]: row for row in rows.values()}}

    def snapshot(self):
        """Work slots of each currently adopted model; operational roles hold none."""
        constraints = self.instance["capacity_constraints"]
        active_refs = {ref["id"] for refs in self.instance.get("role_profile_refs", {}).values() for ref in refs}
        active_constraints = {ref for pid in active_refs for ref in self.instance["execution_profiles"][pid].get("ai", {}).get("capacity_refs", [])}
        result = {constraints[cid]["model"]: {"limit": constraints[cid]["work_slots"], "used": 0, "execution_ids": []}
                  for cid in active_constraints}
        for row in held_reservations(self.runtime):
            if row["unit"] != "execution":
                continue
            model = constraints[row["constraint_id"]]["model"]
            cell = result.setdefault(model, {"limit": 0, "used": 0, "execution_ids": []})
            cell["used"] += row["reserved"]
            cell["execution_ids"].append(row["owner_id"])
        for cell in result.values():
            cell["available"] = max(0, cell["limit"] - cell["used"])
        return result

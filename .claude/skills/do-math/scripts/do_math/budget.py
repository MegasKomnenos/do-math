"""Pure reservation arithmetic for fixed do-math budget snapshots.

This module creates no execution, permission, storage, or mutable counters.
It calculates concurrency and host reservations from caller supplied records.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any
from .state_contract import STATE_FORMAT_VERSION


class BudgetInputError(ValueError):
    """A fixed snapshot or proposed reservation is structurally unusable."""


class BudgetConflict(RuntimeError):
    """At least one required capacity cannot admit the complete request."""

    def __init__(self, message, *, constraint_id=None, constraint_kind=None):
        super().__init__(message)
        self.constraint_id = constraint_id
        self.constraint_kind = constraint_kind


_HOST_LIMITS = {
    "jobs": "max_jobs",
    "memory_bytes": "memory_bytes",
    "cpu_rate_basis_points": "cpu_rate_basis_points",
}


def plan_reservations(
    snapshot: Mapping[str, Any],
    budget: Mapping[str, Any],
    profile: Mapping[str, Any],
    request: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    """Calculate all reservations needed by one profile without mutating inputs.

    ``snapshot['reservations']`` is the complete caller-selected reservation
    population for concurrency and host constraints. Reservation IDs derive
    from a single-use execution ID, so a request never repeats an existing ID.
    """
    reservations = _snapshot_parts(snapshot)
    constraints = _constraints(budget)
    demands, expected_constraints, common = _request_parts(profile, request, constraints)
    _validate_existing_records(reservations)
    records = tuple(_new_record(demand, common) for demand in demands)
    if any(record["id"] in reservations for record in records):
        raise BudgetInputError("a reservation ID already exists")

    demands_by_constraint: dict[str, list[dict[str, Any]]] = {}
    for demand in demands:
        demands_by_constraint.setdefault(demand["constraint_id"], []).append(demand)
    if set(demands_by_constraint) != expected_constraints:
        raise BudgetInputError("demands must cover exactly the profile capacity and host refs")

    for constraint_id, constraint_demands in demands_by_constraint.items():
        constraint = constraints[constraint_id]
        kind = constraint["kind"]
        if kind == "concurrency":
            _check_concurrency(constraint, constraint_demands, reservations)
        elif kind == "host":
            _check_host(constraint, constraint_demands, reservations)
        else:
            raise BudgetInputError(f"unknown constraint kind: {kind!r}")
    return records


def settle_reservation(
    snapshot: Mapping[str, Any],
    reservation_id: str,
    *,
    confirmed_consumed: int,
    returned: int,
    evidence_refs: Sequence[Any],
) -> dict[str, Any]:
    """Create the one complete actual settlement for a held reservation.

    A settlement must account for the whole reserved amount, once. Unknown
    remote use remains ``held`` until a caller has actual evidence and invokes
    this function.
    """
    reservations = _snapshot_parts(snapshot)
    if reservation_id not in reservations:
        raise BudgetInputError("reservation_id is absent from the fixed snapshot")
    current = reservations[reservation_id]
    _validate_reservation(current)
    if current["state"] != "held":
        raise BudgetInputError("only a held reservation can be settled")
    _nonnegative("confirmed_consumed", confirmed_consumed)
    _nonnegative("returned", returned)
    if confirmed_consumed + returned != current["reserved"]:
        raise BudgetInputError("settlement must account for every reserved unit exactly once")
    if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, (str, bytes)) or not evidence_refs:
        raise BudgetInputError("settlement requires actual evidence_refs")
    settled = deepcopy(current)
    settled.update({
        "confirmed_consumed": confirmed_consumed,
        "returned": returned,
        "state": "settled",
        "evidence_refs": deepcopy(list(evidence_refs)),
    })
    settled.pop("reobserve", None)
    return settled


def _snapshot_parts(snapshot: Mapping[str, Any]) -> Mapping[str, Mapping[str, Any]]:
    if not isinstance(snapshot, Mapping):
        raise BudgetInputError("snapshot must be a mapping")
    reservations = snapshot.get("reservations")
    if not isinstance(reservations, Mapping):
        raise BudgetInputError("snapshot requires a reservations mapping")
    for reservation_id, record in reservations.items():
        if not isinstance(reservation_id, str) or not isinstance(record, Mapping) or record.get("id") != reservation_id:
            raise BudgetInputError("reservations must map each ID to its same-ID record")
    return reservations


def _constraints(budget: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if not isinstance(budget, Mapping) or not isinstance(budget.get("constraints"), Sequence):
        raise BudgetInputError("budget requires a constraints sequence")
    constraints: dict[str, Mapping[str, Any]] = {}
    for constraint in budget["constraints"]:
        if not isinstance(constraint, Mapping) or not isinstance(constraint.get("id"), str) or not constraint["id"]:
            raise BudgetInputError("each constraint needs a non-empty id")
        if constraint["id"] in constraints:
            raise BudgetInputError("constraint IDs must be unique")
        constraints[constraint["id"]] = constraint
    return constraints


def _request_parts(
    profile: Mapping[str, Any], request: Mapping[str, Any], constraints: Mapping[str, Mapping[str, Any]]
) -> tuple[tuple[dict[str, Any], ...], set[str], dict[str, Any]]:
    if not isinstance(profile, Mapping) or not isinstance(request, Mapping):
        raise BudgetInputError("profile and request must be mappings")

    ai = profile.get("ai", {}) if profile.get("actor_kind") == "ai" else {}
    capacity_refs = _string_set(ai.get("capacity_refs", ()), "capacity_refs")
    host_refs = _string_set(profile.get("host_capacity_refs", ()), "host_capacity_refs")
    expected = capacity_refs | host_refs
    if not expected:
        raise BudgetInputError("profile has no capacity references to reserve")
    if any(ref not in constraints for ref in expected):
        raise BudgetInputError("profile references a capacity absent from this approved budget")

    demands: list[dict[str, Any]] = []
    demand_ids: set[str] = set()
    pairs: set[tuple[str, str]] = set()
    for demand in request["demands"]:
        if not isinstance(demand, Mapping):
            raise BudgetInputError("each demand must be a mapping")
        required = ("id", "constraint_id", "unit", "amount")
        if any(name not in demand for name in required):
            raise BudgetInputError("a demand lacks id, constraint_id, unit, or amount")
        identifier, constraint_id, unit, amount = (demand[name] for name in required)
        if not isinstance(identifier, str) or not identifier or identifier in demand_ids:
            raise BudgetInputError("demand IDs must be unique non-empty strings")
        if not isinstance(constraint_id, str) or constraint_id not in constraints or not isinstance(unit, str) or not unit:
            raise BudgetInputError("demand has an unknown constraint or invalid unit")
        _nonnegative("demand amount", amount)
        pair = (constraint_id, unit)
        if pair in pairs:
            raise BudgetInputError("one request may have only one demand per constraint and unit")
        demand_ids.add(identifier)
        pairs.add(pair)
        demands.append({"id": identifier, "constraint_id": constraint_id, "unit": unit, "amount": amount})

    for host_id in host_refs:
        supplied = {unit for constraint_id, unit in pairs if constraint_id == host_id}
        if supplied != set(_HOST_LIMITS):
            raise BudgetInputError("each host capacity needs jobs, memory_bytes, and cpu_rate_basis_points demands")
        if profile.get("host_resources") is not None:
            pinned = profile["host_resources"]
            amounts = {d["unit"]: d["amount"] for d in demands if d["constraint_id"] == host_id}
            if pinned.get("constraint_id") != host_id or pinned.get("demands") != amounts:
                raise BudgetInputError("host reservation demands differ from the pinned profile")
    for constraint_id, constraint in constraints.items():
        if constraint_id not in expected:
            continue
        supplied = [demand for demand in demands if demand["constraint_id"] == constraint_id]
        if not supplied:
            raise BudgetInputError("every profile capacity ref needs a demand")
        if constraint["kind"] == "concurrency":
            if len(supplied) != 1 or supplied[0]["unit"] != constraint.get("accounting_unit"):
                raise BudgetInputError("concurrency demand unit must equal accounting_unit")
        elif constraint["kind"] != "host":
            raise BudgetInputError("profile references an unsupported constraint kind")
    return tuple(demands), expected, {
        "owner_kind": request["owner_kind"],
        "owner_id": request["owner_id"],
        "purpose": request["purpose"],
        "authority_refs": deepcopy(list(request["authority_refs"])),
        "reobserve": deepcopy(request["reobserve"]),
    }


def _new_record(demand: Mapping[str, Any], common: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": STATE_FORMAT_VERSION,
        "id": demand["id"],
        "constraint_id": demand["constraint_id"],
        "unit": demand["unit"],
        "authority_refs": deepcopy(common["authority_refs"]),
        "owner_kind": common["owner_kind"],
        "owner_id": common["owner_id"],
        "purpose": common["purpose"],
        "reserved": demand["amount"],
        "confirmed_consumed": 0,
        "returned": 0,
        "state": "held",
        "evidence_refs": [],
        "reconcile_owner": "engine",
        "reobserve": deepcopy(common["reobserve"]),
    }


def _check_concurrency(
    constraint: Mapping[str, Any], demands: Sequence[Mapping[str, Any]], reservations: Mapping[str, Mapping[str, Any]]
) -> None:
    demand = demands[0]
    used = _outstanding_sum(reservations, constraint["id"], demand["unit"])
    _nonnegative("work_slots", constraint.get("work_slots"))
    if used + demand["amount"] > constraint["work_slots"]:
        raise BudgetConflict(f"concurrency capacity unavailable: {constraint['id']}",
                             constraint_id=constraint['id'], constraint_kind='concurrency')


def _check_host(
    constraint: Mapping[str, Any], demands: Sequence[Mapping[str, Any]], reservations: Mapping[str, Mapping[str, Any]]
) -> None:
    for demand in demands:
        limit_key = _HOST_LIMITS.get(demand["unit"])
        if limit_key is None:
            raise BudgetInputError("host demand has an unsupported unit")
        _nonnegative(limit_key, constraint.get(limit_key))
        reserve = constraint.get("control_reserve")
        headroom = 0
        if reserve is not None:
            if not isinstance(reserve, Mapping) or set(reserve) != set(_HOST_LIMITS):
                raise BudgetInputError("control reserve requires all three explicit host units")
            headroom = reserve[demand["unit"]]
            _nonnegative("control reserve", headroom)
            if headroom > constraint[limit_key]:
                raise BudgetInputError("control reserve exceeds the approved host limit")
        used = _outstanding_sum(reservations, constraint["id"], demand["unit"])
        if used + demand["amount"] > constraint[limit_key] - headroom:
            raise BudgetConflict(f"host capacity unavailable: {constraint['id']}/{demand['unit']}",
                                 constraint_id=constraint['id'], constraint_kind='host')


def _validate_existing_records(reservations: Mapping[str, Mapping[str, Any]]) -> None:
    for record in reservations.values():
        _validate_reservation(record)


def _validate_reservation(record: Mapping[str, Any]) -> None:
    for name in ("id", "constraint_id", "unit", "state"):
        if not isinstance(record.get(name), str) or not record[name]:
            raise BudgetInputError(f"reservation lacks valid {name}")
    if record["state"] not in {"held", "settled"}:
        raise BudgetInputError("reservation has an invalid state")
    for name in ("reserved", "confirmed_consumed", "returned"):
        _nonnegative(name, record.get(name))
    if record["confirmed_consumed"] + record["returned"] > record["reserved"]:
        raise BudgetInputError("confirmed_consumed + returned exceeds reserved")
    if record["state"] == "settled":
        if record["confirmed_consumed"] + record["returned"] != record["reserved"]:
            raise BudgetInputError("settled reservation must account for reserved exactly")
        if not record.get("evidence_refs"):
            raise BudgetInputError("settled reservation requires evidence_refs")
    if record["state"] == "held" and "reobserve" not in record:
        raise BudgetInputError("held reservation requires reobserve")


def _outstanding_sum(reservations: Mapping[str, Mapping[str, Any]], constraint_id: str, unit: str) -> int:
    return sum(
        _outstanding(record)
        for record in reservations.values()
        if record["constraint_id"] == constraint_id and record["unit"] == unit
    )


def _outstanding(record: Mapping[str, Any]) -> int:
    return record["reserved"] - record["returned"]


def _string_set(value: Any, name: str) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or any(not isinstance(item, str) or not item for item in value):
        raise BudgetInputError(f"{name} must be a sequence of non-empty strings")
    if len(set(value)) != len(value):
        raise BudgetInputError(f"{name} must not repeat a constraint")
    return set(value)


def _nonnegative(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise BudgetInputError(f"{name} must be a non-negative integer")

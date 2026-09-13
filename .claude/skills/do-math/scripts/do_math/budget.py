"""Pure reservation arithmetic for fixed do-math budget snapshots.

This module creates no execution, permission, storage, or mutable counters.
It calculates concurrency, cumulative usage, and host reservations from caller
supplied records.  Fixed-window populations are caller-bound inputs: their
completeness and time-window validity are deliberately not verified here.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Any


class BudgetInputError(ValueError):
    """A fixed snapshot or proposed reservation is structurally unusable."""


class BudgetConflict(RuntimeError):
    """At least one required capacity cannot admit the complete request."""


class BudgetReplayConflict(BudgetInputError):
    """An existing reservation ID was requested again with different bytes."""


@dataclass(frozen=True, slots=True)
class ReservationPlan:
    """Records for one all-or-nothing reservation calculation.

    ``unverified_window_constraints`` reports fixed-window constraints whose
    arithmetic used a caller-supplied population.  It is never evidence that
    the population is complete or that its members belong to the active window.
    """

    records: tuple[dict[str, Any], ...]
    replayed: bool
    unverified_window_constraints: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SettlementPlan:
    """One fully accounted reservation record, or an idempotent replay."""

    record: dict[str, Any]
    replayed: bool


_HOST_LIMITS = {
    "jobs": "max_jobs",
    "memory_bytes": "memory_bytes",
    "cpu_rate_basis_points": "cpu_rate_basis_points",
}


def canonical_record_bytes(record: Mapping[str, Any]) -> bytes:
    """Return the deterministic bytes used to recognize an idempotent replay."""
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def plan_reservations(
    snapshot: Mapping[str, Any],
    budget: Mapping[str, Any],
    profile: Mapping[str, Any],
    request: Mapping[str, Any],
) -> ReservationPlan:
    """Calculate all reservations needed by one profile without mutating inputs.

    ``snapshot['reservations']`` is the complete caller-selected reservation
    population for concurrency and cumulative constraints.  For every fixed
    window used by ``profile``, ``snapshot['window_population'][constraint_id]``
    must name the exact reservation IDs the caller wants counted.  The module
    validates those IDs against the supplied records but cannot establish that
    the population is complete or temporally effective.
    """
    reservations, window_population = _snapshot_parts(snapshot)
    constraints = _constraints(budget)
    demands, expected_constraints, common = _request_parts(profile, request, constraints)
    _validate_existing_records(reservations)
    records = tuple(_new_record(demand, common) for demand in demands)

    existing_by_id = reservations
    existing_ids = [record["id"] for record in records if record["id"] in existing_by_id]
    if existing_ids:
        if len(existing_ids) != len(records):
            raise BudgetReplayConflict("a reservation request may not partially replay")
        for record in records:
            if canonical_record_bytes(existing_by_id[record["id"]]) != canonical_record_bytes(record):
                raise BudgetReplayConflict("a reservation ID already exists with different bytes")
        windows = tuple(sorted(
            demand["constraint_id"] for demand in demands if constraints[demand["constraint_id"]]["kind"] == "window"
        ))
        return ReservationPlan(tuple(deepcopy(existing_by_id[record["id"]]) for record in records), True, windows)

    demands_by_constraint: dict[str, list[dict[str, Any]]] = {}
    for demand in demands:
        demands_by_constraint.setdefault(demand["constraint_id"], []).append(demand)
    if set(demands_by_constraint) != expected_constraints:
        raise BudgetInputError("demands must cover exactly the profile capacity, usage, and host refs")

    unverified_windows: list[str] = []
    for constraint_id, constraint_demands in demands_by_constraint.items():
        constraint = constraints[constraint_id]
        kind = constraint["kind"]
        if kind == "concurrency":
            _check_concurrency(constraint, constraint_demands, reservations, common["budget_kind"])
        elif kind == "host":
            _check_host(constraint, constraint_demands, reservations)
        elif kind in {"cumulative", "window"}:
            supplied_population = None
            if kind == "window":
                if constraint_id not in window_population:
                    raise BudgetInputError(f"fixed-window population is required for {constraint_id!r}")
                supplied_population = window_population[constraint_id]
                _validate_window_population(constraint_id, supplied_population, reservations)
                unverified_windows.append(constraint_id)
            _check_usage(constraint, constraint_demands, reservations, supplied_population)
        else:
            raise BudgetInputError(f"unknown constraint kind: {kind!r}")
    return ReservationPlan(records, False, tuple(sorted(unverified_windows)))


def settle_reservation(
    snapshot: Mapping[str, Any],
    reservation_id: str,
    *,
    confirmed_consumed: int,
    returned: int,
    evidence_refs: Sequence[Any],
) -> SettlementPlan:
    """Create the one complete actual settlement for a held reservation.

    A settlement must account for the whole reserved amount.  Repeating the
    identical result is idempotent; any different second result is rejected.
    Unknown remote use remains ``held`` until a caller has actual evidence and
    invokes this function.
    """
    reservations, _ = _snapshot_parts(snapshot)
    if reservation_id not in reservations:
        raise BudgetInputError("reservation_id is absent from the fixed snapshot")
    current = reservations[reservation_id]
    _validate_reservation(current)
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
    if current["state"] != "held":
        if canonical_record_bytes(current) == canonical_record_bytes(settled):
            return SettlementPlan(deepcopy(current), True)
        raise BudgetReplayConflict("an already settled or unrecoverable reservation cannot be changed")
    return SettlementPlan(settled, False)


def _snapshot_parts(snapshot: Mapping[str, Any]) -> tuple[Mapping[str, Mapping[str, Any]], Mapping[str, Sequence[str]]]:
    if not isinstance(snapshot, Mapping):
        raise BudgetInputError("snapshot must be a mapping")
    reservations = snapshot.get("reservations")
    window_population = snapshot.get("window_population", {})
    if not isinstance(reservations, Mapping) or not isinstance(window_population, Mapping):
        raise BudgetInputError("snapshot requires reservations and optional window_population mappings")
    for reservation_id, record in reservations.items():
        if not isinstance(reservation_id, str) or not isinstance(record, Mapping) or record.get("id") != reservation_id:
            raise BudgetInputError("reservations must map each ID to its same-ID record")
    return reservations, window_population


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
    budget_kind = request.get("budget_kind")
    if budget_kind not in {"work", "operations"}:
        raise BudgetInputError("request budget_kind must be work or operations")
    common_names = ("owner_kind", "owner_id", "purpose", "authority_refs", "reobserve")
    if any(name not in request for name in common_names):
        raise BudgetInputError("request lacks required reservation fields")
    if request["owner_kind"] not in {"execution", "provider_operation"}:
        raise BudgetInputError("owner_kind must be execution or provider_operation")
    if not isinstance(request["owner_id"], str) or not request["owner_id"]:
        raise BudgetInputError("owner_id must be non-empty")
    if request["purpose"] not in {"normal", "stop_checkpoint"}:
        raise BudgetInputError("purpose must be normal or stop_checkpoint")
    if (not isinstance(request["authority_refs"], Sequence) or isinstance(request["authority_refs"], (str, bytes))
            or not request["authority_refs"]):
        raise BudgetInputError("authority_refs must be a sequence")
    if not isinstance(request["demands"], Sequence) or isinstance(request["demands"], (str, bytes)):
        raise BudgetInputError("demands must be a sequence")

    ai = profile.get("ai", {}) if profile.get("actor_kind") == "ai" else {}
    capacity_refs = _string_set(ai.get("capacity_refs", ()), "capacity_refs")
    usage_refs = _string_set(ai.get("usage_constraint_ids", ()), "usage_constraint_ids")
    host_refs = _string_set(profile.get("host_capacity_refs", ()), "host_capacity_refs")
    expected = capacity_refs | usage_refs | host_refs
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
    for constraint_id, constraint in constraints.items():
        if constraint_id not in expected:
            continue
        supplied = [demand for demand in demands if demand["constraint_id"] == constraint_id]
        if not supplied:
            raise BudgetInputError("every profile capacity ref needs a demand")
        if constraint["kind"] == "concurrency":
            if len(supplied) != 1 or supplied[0]["unit"] != constraint.get("accounting_unit"):
                raise BudgetInputError("concurrency demand unit must equal accounting_unit")
        elif constraint["kind"] in {"cumulative", "window"}:
            if len(supplied) != 1 or supplied[0]["unit"] != constraint.get("unit"):
                raise BudgetInputError("usage demand unit must equal the approved constraint unit")
        elif constraint["kind"] != "host":
            raise BudgetInputError("profile references an unsupported constraint kind")
    return tuple(demands), expected, {
        "budget_kind": budget_kind,
        "owner_kind": request["owner_kind"],
        "owner_id": request["owner_id"],
        "purpose": request["purpose"],
        "authority_refs": deepcopy(list(request["authority_refs"])),
        "reobserve": deepcopy(request["reobserve"]),
    }


def _new_record(demand: Mapping[str, Any], common: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "do-math-draft/resource-reservation/9",
        "id": demand["id"],
        "constraint_id": demand["constraint_id"],
        "unit": demand["unit"],
        "authority_refs": deepcopy(common["authority_refs"]),
        "owner_kind": common["owner_kind"],
        "owner_id": common["owner_id"],
        "purpose": common["purpose"],
        "budget_kind": common["budget_kind"],
        "reserved": demand["amount"],
        "confirmed_consumed": 0,
        "returned": 0,
        "state": "held",
        "evidence_refs": [],
        "reconcile_owner": "engine",
        "reobserve": deepcopy(common["reobserve"]),
    }


def _check_concurrency(
    constraint: Mapping[str, Any], demands: Sequence[Mapping[str, Any]], reservations: Mapping[str, Mapping[str, Any]], budget_kind: str
) -> None:
    demand = demands[0]
    own = _outstanding_sum(reservations, constraint["id"], demand["unit"], budget_kind=budget_kind)
    total = _outstanding_sum(reservations, constraint["id"], demand["unit"])
    _nonnegative("work_slots", constraint.get("work_slots"))
    _nonnegative("operations_slots", constraint.get("operations_slots"))
    _nonnegative("total_slots", constraint.get("total_slots"))
    if constraint["work_slots"] + constraint["operations_slots"] > constraint["total_slots"]:
        raise BudgetInputError("concurrency slots violate work + operations <= total")
    slice_name = "work_slots" if budget_kind == "work" else "operations_slots"
    if own + demand["amount"] > constraint[slice_name] or total + demand["amount"] > constraint["total_slots"]:
        raise BudgetConflict(f"concurrency capacity unavailable: {constraint['id']}")


def _check_host(
    constraint: Mapping[str, Any], demands: Sequence[Mapping[str, Any]], reservations: Mapping[str, Mapping[str, Any]]
) -> None:
    for demand in demands:
        limit_key = _HOST_LIMITS.get(demand["unit"])
        if limit_key is None:
            raise BudgetInputError("host demand has an unsupported unit")
        _nonnegative(limit_key, constraint.get(limit_key))
        used = _outstanding_sum(reservations, constraint["id"], demand["unit"])
        if used + demand["amount"] > constraint[limit_key]:
            raise BudgetConflict(f"host capacity unavailable: {constraint['id']}/{demand['unit']}")


def _check_usage(
    constraint: Mapping[str, Any], demands: Sequence[Mapping[str, Any]], reservations: Mapping[str, Mapping[str, Any]],
    population: Sequence[str] | None,
) -> None:
    demand = demands[0]
    limit = constraint.get("limit")
    if not isinstance(limit, Mapping) or limit.get("kind") not in {"bounded", "unlimited"}:
        raise BudgetInputError("usage constraint requires an explicit bounded or unlimited limit")
    if limit["kind"] == "unlimited":
        return
    _nonnegative("usage limit", limit.get("value"))
    if population is None:
        used = _outstanding_sum(reservations, constraint["id"], demand["unit"])
    else:
        used = sum(_outstanding(reservations[reservation_id]) for reservation_id in population)
    if used + demand["amount"] > limit["value"]:
        raise BudgetConflict(f"usage capacity unavailable: {constraint['id']}")


def _validate_window_population(
    constraint_id: str, population: Any, reservations: Mapping[str, Mapping[str, Any]]) -> None:
    if not isinstance(population, Sequence) or isinstance(population, (str, bytes)):
        raise BudgetInputError("window population must be a sequence of reservation IDs")
    if any(not isinstance(reservation_id, str) for reservation_id in population):
        raise BudgetInputError("window population must contain string reservation IDs")
    if len(set(population)) != len(population):
        raise BudgetInputError("window population must not repeat reservation IDs")
    for reservation_id in population:
        if not isinstance(reservation_id, str) or reservation_id not in reservations:
            raise BudgetInputError("window population refers to an absent reservation")
        record = reservations[reservation_id]
        if record.get("constraint_id") != constraint_id:
            raise BudgetInputError("window population must contain records for its own constraint")


def _validate_existing_records(reservations: Mapping[str, Mapping[str, Any]]) -> None:
    for record in reservations.values():
        _validate_reservation(record)


def _validate_reservation(record: Mapping[str, Any]) -> None:
    for name in ("id", "constraint_id", "unit", "budget_kind", "state"):
        if not isinstance(record.get(name), str) or not record[name]:
            raise BudgetInputError(f"reservation lacks valid {name}")
    if record["budget_kind"] not in {"work", "operations"} or record["state"] not in {"held", "settled", "unrecoverable"}:
        raise BudgetInputError("reservation has an invalid budget_kind or state")
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
    if record["state"] == "unrecoverable" and not record.get("evidence_refs"):
        raise BudgetInputError("unrecoverable reservation requires evidence_refs")


def _outstanding_sum(
    reservations: Mapping[str, Mapping[str, Any]], constraint_id: str, unit: str, *, budget_kind: str | None = None
) -> int:
    return sum(
        _outstanding(record)
        for record in reservations.values()
        if record["constraint_id"] == constraint_id and record["unit"] == unit
        and (budget_kind is None or record["budget_kind"] == budget_kind)
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

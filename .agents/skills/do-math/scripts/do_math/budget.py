"""Pure reservation arithmetic for one execution's pinned profile.

This module creates no execution, permission, storage, or mutable counters.
The demands of an execution come from its profile here, never from a caller.
Stored reservation rows passed the state gate's ``validate_reservation``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from typing import Any


class BudgetInputError(ValueError):
    """A reservation record or settlement is structurally unusable."""


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
    held: Iterable[Mapping[str, Any]],
    constraints: Mapping[str, Mapping[str, Any]],
    profile: Mapping[str, Any],
    *,
    owner_id: str,
) -> tuple[dict[str, Any], ...]:
    """The held records one execution needs on ``profile``, or ``BudgetConflict``.

    ``profile`` reserves one ``accounting_unit`` of each AI ``capacity_refs``
    constraint and each pinned host demand on its host constraint; a profile
    with neither reserves nothing. ``held`` are the reservations still held,
    each counted against the constraint ID it names; ``constraints`` maps IDs
    to the adopted constraints. Nothing is mutated.
    """
    held = list(held)
    demands = [(f"RS-{owner_id}-{index}", ref, constraints[ref]["accounting_unit"], 1)
               for index, ref in enumerate(profile.get("ai", {}).get("capacity_refs", []))]
    host = profile.get("host_resources")
    if host is not None:
        demands += [(f"RS-{owner_id}-host-{unit}", host["constraint_id"], unit, amount)
                    for unit, amount in host["demands"].items()]
    for _, constraint_id, unit, amount in demands:
        constraint = constraints[constraint_id]
        used = outstanding_sum(held, constraint_id, unit)
        if constraint["kind"] == "concurrency":
            if used + amount > constraint["work_slots"]:
                raise BudgetConflict(f"concurrency capacity unavailable: {constraint_id}",
                                     constraint_id=constraint_id, constraint_kind="concurrency")
        # The controller's reserve is never lent to an admitted child Job.
        elif used + amount > constraint[_HOST_LIMITS[unit]] - constraint["control_reserve"][unit]:
            raise BudgetConflict(f"host capacity unavailable: {constraint_id}/{unit}",
                                 constraint_id=constraint_id, constraint_kind="host")
    authority = {key: profile[key] for key in ("id", "revision", "sha256")}
    return tuple({
        "id": identifier,
        "constraint_id": constraint_id,
        "unit": unit,
        "authority_refs": [dict(authority)],
        "owner_kind": "execution",
        "owner_id": owner_id,
        "purpose": "normal",
        "reserved": amount,
        "confirmed_consumed": 0,
        "returned": 0,
        "state": "held",
        "evidence_refs": [],
        "reconcile_owner": "engine",
        "reobserve": {"on": "local_termination_barrier"},
    } for identifier, constraint_id, unit, amount in demands)


def settle_reservation(
    record: Mapping[str, Any],
    *,
    confirmed_consumed: int,
    returned: int,
    evidence_refs: Sequence[Any],
) -> dict[str, Any]:
    """Create the one complete actual settlement of a held reservation record.

    A settlement must account for the whole reserved amount, once. Unknown
    remote use remains ``held`` until a caller has actual evidence and invokes
    this function.
    """
    if record["state"] != "held":
        raise BudgetInputError("only a held reservation can be settled")
    _nonnegative("confirmed_consumed", confirmed_consumed)
    _nonnegative("returned", returned)
    if confirmed_consumed + returned != record["reserved"]:
        raise BudgetInputError("settlement must account for every reserved unit exactly once")
    if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, (str, bytes)) or not evidence_refs:
        raise BudgetInputError("settlement requires actual evidence_refs")
    settled = deepcopy(dict(record))
    settled.update({
        "confirmed_consumed": confirmed_consumed,
        "returned": returned,
        "state": "settled",
        "evidence_refs": deepcopy(list(evidence_refs)),
    })
    settled.pop("reobserve", None)
    return settled


def validate_reservation(record: Mapping[str, Any]) -> None:
    """The state gate's check of one stored reservation record."""
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


def outstanding_sum(records: Iterable[Mapping[str, Any]], constraint_id: str, unit: str) -> int:
    """Units of ``unit`` on ``constraint_id`` that ``records`` have not returned."""
    return sum(record["reserved"] - record["returned"] for record in records
               if record["constraint_id"] == constraint_id and record["unit"] == unit)


def _nonnegative(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise BudgetInputError(f"{name} must be a non-negative integer")

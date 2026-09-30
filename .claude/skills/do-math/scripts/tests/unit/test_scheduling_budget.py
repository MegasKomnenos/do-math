"""Reservation arithmetic of one execution's pinned profile (``budget``, layer 1; ``session_slots.held_reservations``).

``plan_reservations`` computes every held reservation row one execution needs
at once and raises ``BudgetConflict`` without a row when any capacity is short;
``settle_reservation`` settles one held row exactly once with its evidence.
Both are pure functions of dictionaries, so every case is its own input.
"""
from copy import deepcopy
import unittest

from do_math.budget import BudgetConflict, BudgetInputError, plan_reservations, settle_reservation
from do_math.session_slots import held_reservations

RESERVE = {"jobs": 0, "memory_bytes": 0, "cpu_rate_basis_points": 0}


def constraints(*, work_slots=1, max_jobs=1, memory_bytes=100, reserve=None):
    return {
        "exec": {"id": "exec", "kind": "concurrency", "accounting_unit": "execution", "work_slots": work_slots},
        "host": {"id": "host", "kind": "host", "max_jobs": max_jobs, "memory_bytes": memory_bytes,
                 "cpu_rate_basis_points": 10000, "control_reserve": reserve or dict(RESERVE)},
    }


def profile(*, host_memory=50):
    return {
        "id": "EP-1", "revision": 1, "sha256": "0" * 64, "actor_kind": "ai",
        "ai": {"capacity_refs": ["exec"]},
        "host_capacity_refs": ["host"],
        "host_resources": {"constraint_id": "host", "demands": {
            "jobs": 1, "memory_bytes": host_memory, "cpu_rate_basis_points": 5000}},
    }


class BudgetTests(unittest.TestCase):
    def test_one_profile_reserves_its_work_slot_and_host_demands_atomically(self):
        limits = constraints(max_jobs=2, memory_bytes=200)
        before = deepcopy(limits)
        work = plan_reservations([], limits, profile(), owner_id="EX-1")
        self.assertEqual(sorted((r["constraint_id"], r["unit"], r["reserved"]) for r in work),
                         [("exec", "execution", 1), ("host", "cpu_rate_basis_points", 5000),
                          ("host", "jobs", 1), ("host", "memory_bytes", 50)])
        self.assertTrue(all(r["state"] == "held" and r["owner_id"] == "EX-1"
                            and r["authority_refs"] == [{"id": "EP-1", "revision": 1, "sha256": "0" * 64}]
                            for r in work))
        self.assertEqual(limits, before)
        # The host has room for a second execution, so the refusal is the work slot's.
        with self.assertRaisesRegex(BudgetConflict, "concurrency capacity unavailable: exec"):
            plan_reservations(work, limits, profile(), owner_id="EX-2")

    def test_a_profile_without_capacities_reserves_nothing(self):
        machine = {"id": "EP-2", "revision": 1, "sha256": "1" * 64, "actor_kind": "machine"}
        self.assertEqual(plan_reservations([], constraints(), machine, owner_id="EX-1"), ())

    def test_host_capacity_is_checked_separately_and_keeps_the_control_reserve(self):
        with self.assertRaisesRegex(BudgetConflict, "host capacity unavailable: host/memory_bytes"):
            plan_reservations([], constraints(), profile(host_memory=101), owner_id="EX-1")
        # 50 fits the capacity of 100 but not the 40 left beside a reserve of 60.
        reserve = {**RESERVE, "memory_bytes": 60}
        with self.assertRaisesRegex(BudgetConflict, "host capacity unavailable: host/memory_bytes"):
            plan_reservations([], constraints(reserve=reserve), profile(), owner_id="EX-1")

    def test_returned_slot_is_reusable_but_held_slot_remains_occupied(self):
        returned = {"id": "RR-returned", "owner_id": "EX-0", "constraint_id": "exec", "unit": "execution",
                    "reserved": 1, "confirmed_consumed": 0, "returned": 1, "state": "settled",
                    "evidence_refs": [{"receipt": "local_job_empty"}]}
        held = {**returned, "id": "RR-held", "returned": 0, "state": "held", "evidence_refs": [],
                "reobserve": {"on": "local_termination_barrier"}}
        runtime = {"reservations": {row["id"]: row for row in (returned, held)}}
        self.assertEqual(held_reservations(runtime), [held])
        allowed = plan_reservations([], constraints(), profile(), owner_id="EX-1")
        self.assertEqual(len(allowed), 4)
        with self.assertRaisesRegex(BudgetConflict, "concurrency capacity unavailable: exec"):
            plan_reservations(held_reservations(runtime), constraints(), profile(), owner_id="EX-1")

    def test_settlement_is_exactly_once_and_requires_full_accounting(self):
        record = next(r for r in plan_reservations([], constraints(), profile(), owner_id="EX-1")
                      if r["constraint_id"] == "exec")
        with self.assertRaisesRegex(BudgetInputError, "every reserved unit exactly once"):
            settle_reservation(record, confirmed_consumed=0, returned=0, evidence_refs=[{"receipt": "x"}])
        settled = settle_reservation(record, confirmed_consumed=0, returned=1, evidence_refs=[{"receipt": "x"}])
        self.assertEqual(settled["state"], "settled")
        self.assertNotIn("reobserve", settled)
        self.assertEqual(record["state"], "held")
        with self.assertRaisesRegex(BudgetInputError, "only a held reservation"):
            settle_reservation(settled, confirmed_consumed=0, returned=1, evidence_refs=[{"receipt": "x"}])


if __name__ == "__main__":
    unittest.main()

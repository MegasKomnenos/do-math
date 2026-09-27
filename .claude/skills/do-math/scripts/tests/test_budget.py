"""Pure reservation arithmetic of one execution's pinned profile."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math.budget import (  # noqa: E402
    BudgetConflict,
    BudgetInputError,
    plan_reservations,
    settle_reservation,
)
from do_math.session_slots import held_reservations  # noqa: E402

RESERVE = {"jobs": 0, "memory_bytes": 0, "cpu_rate_basis_points": 0}


class BudgetTests(unittest.TestCase):
    def constraints(self, *, work_slots: int = 1, max_jobs: int = 1, memory_bytes: int = 100,
                    reserve: dict | None = None) -> dict:
        return {
            "exec": {"id": "exec", "kind": "concurrency", "accounting_unit": "execution",
                     "work_slots": work_slots},
            "host": {"id": "host", "kind": "host", "max_jobs": max_jobs, "memory_bytes": memory_bytes,
                     "cpu_rate_basis_points": 10000, "control_reserve": reserve or dict(RESERVE)},
        }

    def profile(self, *, host_memory: int = 50) -> dict:
        return {
            "id": "EP-1", "revision": 1, "sha256": "0" * 64, "actor_kind": "ai",
            "ai": {"capacity_refs": ["exec"]},
            "host_capacity_refs": ["host"],
            "host_resources": {"constraint_id": "host", "demands": {
                "jobs": 1, "memory_bytes": host_memory, "cpu_rate_basis_points": 5000}},
        }

    def test_one_profile_reserves_its_work_slot_and_host_demands_atomically(self) -> None:
        constraints = self.constraints(max_jobs=2, memory_bytes=200)
        before = deepcopy(constraints)
        work = plan_reservations([], constraints, self.profile(), owner_id="EX-1")
        self.assertEqual(sorted((r["constraint_id"], r["unit"], r["reserved"]) for r in work),
                         [("exec", "execution", 1), ("host", "cpu_rate_basis_points", 5000),
                          ("host", "jobs", 1), ("host", "memory_bytes", 50)])
        self.assertTrue(all(r["state"] == "held" and r["owner_id"] == "EX-1"
                            and r["authority_refs"] == [{"id": "EP-1", "revision": 1, "sha256": "0" * 64}]
                            for r in work))
        self.assertEqual(constraints, before)
        with self.assertRaisesRegex(BudgetConflict, "concurrency capacity unavailable: exec"):
            plan_reservations(work, constraints, self.profile(), owner_id="EX-2")

    def test_a_profile_without_capacities_reserves_nothing(self) -> None:
        profile = {"id": "EP-2", "revision": 1, "sha256": "1" * 64, "actor_kind": "machine"}
        self.assertEqual(plan_reservations([], self.constraints(), profile, owner_id="EX-1"), ())

    def test_host_capacity_is_checked_separately_and_keeps_the_control_reserve(self) -> None:
        with self.assertRaisesRegex(BudgetConflict, "host capacity unavailable: host/memory_bytes"):
            plan_reservations([], self.constraints(), self.profile(host_memory=101), owner_id="EX-1")
        reserve = {**RESERVE, "memory_bytes": 60}
        with self.assertRaisesRegex(BudgetConflict, "host capacity unavailable: host/memory_bytes"):
            plan_reservations([], self.constraints(reserve=reserve), self.profile(), owner_id="EX-1")

    def test_returned_slot_is_reusable_but_held_slot_remains_occupied(self) -> None:
        returned = {"id": "RR-returned", "owner_id": "EX-0", "constraint_id": "exec", "unit": "execution",
                    "reserved": 1, "confirmed_consumed": 0, "returned": 1, "state": "settled",
                    "evidence_refs": [{"receipt": "local_job_empty"}]}
        held = {**returned, "id": "RR-held", "returned": 0, "state": "held", "evidence_refs": [],
                "reobserve": {"on": "local_termination_barrier"}}
        runtime = {"reservations": {row["id"]: row for row in (returned, held)}}
        self.assertEqual(held_reservations(runtime), [held])
        allowed = plan_reservations([], self.constraints(), self.profile(), owner_id="EX-1")
        self.assertEqual(len(allowed), 4)
        with self.assertRaisesRegex(BudgetConflict, "concurrency capacity unavailable: exec"):
            plan_reservations(held_reservations(runtime), self.constraints(), self.profile(), owner_id="EX-1")

    def test_settlement_is_exactly_once_and_requires_full_accounting(self) -> None:
        record = next(r for r in plan_reservations([], self.constraints(), self.profile(), owner_id="EX-1")
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
    unittest.main(verbosity=2)

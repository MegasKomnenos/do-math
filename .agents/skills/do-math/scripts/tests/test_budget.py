"""Pure, fixed-snapshot budget calculations for the do-math reservation contract."""

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


class BudgetTests(unittest.TestCase):
    def budget(self) -> dict:
        return {
            "constraints": [
                {"id": "exec", "kind": "concurrency", "accounting_unit": "execution",
                 "work_slots": 1},
                {"id": "host", "kind": "host", "max_jobs": 1, "memory_bytes": 100,
                 "cpu_rate_basis_points": 10000},
            ]
        }

    def profile(self) -> dict:
        return {
            "actor_kind": "ai",
            "ai": {"capacity_refs": ["exec"]},
            "host_capacity_refs": ["host"],
        }

    def request(self, *, prefix: str = "RR-new", host_memory: int = 50) -> dict:
        return {
            "owner_kind": "execution",
            "owner_id": "E-01",
            "purpose": "normal",
            "authority_refs": [{"ref_kind": "record", "record_id": "P-01"}],
            "reobserve": {"kind": "time", "at": "2026-09-14T00:00:00.000Z"},
            "demands": [
                {"id": f"{prefix}-exec", "constraint_id": "exec", "unit": "execution", "amount": 1},
                {"id": f"{prefix}-host-jobs", "constraint_id": "host", "unit": "jobs", "amount": 1},
                {"id": f"{prefix}-host-memory", "constraint_id": "host", "unit": "memory_bytes", "amount": host_memory},
                {"id": f"{prefix}-host-cpu", "constraint_id": "host", "unit": "cpu_rate_basis_points", "amount": 5000},
            ],
        }

    def snapshot(self, reservations: dict | None = None) -> dict:
        return {"reservations": {} if reservations is None else reservations}

    def test_shared_profile_refs_reserve_atomically_and_fill_the_work_slot(self) -> None:
        source = self.snapshot()
        before = deepcopy(source)
        budget = self.budget()
        host = next(item for item in budget["constraints"] if item["id"] == "host")
        host["max_jobs"] = 2
        host["memory_bytes"] = 200
        work = plan_reservations(source, budget, self.profile(), self.request())
        self.assertEqual(len(work), 4)
        self.assertEqual(source, before)

        next_snapshot = self.snapshot({record["id"]: record for record in work})
        with self.assertRaises(BudgetConflict):
            plan_reservations(next_snapshot, budget, self.profile(), self.request(prefix="RR-work-2"))

    def test_failure_does_not_create_partial_records(self) -> None:
        budget = self.budget()
        next(item for item in budget["constraints"] if item["id"] == "exec")["work_slots"] = 0
        source = self.snapshot()
        before = deepcopy(source)
        with self.assertRaises(BudgetConflict):
            plan_reservations(source, budget, self.profile(), self.request())
        self.assertEqual(source, before)

    def test_host_capacity_is_checked_separately(self) -> None:
        with self.assertRaises(BudgetConflict):
            plan_reservations(self.snapshot(), self.budget(), self.profile(), self.request(host_memory=101))

    def test_returned_slot_is_reusable_but_held_slot_remains_occupied(self) -> None:
        returned = {
            "RR-returned": {
                "id": "RR-returned", "constraint_id": "exec", "unit": "execution",
                "reserved": 1, "confirmed_consumed": 0, "returned": 1, "state": "settled",
                "evidence_refs": [{"receipt": "local_job_empty"}],
            },
        }
        held = {
            "RR-held": {
                "id": "RR-held", "constraint_id": "exec", "unit": "execution",
                "reserved": 1, "confirmed_consumed": 0, "returned": 0, "state": "held",
                "reobserve": {"kind": "time", "at": "2026-09-14T00:00:00.000Z"},
            },
        }
        allowed = plan_reservations(self.snapshot(returned), self.budget(), self.profile(), self.request())
        self.assertEqual(len(allowed), 4)
        with self.assertRaisesRegex(BudgetConflict, "concurrency capacity unavailable: exec"):
            plan_reservations(self.snapshot(held), self.budget(), self.profile(), self.request())

    def test_existing_reservation_id_is_rejected(self) -> None:
        first = plan_reservations(self.snapshot(), self.budget(), self.profile(), self.request())
        populated = self.snapshot({record["id"]: record for record in first})
        with self.assertRaisesRegex(BudgetInputError, "reservation ID already exists"):
            plan_reservations(populated, self.budget(), self.profile(), self.request())

    def test_settlement_is_exactly_once_and_requires_full_accounting(self) -> None:
        planned = plan_reservations(self.snapshot(), self.budget(), self.profile(), self.request())
        records = {record["id"]: record for record in planned}
        with self.assertRaisesRegex(BudgetInputError, "every reserved unit exactly once"):
            settle_reservation(
                self.snapshot(records), "RR-new-exec", confirmed_consumed=0, returned=0, evidence_refs=[{"receipt": "x"}]
            )
        settled = settle_reservation(
            self.snapshot(records), "RR-new-exec", confirmed_consumed=0, returned=1, evidence_refs=[{"receipt": "x"}]
        )
        self.assertEqual(settled["state"], "settled")
        self.assertNotIn("reobserve", settled)
        settled_snapshot = self.snapshot({**records, settled["id"]: settled})
        with self.assertRaisesRegex(BudgetInputError, "only a held reservation"):
            settle_reservation(
                settled_snapshot, "RR-new-exec", confirmed_consumed=0, returned=1, evidence_refs=[{"receipt": "x"}]
            )

    def test_unsupported_constraint_kind_is_rejected(self) -> None:
        budget = self.budget()
        budget["constraints"].append({"id": "tokens", "kind": "cumulative"})
        profile = self.profile()
        profile["ai"]["capacity_refs"].append("tokens")
        request = self.request()
        request["demands"].append({"id": "RR-new-tokens", "constraint_id": "tokens", "unit": "tokens", "amount": 1})
        with self.assertRaisesRegex(BudgetInputError, "unsupported constraint kind"):
            plan_reservations(self.snapshot(), budget, profile, request)


if __name__ == "__main__":
    unittest.main(verbosity=2)

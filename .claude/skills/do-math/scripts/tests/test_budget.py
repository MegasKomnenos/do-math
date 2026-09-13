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
    BudgetReplayConflict,
    plan_reservations,
    settle_reservation,
)


class BudgetTests(unittest.TestCase):
    def budget(self) -> dict:
        return {
            "constraints": [
                {"id": "exec", "kind": "concurrency", "accounting_unit": "execution",
                 "work_slots": 1, "operations_slots": 1, "total_slots": 2},
                {"id": "provider", "kind": "concurrency", "accounting_unit": "provider_operation",
                 "work_slots": 1, "operations_slots": 1, "total_slots": 2},
                {"id": "tokens", "kind": "cumulative", "unit": "tokens",
                 "limit": {"kind": "bounded", "value": 100}, "window": {"kind": "none"}},
                {"id": "rpm", "kind": "window", "unit": "requests",
                 "limit": {"kind": "bounded", "value": 5}, "window": {"kind": "fixed"}},
                {"id": "host", "kind": "host", "max_jobs": 1, "memory_bytes": 100,
                 "cpu_rate_basis_points": 10000},
            ]
        }

    def profile(self) -> dict:
        return {
            "actor_kind": "ai",
            "ai": {
                "capacity_refs": ["exec", "provider"],
                "usage_constraint_ids": ["tokens", "rpm"],
            },
            "host_capacity_refs": ["host"],
        }

    def request(self, *, prefix: str = "RR-new", budget_kind: str = "work", token_amount: int = 20,
                rpm_amount: int = 2, host_memory: int = 50) -> dict:
        return {
            "budget_kind": budget_kind,
            "owner_kind": "execution",
            "owner_id": "E-01",
            "purpose": "normal",
            "authority_refs": [{"ref_kind": "record", "record_id": "P-01"}],
            "reobserve": {"kind": "time", "at": "2026-09-14T00:00:00.000Z"},
            "demands": [
                {"id": f"{prefix}-exec", "constraint_id": "exec", "unit": "execution", "amount": 1},
                {"id": f"{prefix}-provider", "constraint_id": "provider", "unit": "provider_operation", "amount": 1},
                {"id": f"{prefix}-tokens", "constraint_id": "tokens", "unit": "tokens", "amount": token_amount},
                {"id": f"{prefix}-rpm", "constraint_id": "rpm", "unit": "requests", "amount": rpm_amount},
                {"id": f"{prefix}-host-jobs", "constraint_id": "host", "unit": "jobs", "amount": 1},
                {"id": f"{prefix}-host-memory", "constraint_id": "host", "unit": "memory_bytes", "amount": host_memory},
                {"id": f"{prefix}-host-cpu", "constraint_id": "host", "unit": "cpu_rate_basis_points", "amount": 5000},
            ],
        }

    def snapshot(self, reservations: dict | None = None, window_population: dict | None = None) -> dict:
        return {
            "reservations": {} if reservations is None else reservations,
            "window_population": {"rpm": ()} if window_population is None else window_population,
        }

    def test_shared_profile_refs_reserve_atomically_and_separate_work_from_operations(self) -> None:
        source = self.snapshot()
        before = deepcopy(source)
        budget = self.budget()
        host = next(item for item in budget["constraints"] if item["id"] == "host")
        host["max_jobs"] = 2
        host["memory_bytes"] = 200
        work = plan_reservations(source, budget, self.profile(), self.request())
        self.assertEqual(len(work.records), 7)
        self.assertEqual(source, before)

        next_snapshot = self.snapshot({record["id"]: record for record in work.records})
        operations = plan_reservations(
            next_snapshot, budget, self.profile(), self.request(prefix="RR-ops", budget_kind="operations")
        )
        self.assertEqual(len(operations.records), 7)
        with self.assertRaises(BudgetConflict):
            plan_reservations(next_snapshot, budget, self.profile(), self.request(prefix="RR-work-2"))

    def test_failure_does_not_create_partial_records(self) -> None:
        budget = self.budget()
        next(item for item in budget["constraints"] if item["id"] == "provider")["work_slots"] = 0
        source = self.snapshot()
        before = deepcopy(source)
        with self.assertRaises(BudgetConflict):
            plan_reservations(source, budget, self.profile(), self.request())
        self.assertEqual(source, before)

    def test_host_capacity_is_checked_separately(self) -> None:
        with self.assertRaises(BudgetConflict):
            plan_reservations(self.snapshot(), self.budget(), self.profile(), self.request(host_memory=101))

    def test_cumulative_consumption_is_not_returned_and_unknown_remote_remains_held(self) -> None:
        existing = {
            "RR-consumed": {
                "id": "RR-consumed", "constraint_id": "tokens", "unit": "tokens", "budget_kind": "work",
                "reserved": 30, "confirmed_consumed": 30, "returned": 0, "state": "settled",
                "evidence_refs": [{"receipt": "tokens"}],
            },
            "RR-remote": {
                "id": "RR-remote", "constraint_id": "provider", "unit": "provider_operation", "budget_kind": "work",
                "reserved": 1, "confirmed_consumed": 0, "returned": 0, "state": "held",
                "reobserve": {"kind": "time", "at": "2026-09-14T00:00:00.000Z"},
            },
        }
        with self.assertRaises(BudgetConflict):
            plan_reservations(self.snapshot(existing), self.budget(), self.profile(), self.request(token_amount=80))
        with self.assertRaises(BudgetConflict):
            plan_reservations(self.snapshot(existing), self.budget(), self.profile(), self.request(token_amount=20))

    def test_exact_request_replays_but_changed_request_with_same_id_is_rejected(self) -> None:
        first = plan_reservations(self.snapshot(), self.budget(), self.profile(), self.request())
        populated = self.snapshot({record["id"]: record for record in first.records})
        replay = plan_reservations(populated, self.budget(), self.profile(), self.request())
        self.assertTrue(replay.replayed)
        self.assertEqual(replay.records, first.records)
        with self.assertRaises(BudgetReplayConflict):
            plan_reservations(populated, self.budget(), self.profile(), self.request(token_amount=21))

    def test_settlement_is_exactly_once_and_requires_full_accounting(self) -> None:
        planned = plan_reservations(self.snapshot(), self.budget(), self.profile(), self.request())
        records = {record["id"]: record for record in planned.records}
        settlement = settle_reservation(
            self.snapshot(records), "RR-new-tokens", confirmed_consumed=3, returned=17, evidence_refs=[{"receipt": "x"}]
        )
        self.assertFalse(settlement.replayed)
        self.assertEqual(settlement.record["state"], "settled")
        settled_snapshot = self.snapshot({**records, settlement.record["id"]: settlement.record})
        self.assertTrue(settle_reservation(
            settled_snapshot, "RR-new-tokens", confirmed_consumed=3, returned=17, evidence_refs=[{"receipt": "x"}]
        ).replayed)
        with self.assertRaises(BudgetReplayConflict):
            settle_reservation(
                settled_snapshot, "RR-new-tokens", confirmed_consumed=4, returned=16, evidence_refs=[{"receipt": "x"}]
            )

    def test_window_population_is_caller_bound_not_a_verified_window_complete_set(self) -> None:
        old = {
            "id": "RR-window-old", "constraint_id": "rpm", "unit": "requests", "budget_kind": "work",
            "reserved": 3, "confirmed_consumed": 0, "returned": 0, "state": "held",
            "reobserve": {"kind": "time", "at": "2026-09-14T00:00:00.000Z"},
        }
        source = self.snapshot({old["id"]: old}, {"rpm": (old["id"],)})
        planned = plan_reservations(source, self.budget(), self.profile(), self.request(rpm_amount=2))
        self.assertEqual(planned.unverified_window_constraints, ("rpm",))
        missing_population = self.snapshot({old["id"]: old}, {})
        with self.assertRaises(BudgetInputError):
            plan_reservations(missing_population, self.budget(), self.profile(), self.request(rpm_amount=2))


if __name__ == "__main__":
    unittest.main(verbosity=2)

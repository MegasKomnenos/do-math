"""Shared admission, bounded retries, and single-owner re-observation."""
import multiprocessing
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.session_slots import SessionSlots
from do_math.provider_wait import timestamp


FAILURE = {"kind": "provider_limit", "provider": "claude", "retry_at": None,
           "evidence_ref": "native.jsonl", "limit_windows": []}


def compete(workspace, ready, release, output, name):
    slots = SessionSlots(Path(workspace), "instance")
    try:
        ready.wait(20)
        acquired = slots.acquire(name, "work", "claude-opus-5", provider="claude", current_time=500)
        output.put((name, acquired))
        release.wait(20)
        if acquired:
            slots.release(name)
    finally:
        slots.close()


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.slots = SessionSlots(self.root, "instance")
        self.slots.configure({"work": {"claude-opus-5": 3}, "operations": {"claude-opus-5": 1}})

    def tearDown(self):
        self.slots.close()
        self.temporary.cleanup()

    def reject(self, identifier="original", current=100):
        self.assertTrue(self.slots.acquire(identifier, "work", "claude-opus-5", provider="claude", current_time=current))
        result = self.slots.provider_result(identifier, "claude", failure=FAILURE, current_time=current)
        self.slots.release(identifier)
        return result

    def test_restriction_blocks_both_pools_and_survives_another_owner(self):
        self.reject()
        other = SessionSlots(self.root, "instance")
        try:
            for pool in ("work", "operations"):
                self.assertFalse(other.acquire(pool, pool, "claude-opus-5", provider="claude", current_time=399))
            self.assertEqual(other.admission_reason, "provider_limit")
            self.assertEqual(other.snapshot()["work"]["claude-opus-5"]["used"], 0)
            self.assertTrue(other.acquire("probe", "operations", "claude-opus-5", provider="claude", current_time=400))
            self.assertFalse(self.slots.acquire("next", "work", "claude-opus-5", provider="claude", current_time=401))
            other.provider_result("probe", "claude", current_time=402)
            other.release("probe")
            self.assertTrue(self.slots.acquire("next", "work", "claude-opus-5", provider="claude", current_time=403))
        finally:
            other.close()

    def test_late_success_does_not_release_a_newer_rejection(self):
        self.assertTrue(self.slots.acquire("old", "work", "claude-opus-5", provider="claude", current_time=1))
        first = self.reject()
        self.assertTrue(self.slots.acquire("probe", "work", "claude-opus-5", provider="claude", current_time=400))
        second = self.slots.provider_result("old", "claude", failure=FAILURE, current_time=401)
        self.slots.provider_result("probe", "claude", current_time=402)
        current = self.slots.provider_snapshot(current_time=403)["providers"]["claude"]
        self.assertEqual(current["generation"], first["generation"] + 1)
        self.assertEqual(current["generation"], second["generation"])
        self.assertEqual(current["state"], "waiting")

    def test_classic_mode_uses_gate_without_model_capacity(self):
        self.slots.configure({"work": {}, "operations": {}})
        self.assertTrue(self.slots.acquire("classic", "operations", "claude-opus-5", provider="claude", enforce_capacity=False, current_time=1))
        self.slots.provider_result("classic", "claude", failure=FAILURE, current_time=1)
        self.slots.release("classic")
        self.assertFalse(self.slots.acquire("blocked", "operations", "claude-opus-5", provider="claude", enforce_capacity=False, current_time=2))

    def test_unknown_limit_uses_bounded_backoff_and_known_limit_preserves_time(self):
        first = self.reject()
        self.assertEqual(timestamp(first["retry_at"]), 400)
        self.assertTrue(self.slots.acquire("probe", "work", "claude-opus-5", provider="claude", current_time=400))
        next_wait = self.slots.provider_result("probe", "claude", failure=FAILURE, current_time=400, maximum_seconds=500)
        self.assertEqual(timestamp(next_wait["retry_at"]), 900)
        self.slots.release("probe")

    def test_dead_probe_owner_is_reconciled_without_claiming_success(self):
        self.reject()
        other = SessionSlots(self.root, "instance")
        self.assertTrue(other.acquire("vanished", "work", "claude-opus-5", provider="claude", current_time=400))
        other.close()  # No suspended Job was acknowledged, so local lifetime is known.
        gate = self.slots.provider_snapshot(current_time=500)["providers"]["claude"]
        self.assertEqual(gate["state"], "waiting")
        self.assertTrue(self.slots.acquire("replacement", "operations", "claude-opus-5", provider="claude", current_time=500))

    def test_two_real_processes_admit_one_probe(self):
        self.reject()
        context = multiprocessing.get_context("spawn")
        ready, release, output = context.Event(), context.Event(), context.Queue()
        children = [context.Process(target=compete, args=(str(self.root), ready, release, output, name)) for name in ("one", "two")]
        try:
            for child in children:
                child.start()
            ready.set()
            outcomes = [output.get(timeout=20), output.get(timeout=20)]
            self.assertEqual(sum(success for _, success in outcomes), 1, outcomes)
        finally:
            release.set()
            for child in children:
                child.join(20)
                if child.is_alive():
                    child.terminate()
                    child.join(5)
                self.assertEqual(child.exitcode, 0)


if __name__ == "__main__":
    unittest.main()

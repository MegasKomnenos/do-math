from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import control_transport as transport_module
from do_math.control_transport import ControlTransport


class ControlTransportIoTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.transport = ControlTransport(self.root / "transport")
        self.binding = self.transport.issue("EX-transport", "GR-transport")
        self.endpoint = Path(self.binding["endpoint"])

    def test_nonstring_control_fields_reject_without_breaking_later_requests(self):
        transport = ControlTransport()
        binding = transport.issue("EX-memory", "GR-memory")
        published = []
        def publish(request):
            published.append(request["request_id"])
            return {"state": "rejected", "reason": "fixture receiver"}
        for field in ("transport_id", "kind"):
            for index, value in enumerate(([], {})):
                with self.subTest(field=field, value=value):
                    request_id = field + "-" + str(index)
                    request = {**binding, "request_id": request_id,
                               "kind": "submit_intent", "payload": {}, field: value}
                    receipt = transport.receive(request, publish=publish)
                    self.assertEqual(receipt["state"], "rejected")
                    self.assertEqual(transport.receipt(request_id), receipt)
        self.assertEqual(published, [])
        receipt = transport.receive({**binding, "request_id": "valid-after-errors",
            "kind": "submit_intent", "payload": {}}, publish=publish)
        self.assertEqual(receipt["reason"], "fixture receiver")
        self.assertEqual(published, ["valid-after-errors"])

    def test_competing_different_payloads_cannot_both_submit(self):
        request_id = "race-one"
        request_path = self.endpoint / "inbox" / f"{request_id}.json"
        barrier = threading.Barrier(2)
        original_json = transport_module._json
        observed_absence = threading.local()

        def synchronized_json(path):
            value = original_json(path)
            if Path(path) == request_path and value is None and not getattr(observed_absence, "done", False):
                observed_absence.done = True
                barrier.wait(timeout=10)
            return value

        outcomes = []

        def submit(marker):
            try:
                outcomes.append(ControlTransport.worker_submit(
                    self.binding, request_id=request_id, kind="submit_intent",
                    payload={"manifest": [f"{marker}.json"]},
                ))
            except Exception as error:  # the losing writer must report the collision
                outcomes.append(error)

        with patch.object(transport_module, "_json", side_effect=synchronized_json):
            threads = [threading.Thread(target=submit, args=(marker,)) for marker in ("first", "second")]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=15)

        self.assertTrue(all(not thread.is_alive() for thread in threads), "race reproduction deadlocked")
        submitted = [value for value in outcomes if isinstance(value, dict)]
        collisions = [value for value in outcomes if isinstance(value, ValueError)]
        self.assertEqual(1, len(submitted), outcomes)
        self.assertEqual(1, len(collisions), outcomes)
        self.assertIn("different content", str(collisions[0]))
        stored = json.loads(request_path.read_text(encoding="utf-8"))
        self.assertEqual(submitted[0]["request_id"], stored["request_id"])
        replay = ControlTransport.worker_submit(
            self.binding, request_id=request_id, kind="submit_intent", payload=stored["payload"])
        self.assertEqual("submitted", replay["state"])

    def test_file_identifiers_reject_path_glob_and_windows_device_names(self):
        invalid = ("../escape", "part/name", "part\\name", "wild*card", "query?", "CON", "trail.")
        for request_id in invalid:
            with self.subTest(request_id=request_id):
                with self.assertRaisesRegex(ValueError, "safe file name"):
                    ControlTransport.worker_submit(
                        self.binding, request_id=request_id, kind="submit_intent", payload={"manifest": []})
                with self.assertRaisesRegex(ValueError, "safe file name"):
                    ControlTransport.worker_receipt(self.binding, request_id)
        for self_check_id in invalid:
            with self.subTest(self_check_id=self_check_id):
                with self.assertRaisesRegex(ValueError, "safe file name"):
                    self.transport.request_self_check(self.binding, self_check_id=self_check_id, payload={})
                with self.assertRaisesRegex(ValueError, "safe file name"):
                    ControlTransport.worker_self_check(self.binding, self_check_id=self_check_id)

    def test_transport_id_cannot_load_a_binding_outside_the_transport_root(self):
        outside = self.root / "outside"
        outside_endpoint = outside / "endpoint"
        for name in ("inbox", "outbox", "worker-inbox", "worker-outbox"):
            (outside_endpoint / name).mkdir(parents=True, exist_ok=True)
        malicious = deepcopy(self.binding)
        malicious.update(transport_id="../outside", endpoint=str(outside_endpoint))
        (outside / "binding.json").write_text(json.dumps(malicious), encoding="utf-8")
        (outside_endpoint / "state.json").write_text('{"state":"open"}', encoding="utf-8")
        request = {key: malicious[key] for key in ("transport_id", "capability", "execution_id", "grant_id")}
        request.update(request_id="safe-request", kind="submit_intent", payload={"manifest": []})
        published = []

        receipt = ControlTransport(self.root / "transport").receive(
            request, publish=lambda value: published.append(value) or {
                "state": "accepted", "published": True, "snapshot": "outside-snapshot"})

        self.assertEqual("rejected", receipt["state"])
        self.assertIn("transport_id", receipt["reason"])
        self.assertEqual([], published)
        self.assertFalse((outside_endpoint / "outbox" / "safe-request.json").exists())

    def test_malformed_request_has_queryable_rejection_and_preserves_source(self):
        request_id = "malformed-one"
        source = self.endpoint / "inbox" / f"{request_id}.json"
        raw = b'{"request_id":'
        source.write_bytes(raw)

        results = self.transport.pump(lambda _: self.fail("malformed input must not publish"))

        self.assertEqual(1, len(results))
        receipt = results[0]
        self.assertEqual("rejected", receipt["state"])
        self.assertEqual("delivery_validation", receipt["stage"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt["source_sha256"])
        self.assertEqual(f"inbox/{request_id}.json", receipt["source"])
        self.assertIn("JSON", receipt["reason"])
        self.assertEqual(raw, source.read_bytes())
        self.assertEqual(receipt, ControlTransport.worker_receipt(self.binding, request_id))
        self.assertEqual(receipt, ControlTransport.wait_receipt(self.binding, request_id, 0))
        self.assertEqual(receipt, self.transport.pump(lambda _: self.fail("replay must not publish"))[0])
        source.write_bytes(b'{"different":')
        with self.assertRaisesRegex(ValueError, "different content"):
            self.transport.pump(lambda _: self.fail("changed malformed input must not publish"))
        self.assertEqual(receipt, ControlTransport.worker_receipt(self.binding, request_id))

    def test_concurrent_real_files_do_not_reproduce_old_permission_error(self):
        errors = []
        start = threading.Barrier(3)
        stopping = threading.Event()

        def producer(prefix):
            try:
                start.wait(timeout=10)
                for index in range(40):
                    if stopping.is_set():
                        return
                    ControlTransport.worker_submit(
                        self.binding, request_id=f"{prefix}-{index}", kind="submit_intent",
                        payload={"manifest": [f"{prefix}-{index}.json"]})
            except Exception as error:
                errors.append(error)

        # A broken I/O implementation must not keep the test process alive.
        threads = [threading.Thread(target=producer, args=(prefix,), daemon=True) for prefix in ("left", "right")]
        for thread in threads:
            thread.start()
        start.wait(timeout=10)
        deadline = time.monotonic() + 15
        while any(thread.is_alive() for thread in threads):
            if time.monotonic() >= deadline:
                errors.append(TimeoutError("request producers did not finish; inbox=" +
                    repr(sorted(p.name for p in (self.endpoint / "inbox").glob("*.json")))))
                break
            try:
                self.transport.pump(lambda _: {"state": "rejected", "reason": "stress observation"})
            except Exception as error:
                errors.append(error)
                break
            time.sleep(.01)
        stopping.set()
        for thread in threads:
            thread.join(timeout=1)
        self.assertFalse(any(thread.is_alive() for thread in threads), errors)
        self.transport.pump(lambda _: {"state": "rejected", "reason": "stress observation"})

        self.assertFalse(any(isinstance(error, PermissionError) for error in errors), errors)
        self.assertEqual([], errors)

    def test_final_delivery_is_not_reread_until_its_fingerprint_changes(self):
        import os
        from do_math import file_io
        ControlTransport.worker_submit(self.binding, request_id='cached', kind='submit_intent',
                                       payload={'manifest': ['first.json']})
        path = self.endpoint / 'inbox/cached.json'
        original = path.stat()
        # A fresh file's birth time cannot be aged; treat any past fingerprint as settled.
        with patch.object(self.transport, 'receive', wraps=self.transport.receive) as receive, \
                patch.object(file_io, 'RACY_NS', 0):
            first = self.transport.pump(lambda _: {'state': 'rejected', 'reason': 'fixture'})
            with patch.object(transport_module, '_decode_json', side_effect=AssertionError('final delivery reread')):
                self.assertEqual(self.transport.pump(lambda _: self.fail('must not republish')), first)
            self.assertEqual(receive.call_count, 1)
            raw = path.read_bytes()
            path.write_bytes(raw.replace(b'first.json', b'other.json'))
            os.utime(path, ns=(original.st_atime_ns, original.st_mtime_ns + 10 ** 9))
            with self.assertRaisesRegex(ValueError, 'different content'):
                self.transport.pump(lambda _: self.fail('changed identity must not publish'))
            self.assertEqual(receive.call_count, 2)


if __name__ == "__main__":
    unittest.main()

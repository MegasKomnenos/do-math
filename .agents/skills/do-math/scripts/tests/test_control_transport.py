"""The execution control transport: requests and receipts, previews, and the worker-side MCP child over real files."""
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
import subprocess
import os

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
                    # The rejection is recorded: the same request replays it.
                    self.assertEqual(transport.receive(request, publish=publish), receipt)
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
                    self.transport.request_self_check(self.binding, request={"self_check_id": self_check_id,
                        "execution_id": self.binding["execution_id"], "payload": {}})
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

    def test_pump_reads_only_open_transports_and_close_answers_a_raced_delivery(self):
        closed = self.transport.issue("EX-closed", "GR-closed")
        inbox = Path(closed["endpoint"]) / "inbox"
        raced = {key: closed[key] for key in ("transport_id", "capability", "execution_id", "grant_id")}
        raced.update(request_id="raced", kind="submit_intent", payload={})
        (inbox / "raced.json").write_text(json.dumps(raced), encoding="utf-8")
        self.transport.close(closed, reason="execution ended")
        self.assertEqual(ControlTransport.worker_receipt(closed, "raced")["state"], "closed")
        (inbox / "late.json").write_text(json.dumps({**raced, "request_id": "late"}), encoding="utf-8")
        refuse = lambda _: self.fail("a closed transport's delivery must not publish")
        self.assertEqual(self.transport.pump(refuse), [])
        self.assertEqual(ControlTransport(self.root / "transport").pump(refuse), [])
        self.assertIsNone(ControlTransport.worker_receipt(closed, "late"))

    def test_open_transports_are_read_at_the_first_pump_not_at_construction(self):
        with patch.object(transport_module, "_is_open", side_effect=AssertionError("constructor read a transport")):
            later = ControlTransport(self.root / "transport")
        # A transport issued and one closed through this object before its first pump.
        issued = later.issue("EX-later", "GR-later")
        closed = later.issue("EX-closed", "GR-closed")
        later.close(closed, reason="execution ended")
        for binding, request_id in ((self.binding, "first-open"), (issued, "second-open"), (closed, "after-close")):
            request = {key: binding[key] for key in ("transport_id", "capability", "execution_id", "grant_id")}
            request.update(request_id=request_id, kind="submit_intent", payload={})
            (Path(binding["endpoint"]) / "inbox" / (request_id + ".json")).write_text(json.dumps(request), encoding="utf-8")
        published = []
        later.pump(lambda request: published.append(request["request_id"]) or {"state": "rejected", "reason": "fixture"})
        self.assertEqual(sorted(published), ["first-open", "second-open"])

    def test_request_id_rejected_without_engine_record_stays_taken_in_every_transport(self):
        # The engine records no receipt for an early rejection; the transport's outbox alone keeps the ID taken.
        first = {key: self.binding[key] for key in ("transport_id", "capability", "execution_id", "grant_id")}
        first.update(request_id="shared", kind="submit_intent", payload={"draft_path": "a.json"})
        (self.endpoint / "inbox" / "shared.json").write_text(json.dumps(first), encoding="utf-8")
        self.transport.pump(lambda _: {"state": "rejected", "reason": "execution is no longer running"})
        other = self.transport.issue("EX-other", "GR-other")
        second = {key: other[key] for key in ("transport_id", "capability", "execution_id", "grant_id")}
        second.update(request_id="shared", kind="submit_intent", payload={"draft_path": "b.json"})
        (Path(other["endpoint"]) / "inbox" / "shared.json").write_text(json.dumps(second), encoding="utf-8")
        # A new transport object has no memory of the first receipt; it must find it on disk.
        fresh = ControlTransport(self.root / "transport")
        fresh.pump(lambda _: self.fail("a reused request ID must not reach the engine"))
        receipt = ControlTransport.worker_receipt(other, "shared")
        self.assertEqual((receipt["state"], receipt["stage"]), ("rejected", "delivery_validation"))
        self.assertIn("different content", receipt["reason"])

    def test_close_records_a_changed_redelivery_it_cannot_settle(self):
        ControlTransport.worker_submit(self.binding, request_id="changed", kind="submit_intent",
                                       payload={"manifest": ["first.json"]})
        self.transport.pump(lambda _: {"state": "rejected", "reason": "fixture"})
        path = self.endpoint / "inbox" / "changed.json"
        path.write_bytes(path.read_bytes().replace(b"first.json", b"other.json"))
        state = self.transport.close(self.binding, reason="execution ended")
        self.assertEqual(ControlTransport.worker_receipt(self.binding, "changed")["reason"], "fixture")
        stored = json.loads((self.endpoint / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(stored, state)
        self.assertEqual([row["source"] for row in stored["unsettled_deliveries"]], ["inbox/changed.json"])
        self.assertIn("different content", stored["unsettled_deliveries"][0]["reason"])

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


class ControlPreviewTests(unittest.TestCase):
    def test_preview_is_replayable_but_never_a_publication_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory)
            binding = transport.issue("EX-preview", "GR-preview")
            ControlTransport.worker_submit(binding, request_id="preview-1", kind="submission_preview",
                                           payload={"output_sha256": "a" * 64})
            calls = []
            def inspect(request):
                calls.append(request)
                return {"state": "previewed", "result": {"valid": True, "snapshot": "checked-snapshot"}}
            receipt = transport.pump(inspect)[0]
            self.assertEqual(receipt["state"], "previewed")
            self.assertTrue(receipt["result"]["valid"])
            self.assertNotIn("publication_id", receipt)
            self.assertNotIn("snapshot", receipt)
            self.assertEqual(ControlTransport.wait_receipt(binding, "preview-1", 0), receipt)
            self.assertEqual(ControlTransport(directory).pump(lambda _: self.fail("duplicate preview"))[0], receipt)
            self.assertEqual(len(calls), 1)

    def test_preview_cannot_be_misreported_as_accepted_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory)
            binding = transport.issue("EX-preview", "GR-preview")
            request = {**binding, "request_id": "preview-1", "kind": "submission_preview", "payload": {}}
            with self.assertRaisesRegex(ValueError, "without publication"):
                transport.receive(request, publish=lambda _: {"state": "accepted", "published": True, "snapshot": "head"})
            self.assertIsNone(ControlTransport.worker_receipt(binding, "preview-1"))

    def test_real_mcp_child_delivers_preview_and_returns_its_structured_result(self):
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory)
            binding = transport.issue("EX-preview", "GR-preview")
            server = transport.mcp_server_config(binding)
            child = subprocess.Popen([server["command"], *server["args"]], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            def rpc(number, method, params):
                child.stdin.write(json.dumps({"jsonrpc": "2.0", "id": number, "method": method, "params": params}) + "\n")
                child.stdin.flush()
                return json.loads(child.stdout.readline())
            try:
                rpc(1, "initialize", {"protocolVersion": "2024-11-05"})
                tools = rpc(2, "tools/list", {})["result"]["tools"]
                submit_schema = next(tool for tool in tools if tool["name"] == "control_submit")["inputSchema"]
                self.assertIn("submission_preview", submit_schema["properties"]["kind"]["enum"])
                submitted = rpc(3, "tools/call", {"name": "control_submit", "arguments": {
                    "request_id": "preview-mcp", "kind": "submission_preview", "payload": {"draft": "fixture"}}})
                self.assertNotIn("error", submitted)
                transport.pump(lambda _: {"state": "previewed", "result": {"valid": False, "issues": ["stale input"]}})
                reply = rpc(4, "tools/call", {"name": "control_receipt", "arguments": {"request_id": "preview-mcp", "wait_seconds": 0}})
                receipt = json.loads(reply["result"]["content"][0]["text"])
                self.assertEqual(receipt["state"], "previewed")
                self.assertEqual(receipt["result"]["issues"], ["stale input"])
            finally:
                child.stdin.close()
                child.wait(timeout=10)
                child.stdout.close()
                child.stderr.close()


class ControlTransportTests(unittest.TestCase):
    def test_mcp_child_offers_the_self_check_tool_only_to_self_checking_executions(self):
        # Only research work answers self checks (observations.tracker_config).
        listed = {}
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory)
            for self_check in (True, False):
                binding = transport.issue("EX-" + str(self_check), "GR-1", self_check=self_check)
                ControlTransport.validate_binding(binding, execution_id=binding["execution_id"])
                server = transport.mcp_server_config(binding)
                child = subprocess.Popen([server["command"], *server["args"]], stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                try:
                    child.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}) + "\n")
                    child.stdin.flush()
                    listed[self_check] = {tool["name"] for tool in json.loads(child.stdout.readline())["result"]["tools"]}
                finally:
                    child.stdin.close()
                    child.wait(timeout=10)
                    child.stdout.close()
                    child.stderr.close()
        self.assertEqual(listed[True] - listed[False], {transport_module.SELF_CHECK_TOOL})

    def test_control_rejects_an_unconfirmed_boundary_and_request_id_reuse(self):
        with tempfile.TemporaryDirectory() as root:
            transport = ControlTransport(root)
            capability = transport.issue("EX-1", "GR-1")
            request = {**capability, "request_id": "CT-1", "kind": "safety_boundary",
                       "payload": {"inflight_calls": True}}
            self.assertEqual(transport.receive(request)["state"], "rejected")
            self.assertEqual(transport.receive(request)["state"], "rejected")
            with self.assertRaisesRegex(ValueError, "different content"):
                transport.receive({**request, "payload": {"inflight_calls": False}})
            self.assertNotIn("capability", ControlTransport.worker_receipt(capability, "CT-1"))

    def test_received_but_unpublished_request_is_published_on_recovery(self):
        with tempfile.TemporaryDirectory() as root:
            transport = ControlTransport(root)
            binding = transport.issue("EX-receive", "GR-receive")
            ControlTransport.worker_submit(binding, request_id="request-receive", kind="submit_intent",
                                           payload={"manifest": []})
            self.assertEqual(transport.pump()[0]["state"], "received")
            recovered = ControlTransport(root)
            calls = []
            def publish(request):
                calls.append(request)
                return {"state": "accepted", "published": True, "snapshot": "verified-CAS"}
            self.assertEqual(recovered.pump(publish)[0]["state"], "accepted")
            self.assertEqual(len(calls), 1)

    def test_child_process_round_trips_submit_receipt_self_check_and_close(self):
        package_root = str(Path(__file__).resolve().parents[1])
        def child(statement, binding):
            environment = {**os.environ, "PYTHONPATH": package_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
            result = subprocess.run([sys.executable, "-c", statement, json.dumps(binding)], capture_output=True,
                                    text=True, check=True, env=environment)
            return json.loads(result.stdout)
        with tempfile.TemporaryDirectory() as root:
            transport = ControlTransport(root)
            binding = transport.issue("EX-1", "GR-1")
            submit = "import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); print(json.dumps(ControlTransport.worker_submit(b, request_id='CT-1', kind='submit_intent', payload={'manifest':['result.json']})))"
            self.assertEqual(child(submit, binding)["state"], "submitted")
            published = []
            receipts = transport.pump(lambda request: (published.append(request) or {"state": "accepted", "published": True, "snapshot": "SN-1", "publication_id": "PR-1"}))
            self.assertEqual(receipts[0]["state"], "accepted")
            query = "import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); print(json.dumps(ControlTransport.wait_receipt(b, 'CT-1', 0)))"
            self.assertEqual(child(query, binding)["snapshot"], "SN-1")
            recovered = ControlTransport(root)
            self.assertEqual(recovered.pump(lambda _: self.fail("published request must not republish"))[0]["publication_id"], "PR-1")
            transport.request_self_check(binding, request={"self_check_id": "SC-1", "execution_id": "EX-1",
                                                           "payload": {"obligation": "report scope"}})
            poll = "import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); print(json.dumps(ControlTransport.worker_self_check(b, self_check_id='SC-1')))"
            self.assertEqual(child(poll, binding)["payload"]["obligation"], "report scope")
            answer = {"obligation_id": "SC-1", "execution_id": "EX-1", "rule_revision": 0,
                      "rule_results": [{"rule_id": "R-1", "status": "normal", "evidence_refs": ["EV-1"],
                                        "missing_evidence_refs": [], "reason": "checked"}],
                      "progress": "progress", "attempts": ["checked"], "next_method": "continue"}
            reply = ("import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); "
                     "print(json.dumps(ControlTransport.worker_self_check(b, self_check_id='SC-1', response=" + repr(answer) + ")))")
            self.assertEqual(child(reply, binding)["state"], "submitted")
            self.assertEqual(transport.pump(lambda _: {"state": "accepted", "published": True, "snapshot": "SN-2"})[-1]["kind"], "self_check_response")
            transport.close(binding, reason="execution ended")
            self.assertEqual(ControlTransport.worker_submit(binding, request_id="CT-2", kind="submit_intent", payload={"manifest": []})["state"], "closed")


if __name__ == "__main__":
    unittest.main()

"""RV_CONTEXT 03/04/08 regression cases, using real local repair effects."""
from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_redesign_OBSERVATION as h
from do_math import observations as obs, operational_dispositions as od
from do_math.execution_profiles import seal_profile, BOUNDARY


def profile(bindings):
    return seal_profile({"role": "research_work", "actor_kind": "ai", "budget_kind": "work", "boundary": BOUNDARY,
        "ai": {"model": "test"}, "observation": {"mode": "event_driven", "settings": {
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
            "observation_interval_seconds": 300}, "rule_bindings": bindings}})


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ws = Path(self.temp.name)
        self.clock = h.Clock()
    def tearDown(self): self.temp.cleanup()

    def tracker(self):
        return obs.ObservationTracker("EX-1", self.ws, {"observation_rules": [h.rule()],
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=self.clock)

    def submission(self, tracker):
        obligation = next(r for r in tracker.observe({"type": "tick", "counters": {"attempts": 2}}) if r["kind"] == "self_check_due")
        response = h.ObservationRedesignTests.response(obligation)
        request = {"request_id": "self-check-" + obligation["id"], "execution_id": "EX-1", "kind": "self_check_response",
                   "payload": {"self_check_id": obligation["id"], "response": response}}
        event = {"type": "item.started", "item": {"id": "CALL-SC", "type": "mcp_tool_call", "server": "execution_control",
                 "tool": "control_self_check", "arguments": {"self_check_id": obligation["id"], "response": response}}}
        return response, request, event

    def test_real_control_submission_is_not_research_action(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        rows = tracker.observe(event)
        self.assertFalse(any(r["kind"] == "self_check_missed" for r in rows))
        tracker.bind_control_request(request, receipt_id="CT-1")
        record = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"}, receipt_id="CT-1")
        self.assertEqual(record["kind"], "self_check_received")
        self.assertEqual(record["control_call_ids"], ["CALL-SC"])

    def test_receipt_before_adapter_event_and_claude_shape(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        tracker.bind_control_request(request, receipt_id="CT-1")
        item = event["item"]
        tracker.observe({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": item["id"],
            "name": "mcp__execution_control__control_self_check", "input": item["arguments"]}]}})
        self.assertEqual(tracker.record_self_check_response(response, available_evidence_refs={"EV-1"}, receipt_id="CT-1")["kind"], "self_check_received")

    def test_unbound_or_different_control_request_cannot_acknowledge_response(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        tracker.observe(event)
        rejected = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"})
        self.assertIn("control_request_unconfirmed", rejected["errors"])
        altered = deepcopy(request)
        altered["payload"]["response"]["next_method"] = "different"
        with self.assertRaises(ValueError): tracker.bind_control_request(altered, receipt_id="CT-2")

    def test_other_control_submit_and_wrong_server_remain_research_actions(self):
        for change in ("kind", "server"):
            tracker = self.tracker()
            _, _, event = self.submission(tracker)
            if change == "server": event["item"]["server"] = "untrusted"
            else:
                event["item"].update(tool="control_submit", arguments={"request_id": "P", "kind": "submission_preview", "payload": {}})
            self.assertTrue(any(r["kind"] == "self_check_missed" for r in tracker.observe(event)))

    def test_profile_binds_source_unit_and_current_execution(self):
        binding = {"operator": "checkpoint_count_gte", "subject_kind": "checkpoint", "source": "checkpoint", "unit": "count"}
        good = h.rule("checkpoint_count_gte", "checkpoint", "EX-1", 1, basis={"source": binding["source"], "unit": binding["unit"]})
        for bad in ({**good, "subject": {"kind": "checkpoint", "id": "EX-other"}},
                    {**good, "basis": {"source": "invented", "unit": "count"}}):
            with self.assertRaises(ValueError):
                config = obs.tracker_config(profile([binding]), initial_self_check_rules=[bad])
                obs.ObservationTracker("EX-1", self.ws, config, clock=self.clock)
        config = obs.tracker_config(profile([binding]), initial_self_check_rules=[good])
        tracker = obs.ObservationTracker("EX-1", self.ws, config, clock=self.clock)
        self.assertEqual(tracker.rules, [good])
        self.assertEqual(tracker._replace_rules({"current_revision": 0, "reason": "change", "rules": [h.rule()]})["kind"], "observation_rules_rejected")

    def test_missing_profile_observability_contract_is_not_support(self):
        with self.assertRaises(ValueError): obs.tracker_config(profile([]), initial_self_check_rules=[h.rule()])

    def test_profile_cannot_register_nonexistent_source_or_mix_counter_sources(self):
        import json
        rule = h.rule(basis={"source": "checkpoint", "unit": "count"})
        binding = {"operator": rule["operator"], "subject_kind": rule["subject"]["kind"], **rule["basis"]}
        forged = deepcopy(binding)
        forged["source"] = "invented"
        with self.assertRaises(ValueError):
            obs.tracker_config(profile([forged]), initial_self_check_rules=[{**rule, "basis": {"source": forged["source"], "unit": forged["unit"]}}])
        tracker = obs.ObservationTracker("EX-1", self.ws, obs.tracker_config(profile([binding]), initial_self_check_rules=[rule]), clock=self.clock)
        rows = tracker.observe({"type": "tick", "counters": {"attempts": 2}})
        self.assertFalse(any(r["kind"] == "self_check_due" for r in rows))
        (self.ws / "checkpoint.json").write_text(json.dumps({"current_claim": "c", "evidence_paths": [], "attempts": [],
            "remaining_work": [], "next_step": "n", "progress_state": "working", "counters": {"attempts": 2}}), encoding="utf-8")
        self.assertTrue(any(r["kind"] == "self_check_due" for r in tracker.observe({"type": "tick"})))

    def test_repair_performs_restoration_then_verifies_before_resume_and_publication(self):
        target = self.ws / "input.txt"
        target.write_bytes(b"broken")
        wanted = hashlib.sha256(b"restored").hexdigest()
        record = {"id": "OD-1", "target_execution_id": "EX-1", "status": "pending", "disposition": {
            "kind": "repair", "basis_refs": ["EX-1"], "next_owner": "maintenance", "reason": "restore missing input",
            "repair_target": str(target), "meaning_preserving": True, "verification": "SHA-256=" + wanted}}
        published, order = [], []
        def repair(plan):
            order.append("repair")
            target.write_bytes(b"restored")
            return {"execution_id": "FIX-1", "target": plan["repair_target"], "effect_refs": ["ART-restored"]}
        def verify(plan, effect):
            order.append("verify")
            return {"execution_id": "VERIFY-1", "passed": hashlib.sha256(target.read_bytes()).hexdigest() == wanted,
                    "effect_refs": effect["effect_refs"], "evidence_refs": ["ART-hash"], "meaning_preserved": True}
        def resume(plan, verification):
            order.append("resume")
            self.assertTrue(verification["passed"])
            return {"request_id": "AC-resume", "continuation_of": "EX-1"}
        result = od.execute_repair(record, target_execution={"id": "EX-1", "status": "ended"},
            current_basis_refs={"EX-1"}, repair=repair, verify=verify, resume=resume, publish=lambda r: published.append(deepcopy(r)))
        self.assertEqual(order, ["repair", "verify", "resume"])
        self.assertEqual(result["status"], "applied")
        self.assertEqual(result["repair_effect"]["execution_id"], "FIX-1")
        self.assertEqual(result["repair_verification"]["evidence_refs"], ["ART-hash"])
        self.assertEqual(published[-1], result)

    def test_failed_verification_and_stale_basis_never_resume(self):
        record = {"id": "OD-1", "target_execution_id": "EX-1", "status": "pending", "disposition": {
            "kind": "repair", "basis_refs": ["EX-1"], "next_owner": "maintenance", "reason": "fix",
            "repair_target": "input", "meaning_preserving": True, "verification": "hash"}}
        calls = []
        args = dict(target_execution={"id": "EX-1", "status": "ended"}, repair=lambda p: {"execution_id": "F", "target": "input", "effect_refs": ["A"]},
            verify=lambda p,e: {"execution_id": "V", "passed": False, "effect_refs": ["A"], "evidence_refs": ["V-log"], "meaning_preserved": True},
            resume=lambda *a: calls.append("resume"), publish=lambda r: None)
        with self.assertRaises(ValueError): od.execute_repair(record, current_basis_refs=set(), **args)
        result = od.execute_repair(record, current_basis_refs={"EX-1"}, **args)
        self.assertEqual(result["status"], "repair_verification_failed")
        self.assertEqual(calls, [])

    def test_interrupted_repair_requires_reconciliation_and_never_replays_blindly(self):
        record = {"id": "OD-1", "target_execution_id": "EX-1", "status": "pending", "disposition": {
            "kind": "repair", "basis_refs": ["EX-1"], "next_owner": "maintenance", "reason": "fix",
            "repair_target": "input", "meaning_preserving": True, "verification": "hash"}}
        published, effects = [], []
        def repair(plan):
            effects.append(plan["effect_key"])
            raise OSError("lost after partial effect")
        args = dict(target_execution={"id": "EX-1", "status": "ended"}, current_basis_refs={"EX-1"},
            repair=repair, verify=lambda *a: self.fail("verification must wait"), resume=lambda *a: self.fail("no resume"),
            publish=lambda r: published.append(deepcopy(r)))
        with self.assertRaises(OSError): od.execute_repair(record, **args)
        self.assertEqual(published[-1]["status"], "repair_running")
        with self.assertRaisesRegex(ValueError, "reconciliation"): od.execute_repair(published[-1], **args)
        self.assertEqual(effects, ["OD-1:repair"])

    def test_receipt_cannot_be_reused_for_a_different_response_body(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        tracker.observe(event)
        tracker.bind_control_request(request, receipt_id="CT-1")
        changed = {**response, "next_method": "not the submitted method"}
        self.assertIn("control_response_mismatch", tracker.record_self_check_response(changed,
                      available_evidence_refs={"EV-1"}, receipt_id="CT-1")["errors"])


if __name__ == "__main__":
    import json
    evidence = None
    if "--evidence" in sys.argv:
        index = sys.argv.index("--evidence")
        evidence = Path(sys.argv[index + 1])
        del sys.argv[index:index + 2]
    program = unittest.main(verbosity=2, exit=False)
    if evidence:
        source = Path(obs.__file__)
        evidence.write_text(json.dumps({"tests": program.result.testsRun, "passed": program.result.wasSuccessful(),
            "failures": [(str(test), detail) for test, detail in program.result.failures],
            "errors": [(str(test), detail) for test, detail in program.result.errors],
            "source_sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in
                (source, Path(od.__file__), Path(__file__))},
            "scope": "Actual local file restoration/hash verification; provider events and central publication are test fixtures."},
            ensure_ascii=False, indent=2), encoding="utf-8")
    sys.exit(0 if program.result.wasSuccessful() else 1)

"""Writing workflow contracts. Run this file directly; no model calls in this suite."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("writing_flow.py")
ROOT = SCRIPT.parents[4]


class IntegrationContract(unittest.TestCase):
    def test_codex_registers_the_writing_stop_command(self):
        path = ROOT / ".codex/hooks.json"
        self.assertTrue(path.is_file(), "Codex has no project writing Stop hook")
        groups = json.loads(path.read_text(encoding="utf-8"))["hooks"]["Stop"]
        self.assertTrue(any("writing_flow.py" in hook.get("command", "")
                            for group in groups for hook in group["hooks"]))

    def test_skill_requires_reader_result_before_completion(self):
        text = SCRIPT.parents[1].joinpath("SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/독해_검토.md", text)
        self.assertIn("writing_flow.py", text)


class WritingFlowContract(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "Independent reading and version-bound completion are not implemented")
        spec = importlib.util.spec_from_file_location("writing_flow_contract", SCRIPT)
        self.wf = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.wf
        spec.loader.exec_module(self.wf)
        self.temp = tempfile.TemporaryDirectory(prefix="writing-flow-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.draft = self.root / "원고.md"
        self.brief = self.root / "합의.md"
        self.audience = self.root / "독자.md"
        self.draft.write_text("연구 문서를 기존 학술 개념과 비교한다.\n근거를 함께 제공한다.\n", encoding="utf-8")
        self.brief.write_text("PRIVATE_BRIEF_CANARY: 연구자의 개념 비교를 지원한다.", encoding="utf-8")
        self.audience.write_text("프로젝트의 사전 설명을 듣지 않은 독자", encoding="utf-8")
        self.flow = self.wf.WritingFlow(self.root, "test-session")
        self.reader = {
            "status": "complete",
            "understanding": [{"statement": "학술 개념과 연구 문서를 비교하고 근거를 제시한다.",
                               "evidence": [{"line": 1, "quote": "연구 문서를 기존 학술 개념과 비교한다."}]}],
            "difficulties": [], "uncertainties": []}
        self.last_command = None
        self.last_prompt = None

    def begin(self):
        return self.flow.begin(self.draft, self.brief, self.audience)

    def fake_codex(self, command, **kwargs):
        self.last_command = command
        self.last_prompt = kwargs["input"].decode("utf-8")
        output = Path(command[command.index("-o") + 1])
        output.write_text(json.dumps(self.reader, ensure_ascii=False), encoding="utf-8")
        events = [{"type": "thread.started", "thread_id": getattr(self, "reader_session", "different-reader-session")},
                  {"type": "turn.started"},
                  {"type": "item.completed", "item": {"type": "agent_message"}},
                  {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 10}}]
        kwargs["stdout"].write(("\n".join(json.dumps(x) for x in events) + "\n").encode())
        return subprocess.CompletedProcess(command, 0)

    def read(self, scope="whole"):
        with patch.object(self.wf.subprocess, "run", side_effect=self.fake_codex):
            return self.flow.read(scope=scope, codex=sys.executable)

    def decide(self, verdict="accept", findings=None):
        path = self.root / "대조.json"
        path.write_text(json.dumps({"verdict": verdict,
            "alignment": "원고의 비교 대상과 근거 제공은 합의와 일치한다.",
            "findings": findings or []}, ensure_ascii=False), encoding="utf-8")
        return self.flow.decide(path)

    def stop(self, repeated=False):
        return self.flow.on_stop({"session_id": "test-session", "stop_hook_active": repeated})

    def test_unregistered_session_is_unaffected(self):
        self.assertEqual(self.stop(), {})

    def test_can_register_before_draft_exists(self):
        self.draft.unlink()
        self.begin()
        self.assertEqual(self.stop().get("decision"), "block")

    def test_unreviewed_draft_continues_once_without_infinite_loop(self):
        self.begin()
        self.assertEqual(self.stop().get("decision"), "block")
        repeated = self.stop(True)
        self.assertFalse(repeated["continue"])
        self.assertIn("미완료", repeated["systemMessage"])

    def test_reader_gets_draft_and_audience_but_not_private_brief(self):
        self.begin(); self.read()
        self.assertIn("연구 문서를", self.last_prompt)
        self.assertIn("사전 설명", self.last_prompt)
        self.assertNotIn("PRIVATE_BRIEF_CANARY", self.last_prompt)
        command = self.last_command
        self.assertNotIn("resume", command)
        self.assertNotIn("fork", command)
        self.assertIn("--ignore-user-config", command)
        self.assertEqual(command[command.index("-s") + 1], "read-only")
        self.assertFalse(Path(command[command.index("-C") + 1]).is_relative_to(self.root))

    def test_reading_alone_does_not_approve_the_document(self):
        self.begin(); self.read()
        self.assertEqual(self.stop().get("decision"), "block")

    def test_current_whole_reading_and_reasoned_decision_allow_completion(self):
        self.begin(); self.read(); self.decide()
        self.assertEqual(self.stop(), {})
        self.assertEqual(self.flow.status()["status"], "completed")

    def test_sample_approval_cannot_approve_whole_document(self):
        self.begin(); self.read(scope="sample"); self.decide()
        self.assertEqual(self.stop().get("decision"), "block")

    def test_draft_change_invalidates_previous_approval(self):
        self.begin(); self.read(); self.decide()
        self.draft.write_text("변경된 설명", encoding="utf-8")
        self.assertEqual(self.stop().get("decision"), "block")

    def test_brief_change_invalidates_previous_approval(self):
        self.begin(); self.read(); self.decide()
        self.brief.write_text("다른 합의", encoding="utf-8")
        self.assertEqual(self.stop().get("decision"), "block")

    def test_audience_change_invalidates_previous_approval(self):
        self.begin(); self.read(); self.decide()
        self.audience.write_text("다른 독자", encoding="utf-8")
        self.assertEqual(self.stop().get("decision"), "block")

    def test_changed_report_cannot_be_accepted(self):
        self.begin(); receipt = self.read()
        Path(receipt["report_path"]).write_text("{}", encoding="utf-8")
        with self.assertRaises(self.wf.WorkflowError): self.decide()

    def test_uncited_or_fabricated_reader_quotes_do_not_pass(self):
        self.begin()
        self.reader["understanding"][0]["evidence"][0]["quote"] = "원고에 없는 문장"
        with self.assertRaises(self.wf.WorkflowError): self.read()
        self.assertEqual(self.flow.status()["status"], "blocked")

    def test_incomplete_reading_is_not_a_success(self):
        self.begin(); self.reader["status"] = "incomplete"
        with self.assertRaises(self.wf.WorkflowError): self.read()
        self.assertEqual(self.flow.status()["status"], "blocked")

    def test_every_reader_difficulty_requires_disposition(self):
        self.begin()
        self.reader["difficulties"] = [{"line": 2, "quote": "근거를 함께 제공한다.",
                                        "reason": "무엇의 근거인지 독자가 보충해야 한다."}]
        self.read()
        with self.assertRaises(self.wf.WorkflowError): self.decide()
        self.decide(findings=[{"index": 1, "action": "keep", "reason": "바로 앞 문장의 비교 판단을 받는 관계가 명확하다."}])
        self.assertEqual(self.stop(), {})

    def test_open_revision_cannot_be_marked_accepted(self):
        self.begin()
        self.reader["difficulties"] = [{"line": 2, "quote": "근거를 함께 제공한다.", "reason": "설명 부족"}]
        self.read()
        with self.assertRaises(self.wf.WorkflowError):
            self.decide(findings=[{"index": 1, "action": "revise", "reason": "설명을 보완해야 한다."}])

    def test_provider_failure_is_incomplete_and_does_not_force_retries(self):
        self.begin()
        with patch.object(self.wf.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)):
            with self.assertRaises(self.wf.WorkflowError): self.flow.read(codex=sys.executable)
        self.assertEqual(self.flow.status()["status"], "blocked")
        self.assertNotEqual(self.stop().get("decision"), "block")

    def test_failed_new_read_cannot_fall_back_to_an_old_read_silently(self):
        self.begin(); self.read()
        with patch.object(self.wf.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)):
            with self.assertRaises(self.wf.WorkflowError): self.flow.read(codex=sys.executable)
        self.flow.resume()
        with self.assertRaises(self.wf.WorkflowError): self.decide()

    def test_repeating_sample_reads_does_not_reset_stop_loop_detection(self):
        self.begin(); self.read(scope="sample"); self.decide()
        self.assertEqual(self.stop().get("decision"), "block")
        self.read(scope="sample"); self.decide()
        self.assertFalse(self.stop(True).get("continue", True))

    def test_paused_and_cancelled_jobs_do_not_hold_user_hostage(self):
        self.begin(); self.flow.suspend("paused", "사용자 답변 대기")
        self.assertNotEqual(self.stop().get("decision"), "block")
        self.flow.resume()
        self.assertEqual(self.stop().get("decision"), "block")
        self.flow.suspend("cancelled", "사용자가 중단함")
        self.assertEqual(self.stop(), {})

    def test_other_session_cannot_finish_this_job(self):
        self.begin()
        other = self.wf.WritingFlow(self.root, "other-session")
        self.assertEqual(other.on_stop({"session_id": "other-session"}), {})
        self.assertEqual(self.stop().get("decision"), "block")

    def test_cancel_during_reader_execution_stays_cancelled(self):
        self.begin()
        def cancel_then_complete(command, **kwargs):
            self.flow.suspend("cancelled", "사용자 중단")
            return self.fake_codex(command, **kwargs)
        with patch.object(self.wf.subprocess, "run", side_effect=cancel_then_complete):
            with self.assertRaises(self.wf.WorkflowError): self.flow.read(codex=sys.executable)
        self.assertEqual(self.flow.status()["status"], "cancelled")

    def test_session_path_traversal_is_rejected(self):
        with self.assertRaises(self.wf.WorkflowError): self.wf.WritingFlow(self.root, "../outside")

    def test_shell_uses_root_session_identity_for_parent_stop_hook(self):
        env = dict(os.environ, CODEX_SESSION_ID="root-session", CODEX_THREAD_ID="child-thread")
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), "status"],
                                env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["session_id"], "root-session")

    def test_nonfinite_timeout_is_rejected_before_starting_reader(self):
        self.begin()
        for timeout in (float("inf"), float("nan")):
            with patch.object(self.wf.subprocess, "run", side_effect=self.fake_codex) as run:
                with self.assertRaises(self.wf.WorkflowError):
                    self.flow.read(timeout=timeout, codex=sys.executable)
                run.assert_not_called()
        self.assertIsNone(self.flow.status()["pending_read"])

    def test_unexpected_reader_exception_releases_pending_read(self):
        self.begin()
        with patch.object(self.wf.subprocess, "run", side_effect=OverflowError("timeout overflow")):
            with self.assertRaises(self.wf.WorkflowError): self.flow.read(codex=sys.executable)
        self.assertEqual(self.flow.status()["status"], "blocked")
        self.assertIsNone(self.flow.status()["pending_read"])

    def test_malformed_event_is_incomplete_instead_of_leaving_reader_running(self):
        self.begin()
        def malformed(command, **kwargs):
            kwargs["stdout"].write(b"null\n")
            return subprocess.CompletedProcess(command, 0)
        with patch.object(self.wf.subprocess, "run", side_effect=malformed):
            with self.assertRaises(self.wf.WorkflowError): self.flow.read(codex=sys.executable)
        self.assertEqual(self.flow.status()["status"], "blocked")
        self.assertIsNone(self.flow.status()["pending_read"])

    def test_invalid_reader_session_identity_cannot_support_approval(self):
        self.begin(); self.reader_session = 123
        with self.assertRaises(self.wf.WorkflowError): self.read()


if __name__ == "__main__":
    unittest.main(verbosity=2)

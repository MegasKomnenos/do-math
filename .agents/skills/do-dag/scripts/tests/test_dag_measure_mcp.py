"""dag_measure_mcp 서버의 시험. 직접 실행이 정본이다: python .agents/skills/do-dag/scripts/tests/test_dag_measure_mcp.py"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import dag_measure_mcp as mcp  # noqa: E402


class TestHandle(unittest.TestCase):
    def test_initialize_and_list(self):
        r = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertEqual(r["result"]["serverInfo"]["name"], "dag-measure")
        r = mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {t["name"] for t in r["result"]["tools"]}
        self.assertEqual(names, {"count", "anchor", "table", "same", "attrib", "changes", "budget"})

    def test_changes_스키마가_worktree와_base를_받는다(self):
        r = mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        changes = next(t for t in r["result"]["tools"] if t["name"] == "changes")
        self.assertEqual(changes["inputSchema"]["required"], ["worktree"])
        argv = mcp._argv("changes", {"worktree": "C:/repo", "base": "HEAD"})
        self.assertEqual(argv, ["changes", "--worktree", "C:/repo", "--base", "HEAD"])

    def test_budget_스키마와_호출이_저작량과_미존재_산출을_받는다(self):
        r = mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        budget = next(t for t in r["result"]["tools"] if t["name"] == "budget")
        properties = budget["inputSchema"]["properties"]
        self.assertIn("writes", properties)
        self.assertIn("pending", properties)

        argv = mcp._argv("budget", {
            "files": "a.md",
            "model": "opus",
            "writes": 1200,
            "pending": 3400,
        })
        self.assertIn("--writes", argv)
        self.assertIn("1200", argv)
        self.assertIn("--pending", argv)
        self.assertIn("3400", argv)

    def test_notification_is_silent(self):
        self.assertIsNone(mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_unknown_method_errors(self):
        r = mcp.handle({"jsonrpc": "2.0", "id": 3, "method": "resources/list"})
        self.assertIn("error", r)

    def test_call_count_emits_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.md").write_text("패턴 있음\n", encoding="utf-8")
            r = mcp.handle({
                "jsonrpc": "2.0", "id": 4, "method": "tools/call",
                "params": {"name": "count",
                           "arguments": {"pattern": "패턴", "files": "a.md", "root": tmp}},
            })
            text = r["result"]["content"][0]["text"]
            self.assertFalse(r["result"]["isError"])
            self.assertIn("[실측기 count]", text)
            self.assertIn("합계: 1", text)

    def test_unknown_tool_is_error(self):
        r = mcp.handle({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                        "params": {"name": "없는도구", "arguments": {}}})
        self.assertTrue(r["result"]["isError"])

    def test_measure_failure_is_error(self):
        r = mcp.handle({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "count",
                "arguments": {"pattern": "x", "files": "없는경로*.md"},
            },
        })
        self.assertTrue(r["result"]["isError"])
        self.assertIn("대상 0파일", r["result"]["content"][0]["text"])


class TestStdioRoundTrip(unittest.TestCase):
    def test_full_cycle_over_stdio(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.md").write_text("x\n", encoding="utf-8")
            messages = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                 "params": {"name": "budget",
                            "arguments": {"files": "a.md", "model": "opus", "root": tmp}}},
            ]
            payload = "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in messages)
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "dag_measure_mcp.py")],
                input=payload.encode("utf-8"), capture_output=True, timeout=30,
            )
            lines = [json.loads(ln) for ln in proc.stdout.decode("utf-8").splitlines() if ln.strip()]
            self.assertEqual(len(lines), 2)  # 알림에는 답이 없다
            self.assertEqual(lines[0]["id"], 1)
            self.assertIn("예산 안", lines[1]["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main(verbosity=1)

"""agent_usage 오케 적재량 판독기 시험. 직접 실행이 정본이다: python .agents/skills/do-dag/scripts/tests/test_agent_usage.py

계약(do-dag 「메인의 임무 넷」 4항): 메인이 열쇠 하나로
`<세션>/subagents/agent-<id>.meta.json`을 역탐색해 짝 `.jsonl`을 특정하고,
마지막 assistant 행 `message.usage`의 (input + cache_creation + cache_read)를
합산한다. 판정(임계 도달 여부)은 코드가 아니라 메인의 몫이다 — 이 스크립트는
읽기만 한다.

열쇠는 둘이고 정확히 하나를 준다. `description`은 메인이 Agent 호출에 직접 써 넣는
값이라 메인이 아는 유일한 열쇠이고, `toolUseId`는 하네스 내부 값이다. 여럿이 걸리면
고르지 않고 오류다 — 잘못 고르면 교대 판정이 남의 적재를 읽는다.

검색 범위도 계약이다. description의 유일성은 국면 안에서만 요구되므로
`--phase`(마커의 `opened_at`)·`--since`가 범위를 국면으로 좁힌다.

fixture의 meta는 판독이 쓰는 두 키(`description`·`toolUseId`)를 실측 형태로 낸다.
그 밖의 키는 하네스가 정하고 에이전트 유형마다 갈리므로 계수를 박지 않는다.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import agent_usage  # noqa: E402


def _make_agent(session_dir: Path, agent_id: str, tool_use_id: str, usages, description="오케 A"):
    sub = session_dir / "subagents"
    sub.mkdir(parents=True, exist_ok=True)
    (sub / f"agent-{agent_id}.meta.json").write_text(
        json.dumps({
            "agentType": "general-purpose",
            "description": description,
            "toolUseId": tool_use_id,
            "spawnDepth": 1,
        }),
        encoding="utf-8",
    )
    lines = []
    lines.append(json.dumps({"type": "user", "message": {"content": "x"}}))
    for u in usages:
        lines.append(json.dumps({"type": "assistant", "message": {"usage": u}}))
    (sub / f"agent-{agent_id}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


class FindTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_finds_agent_across_sessions(self):
        _make_agent(self.root / "session-a", "aaa", "toolu_001", [{"input_tokens": 1}])
        _make_agent(self.root / "session-b", "bbb", "toolu_002", [{"input_tokens": 2}])
        found = agent_usage.find_agent_transcript(self.root, "toolu_002")
        self.assertIsNotNone(found)
        self.assertTrue(found.name.endswith("agent-bbb.jsonl"))

    def test_missing_id_returns_none(self):
        _make_agent(self.root / "session-a", "aaa", "toolu_001", [{"input_tokens": 1}])
        self.assertIsNone(agent_usage.find_agent_transcript(self.root, "toolu_999"))

    def test_finds_agent_by_description(self):
        """메인이 아는 열쇠는 이것뿐이다 — tool_use id는 하네스 내부 값이다."""
        _make_agent(self.root / "s", "aaa", "toolu_001", [{"input_tokens": 1}],
                    description="do-dag 오케 국면A")
        _make_agent(self.root / "s", "bbb", "toolu_002", [{"input_tokens": 2}],
                    description="do-dag 오케 국면B")
        found = agent_usage.find_agent_transcript(self.root, description="do-dag 오케 국면B")
        self.assertIsNotNone(found)
        self.assertTrue(found.name.endswith("agent-bbb.jsonl"))

    def test_missing_description_returns_none(self):
        _make_agent(self.root / "s", "aaa", "toolu_001", [{"input_tokens": 1}],
                    description="do-dag 오케 국면A")
        self.assertIsNone(agent_usage.find_agent_transcript(self.root, description="없는 국면"))

    def test_two_agents_on_one_key_is_an_error(self):
        """조용히 하나를 고르면 교대 판정이 남의 적재를 읽는다."""
        _make_agent(self.root / "s", "aaa", "toolu_001", [{"input_tokens": 1}],
                    description="do-dag 오케 국면A")
        _make_agent(self.root / "s", "bbb", "toolu_002", [{"input_tokens": 2}],
                    description="do-dag 오케 국면A")
        with self.assertRaises(agent_usage.AmbiguousKeyError) as caught:
            agent_usage.find_agent_transcript(self.root, description="do-dag 오케 국면A")
        message = str(caught.exception)
        self.assertIn("agent-aaa.jsonl", message)
        self.assertIn("agent-bbb.jsonl", message)


class ScopeTest(unittest.TestCase):
    """검색 범위는 계약의 범위와 같아야 한다 — 좁히지 않으면 지난 런의 동명 오케가 함께 걸린다."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.opened_at = datetime(2026, 7, 28, 12, 0, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self._tmp.cleanup()

    def _aged(self, agent_id, minutes, description="do-dag 오케 국면A"):
        """개설 시각 기준 상대 시각의 에이전트 하나."""
        _make_agent(self.root / "s", agent_id, f"toolu_{agent_id}", [{"input_tokens": 1}],
                    description=description)
        stamp = (self.opened_at + timedelta(minutes=minutes)).timestamp()
        for suffix in (".meta.json", ".jsonl"):
            os.utime(self.root / "s" / "subagents" / f"agent-{agent_id}{suffix}", (stamp, stamp))

    def test_the_first_orchestrator_is_inside_the_bound(self):
        """1기 오케는 `open` 뒤에 파견되므로 하한이 자르지 않는다.

        열기와 파견이 같은 초에 들어도 안이다 — `stale`은 `<` 비교다.
        """
        self._aged("first", 0)    # 열자마자 쏜 1기 오케
        found = agent_usage.find_agent_transcript(
            self.root, description="do-dag 오케 국면A", since=self.opened_at.timestamp(),
        )
        self.assertIsNotNone(found, "1기 오케가 하한 밖으로 잘렸다")
        self.assertTrue(found.name.endswith("agent-first.jsonl"))

    def test_a_past_run_with_the_same_phase_name_no_longer_collides(self):
        self._aged("old", -600)   # 지난 런의 오케
        self._aged("now", 5)      # 이번 국면의 오케(교대 뒤 2기)
        with self.assertRaises(agent_usage.AmbiguousKeyError):
            agent_usage.find_agent_transcript(self.root, description="do-dag 오케 국면A")
        found = agent_usage.find_agent_transcript(
            self.root, description="do-dag 오케 국면A",
            since=self.opened_at.timestamp(),
        )
        self.assertIsNotNone(found)
        self.assertTrue(found.name.endswith("agent-now.jsonl"))

    def test_two_agents_inside_the_scope_are_still_an_error(self):
        """좁혀도 남는 중복은 차수를 빠뜨린 것이다 — 고르지 않는다."""
        self._aged("one", 5)
        self._aged("two", 6)
        with self.assertRaises(agent_usage.AmbiguousKeyError) as caught:
            agent_usage.find_agent_transcript(
                self.root, description="do-dag 오케 국면A",
                since=self.opened_at.timestamp(),
            )
        self.assertIn("차수", str(caught.exception))

    def test_parse_since_takes_the_marker_format(self):
        """마커의 `opened_at`은 `...Z` 표기다."""
        self.assertEqual(
            agent_usage.parse_since("2026-07-28T12:00:00Z"), self.opened_at.timestamp()
        )

    def test_phase_opened_at_reads_the_marker(self):
        project = self.root / "repo"
        (project / ".sdd" / "dag").mkdir(parents=True)
        (project / ".sdd" / "dag" / "marker.json").write_text(
            json.dumps({"active_phases": {"국면A": {"opened_at": "2026-07-28T12:00:00Z"}}}),
            encoding="utf-8",
        )
        self.assertEqual(
            agent_usage.phase_opened_at("국면A", str(project)), self.opened_at.timestamp()
        )
        with self.assertRaises(KeyError):
            agent_usage.phase_opened_at("닫힌국면", str(project))

    def test_cli_phase_narrows_the_search(self):
        import contextlib
        import io

        project = self.root / "repo"
        (project / ".sdd" / "dag").mkdir(parents=True)
        (project / ".sdd" / "dag" / "marker.json").write_text(
            json.dumps({"active_phases": {"국면A": {"opened_at": "2026-07-28T12:00:00Z"}}}),
            encoding="utf-8",
        )
        self._aged("old", -600)
        self._aged("now", 5)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = agent_usage.main([
                "--description", "do-dag 오케 국면A",
                "--phase", "국면A",
                "--project-dir", str(project),
                "--transcripts-root", str(self.root),
                "--json",
            ])
        self.assertEqual(rc, 0)
        self.assertIn("agent-now.jsonl", json.loads(buf.getvalue())["transcript"])

    def test_cli_reports_a_phase_it_cannot_scope(self):
        """닫힌 국면은 마커에 없다 — 조용히 범위를 넓히지 않는다."""
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = agent_usage.main([
                "--description", "x", "--phase", "닫힌국면",
                "--project-dir", str(self.root / "없는저장소"),
                "--transcripts-root", str(self.root),
            ])
        self.assertEqual(rc, 1)
        self.assertIn("--since", buf.getvalue())


class DispatchOrderContractTest(unittest.TestCase):
    """`--phase` 하한은 파견 순서에 기댄다 — `open`이 오케 파견보다 뒤면 1기 오케가 잘린다.

    코드로 막을 수 없는 순서라 문면을 시험한다.
    """

    SKILL = Path(__file__).resolve().parents[2] / "SKILL.md"

    def test_the_marker_opens_before_the_orchestrator_is_dispatched(self):
        text = self.SKILL.read_text(encoding="utf-8")
        section = text[text.index("### 1. 오케 파견"):text.index("### 2. ")]
        self.assertLess(
            section.index("dag_marker.py open --phase"),
            section.index("오케를 파견한다"),
            section,
        )

    def test_the_heartbeat_still_requires_the_phase_flag(self):
        """하한을 떠받쳤다고 범위를 도로 넓히지 않는다."""
        text = self.SKILL.read_text(encoding="utf-8")
        self.assertIn("--phase {국면명}", text)
        self.assertIn("`--phase`를 빠뜨리지 않는다", text)


class UsageTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_last_assistant_usage_wins_and_sums(self):
        _make_agent(
            self.root / "s", "aaa", "toolu_001",
            [
                {"input_tokens": 5, "cache_creation_input_tokens": 5, "cache_read_input_tokens": 5},
                {"input_tokens": 2, "cache_creation_input_tokens": 286, "cache_read_input_tokens": 198025},
            ],
        )
        path = agent_usage.find_agent_transcript(self.root, "toolu_001")
        result = agent_usage.read_usage(path)
        self.assertEqual(result["context_tokens"], 2 + 286 + 198025)
        self.assertEqual(result["usage"]["cache_read_input_tokens"], 198025)

    def test_missing_usage_fields_default_to_zero(self):
        _make_agent(self.root / "s", "aaa", "toolu_001", [{"input_tokens": 7}])
        path = agent_usage.find_agent_transcript(self.root, "toolu_001")
        self.assertEqual(agent_usage.read_usage(path)["context_tokens"], 7)

    def test_no_assistant_rows_is_error(self):
        sub = self.root / "s" / "subagents"
        sub.mkdir(parents=True)
        (sub / "agent-x.meta.json").write_text(json.dumps({"toolUseId": "toolu_001"}), encoding="utf-8")
        (sub / "agent-x.jsonl").write_text(json.dumps({"type": "user"}) + "\n", encoding="utf-8")
        path = agent_usage.find_agent_transcript(self.root, "toolu_001")
        with self.assertRaises(agent_usage.NoUsageError):
            agent_usage.read_usage(path)


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_json_output(self):
        import contextlib
        import io

        _make_agent(
            self.root / "s", "aaa", "toolu_001",
            [{"input_tokens": 2, "cache_creation_input_tokens": 3, "cache_read_input_tokens": 5}],
        )
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = agent_usage.main(
                ["--tool-use-id", "toolu_001", "--transcripts-root", str(self.root), "--json"]
            )
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["context_tokens"], 10)

    def test_not_found_exits_one(self):
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = agent_usage.main(["--tool-use-id", "toolu_404", "--transcripts-root", str(self.root)])
        self.assertEqual(rc, 1)

    def test_description_output(self):
        import contextlib
        import io

        _make_agent(
            self.root / "s", "aaa", "toolu_001", [{"input_tokens": 11}],
            description="do-dag 오케 국면A",
        )
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = agent_usage.main(
                ["--description", "do-dag 오케 국면A",
                 "--transcripts-root", str(self.root), "--json"]
            )
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["context_tokens"], 11)
        self.assertEqual(data["key"], "description")

    def test_ambiguous_key_exits_one_and_lists_the_hits(self):
        import contextlib
        import io

        for agent_id, tool_use_id in [("aaa", "toolu_001"), ("bbb", "toolu_002")]:
            _make_agent(self.root / "s", agent_id, tool_use_id, [{"input_tokens": 1}],
                        description="do-dag 오케 국면A")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = agent_usage.main(
                ["--description", "do-dag 오케 국면A", "--transcripts-root", str(self.root)]
            )
        self.assertEqual(rc, 1)
        self.assertIn("agent-bbb.jsonl", buf.getvalue())

    def test_exactly_one_key_is_required(self):
        """둘을 함께 주거나 하나도 주지 않으면 인자 계약 위반이다."""
        import contextlib
        import io

        for argv in (
            ["--transcripts-root", str(self.root)],
            ["--description", "x", "--tool-use-id", "toolu_001",
             "--transcripts-root", str(self.root)],
        ):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    agent_usage.main(argv)

    def test_munge_matches_windows_convention(self):
        """Windows 절대 경로를 프로젝트 키 형식으로 바꾼다."""
        self.assertEqual(
            agent_usage.munge_project_dir(r"C:\Users\example\Workspace\sample-project"),
            "C--Users-example-Workspace-sample-project",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

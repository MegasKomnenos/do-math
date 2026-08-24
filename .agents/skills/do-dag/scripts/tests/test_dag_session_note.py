"""세션 주입 훅의 시험. 직접 실행이 정본이다: python .agents/skills/do-dag/scripts/tests/test_dag_session_note.py

훅은 진단 채널이다. 계약 셋이 이 파일의 전부다.

- **어떤 경우에도 exit 0**이다. 주입을 배제하더라도 그 사실을 고지한다 — 진단 채널이
  침묵으로 죽으면 수신자가 알아챌 방법이 없다.
- **주입하는 것은 좌표뿐**이다. 상태·계수를 렌더하지 않는다. 그 정본은 파견표이고,
  요약을 주입하면 요약과 실물이 갈리는 이중 정본이 생긴다.
- **무국면·무잔재면 무출력**이다. 상시 1줄은 DAG를 드물게 도는 저장소에 영구 소음이다.

훅을 실제 프로세스로 돌려 잰다. 모듈을 import해 함수를 부르면 `sys.path` 주입과
인코딩 재설정 같은 이 파일의 실질이 시험 밖에 남는다.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
HOOK = SCRIPTS / "hooks" / "dag_session_note.py"
sys.path.insert(0, str(SCRIPTS))

import dag_marker  # noqa: E402


def _phases(*names):
    return {n: {"opened_at": "2026-07-28T00:00:00Z"} for n in names}


class HookTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        self.wt_root = Path(self._tmp.name) / "wt"
        self.root.mkdir()
        self.wt_root.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self):
        env = dict(
            os.environ,
            CLAUDE_PROJECT_DIR=str(self.root),
            DAG_WT_ROOT=str(self.wt_root),
            PYTHONIOENCODING="utf-8",
        )
        return subprocess.run(
            [sys.executable, str(HOOK)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=env,
        )

    def _marker(self, data):
        path = self.root / ".sdd" / "dag" / "marker.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            data if isinstance(data, str) else json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )


class SilenceTest(HookTest):
    def test_no_phase_is_silent_and_zero(self):
        r = self._run()
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_a_corrupt_marker_exits_zero_but_says_so(self):
        for marker in (
            "깨짐",
            {"active_phases": {"demo": "2026-01-01T00:00:00Z"}},
        ):
            with self.subTest(marker=marker):
                self._marker(marker)
                r = self._run()
                self.assertEqual(r.returncode, 0, "진단 채널은 침묵으로 죽지 않는다")
                self.assertIn("못했다", r.stdout)


class InjectionTest(HookTest):
    def test_an_active_phase_injects_coordinates(self):
        self._marker({"active_phases": _phases("demo")})
        r = self._run()
        self.assertEqual(r.returncode, 0)
        self.assertIn("demo", r.stdout)
        self.assertIn("파견표.md", r.stdout)

    def test_every_active_phase_is_injected(self):
        self._marker({"active_phases": _phases("a", "b")})
        r = self._run()
        self.assertIn("'a'", r.stdout)
        self.assertIn("'b'", r.stdout)

    def test_no_grant_is_reported_as_a_blocked_gate(self):
        self._marker({"active_phases": _phases("demo")})
        self.assertIn("차단", self._run().stdout)

    def test_a_fresh_grant_is_reported_with_its_deadline(self):
        self._marker({
            "active_phases": _phases("demo"),
            "commit_grants": {"grant-1": {"until": "2099-01-01T00:00:00Z", "reason": "병합"}},
        })
        out = self._run().stdout
        self.assertIn("grant-1", out)
        self.assertIn("2099-01-01T00:00:00Z", out)


class LeaseNoticeTest(HookTest):
    """점유 중인 lease만 고지한다. 비어 있는 것은 정상이라 알릴 것이 없다."""

    def test_a_held_lease_is_reported(self):
        self._marker({
            "active_phases": _phases("demo"),
            "merge_lease": {"owner": "2.5.z", "until": "2099-01-01T00:00:00Z"},
        })
        out = self._run().stdout
        self.assertIn("2.5.z", out)
        self.assertIn("인덱스를 건드리지 않는다", out)

    def test_an_empty_lease_is_not_mentioned(self):
        self._marker({"active_phases": _phases("demo")})
        self.assertNotIn("lease", self._run().stdout)

    def test_an_expired_lease_is_not_mentioned(self):
        self._marker({
            "active_phases": _phases("demo"),
            "merge_lease": {"owner": "2.5.z", "until": "2000-01-01T00:00:00Z"},
        })
        self.assertNotIn("2.5.z", self._run().stdout)


class LeftoverNoticeTest(HookTest):
    """활성 국면의 트리는 잔재가 아니다 — 상시 참인 경고는 읽히지 않는다."""

    def setUp(self):
        super().setUp()
        (self.wt_root / "죽은국면+1").mkdir()

    def test_a_stranded_tree_is_reported_even_without_a_phase(self):
        out = self._run().stdout
        self.assertIn("죽은국면+1", out)
        self.assertIn("sweep", out)

    def test_the_active_phases_own_tree_is_not_a_leftover(self):
        (self.wt_root / "도는국면+2.5").mkdir()
        self._marker({"active_phases": _phases("도는국면")})
        out = self._run().stdout
        self.assertNotIn("도는국면+2.5", out)
        self.assertIn("죽은국면+1", out, "다른 국면의 잔재까지 사라지면 채널이 죽은 것이다")


class NoLedgerRenderTest(HookTest):
    """상태·계수를 렌더하지 않는다. 파견표가 그 정본이다."""

    def test_the_dispatch_table_is_pointed_at_not_summarized(self):
        table = self.root / ".sdd" / "dag" / "demo" / "파견표.md"
        table.parent.mkdir(parents=True, exist_ok=True)
        table.write_text(
            "| 행 | 유형 | 파견문 | 선행 | 완료 신호 | 모델 | 상태 |\n"
            "|---|---|---|---|---|---|---|\n"
            "| 1 | 파견 | 행/1.md | — | 기준선.md | opus high | 완 |\n"
            "\n<!-- 행 끝 -->\n",
            encoding="utf-8",
        )
        self._marker({"active_phases": _phases("demo")})
        out = self._run().stdout
        self.assertIn(str(table), out)
        for token in ("완", "미착수", "행/1.md"):
            self.assertNotIn(token, out.replace(str(table), ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)

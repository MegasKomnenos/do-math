"""dag_marker·session hook 시험. 직접 실행이 정본이다: python .claude/skills/do-dag/scripts/tests/test_dag_marker.py

fixture 원칙: 공개 API로만 구축하고 tempfile로 격리한다. 실 `.sdd/` 무접촉을
env seam(CLAUDE_PROJECT_DIR)으로, 실 격리 트리 무접촉을 DAG_WT_ROOT로 보장한다.

판별성: 게이트 시험은 합성 git 저장소에서 **실제 `git commit`을 실행**해 차단·통과를
잰다. 격리 시험은 실물 worktree를 만들어 파일시스템 실재로 판정한다. 순수 함수 단언과
경로 문자열 조립만 두면 shim·훅 설치·종료값 전파·`git worktree` 호출 중 어디가 끊겨도
GREEN이다.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import dag_marker  # noqa: E402


def _iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _phases(*names):
    return {n: {"opened_at": "2026-07-27T00:00:00Z"} for n in names}


def _grants(**kw):
    return {gid: {"until": until, "reason": "t"} for gid, until in kw.items()}


class GateDecisionTest(unittest.TestCase):
    """gate_decision은 순수 함수다 — 표로 전건을 잰다."""

    def test_table(self):
        now = datetime(2026, 7, 26, 12, 0, 0, tzinfo=timezone.utc)
        future = _iso(now + timedelta(minutes=10))
        past = _iso(now - timedelta(minutes=1))
        cases = [
            ("마커 공백 = 무국면", {}, 0),
            ("활성 국면 없음", {"active_phases": {}}, 0),
            ("무국면인데 grant만 있음", {"commit_grants": _grants(g1=future)}, 0),
            ("국면 O · grant X", {"active_phases": _phases("p")}, 1),
            ("국면 O · grant 만료", {"active_phases": _phases("p"), "commit_grants": _grants(g1=past)}, 1),
            ("국면 O · grant 신선", {"active_phases": _phases("p"), "commit_grants": _grants(g1=future)}, 0),
            ("국면 O · 만료분과 신선분 공존",
             {"active_phases": _phases("p"), "commit_grants": _grants(g1=past, g2=future)}, 0),
            ("국면 O · grant 불량 형식",
             {"active_phases": _phases("p"), "commit_grants": {"g1": {"until": "어제"}}}, 1),
            ("국면 둘 · grant X", {"active_phases": _phases("a", "b")}, 1),
        ]
        for label, data, expected in cases:
            with self.subTest(label):
                code, _ = dag_marker.gate_decision(data, now=now)
                self.assertEqual(code, expected, label)

    def test_isolation_exception_table(self):
        """격리 예외의 경계. 통과하는 것은 활성 국면의 노드 브랜치 하나뿐이다."""
        data = {"active_phases": _phases("demo")}
        cases = [
            ("메인 체크아웃(브랜치 없음)", None, 1),
            ("활성 국면의 노드 브랜치", "dag/demo/2.1", 0),
            ("닫힌 국면의 노드 브랜치", "dag/죽은국면/1", 1),
            ("접두사만 같은 국면 이름", "dag/demo2/1", 1),
            ("dag 밖 브랜치", "feature/x", 1),
            ("master", "master", 1),
            # 아래 여섯은 `worktree_open`이 만들 수 없는 이름이다. 관문이 국면 마디만
            # 재면 사람이 손으로 만든 이 트리들이 grant 없이 커밋을 세운다.
            ("행 마디가 없다", "dag/demo", 1),
            ("행이 빈 값이다", "dag/demo/", 1),
            ("행에 슬래시가 들었다", "dag/demo/2/extra", 1),
            ("행이 상위 경로다", "dag/demo/..", 1),
            ("행에 공백이 들었다", "dag/demo/x y", 1),
            ("행이 .lock으로 끝난다", "dag/demo/2.lock", 1),
        ]
        for label, branch, expected in cases:
            with self.subTest(label):
                code, _ = dag_marker.gate_decision(data, isolated_branch=branch)
                self.assertEqual(code, expected, label)

    def test_block_message_names_both_escapes(self):
        """차단 문면은 탈출 경로를 상시 병기한다 — 사용자를 가두지 않는 조건."""
        _, message = dag_marker.gate_decision({"active_phases": _phases("p")})
        self.assertIn("allow", message)
        self.assertIn("close", message)
        self.assertIn("파견표.md", message)

    def test_block_message_names_every_active_phase(self):
        _, message = dag_marker.gate_decision({"active_phases": _phases("a", "b")})
        self.assertIn("'a'", message)
        self.assertIn("'b'", message)

    def test_expiry_boundary_is_strict(self):
        now = datetime(2026, 7, 26, 12, 0, 0, tzinfo=timezone.utc)
        data = {"active_phases": _phases("p"), "commit_grants": _grants(g1=_iso(now))}
        self.assertEqual(dag_marker.fresh_grants(data, now=now), {})


class NameSyntaxTest(unittest.TestCase):
    """국면명·행 번호는 경로와 Git ref 두 문법의 교집합 안에 있어야 한다."""

    def test_accepted_phase_names(self):
        for name in ("demo", "veridict-개정", "국면_2", "a1", "x" * 64):
            with self.subTest(name):
                self.assertEqual(dag_marker.validate_phase(name), name)

    def test_rejected_phase_names(self):
        cases = {
            "슬래시": "alpha/beta",
            "백슬래시": "alpha\\beta",
            "상위 경로": "..",
            "점": "a.b",
            "공백": "a b",
            "빈 이름": "",
            "Git ref 금지 문자 ~": "a~1",
            "Git ref 금지 문자 :": "a:b",
            "Git ref 금지 문자 ?": "a?",
            "Git ref 금지 문자 *": "a*",
            "제어 문자": "a\nb",
            "64자 초과": "x" * 65,
        }
        for label, name in cases.items():
            with self.subTest(label):
                with self.assertRaises(ValueError):
                    dag_marker.validate_phase(name)

    def test_row_numbers_take_dots_but_not_traversal(self):
        for row in ("2", "2.1", "2.z", "2.g1"):
            with self.subTest(row):
                self.assertEqual(dag_marker.validate_row(row), row)
        for row in ("..", "2/1", ".2", "2.", "2..1", ""):
            with self.subTest(row):
                with self.assertRaises(ValueError):
                    dag_marker.validate_row(row)

    def test_a_row_may_not_end_in_dot_lock(self):
        """Git ref 마디는 `.lock`으로 끝날 수 없다. 여기서 막지 않으면 검증을 통과한
        값이 `git worktree add`에서 뒤늦게 깨지고, 오류 문면이 행 번호를 가리키지
        않는다."""
        for row in ("2.lock", "2.1.lock", "lock.lock"):
            with self.subTest(row):
                with self.assertRaises(ValueError):
                    dag_marker.validate_row(row)
        for row in ("2.locked", "2.lock.1", "lock"):
            with self.subTest(row):
                self.assertEqual(dag_marker.validate_row(row), row)

    def test_trailing_newline_is_rejected(self):
        """두 검증기는 `fullmatch`를 쓰므로 후행 개행을 거부한다. `match`로 바뀌면
        정규식의 `$`가 끝의 개행 직전에도 걸려 후행 개행이 통과한다. 통과한 값은
        하류에서 드러난다 — 국면명은 경로로, 행 번호는 Git ref로 간다."""
        for name in ("a\n", "국면_2\n", "x" * 64 + "\n"):
            with self.subTest(name=repr(name)):
                with self.assertRaises(ValueError):
                    dag_marker.validate_phase(name)
        for row in ("2\n", "2.1\n", "2.g1\n"):
            with self.subTest(row=repr(row)):
                with self.assertRaises(ValueError):
                    dag_marker.validate_row(row)

    def test_derivations_refuse_a_sliced_phase_name(self):
        """국면 `alpha/beta`는 브랜치 `dag/alpha/beta/2`를 만들고 관문은 그것을
        `alpha`로 잘라 읽는다. 파생 자리에서 막는다."""
        with self.assertRaises(ValueError):
            dag_marker.branch_name("alpha/beta", "2")
        with self.assertRaises(ValueError):
            dag_marker.wt_path("alpha/beta", "2")

    def test_the_gate_reads_a_valid_phase_name_whole(self):
        """문법을 통과한 이름에서는 관문의 자르기와 활성 국면 대조가 일치한다."""
        data = {"active_phases": _phases("veridict-개정")}
        branch = dag_marker.branch_name("veridict-개정", "2.1")
        code, _ = dag_marker.gate_decision(data, isolated_branch=branch)
        self.assertEqual(code, 0)

    def test_commands_refuse_a_bad_phase_name(self):
        import contextlib
        import io

        for argv in (
            ["open", "--phase", "alpha/beta"],
            ["close", "--phase", "alpha/beta"],
            ["sweep", "--phase", "alpha/beta"],
            ["worktree-open", "--phase", "alpha/beta", "--row", "2", "--base", "HEAD"],
            ["worktree-open", "--phase", "demo", "--row", "../x", "--base", "HEAD"],
        ):
            with self.subTest(argv[0] + " " + argv[2]):
                with contextlib.redirect_stderr(io.StringIO()) as err:
                    with self.assertRaises(SystemExit):
                        dag_marker.main(argv)
                self.assertIn("문법 밖", err.getvalue())

    def test_the_rule_reaches_the_one_who_names_the_phase(self):
        """국면명을 정하는 것은 메인이므로 `SKILL.md`가 문법을 적어야 한다.

        드리프트를 막으려고 `NAME_RULE`을 축자로 대조한다.
        """
        skill = (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(dag_marker.NAME_RULE, skill)


class MarkerRootTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._prev = os.environ.get("CLAUDE_PROJECT_DIR")
        os.environ["CLAUDE_PROJECT_DIR"] = str(self.root)

    def tearDown(self):
        if self._prev is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = self._prev
        self._tmp.cleanup()

    def _write_marker(self, body: str):
        path = dag_marker.marker_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path


class MarkerRoundTripTest(MarkerRootTest):
    def test_absent_marker_is_no_phase_not_an_error(self):
        """부재와 손상은 다른 사건이다 — 부재는 정상, 손상은 예외."""
        self.assertEqual(dag_marker.active_phases(dag_marker.load()), {})

    def test_corrupt_marker_raises(self):
        self._write_marker("{ 이건 json이 아니다")
        with self.assertRaises(json.JSONDecodeError):
            dag_marker.load()

    def test_non_object_marker_raises(self):
        self._write_marker("[1, 2]")
        with self.assertRaises(ValueError):
            dag_marker.load()

    def test_corrupt_marker_blocks_the_gate(self):
        """판독 불가는 차단 방향이다. 통과시키면 국면 진행 여부를 모른 채 여는 것이다."""
        self._write_marker("깨진 마커")
        self.assertEqual(dag_marker.main(["gate"]), 1)

    def test_single_phase_marker_is_read_as_the_plural_form(self):
        """단일 국면 형태의 마커도 복수 형태로 읽힌다."""
        self._write_marker(json.dumps({
            "phase": "옛국면", "opened_at": "2026-07-01T00:00:00Z",
            "commit_ok_until": "2099-01-01T00:00:00Z", "commit_reason": "옛 토큰",
        }))
        data = dag_marker.load()
        self.assertIn("옛국면", dag_marker.active_phases(data))
        self.assertEqual(dag_marker.gate_decision(data)[0], 0)

    def test_open_allow_clear_close_cycle(self):
        self.assertEqual(dag_marker.main(["open", "--phase", "demo"]), 0)
        self.assertIn("demo", dag_marker.active_phases(dag_marker.load()))
        self.assertEqual(dag_marker.main(["gate"]), 1)

        self.assertEqual(dag_marker.main(["allow", "--minutes", "5", "--reason", "병합"]), 0)
        self.assertEqual(dag_marker.main(["gate"]), 0)
        self.assertEqual(dag_marker.load()["commit_grants"]["grant-1"]["reason"], "병합")

        self.assertEqual(dag_marker.main(["clear-token", "--grant", "grant-1"]), 0)
        self.assertEqual(dag_marker.main(["gate"]), 1)

        self.assertEqual(dag_marker.main(["close", "--phase", "demo"]), 0)
        self.assertEqual(dag_marker.active_phases(dag_marker.load()), {})
        self.assertEqual(dag_marker.main(["gate"]), 0)

    def test_reopening_the_same_phase_is_a_resume(self):
        dag_marker.main(["open", "--phase", "demo"])
        opened = dag_marker.load()["active_phases"]["demo"]["opened_at"]
        dag_marker.main(["open", "--phase", "demo"])
        after = dag_marker.load()["active_phases"]
        self.assertEqual(list(after), ["demo"])
        self.assertEqual(after["demo"]["opened_at"], opened)

    def test_allow_without_phase_is_a_noop(self):
        self.assertEqual(dag_marker.main(["allow", "--minutes", "5"]), 0)
        self.assertEqual(dag_marker.load()["commit_grants"], {})

    def test_close_needs_a_target(self):
        with self.assertRaises(SystemExit):
            dag_marker.main(["close"])

    def test_close_all_empties_the_marker(self):
        dag_marker.main(["open", "--phase", "a"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "x"])
        self.assertEqual(dag_marker.main(["close", "--all"]), 0)
        self.assertEqual(dag_marker.load()["active_phases"], {})
        self.assertEqual(dag_marker.load()["commit_grants"], {})

    def test_close_all_keeps_the_grant_serial(self):
        """탈출은 활성 상태를 비우지 grant ID의 수명을 되감지 않는다. 되감으면
        옛 `clear-token` 하나가 새 국면의 같은 번호를 해제하고, 그 싱크는 exit 0과
        「해제」를 받아 남의 것을 지웠다는 신호를 얻지 못한다."""
        dag_marker.main(["open", "--phase", "p"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "x"])
        serial = dag_marker.load()["next_grant"]

        dag_marker.main(["close", "--all"])

        self.assertEqual(dag_marker.load()["next_grant"], serial)
        dag_marker.main(["open", "--phase", "q"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "y"])
        self.assertNotIn("grant-1", dag_marker.load()["commit_grants"])

    def test_an_unreadable_marker_shows_the_escape_path(self):
        """손상 마커를 처음 만나는 자리가 `status`와 `lease --status`다. 거기서
        `close --all`을 못 보면 커밋이 막힌 채 탈출 경로를 다른 파일에서 찾는다."""
        import contextlib
        import io

        path = dag_marker.marker_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{깨진", encoding="utf-8")
        for argv in (["status"], ["lease", "--status"]):
            with self.subTest(argv[0]):
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    self.assertEqual(dag_marker.main(argv), 1)
                self.assertIn("close --all", err.getvalue())

    def test_save_is_utf8_and_stable(self):
        dag_marker.save({"active_phases": _phases("국면")})
        raw = dag_marker.marker_path().read_text(encoding="utf-8")
        self.assertIn("국면", raw)
        self.assertIn("국면", json.loads(raw)["active_phases"])


class MultiPhaseTest(MarkerRootTest):
    """국면 A가 도는 동안 B를 열 수 있고, A의 종결이 B를 닫지 않는다."""

    def test_second_open_does_not_evict_the_first(self):
        dag_marker.main(["open", "--phase", "a"])
        dag_marker.main(["open", "--phase", "b"])
        self.assertEqual(sorted(dag_marker.active_phases(dag_marker.load())), ["a", "b"])

    def test_closing_one_phase_leaves_the_other_running(self):
        dag_marker.main(["open", "--phase", "a"])
        dag_marker.main(["open", "--phase", "b"])
        dag_marker.main(["close", "--phase", "a"])
        self.assertEqual(list(dag_marker.active_phases(dag_marker.load())), ["b"])
        self.assertEqual(dag_marker.main(["gate"]), 1, "남은 국면이 관문을 계속 지킨다")

    def test_the_last_close_returns_to_the_ordinary_commit_state(self):
        dag_marker.main(["open", "--phase", "a"])
        dag_marker.main(["open", "--phase", "b"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "x"])
        dag_marker.main(["close", "--phase", "a"])
        dag_marker.main(["close", "--phase", "b"])
        self.assertEqual(dag_marker.main(["gate"]), 0)
        self.assertEqual(dag_marker.load()["commit_grants"], {}, "grant가 국면 밖으로 살아남았다")


class GrantTest(MarkerRootTest):
    """grant는 독립이다 — 발급이 서로를 덮지 않고, 해제가 남의 것을 건드리지 않는다."""

    def test_two_grants_coexist(self):
        dag_marker.main(["open", "--phase", "p"])
        self.assertEqual(dag_marker.main(["allow", "--minutes", "30", "--reason", "싱크 A"]), 0)
        self.assertEqual(dag_marker.main(["allow", "--minutes", "30", "--reason", "싱크 B"]), 0)
        grants = dag_marker.load()["commit_grants"]
        self.assertEqual(sorted(grants), ["grant-1", "grant-2"])
        self.assertEqual(grants["grant-1"]["reason"], "싱크 A", "먼저 받은 grant가 덮였다")

    def test_clearing_one_grant_leaves_the_other(self):
        dag_marker.main(["open", "--phase", "p"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "A"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "B"])
        self.assertEqual(dag_marker.main(["clear-token", "--grant", "grant-1"]), 0)
        self.assertEqual(list(dag_marker.load()["commit_grants"]), ["grant-2"])
        self.assertEqual(dag_marker.main(["gate"]), 0, "남의 grant까지 해제됐다")

    def test_clearing_an_unknown_grant_fails_loudly(self):
        dag_marker.main(["open", "--phase", "p"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "A"])
        self.assertEqual(dag_marker.main(["clear-token", "--grant", "grant-9"]), 1)
        self.assertEqual(list(dag_marker.load()["commit_grants"]), ["grant-1"])

    def test_clear_all_releases_every_grant(self):
        dag_marker.main(["open", "--phase", "p"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "A"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "B"])
        self.assertEqual(dag_marker.main(["clear-token", "--all"]), 0)
        self.assertEqual(dag_marker.load()["commit_grants"], {})

    def test_expired_grants_are_swept_on_the_next_issue(self):
        dag_marker.main(["open", "--phase", "p"])
        dag_marker.main(["allow", "--minutes", "0", "--reason", "만료"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "신규"])
        grants = dag_marker.load()["commit_grants"]
        self.assertEqual(list(grants), ["grant-2"])
        self.assertEqual(grants["grant-2"]["reason"], "신규")

    def test_grant_numbers_are_never_reused(self):
        """만료로 비워진 번호를 다시 쓰면, ID를 쥔 싱크의 뒤늦은 해제가 남의 grant를 푼다."""
        dag_marker.main(["open", "--phase", "p"])
        dag_marker.main(["allow", "--minutes", "0", "--reason", "먼저 받고 만료됨"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "뒤에 받음"])

        self.assertEqual(dag_marker.main(["clear-token", "--grant", "grant-1"]), 1)
        self.assertEqual(dag_marker.main(["gate"]), 0, "남의 grant가 해제됐다")

    def test_numbering_survives_a_full_release(self):
        dag_marker.main(["open", "--phase", "p"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "A"])
        dag_marker.main(["clear-token", "--all"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "B"])
        self.assertEqual(list(dag_marker.load()["commit_grants"]), ["grant-2"])

    def test_the_lock_is_not_held_between_commands(self):
        """락은 읽고-고쳐-쓰기 동안만 산다 — 남으면 다음 grant가 영영 막힌다."""
        dag_marker.main(["open", "--phase", "p"])
        dag_marker.main(["allow", "--minutes", "30", "--reason", "A"])
        self.assertFalse(dag_marker.lock_path().exists())

    def test_a_stale_lock_does_not_wedge_the_marker(self):
        dag_marker.main(["open", "--phase", "p"])
        lock = dag_marker.lock_path()
        lock.write_text("죽은 에이전트", encoding="utf-8")
        os.utime(lock, (0, 0))
        self.assertEqual(dag_marker.main(["allow", "--minutes", "30", "--reason", "A"]), 0)

    def test_concurrent_allows_lose_no_grant(self):
        """락의 봉인. 별도 프로세스로 겹쳐 발급해 grant가 하나도 유실되지 않음을 잰다.

        락이 없어도 위 시험들은 통과한다(락 부재는 '락이 안 남았다'를 자동으로 만족시킨다).
        직렬화 자체를 재는 것은 이 시험뿐이다.
        """
        dag_marker.main(["open", "--phase", "p"])
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.root), PYTHONIOENCODING="utf-8")
        procs = [
            subprocess.Popen(
                [sys.executable, str(SCRIPTS / "dag_marker.py"),
                 "allow", "--minutes", "30", "--reason", f"싱크-{i}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
            )
            for i in range(8)
        ]
        codes = []
        for p in procs:
            # 파이프를 회수하지 않으면 자식이 출력 버퍼에서 막힐 수 있고 fd가 샌다.
            with p:
                p.communicate()
                codes.append(p.returncode)

        self.assertEqual(codes, [0] * 8, "발급이 거부됐다")
        grants = dag_marker.load()["commit_grants"]
        self.assertEqual(len(grants), 8, f"grant가 유실됐다: {sorted(grants)}")
        self.assertEqual(
            sorted(g["reason"] for g in grants.values()),
            sorted(f"싱크-{i}" for i in range(8)),
        )
        self.assertFalse(dag_marker.lock_path().exists())


class LeaseTest(MarkerRootTest):
    """병합 lease는 단수다 — 메인 체크아웃 인덱스가 하나뿐이라는 사실의 직접 표현이다."""

    def setUp(self):
        super().setUp()
        dag_marker.main(["open", "--phase", "p"])

    def _acquire(self, owner, minutes=30):
        return dag_marker.main(["lease", "--acquire", "--owner", owner, "--minutes", str(minutes)])

    def test_second_owner_is_refused(self):
        self.assertEqual(self._acquire("2.5.z"), 0)
        self.assertEqual(self._acquire("3.z"), 1, "두 싱크가 동시에 병합권을 쥐었다")
        self.assertEqual(dag_marker.load()["merge_lease"]["owner"], "2.5.z")

    def test_same_owner_reacquires(self):
        """재시도로 다시 쏘아진 싱크가 자기 lease에 막히면 그 국면은 영영 못 닫는다."""
        self.assertEqual(self._acquire("2.5.z"), 0)
        self.assertEqual(self._acquire("2.5.z"), 0)

    def test_release_by_a_stranger_is_refused(self):
        self._acquire("2.5.z")
        self.assertEqual(dag_marker.main(["lease", "--release", "--owner", "3.z"]), 1)
        self.assertEqual(dag_marker.load()["merge_lease"]["owner"], "2.5.z")

    def test_release_by_the_owner_frees_it(self):
        self._acquire("2.5.z")
        self.assertEqual(dag_marker.main(["lease", "--release", "--owner", "2.5.z"]), 0)
        self.assertEqual(dag_marker.load()["merge_lease"], {})
        self.assertEqual(self._acquire("3.z"), 0)

    def test_an_expired_lease_is_reclaimed(self):
        """죽은 싱크의 lease가 국면을 영구히 멎게 하지 않는다."""
        data = dag_marker.load()
        data["merge_lease"] = {"owner": "죽은싱크", "until": "2000-01-01T00:00:00Z"}
        dag_marker.save(data)
        self.assertEqual(self._acquire("3.z"), 0)
        self.assertEqual(dag_marker.load()["merge_lease"]["owner"], "3.z")

    def test_a_broken_lease_does_not_wedge_the_phase(self):
        """grant와 반대 방향이다 — 파손을 점유로 읽으면 아무도 병합하지 못한다."""
        data = dag_marker.load()
        data["merge_lease"] = {"owner": "x"}  # until 없음
        dag_marker.save(data)
        self.assertEqual(self._acquire("3.z"), 0)

    def test_a_marker_without_the_key_reads_as_empty(self):
        self._write_marker(json.dumps({"active_phases": _phases("옛국면")}))
        self.assertEqual(dag_marker.load()["merge_lease"], {})
        self.assertEqual(dag_marker.fresh_lease(dag_marker.load()), {})

    def test_the_last_close_clears_the_lease(self):
        self._acquire("2.5.z")
        dag_marker.main(["close", "--phase", "p"])
        self.assertEqual(dag_marker.load()["merge_lease"], {})

    def test_lease_needs_exactly_one_mode(self):
        with self.assertRaises(SystemExit):
            dag_marker.main(["lease", "--acquire", "--release", "--owner", "z"])
        with self.assertRaises(SystemExit):
            dag_marker.main(["lease", "--acquire"])

    def test_concurrent_acquires_leave_exactly_one_owner(self):
        """락과 lease의 봉인. 별도 프로세스 여덟이 겹쳐 병합권을 다툰다.

        획득 성공이 하나를 넘으면 두 싱크가 같은 인덱스에서 병합해 서로의 병합을
        삼킨다. `--acquire`를 무조건 성공으로 바꾸면 이 시험이 RED가 된다.
        """
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.root), PYTHONIOENCODING="utf-8")
        procs = []
        for i in range(8):
            procs.append(subprocess.Popen(
                [sys.executable, str(SCRIPTS / "dag_marker.py"),
                 "lease", "--acquire", "--owner", f"{i}.z", "--minutes", "30"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
            ))
        codes = []
        for p in procs:
            with p:
                p.communicate()
                codes.append(p.returncode)

        self.assertEqual(codes.count(0), 1, f"병합권을 여럿이 쥐었다: {codes}")
        self.assertEqual(codes.count(1), 7, codes)
        owner = dag_marker.load()["merge_lease"]["owner"]
        self.assertEqual(owner, f"{codes.index(0)}.z", "이긴 프로세스와 기록된 소유자가 다르다")
        self.assertFalse(dag_marker.lock_path().exists())


# 세션 주입 훅의 시험은 `test_dag_session_note.py`에 산다 — 훅은 별개 진입점이고
# 그 계약(항상 exit 0 · 좌표만 주입 · 무국면 무출력)은 마커의 계약이 아니다.


class LeftoverScopeTest(unittest.TestCase):
    """활성 국면의 트리·브랜치는 잔재가 아니다 — 상시 참인 경고는 읽히지 않는다."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        self.wt_root = Path(self._tmp.name) / "wt"
        self.root.mkdir()
        self.wt_root.mkdir()
        self._prev = {k: os.environ.get(k) for k in ("CLAUDE_PROJECT_DIR", "DAG_WT_ROOT")}
        os.environ["CLAUDE_PROJECT_DIR"] = str(self.root)
        os.environ["DAG_WT_ROOT"] = str(self.wt_root)
        for name in ("도는국면+2.5", "죽은국면+1"):
            (self.wt_root / name).mkdir()

    def tearDown(self):
        for k, v in self._prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self._tmp.cleanup()

    def _names(self):
        return sorted(Path(p).name for p in dag_marker.leftovers(self.root)["worktrees"])

    def test_without_an_active_phase_everything_is_a_leftover(self):
        self.assertEqual(self._names(), ["도는국면+2.5", "죽은국면+1"])

    def test_an_active_phase_is_excluded(self):
        dag_marker.save({"active_phases": _phases("도는국면")}, self.root)
        self.assertEqual(self._names(), ["죽은국면+1"])

    def test_an_unreadable_marker_excludes_nothing(self):
        """판독 불가는 고지 쪽으로 기운다 — 조용히 빠뜨리지 않는다."""
        path = dag_marker.marker_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("깨짐", encoding="utf-8")
        self.assertEqual(self._names(), ["도는국면+2.5", "죽은국면+1"])

    def test_invalid_active_phase_name_does_not_kill_leftover_notice(self):
        dag_marker.save(
            {"active_phases": {"a/b": {"opened_at": "2026-01-01T00:00:00Z"}}},
            self.root,
        )
        self.assertEqual(self._names(), ["도는국면+2.5", "죽은국면+1"])
        self.assertEqual(self._names(), ["도는국면+2.5", "죽은국면+1"])

    def test_a_tree_owned_by_another_repo_is_not_a_leftover(self):
        """dag-wt 루트는 저장소 간 공유다 — 남의 트리를 이 저장소의 잔재로 세지 않는다."""
        other_gitdir = Path(self._tmp.name) / "other-repo" / ".git" / "worktrees" / "남의국면+1"
        other_gitdir.mkdir(parents=True)
        foreign = self.wt_root / "남의국면+1"
        foreign.mkdir()
        (foreign / ".git").write_text(f"gitdir: {other_gitdir}\n", encoding="utf-8")
        self.assertEqual(self._names(), ["도는국면+2.5", "죽은국면+1"])

    def test_a_tree_owned_by_this_repo_stays_a_leftover(self):
        """소속이 이 저장소로 확인된 트리는 그대로 잔재다."""
        own_gitdir = self.root / ".git" / "worktrees" / "죽은국면+1"
        own_gitdir.mkdir(parents=True)
        (self.wt_root / "죽은국면+1" / ".git").write_text(
            f"gitdir: {own_gitdir}\n", encoding="utf-8"
        )
        self.assertEqual(self._names(), ["도는국면+2.5", "죽은국면+1"])


class SyntheticRepoTest(unittest.TestCase):
    """합성 저장소 하나. 격리 시험과 관문 시험이 같은 기반을 쓴다."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        self.wt_root = Path(self._tmp.name) / "wt"
        self.root.mkdir()
        self.wt_root.mkdir()
        self._prev = {k: os.environ.get(k) for k in ("CLAUDE_PROJECT_DIR", "DAG_WT_ROOT")}
        os.environ["CLAUDE_PROJECT_DIR"] = str(self.root)
        os.environ["DAG_WT_ROOT"] = str(self.wt_root)
        self.env = dict(
            os.environ,
            CLAUDE_PROJECT_DIR=str(self.root),
            DAG_WT_ROOT=str(self.wt_root),
            PYTHONIOENCODING="utf-8",
        )
        self._git("init", "-q")
        self._git("config", "user.email", "t@example.com")
        self._git("config", "user.name", "t")
        self._git("config", "commit.gpgsign", "false")
        (self.root / "seed.txt").write_text("seed", encoding="utf-8")
        self._git("add", "seed.txt")
        self._git("commit", "-q", "-m", "seed")

    def tearDown(self):
        for k, v in self._prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self._tmp.cleanup()

    def _git(self, *args, cwd=None):
        return subprocess.run(
            ["git", *args], cwd=str(cwd or self.root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=self.env,
        )

    def _head(self, cwd=None) -> str:
        return self._git("rev-parse", "HEAD", cwd=cwd).stdout.strip()

    def _branches(self):
        return self._git("branch", "--format=%(refname:short)").stdout.split()

    def _commit(self, name, cwd=None):
        base = Path(cwd or self.root)
        (base / name).write_text(name, encoding="utf-8")
        self._git("add", name, cwd=base)
        self._git("commit", "-q", "-m", name, cwd=base)


class WorktreeOpenTest(SyntheticRepoTest):
    """격리 트리의 생성·재사용·복구와, 지우지 않고 멈추는 세 경우.

    처분 쪽(정상 완료의 회수, 파킹 트리의 보존)은 SweepTest가 잰다. 작업 실패·병합
    충돌의 처분은 코드가 아니라 싱크 파견문의 절차다.
    """

    def test_creates_the_tree_and_the_branch(self):
        base = self._head()
        result = dag_marker.worktree_open("demo", "2.1", base)
        self.assertEqual(result["action"], "생성")
        path = dag_marker.wt_path("demo", "2.1")
        self.assertTrue((path / "seed.txt").is_file())
        self.assertIn("dag/demo/2.1", self._branches())
        self.assertEqual(self._head(cwd=path), base, "base가 동결되지 않았다")

    def test_reopening_the_same_row_reuses_the_tree(self):
        base = self._head()
        dag_marker.worktree_open("demo", "2.1", base)
        self._commit("작업중.txt", cwd=dag_marker.wt_path("demo", "2.1"))

        result = dag_marker.worktree_open("demo", "2.1", base)

        self.assertEqual(result["action"], "재사용")
        self.assertTrue(
            (dag_marker.wt_path("demo", "2.1") / "작업중.txt").is_file(),
            "이전 시도의 부분 산출을 지웠다",
        )

    def test_a_leftover_branch_is_restored_into_a_tree(self):
        base = self._head()
        path = dag_marker.worktree_open("demo", "2.1", base)["path"]
        self._commit("작업.txt", cwd=Path(path))
        self._git("worktree", "remove", "--force", path)
        self.assertFalse(Path(path).exists())

        result = dag_marker.worktree_open("demo", "2.1", base)

        self.assertEqual(result["action"], "복구")
        self.assertTrue((Path(path) / "작업.txt").is_file(), "브랜치의 커밋이 복구되지 않았다")

    def test_an_unregistered_path_is_not_deleted(self):
        path = dag_marker.wt_path("demo", "2.1")
        path.mkdir(parents=True)
        (path / "남의 것.txt").write_text("실물", encoding="utf-8")

        with self.assertRaises(dag_marker.WorktreeConflict):
            dag_marker.worktree_open("demo", "2.1", self._head())

        self.assertTrue((path / "남의 것.txt").is_file(), "등록되지 않은 실물을 지웠다")

    def test_a_path_checked_out_to_another_branch_is_refused(self):
        path = dag_marker.wt_path("demo", "2.1")
        self._git("worktree", "add", "-b", "남의브랜치", str(path))

        with self.assertRaises(dag_marker.WorktreeConflict):
            dag_marker.worktree_open("demo", "2.1", self._head())

        self.assertTrue(path.exists())
        self.assertIn("남의브랜치", self._branches())

    def test_a_different_base_is_refused_instead_of_reset(self):
        """base 동결이 깨진 트리에서 계속하면 RED 관찰과 GREEN 확인이 다른 저장소에서 난다."""
        first = self._head()
        dag_marker.worktree_open("demo", "2.1", first)
        self._commit("master가 움직였다.txt")
        moved = self._head()
        self.assertNotEqual(first, moved)

        with self.assertRaises(dag_marker.WorktreeConflict):
            dag_marker.worktree_open("demo", "2.1", moved)

        self.assertTrue(dag_marker.wt_path("demo", "2.1").exists(), "base 불일치로 트리를 지웠다")

    def test_an_unresolvable_base_is_refused(self):
        with self.assertRaises(dag_marker.WorktreeConflict):
            dag_marker.worktree_open("demo", "2.1", "0" * 40)

    def test_command_exit_codes_and_coordinates(self):
        base = self._head()
        self.assertEqual(
            dag_marker.main(["worktree-open", "--phase", "demo", "--row", "2.1", "--base", base]), 0
        )
        self.assertEqual(
            dag_marker.main(["worktree-open", "--phase", "demo", "--row", "2.1", "--base", "0" * 40]), 1
        )


class GateEndToEndTest(SyntheticRepoTest):
    """합성 저장소에서 실제 `git commit`을 돌려 차단·통과를 잰다.

    이 시험이 없으면 shim 생성·훅 설치·종료값 전파 중 어디가 끊겨도 순수 함수
    단언만으로 GREEN이 된다.
    """

    def _marker(self, argv):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "dag_marker.py"), *argv],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=self.env,
        )

    def _commit_attempt(self, name):
        (self.root / name).write_text("x", encoding="utf-8")
        self._git("add", name)
        return self._git("commit", "-m", name)

    def test_install_then_block_then_allow(self):
        install = self._marker(["install-hook"])
        self.assertEqual(install.returncode, 0, install.stderr)
        self.assertTrue((self.root / ".git" / "hooks" / "pre-commit").exists())

        # 무국면: 통과한다.
        self.assertEqual(self._commit_attempt("a.txt").returncode, 0)

        # 국면 개설 + grant 없음: 차단된다.
        self.assertEqual(self._marker(["open", "--phase", "demo"]).returncode, 0)
        blocked = self._commit_attempt("b.txt")
        self.assertNotEqual(blocked.returncode, 0, "국면 중 grant 없는 커밋이 통과했다")
        self.assertIn("demo", blocked.stderr + blocked.stdout)

        # grant 발급: 통과한다.
        self.assertEqual(self._marker(["allow", "--minutes", "5", "--reason", "병합"]).returncode, 0)
        self.assertEqual(self._commit_attempt("b.txt").returncode, 0)

        # 국면 종결: 다시 통과한다.
        self.assertEqual(self._marker(["close", "--phase", "demo"]).returncode, 0)
        self.assertEqual(self._commit_attempt("c.txt").returncode, 0)

    def test_a_second_phase_keeps_the_gate_shut(self):
        self._marker(["install-hook"])
        self._marker(["open", "--phase", "a"])
        self._marker(["open", "--phase", "b"])
        self._marker(["close", "--phase", "a"])
        blocked = self._commit_attempt("b.txt")
        self.assertNotEqual(blocked.returncode, 0, "국면 a의 종결이 국면 b의 관문을 열었다")

    def test_a_worktree_commit_needs_no_grant(self):
        """격리 안의 커밋은 grant 없이 통과한다.

        예외를 무력화하면(`isolated_commit_branch`가 늘 None) 이 시험이 RED가 된다.
        """
        self._marker(["install-hook"])
        self._marker(["open", "--phase", "demo"])
        path = Path(dag_marker.worktree_open("demo", "2.1", self._head())["path"])

        (path / "노드 산출.txt").write_text("x", encoding="utf-8")
        self._git("add", "-A", cwd=path)
        result = self._git("commit", "-m", "노드 작업", cwd=path)

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertNotEqual(
            self._commit_attempt("메인.txt").returncode, 0,
            "격리 예외가 메인 체크아웃까지 열었다",
        )

    def test_a_worktree_of_a_closed_phase_is_still_blocked(self):
        """예외의 경계는 활성 국면의 노드 브랜치다 — 잔재 트리는 평시 처분으로 돌아간다."""
        self._marker(["install-hook"])
        self._marker(["open", "--phase", "죽은국면"])
        path = Path(dag_marker.worktree_open("죽은국면", "1", self._head())["path"])
        (path / "잔재.txt").write_text("x", encoding="utf-8")  # 미커밋 산출이라 회수되지 않는다
        self._marker(["open", "--phase", "demo"])
        self._marker(["close", "--phase", "죽은국면"])

        self._git("add", "-A", cwd=path)
        result = self._git("commit", "-m", "잔재 커밋", cwd=path)

        self.assertNotEqual(result.returncode, 0, "닫힌 국면의 트리가 관문을 통과했다")

    def test_a_foreign_branch_in_a_worktree_is_blocked(self):
        """링크된 트리라는 사실만으로는 열리지 않는다 — 이름이 노드 브랜치여야 한다."""
        self._marker(["install-hook"])
        self._marker(["open", "--phase", "demo"])
        path = self.wt_root / "남의트리"
        self._git("worktree", "add", "-b", "남의브랜치", str(path))

        (path / "x.txt").write_text("x", encoding="utf-8")
        self._git("add", "-A", cwd=path)
        result = self._git("commit", "-m", "남의 커밋", cwd=path)

        self.assertNotEqual(result.returncode, 0, "국면 밖 브랜치가 관문을 통과했다")

    def test_the_main_checkout_is_not_read_as_isolated(self):
        self.assertIsNone(dag_marker.isolated_commit_branch(self.root))

    def test_a_node_tree_is_read_as_isolated(self):
        path = Path(dag_marker.worktree_open("demo", "2.1", self._head())["path"])
        self.assertEqual(dag_marker.isolated_commit_branch(path), "dag/demo/2.1")

    def test_install_does_not_clobber_an_existing_hook(self):
        hooks = self.root / ".git" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        (hooks / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        r = self._marker(["install-hook"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("--force", r.stdout)
        self.assertEqual((hooks / "pre-commit").read_text(encoding="utf-8").count("exit 0"), 1)


class SweepTest(SyntheticRepoTest):
    """회수는 실제 worktree·브랜치로만 잰다.

    판별성: 경로 문자열 조립만 단언하면 `git worktree remove`가 실패해도 GREEN이다.
    그래서 합성 저장소에 실물 worktree를 만들고 파일시스템 실재로 판정한다.

    안전 방향: 미커밋 산출과 미병합 커밋은 **지우지 않고 남겨 보고한다**.
    """

    def _add_worktree(self, phase, row):
        return Path(dag_marker.worktree_open(phase, row, self._head())["path"])

    def _add_unregistered_worktree(self, phase, row):
        path = dag_marker.wt_path(phase, row)
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(path), self._head()],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        return path

    def test_sweep_recovers_a_detached_worktree_by_path(self):
        path = self._add_unregistered_worktree("죽은국면", "1")
        self.assertTrue(path.exists())
        dag_marker.sweep("죽은국면")
        self.assertFalse(path.exists())

    def test_derived_names_are_a_pure_function_of_phase_and_row(self):
        """생성·회수·종결이 각자 재도출해도 같은 값이어야 한다 — 좌표 발명 금지의 기제."""
        self.assertEqual(dag_marker.branch_name("데모", "2.5"), "dag/데모/2.5")
        self.assertEqual(dag_marker.wt_path("데모", "2.5"), self.wt_root / "데모+2.5")

    def test_the_tree_name_separator_splits_phase_from_row(self):
        """국면명과 행 번호가 둘 다 `-`를 받으므로 구분자가 `-`이면 두 좌표가 한
        경로로 붕괴한다. 구분자는 두 문법이 함께 막는 문자라야 한다."""
        self.assertNotEqual(dag_marker.wt_path("a-1", "2"),
                            dag_marker.wt_path("a", "1-2"))
        with self.assertRaises(ValueError):
            dag_marker.validate_phase(f"a{dag_marker.WT_SEP}1")
        with self.assertRaises(ValueError):
            dag_marker.validate_row(f"1{dag_marker.WT_SEP}2")

    def test_clean_worktree_and_its_branch_are_recovered(self):
        path = self._add_worktree("demo", "2")
        dag_marker.main(["open", "--phase", "demo"])

        self.assertEqual(dag_marker.main(["close", "--phase", "demo"]), 0)

        self.assertFalse(path.exists(), "깨끗한 트리가 회수되지 않았다")
        self.assertNotIn("dag/demo/2", self._branches())
        self.assertEqual(dag_marker.active_phases(dag_marker.load()), {})

    def test_dirty_worktree_survives_and_is_reported(self):
        path = self._add_worktree("demo", "3")
        (path / "미커밋.txt").write_text("채록 전이다", encoding="utf-8")
        dag_marker.main(["open", "--phase", "demo"])

        report = dag_marker.sweep("demo")

        self.assertIn(str(path), report["kept_worktrees"])
        self.assertTrue(path.exists(), "미커밋 산출이 있는 트리를 지웠다")
        self.assertEqual(report["removed_worktrees"], [])
        # 살아남은 트리에 체크아웃된 브랜치를 "미병합"으로 보고하면 잔존 사유를 오독시킨다.
        self.assertIn("체크아웃", report["kept_branch_reason"]["dag/demo/3"])

    def test_unmerged_branch_survives(self):
        path = self._add_worktree("demo", "4")
        self._commit("작업.txt", cwd=path)
        self._git("worktree", "remove", str(path))

        report = dag_marker.sweep("demo")

        self.assertIn("dag/demo/4", report["kept_branches"])
        self.assertIn("dag/demo/4", self._branches(), "병합되지 않은 커밋을 지웠다")
        self.assertIn("병합", report["kept_branch_reason"]["dag/demo/4"])

    def test_other_phases_are_untouched(self):
        mine = self._add_worktree("demo", "1")
        theirs = self._add_worktree("other", "1")

        dag_marker.sweep("demo")

        self.assertFalse(mine.exists())
        self.assertTrue(theirs.exists(), "국면 경계를 넘어 회수했다")
        self.assertIn("dag/other/1", self._branches())

    def test_sweep_command_exit_code_signals_leftovers(self):
        """종결 행이 exit 0으로 '잔존 0'을 기계 판정할 수 있어야 한다."""
        self.assertEqual(dag_marker.main(["sweep", "--phase", "demo"]), 0)

        path = self._add_worktree("demo", "5")
        (path / "미커밋.txt").write_text("x", encoding="utf-8")
        self.assertEqual(dag_marker.main(["sweep", "--phase", "demo"]), 1)

    def test_close_all_survives_a_broken_git(self):
        """close --all은 탈출 경로다 — 회수가 무엇에 걸려 넘어져도 마커는 비워진다."""
        dag_marker.main(["open", "--phase", "demo"])
        broken = dag_marker.sweep

        def explode(*a, **k):
            raise RuntimeError("git이 없다")

        dag_marker.sweep = explode
        try:
            self.assertEqual(dag_marker.main(["close", "--all"]), 0)
        finally:
            dag_marker.sweep = broken
        self.assertEqual(dag_marker.active_phases(dag_marker.load()), {})

    def test_session_hook_reports_leftovers(self):
        self._add_worktree("demo", "6")
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "hooks" / "dag_session_note.py")],
            capture_output=True, text=True, encoding="utf-8", env=self.env,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("잔재", r.stdout)
        self.assertIn("dag/demo/6", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)

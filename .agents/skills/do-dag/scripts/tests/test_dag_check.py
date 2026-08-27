"""dag_check 파견표 검산 시험. 직접 실행이 정본이다: python .agents/skills/do-dag/scripts/tests/test_dag_check.py

검산 대상은 아홉으로 한정한다:
① 행 서식(칸이 정확히 일곱 + 행 번호 실재·문법·유일성)
② 상태·유형 어휘(닫힌 목록, 공백 불허)
③ 칸 계약(행 유형별 파견문·완료 신호·모델. 값 · `—` · 빈 칸을 셋으로 가르고,
   미완결 전개의 완료 신호는 `<번호>-보고.md`로 둔다)
④ 서브트리 폐쇄(자식은 자기 범위 밖을 선행으로 지목하지 않는다)
⑤ 싱크 수렴(전개의 모든 자손은 그 전개의 싱크에, 최상위 행은 국면 싱크에 도달한다.
   마디 있는 행은 부모가 실재하고, 완결된 전개는 싱크를 실제로 깔았고,
   국면 종결 싱크는 정확히 하나다)
⑥ 순환 부재
⑦ 좌표 실재(파견문·계약·불변식 승계와 적재·모델 배정 근거·반환·완료 신호 전건. 비면 미충족.
   완결된 싱크는 결산 `단계`가 `종결`)
⑧ 게이트 결정(완결된 게이트의 결정 절·상태, 결정 파일을 낳는 행이 선행 사슬에 있는가,
   게이트를 선행으로 지목한 행이 전개이고 그 파견문 `정본:` 슬롯이 결정 좌표를 싣는가)
⑨ 운전(파견 직전 행의 모델·노력 — drive 모드 전용)

그 밖의 검사는 두지 않는다.

모드 둘의 차이도 여기서 잰다: partial은 살아 있는 전개의 서브트리를 발견에서
제외하고(`--writer`가 자기 서브트리를 그 제외에서 뺀다), 제외된 행도 남의 선행으로는
실재한다.

`--sink-return`은 별도 반환 게이트다. 실제 싱크 반환과 결산 frontmatter를 상태 열
변경 전에 대조한다.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import dag_check  # noqa: E402

# 파견문이 실제로 싣는 계약 좌표. 실물이라 이 상수가 자산의 실재도 함께 잰다.
CONTRACT = SCRIPTS.parent / "계약" / "공통.md"
CONTRACT_LINE = f"- 계약: {CONTRACT}\n"
VERIFY_CONTRACT = SCRIPTS.parent / "계약" / "검증런.md"
ASSIGN_LINE = "- 모델 배정 근거: 배정표 기본(작업자 opus med)\n"
RETURN_LINE = "- 반환: 공통 최종 반환 계약. 완료 첫 줄 DONE. 추가 필드 없음\n"


def invariant_path(run_dir: Path, owner: str = "0", *, suffix: str = "") -> Path:
    parts = owner.split(".")
    parent = run_dir / "행"
    for part in parts[:-1]:
        parent /= f"{part}.d"
    return parent / f"{parts[-1]}.d" / f"불변식{suffix}.md"


def valid_brief_body(run_dir: Path, *owners: str) -> str:
    owners = owners or ("0",)
    coords = [invariant_path(run_dir, owner) for owner in owners]
    for coord in coords:
        coord.parent.mkdir(parents=True, exist_ok=True)
        coord.write_text("# 불변식\n\n- 닫힌 값: A · B · C\n", encoding="utf-8")
    joined = " · ".join(str(coord) for coord in coords)
    budget_files = ",".join(str(coord) for coord in coords)
    return (
        CONTRACT_LINE
        + ASSIGN_LINE
        + RETURN_LINE
        + f"- 불변식: {joined}\n"
        + f"- 읽기 목록: {joined}\n"
        + f"- 예산: python dag_measure.py budget --files {budget_files}\n"
    )

HEAD = (
    "# 파견표: demo\n\n"
    "| 행 | 유형 | 파견문 | 선행 | 완료 신호 | 모델 | 상태 |\n"
    "|---|---|---|---|---|---|---|\n"
)


def table(*rows: str) -> str:
    return HEAD + "".join(rows) + "\n<!-- 행 끝 -->\n"


def row(rid, kind="파견", brief="—", deps="—", signal="—", model="opus low", state="미착수"):
    return f"| {rid} | {kind} | {brief} | {deps} | {signal} | {model} | {state} |\n"


class ParseTest(unittest.TestCase):
    def test_columns(self):
        rows = dag_check.parse_rows(table(row("2.1", deps="2", signal="행/2.d/1-보고.md")))
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r.id, "2.1")
        self.assertEqual(r.kind, "파견")
        self.assertEqual(r.deps, ["2"])
        self.assertEqual(r.signal, "행/2.d/1-보고.md")
        self.assertEqual(r.state, "미착수")

    def test_dash_is_not_the_same_as_a_blank_cell(self):
        """`—`는 명시적 해당 없음이고 빈 칸은 누락이다 — 칸 계약이 진단을 가른다."""
        none_row = dag_check.parse_rows(
            HEAD + "| 1 | 파견 | — | — | — | opus low | 미착수 |\n"
        )[0]
        blank_row = dag_check.parse_rows(
            HEAD + "| 1 | 파견 |  | — | — | opus low | 미착수 |\n"
        )[0]

        none_findings = dag_check.check_columns([none_row])
        blank_findings = dag_check.check_columns([blank_row])

        self.assertTrue(any("해당 없음(—)" in finding for finding in none_findings))
        self.assertTrue(any("빈 칸(누락)" in finding for finding in blank_findings))

    def test_multiple_deps(self):
        rows = dag_check.parse_rows(table(row("2.z", kind="싱크", deps="2.1, 2.2")))
        self.assertEqual(rows[0].deps, ["2.1", "2.2"])

    def test_header_and_anchor_are_not_rows(self):
        rows = dag_check.parse_rows(table(row("1")))
        self.assertEqual([r.id for r in rows], ["1"])


class ClosureTest(unittest.TestCase):
    def test_child_may_depend_on_its_expander(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="2"),
            row("2.z", kind="싱크", deps="2.1"),
        )
        self.assertEqual(dag_check.check_closure(dag_check.parse_rows(text)), [])

    def test_child_may_depend_on_sibling_sink(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", kind="전개", signal="행/2.d/1.d/"),
            row("2.1.z", kind="싱크", deps="2.1"),
            row("2.2", deps="2.1.z"),
            row("2.z", kind="싱크", deps="2.1.z, 2.2"),
        )
        self.assertEqual(dag_check.check_closure(dag_check.parse_rows(text)), [])

    def test_child_reaching_outside_its_scope_is_found(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="3"),
            row("2.z", kind="싱크", deps="2.1"),
            row("3"),
        )
        found = dag_check.check_closure(dag_check.parse_rows(text))
        self.assertTrue(any("2.1" in f and "3" in f for f in found), found)

    def test_top_level_reaching_into_a_subtree_is_found(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="2"),
            row("2.z", kind="싱크", deps="2.1"),
            row("3", deps="2.1"),
        )
        found = dag_check.check_closure(dag_check.parse_rows(text))
        self.assertTrue(any("3" in f and "2.1" in f for f in found), found)

    def test_top_level_depending_on_a_sink_is_allowed(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="2"),
            row("2.z", kind="싱크", deps="2.1"),
            row("3", deps="2.z"),
        )
        self.assertEqual(dag_check.check_closure(dag_check.parse_rows(text)), [])

    def test_unknown_dependency_is_found(self):
        text = table(row("1", deps="9"))
        found = dag_check.check_closure(dag_check.parse_rows(text))
        self.assertTrue(any("9" in f for f in found), found)

    def test_promised_sink_of_an_unexpanded_expander_is_allowed(self):
        """전개는 반드시 자기 싱크를 만든다 — 펼치기 전에도 지목할 수 있다."""
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("z", kind="싱크", deps="2.z"),
        )
        self.assertEqual(dag_check.check_closure(dag_check.parse_rows(text)), [])

    def test_promised_sink_of_a_non_expander_is_found(self):
        text = table(row("2", kind="파견"), row("z", kind="싱크", deps="2.z"))
        found = dag_check.check_closure(dag_check.parse_rows(text))
        self.assertTrue(any("2.z" in f for f in found), found)

    def test_promised_sink_of_an_unknown_row_is_found(self):
        text = table(row("z", kind="싱크", deps="9.z"))
        found = dag_check.check_closure(dag_check.parse_rows(text))
        self.assertTrue(any("9.z" in f for f in found), found)


class ConvergenceTest(unittest.TestCase):
    """국면 종결 싱크가 없는 조각 표들이라 부분 검사로 잰다."""

    def _check(self, text):
        return dag_check.check_convergence(dag_check.parse_rows(text), "partial")

    def test_expander_without_sink_is_found(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="2"),
        )
        found = self._check(text)
        self.assertTrue(any("2.z" in f for f in found), found)

    def test_descendant_not_reaching_sink_is_found(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="2"),
            row("2.2", deps="2"),
            row("2.z", kind="싱크", deps="2.1"),
        )
        found = self._check(text)
        self.assertTrue(any("2.2" in f for f in found), found)

    def test_transitive_convergence_is_accepted(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", kind="전개", signal="행/2.d/1.d/"),
            row("2.1.1", deps="2.1"),
            row("2.1.z", kind="싱크", deps="2.1.1"),
            row("2.z", kind="싱크", deps="2.1.z"),
        )
        self.assertEqual(self._check(text), [])

    def test_expander_with_no_children_yet_is_accepted(self):
        """파견 전 전개 행은 자손이 없다 — 미전개는 위반이 아니다."""
        text = table(row("2", kind="전개", signal="행/2.d/"))
        self.assertEqual(self._check(text), [])

    def test_promised_sink_of_an_unexpanded_child_is_traversed(self):
        """자식 전개가 아직 펼쳐지지 않아도 그 약속된 싱크로 수렴이 성립한다."""
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.5", kind="전개", deps="2", signal="행/2.d/5.d/"),
            row("2.z", kind="싱크", deps="2.5.z"),
        )
        self.assertEqual(self._check(text), [])


class TopLevelConvergenceTest(unittest.TestCase):
    """최상위 층의 수렴. 0번 행이 까는 층이며 그 층을 소유한 전개 행은 파견표에 없다."""

    def test_top_level_orphan_is_found(self):
        text = table(
            row("1", signal="기준선.md"),
            row("2", kind="전개", deps="1", signal="행/2.d/"),
            row("2.1", deps="2"),
            row("2.z", kind="싱크", deps="2.1"),
            row("3", deps="1"),  # 아무도 기다리지 않는다
            row("z", kind="싱크", deps="2.z"),
        )
        found = dag_check.check_convergence(dag_check.parse_rows(text))
        self.assertTrue(any("행 3" in f and "z" in f for f in found), found)

    def test_top_level_chain_reaching_the_phase_sink_is_clean(self):
        """행_0.md 초판의 형태. 전개 2는 아직 펼쳐지지 않았다."""
        text = table(
            row("1", signal="기준선.md"),
            row("g1", kind="게이트", deps="1"),
            row("2", kind="전개", deps="g1", signal="행/2.d/"),
            row("z", kind="싱크", deps="2.z"),
        )
        self.assertEqual(dag_check.check_convergence(dag_check.parse_rows(text)), [])

    def test_table_without_a_phase_sink_is_allowed_while_partial(self):
        """표를 쓰는 도중에는 최상위 수렴점이 아직 없을 수 있다."""
        text = table(row("1"), row("2", deps="1"))
        rows = dag_check.parse_rows(text)
        self.assertEqual(dag_check.check_convergence(rows, "partial"), [])

    def test_table_without_a_phase_sink_is_found_when_driving(self):
        """오케가 소비하는 표에 수렴점이 없으면 종결이 서지 않는다."""
        text = table(row("1"), row("2", deps="1"))
        found = dag_check.check_convergence(dag_check.parse_rows(text))
        self.assertTrue(any("국면 종결 싱크가 없다" in f for f in found), found)

    def test_two_phase_sinks_are_found(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("z", kind="싱크", deps="2.z"),
            row("z2", kind="싱크", deps="2.z"),
        )
        found = dag_check.check_convergence(dag_check.parse_rows(text))
        self.assertTrue(any("둘 이상" in f for f in found), found)

    def test_completed_expander_without_its_sink_is_found(self):
        """서브트리를 약속(완료 신호가 디렉토리)하고 `완`이 된 전개 — 그 약속이 사라졌다."""
        text = table(
            row("2", kind="전개", signal="행/2.d/", state="완"),
            row("z", kind="싱크", deps="2.z"),
        )
        found = dag_check.check_convergence(dag_check.parse_rows(text))
        self.assertTrue(any("2.z" in f and "만들지 않았다" in f for f in found), found)

    def test_completed_expander_that_lays_siblings_is_clean(self):
        """수리·재검 전개는 자식을 형제로 깐다 — 서브트리도 자기 싱크도 갖지 않는다.

        완료 신호가 파일이면 서브트리를 약속하지 않은 것이다.
        """
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="2"),
            row("2.2", kind="전개", deps="2.1", signal="행/2.d/2-보고.md", state="완"),
            row("2.3", deps="2.2"),
            row("2.z", kind="싱크", deps="2.2, 2.3"),
            row("z", kind="싱크", deps="2.z"),
        )
        self.assertEqual(dag_check.check_convergence(dag_check.parse_rows(text)), [])

    def test_unfinished_expander_without_children_is_still_clean(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("z", kind="싱크", deps="2.z"),
        )
        self.assertEqual(dag_check.check_convergence(dag_check.parse_rows(text)), [])


class ParentExistenceTest(unittest.TestCase):
    """마디 있는 행의 부모가 표에 있는가.

    부모 없는 서브트리는 ⑤의 두 모집단 어디에도 들지 않는다.
    """

    def test_an_orphan_subtree_is_found(self):
        text = table(
            row("3.1", signal="행/3.d/1-보고.md"),  # 행 3이 없다
            row("z", kind="싱크", brief="행/z.md", signal="행/z-결산.md"),
        )
        found = dag_check.check_convergence(dag_check.parse_rows(text))
        self.assertTrue(any("3.1" in f and "부모 3" in f for f in found), found)

    def test_an_orphan_escapes_every_other_axis(self):
        """국면 싱크가 `완`이고 고아 `3.1`이 미착수인 표는 ⑤ 밖의 어느 축에도 걸리지 않는다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "행" / "3.d").mkdir(parents=True)
            for rel in ["행/3.d/1.md", "행/z.md", "행/z-결산.md"]:
                (run_dir / rel).write_text(
                    "---\n유형: 결산\n단계: 종결\n---\nx\n", encoding="utf-8"
                )
            text = table(
                row("3.1", brief="행/3.d/1.md", signal="행/3.d/1-보고.md"),
                row("z", kind="싱크", brief="행/z.md", signal="행/z-결산.md", state="완"),
            )
            found = dag_check.run(text, run_dir)
            self.assertTrue(any("부모 3" in f for f in found), found)

    def test_a_grandchild_wants_its_own_parent(self):
        """`2.5.1`의 부모는 `2`가 아니라 `2.5`다."""
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.5.1", deps="2"),
            row("2.z", kind="싱크", deps="2.5.1"),
        )
        found = dag_check.check_convergence(dag_check.parse_rows(text), "partial")
        self.assertTrue(any("부모 2.5" in f for f in found), found)

    def test_a_sink_of_an_existing_expander_is_clean(self):
        """`2.z`의 부모는 `2`다 — 정상 형태를 발견으로 세우지 않는다."""
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="2"),
            row("2.z", kind="싱크", deps="2.1"),
            row("z", kind="싱크", deps="2.z"),
        )
        self.assertEqual(dag_check.check_convergence(dag_check.parse_rows(text)), [])

    def test_top_level_rows_have_no_parent(self):
        text = table(
            row("1"),
            row("g1", kind="게이트", deps="1"),
            row("2", kind="전개", deps="g1", signal="행/2.d/"),
            row("z", kind="싱크", deps="2.z"),
        )
        self.assertEqual(dag_check.check_convergence(dag_check.parse_rows(text)), [])


class SubmittedStateTest(unittest.TestCase):
    """`상신중` — 상신이 메인에 올라가 있는 행. 수확은 끝났고 하류는 아직 막혀 있다."""

    def test_it_is_in_the_closed_list(self):
        self.assertIn("상신중", dag_check.STATES)
        self.assertNotIn("상신중", dag_check.DONE_STATES)

    def test_it_blocks_the_downstream_from_being_ready(self):
        """ready 판정은 선행이 `완`·`비준`인 것이다 — `상신중`은 둘 중 어느 것도 아니다."""
        text = table(
            row("1", brief="행/1.md", signal="행/1-보고.md", state="상신중"),
            row("2", brief="행/2.md", deps="1", signal="행/2-보고.md", model="opus"),
        )
        self.assertEqual(dag_check.check_drive(dag_check.parse_rows(text)), [])

    def test_its_completion_signal_is_not_yet_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(row("1", signal="기준선.md", state="상신중"))
            self.assertEqual(dag_check.check_signals(dag_check.parse_rows(text), Path(tmp)), [])


class WriterScopeTest(unittest.TestCase):
    """partial의 서브트리 제외 — 쓰이는 중인 표에 두 번째 필자가 붙지 않게 한다."""

    LIVE = table(
        row("2", kind="전개", brief="행/2.md", signal="행/2.d/", state="진행"),
        row("2.1", brief="행/2.d/1.md", signal="행/2.d/1-보고.md"),
        row("3", kind="전개", brief="행/3.md", signal="행/3.d/", state="진행"),
        row("3.1", brief="행/3.d/1.md", signal="행/3.d/1-보고.md"),
        row("z", kind="싱크", brief="행/z.md", deps="2.z, 3.z", signal="행/z-결산.md"),
    )

    def _rows(self):
        return dag_check.parse_rows(self.LIVE)

    def test_a_live_expander_subtree_is_excluded(self):
        """자식 하나를 등재하고 자기 싱크를 등재하기 전의 구간은 발견을 내지 않는다."""
        rows = self._rows()
        hidden = dag_check.hidden_rows(rows, "partial")
        self.assertEqual(hidden, {"2", "2.1", "3", "3.1"})
        self.assertEqual(dag_check.check_convergence(rows, "partial", hidden), [])

    def test_without_the_exclusion_the_same_table_is_found(self):
        """제외를 끄면 같은 표가 발견을 낸다."""
        found = dag_check.check_convergence(self._rows(), "partial")
        self.assertTrue(any("2.z" in f for f in found), found)

    # 제외된 행이 남의 선행으로 지목되는 형태. `2.z`가 실제 행이라 제외 대상에 들고,
    # 국면 싱크 `z`가 그것을 지목한다. `LIVE`로는 이 자리를 재지 못한다 — 거기서
    # `2.z`는 등재된 행이 아니라 전개가 약속한 싱크라 제외 대상이 아니다.
    NAMED = table(
        row("2", kind="전개", brief="행/2.md", signal="행/2.d/", state="진행"),
        row("2.1", brief="행/2.d/1.md", deps="2", signal="행/2.d/1-보고.md"),
        row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2.1", signal="행/2.d/z-결산.md"),
        row("z", kind="싱크", brief="행/z.md", deps="2.z", signal="행/z-결산.md"),
    )

    def test_an_excluded_row_still_exists_for_others(self):
        """제외는 발견의 억제이지 행의 삭제가 아니다 — 제외된 `2.z`는 `z`의 선행으로 실재한다."""
        rows = dag_check.parse_rows(self.NAMED)
        hidden = dag_check.hidden_rows(rows, "partial")
        self.assertIn("2.z", hidden, "제외 대상이 남의 선행이어야 이 시험이 함정을 잰다")
        self.assertEqual(dag_check.check_closure(rows, hidden), [])

    def test_the_writer_sees_its_own_subtree(self):
        rows = self._rows()
        hidden = dag_check.hidden_rows(rows, "partial", writer="2")
        self.assertEqual(hidden, {"3", "3.1"})
        found = dag_check.check_convergence(rows, "partial", hidden)
        self.assertTrue(any("전개 2에 싱크 2.z가 없다" in f for f in found), found)
        self.assertFalse(any("3" in f for f in found), found)

    def test_drive_excludes_nothing(self):
        self.assertEqual(dag_check.hidden_rows(self._rows(), "drive"), set())
        self.assertEqual(dag_check.hidden_rows(self._rows(), "drive", writer="2"), set())

    def test_a_finished_expander_is_not_excluded(self):
        text = table(
            row("2", kind="전개", signal="행/2.d/", state="완"),
            row("z", kind="싱크", deps="2.z"),
        )
        self.assertEqual(dag_check.hidden_rows(dag_check.parse_rows(text), "partial"), set())

    def test_the_report_names_the_excluded_subtrees(self):
        """무발견 문면은 재지 않은 것을 열거하지 않는다 — 제외도 같은 규율이다."""
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "행").mkdir()
            for rel in ["행/2.md", "행/2.d/1.md", "행/3.md", "행/3.d/1.md", "행/z.md"]:
                (run_dir / rel).parent.mkdir(parents=True, exist_ok=True)
                (run_dir / rel).write_text("x", encoding="utf-8")
            (run_dir / "파견표.md").write_text(self.LIVE, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = dag_check.main(
                    ["--table", str(run_dir / "파견표.md"), "--mode", "partial", "--writer", "2"]
                )
            self.assertEqual(code, 1, out.getvalue())  # 필자 자신의 미완 싱크는 보인다
            self.assertTrue(any("2.z" in ln for ln in out.getvalue().splitlines()))

    def test_the_clean_report_does_not_claim_the_deferred_gate_checks(self):
        """partial의 ⑧은 완결분의 축자·상태만 본다 — 나머지 둘은 drive 전용이다."""
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "행").mkdir()
            (run_dir / "행" / "2.md").write_text("x", encoding="utf-8")
            (run_dir / "파견표.md").write_text(
                table(row("2", kind="전개", brief="행/2.md", signal="행/2.d/", state="진행")),
                encoding="utf-8",
            )
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                dag_check.main(["--table", str(run_dir / "파견표.md"), "--mode", "partial"])
            text = out.getvalue()
            self.assertIn("무발견 (partial:", text)
            self.assertIn("게이트 결정(완결분 축자·상태)", text)
            self.assertIn("제외 서브트리 2", text)
            self.assertNotIn("·운전", text)

    def test_writer_outside_partial_is_refused(self):
        """조용히 무시하면 부르는 쪽은 자기를 밝혔다고 믿는다."""
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                dag_check.main(["--table", str(Path(tmp) / "파견표.md"), "--writer", "2"])


class CycleTest(unittest.TestCase):
    def test_cycle_is_found(self):
        text = table(row("1", deps="2"), row("2", deps="1"))
        found = dag_check.check_cycle(dag_check.parse_rows(text))
        self.assertTrue(found)
        self.assertIn("순환", found[0])

    def test_acyclic_is_clean(self):
        text = table(row("1"), row("2", deps="1"), row("3", deps="2"))
        self.assertEqual(dag_check.check_cycle(dag_check.parse_rows(text)), [])

    def test_hidden_subtree_cycle_is_suppressed(self):
        """제외된 행이 낸 간선은 검사 그래프에 들지 않는다."""
        rows = dag_check.parse_rows(
            table(
                row("2", kind="전개", brief="행/2.md", signal="행/2.d/", state="진행"),
                row("2.1", brief="행/2.d/1.md", deps="2.2"),
                row("2.2", brief="행/2.d/2.md", deps="2.1"),
            )
        )
        hidden = dag_check.hidden_rows(rows, "partial")
        self.assertEqual(hidden, {"2", "2.1", "2.2"})
        self.assertEqual(dag_check.check_cycle(rows, hidden), [])

    def test_writer_self_check_still_sees_its_own_cycle(self):
        """제외에서 빠진 서브트리의 순환은 그 전개가 자기검사로 잡는다."""
        rows = dag_check.parse_rows(
            table(
                row("2", kind="전개", brief="행/2.md", signal="행/2.d/", state="진행"),
                row("2.1", brief="행/2.d/1.md", deps="2.2"),
                row("2.2", brief="행/2.d/2.md", deps="2.1"),
            )
        )
        hidden = dag_check.hidden_rows(rows, "partial", writer="2")
        self.assertEqual(hidden, set())
        found = dag_check.check_cycle(rows, hidden)
        self.assertTrue(any("순환" in f for f in found), found)

    def test_edge_into_a_hidden_row_does_not_close_a_cycle(self):
        """제외된 행은 남의 선행으로는 실재하되 간선을 내지 않는다."""
        rows = dag_check.parse_rows(
            table(
                row("2", kind="전개", brief="행/2.md", signal="행/2.d/", state="진행", deps="1"),
                row("1", brief="행/1.md", deps="2"),
            )
        )
        hidden = dag_check.hidden_rows(rows, "partial")
        self.assertIn("2", hidden)
        self.assertEqual(dag_check.check_cycle(rows, hidden), [])


class SettlementStageContractTest(unittest.TestCase):
    """단계 원장의 값 목록은 코드와 서식이 같은 것을 말해야 한다 — 재개의 유일한 근거다."""

    SINK_DOC = SCRIPTS.parent / "계약" / "싱크.md"

    # 원장은 싱크 종류마다 하나다. (표 머리, 값 순서)의 짝으로 함께 시험한다.
    LEDGERS = (
        ("| 단계 값 (노드 싱크) |", "NODE_SETTLEMENT_STAGES"),
        ("| 단계 값 (국면 종결 싱크) |", "PHASE_SETTLEMENT_STAGES"),
    )

    def _doc(self) -> str:
        return self.SINK_DOC.read_text(encoding="utf-8")

    def test_settled_ends_both_ledgers(self):
        self.assertEqual(dag_check.SETTLED, dag_check.NODE_SETTLEMENT_STAGES[-1])
        self.assertEqual(dag_check.SETTLED, dag_check.PHASE_SETTLEMENT_STAGES[-1])

    def test_every_stage_appears_in_the_sink_contract(self):
        text = self._doc()
        for _, attr in self.LEDGERS:
            for stage in getattr(dag_check, attr):
                self.assertIn(stage, text, f"단계 '{stage}'가 계약/싱크.md에 없다")

    def test_each_stage_table_lists_them_in_declared_order(self):
        """단계 표의 순서가 곧 재개 순서다. 표는 싱크 종류마다 하나다."""
        text = self._doc()
        for heading, attr in self.LEDGERS:
            with self.subTest(ledger=attr):
                start = text.index(heading)
                block = text[start:text.index("\n\n", start)]
                # 여는 백틱까지만 찾는다 — 두 커밋 값은 뒤에 `<SHA>`를 달고,
                # `격리커밋완료`는 `커밋완료`를 꼬리로 품는다.
                positions = [block.index(f"`{s}") for s in getattr(dag_check, attr)]
                self.assertEqual(positions, sorted(positions), block)

    def test_the_two_ledgers_order_commit_and_reclaim_differently(self):
        """원장을 둘로 두는 이유. 뭉치면 재개가 이미 끝난 행위로 되돌아간다."""
        node = dag_check.NODE_SETTLEMENT_STAGES
        phase = dag_check.PHASE_SETTLEMENT_STAGES
        self.assertLess(node.index("커밋완료"), node.index("회수완료"))
        self.assertLess(phase.index("회수완료"), phase.index("커밋완료"))

    def test_the_judgment_stage_precedes_the_first_irreversible_act(self):
        """`판정완료`가 첫 비가역 행위 앞에 선다 — 노드 싱크는 worktree 커밋, 국면 종결 싱크는 sweep."""
        text = self._doc()
        node_section = text.index("## 노드 싱크")
        phase_section = text.index("## 국면 종결 싱크")
        node = text[node_section:phase_section]
        phase = text[phase_section:]
        self.assertLess(node.index("단계: 판정완료"), node.index("격리커밋완료"))
        self.assertLess(phase.index("단계: 판정완료"), phase.index("sweep --phase"))

    def test_each_procedure_records_its_stages_in_the_declared_order(self):
        """절차 문면의 기입 순서가 선언한 원장 순서와 같아야 한다 — 갈라지면 재개가 되돌아간다."""
        text = self._doc()
        node_section = text.index("## 노드 싱크")
        phase_section = text.index("## 국면 종결 싱크")
        sections = (
            (text[node_section:phase_section], "NODE_SETTLEMENT_STAGES"),
            (text[phase_section:], "PHASE_SETTLEMENT_STAGES"),
        )
        for section, attr in sections:
            with self.subTest(ledger=attr):
                written = [section.index(f"단계: {s}") for s in getattr(dag_check, attr)]
                self.assertEqual(written, sorted(written), attr)

    def test_sink_uses_common_return_words_and_keeps_detailed_statuses(self):
        text = self._doc()
        for word in ("귀속불일치", "완료미충족", "병합충돌", "계약이동", "대기"):
            self.assertIn(word, text)
        self.assertIn("첫 줄에 `DONE`·`DONE-비준`·`상신`·", text)
        self.assertIn("`예외` 중 하나만 쓴다", text)

    def test_settlement_status_extends_the_common_return_word(self):
        text = self._doc()
        self.assertIn("상세 결과는 결산", text)
        self.assertIn("`상태:`에만 기록한다", text)

    def test_attribution_mismatch_is_closed_in_the_fact_and_common_contract(self):
        fact = (SCRIPTS.parent / "전거" / "의무.md").read_text(encoding="utf-8")
        common = (SCRIPTS.parent / "계약" / "공통.md").read_text(encoding="utf-8")
        for text in (fact, common):
            self.assertIn("결산 상태를 `귀속불일치`로 쓴다", text)
            self.assertIn("반환 첫 줄은 `예외`다", text)
            self.assertNotIn("`DONE`이 아닌 낱말로 반환한다", text)


class ClaudeDispatchPromptContractTest(unittest.TestCase):
    """Claude 일반 파견과 0번 파견은 경로 뒤에 실행 지시를 함께 보낸다."""

    TABLE = SCRIPTS.parent / "대응표.md"
    PATH_LINE = "파견문: <절대 경로>"
    EXECUTION_LINE = "이 파일 전문을 읽고 임무를 실행한다. 반환은 파견문의 반환 서식을 따른다."

    def _doc(self) -> str:
        return self.TABLE.read_text(encoding="utf-8")

    def test_general_claude_dispatch_has_path_and_execution_instruction(self):
        text = self._doc()
        start = text.index("**2.**")
        block = text[start:text.index("**3.**", start)]
        claude_row = next(line for line in block.splitlines() if "`파견`·`전개`" in line)
        self.assertIn(self.PATH_LINE, claude_row)
        self.assertIn(self.EXECUTION_LINE, claude_row)

    def test_row_zero_dispatch_has_path_and_execution_instruction(self):
        text = self._doc()
        start = text.index("**0.**")
        block = text[start:text.index("**0.5.**", start)]
        self.assertIn(self.PATH_LINE, block)
        self.assertIn(self.EXECUTION_LINE, block)

    def test_sink_return_is_checked_before_state_mapping(self):
        text = self._doc()
        start = text.index("**4.**")
        block = text[start:text.index("**5.**", start)]
        check = block.index("--sink-return <행번호> <첫 낱말>")
        mapping = block.index("| `DONE` |")
        self.assertLess(check, mapping)

    def test_external_budget_cannot_close_or_shorten_the_phase(self):
        table = self._doc()
        skill = (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8")
        for text in (table, skill):
            self.assertIn("비용·시간·토큰 상한", text)
            self.assertIn("국면을", text)
        self.assertIn("국면을 활성 상태로 두고", skill)

    def test_row_zero_resolves_user_relative_paths_from_repo_root(self):
        row_zero = (SCRIPTS.parent / "행_0.md").read_text(encoding="utf-8")
        self.assertIn("상대 경로는 저장소 루트 기준으로 해소한다", row_zero)
        self.assertIn("런 디렉토리 기준으로 붙이지 않는다", row_zero)

    def test_byte_counts_must_be_measured_from_the_file(self):
        common = (SCRIPTS.parent / "계약" / "공통.md").read_text(encoding="utf-8")
        skill = (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("파일의 바이트 수는 파일시스템이나 파일 바이트를 읽는 명령으로 잰다", common)
        self.assertIn("종결 보고의 바이트 수와 계수는 실물에서 다시 측정한다", skill)


class CodexDispatchPathContractTest(unittest.TestCase):
    """Codex 셸 명령이 다루는 런 디렉토리 파일은 절대 경로로 넘긴다."""

    FORM = SCRIPTS.parent / "references" / "배정.md"

    def _section(self) -> str:
        text = self.FORM.read_text(encoding="utf-8")
        return text[text.index("### Codex 일반 파견"):]

    def test_initial_dispatch_and_wait_use_absolute_run_paths(self):
        section = self._section()
        self.assertIn(
            "- < <파견문 절대 경로> > <반환 절대 경로> 2> <로그 절대 경로>",
            section,
        )
        self.assertIn(
            "wait_outputs.py <반환 절대 경로 ...>",
            section,
        )

    def test_resume_dispatch_uses_absolute_run_paths(self):
        section = self._section()
        self.assertIn(
            "- < <재개 지시문 절대 경로> > <재개 반환 절대 경로> "
            "2> <재개 로그 절대 경로>",
            section,
        )


class SignalTest(unittest.TestCase):
    def test_done_row_without_signal_file_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            text = table(row("1", signal="기준선.md", state="완"))
            found = dag_check.check_signals(dag_check.parse_rows(text), run_dir)
            self.assertTrue(any("기준선.md" in f for f in found), found)

    def test_done_row_with_signal_file_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "기준선.md").write_text("x", encoding="utf-8")
            text = table(row("1", signal="기준선.md", state="완"))
            self.assertEqual(dag_check.check_signals(dag_check.parse_rows(text), run_dir), [])

    def test_unfinished_row_is_not_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(row("1", signal="기준선.md", state="진행"))
            self.assertEqual(dag_check.check_signals(dag_check.parse_rows(text), Path(tmp)), [])


    def test_ratified_row_is_checked_like_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(row("1", signal="기준선.md", state="비준"))
            found = dag_check.check_signals(dag_check.parse_rows(text), Path(tmp))
            self.assertTrue(found, found)

    def test_zero_byte_signal_is_found(self):
        """실재는 충족이 아니다 — 소멸한 에이전트가 남긴 껍데기를 통과시키지 않는다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "기준선.md").write_text("", encoding="utf-8")
            text = table(row("1", signal="기준선.md", state="완"))
            found = dag_check.check_signals(dag_check.parse_rows(text), run_dir)
            self.assertTrue(any("기준선.md" in f for f in found), found)

    def test_empty_directory_signal_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "행" / "2.d").mkdir(parents=True)
            text = table(row("2", kind="전개", signal="행/2.d/", state="완"))
            found = dag_check.check_signals(dag_check.parse_rows(text), run_dir)
            self.assertTrue(any("2.d" in f for f in found), found)

    def test_completed_legacy_directory_signal_with_content_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            d = run_dir / "행" / "2.d"
            d.mkdir(parents=True)
            (d / "1.md").write_text("x", encoding="utf-8")
            text = table(row("2", kind="전개", signal="행/2.d/", state="완"))
            self.assertEqual(dag_check.check_signals(dag_check.parse_rows(text), run_dir), [])


class VerificationRunArtifactTest(unittest.TestCase):
    """검증런의 DONE은 동결·장부·종료보고와 라운드 1 장부 구조를 전건 요구한다."""

    SIGNAL = "행/1.d/종료보고.md"

    def _run_dir(self, tmp: str, *, ledger: str | None = None) -> Path:
        run_dir = Path(tmp)
        (run_dir / "행" / "1.d").mkdir(parents=True)
        body = valid_brief_body(run_dir).replace(
            CONTRACT_LINE,
            f"- 계약: {CONTRACT} · {VERIFY_CONTRACT}\n",
        )
        (run_dir / "행" / "1.md").write_text(body, encoding="utf-8")
        (run_dir / self.SIGNAL).write_text("# 종료보고\n", encoding="utf-8")
        if ledger is not None:
            (run_dir / "행" / "1.d" / "동결.md").write_text("# 동결\n", encoding="utf-8")
            (run_dir / "행" / "1.d" / "장부.md").write_text(ledger, encoding="utf-8")
        return run_dir

    def _rows(self):
        return dag_check.parse_rows(table(
            row("1", brief="행/1.md", signal=self.SIGNAL, state="완"),
        ))

    def test_a_run_with_only_the_final_report_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = dag_check.check_signals(self._rows(), self._run_dir(tmp))
            self.assertTrue(any("동결.md" in item for item in found), found)
            self.assertTrue(any("장부.md" in item for item in found), found)

    def test_three_canonical_files_and_round_one_ledger_are_clean(self):
        ledger = "# 검증 장부\n\n## 라운드 1 — 본표\n\n| ID | 상태 |\n|---|---|\n\n## 라운드 1 — 결산\n\n- 합 0\n"
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, ledger=ledger)
            self.assertEqual(dag_check.check_signals(self._rows(), run_dir), [])

    def test_round_one_table_and_settlement_are_both_required(self):
        cases = (
            ("# 검증 장부\n\n## 라운드 1 — 결산\n", "본표"),
            ("# 검증 장부\n\n## 라운드 1 — 본표\n", "결산"),
        )
        for ledger, missing in cases:
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as tmp:
                found = dag_check.check_signals(
                    self._rows(), self._run_dir(tmp, ledger=ledger)
                )
                self.assertTrue(any(missing in item for item in found), found)


class DiscoveryFollowupTest(unittest.TestCase):
    """검증런 종료보고에 발견이 있으면 같은 층에 그 종료보고를 정본으로 싣는 전개가 있어야 한다."""

    SIGNAL = "행/1.d/종료보고.md"
    LEDGER = "# 검증 장부\n\n## 라운드 1 — 본표\n\n| ID | 상태 |\n|---|---|\n\n## 라운드 1 — 결산\n\n- 합 0\n"

    def _run_dir(self, tmp: str, report: str, *, reviewer: str | None) -> Path:
        run_dir = Path(tmp)
        (run_dir / "행" / "1.d").mkdir(parents=True)
        body = valid_brief_body(run_dir).replace(
            CONTRACT_LINE, f"- 계약: {CONTRACT} · {VERIFY_CONTRACT}\n"
        )
        (run_dir / "행" / "1.md").write_text(body, encoding="utf-8")
        (run_dir / "행" / "1.d" / "동결.md").write_text("# 동결\n", encoding="utf-8")
        (run_dir / "행" / "1.d" / "장부.md").write_text(self.LEDGER, encoding="utf-8")
        (run_dir / self.SIGNAL).write_text(report, encoding="utf-8")
        if reviewer is not None:
            (run_dir / "행" / "2.md").write_text(
                valid_brief_body(run_dir) + f"- 정본: {reviewer}\n", encoding="utf-8"
            )
        return run_dir

    def _rows(self, with_reviewer: bool):
        rows = [row("1", brief="행/1.md", signal=self.SIGNAL, state="완")]
        if with_reviewer:
            rows.append(row("2", kind="전개", brief="행/2.md", deps="1", signal="행/2-보고.md", model="opus med"))
        return dag_check.parse_rows(table(*rows))

    REPORT = "# 종료보고\n\n## 9. 운영 기록\n\n없음\n\n## 발견\n\n- R1-25 수량 기록 자리가 없다\n\n## 운영 기록 요지\n\n없음\n"

    def test_discovery_without_reviewer_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, self.REPORT, reviewer=None)
            found = dag_check.check_signals(self._rows(False), run_dir)
            self.assertTrue(any("검토전개" in item and "1건" in item for item in found), found)

    def test_discovery_with_reviewer_in_same_scope_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, self.REPORT, reviewer=str(Path(tmp) / "행" / "1.d" / "종료보고.md"))
            found = dag_check.check_signals(self._rows(True), run_dir)
            self.assertEqual([item for item in found if "검토전개" in item], [], found)

    def test_no_discovery_needs_no_reviewer(self):
        report = "# 종료보고\n\n## 발견\n\n없음\n"
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, report, reviewer=None)
            found = dag_check.check_signals(self._rows(False), run_dir)
            self.assertEqual([item for item in found if "검토전개" in item], [], found)

    def test_discovery_count_reads_only_the_section(self):
        self.assertEqual(dag_check._discovery_count(self.REPORT), 1)
        self.assertEqual(dag_check._discovery_count("## 발견\n\n없음\n"), 0)
        self.assertEqual(dag_check._discovery_count("## 10. 발견\n- a\n- b\n## 다음\n- c\n"), 2)
        self.assertEqual(dag_check._discovery_count("# 종료보고\n본문\n"), 0)


class ShapeTest(unittest.TestCase):
    """칸 수가 어긋난 행은 사라지지 않고 발견으로 남는다."""

    def test_well_formed_row_is_clean(self):
        self.assertEqual(dag_check.check_shape(table(row("2.1", deps="2"))), [])

    def test_row_missing_a_column_is_found(self):
        text = HEAD + "| 2.2 | 파견 | 행/2.d/2.md | 2 | b.md | 미착수 |\n"
        found = dag_check.check_shape(text)
        self.assertTrue(any("2.2" in f for f in found), found)

    def test_row_with_an_extra_column_is_found(self):
        text = HEAD + "| 2.3 | 파견 | 행/2.d/3.md | 2 | c.md | opus low | 미착수 | 비고 |\n"
        found = dag_check.check_shape(text)
        self.assertTrue(any("2.3" in f for f in found), found)

    def test_header_separator_and_prose_are_not_rows(self):
        text = HEAD + "\n대상: 파이프가 없는 산문\n\n<!-- 행 끝 -->\n"
        self.assertEqual(dag_check.check_shape(text), [])

    def test_blank_row_number_is_found(self):
        text = HEAD + "|  | 파견 | 행/2.d/2.md | 2 | b.md | opus low | 미착수 |\n"
        self.assertTrue(dag_check.check_shape(text))

    def test_row_number_written_as_nothing_is_found(self):
        """`—`·`-`·`–`·`없음`은 전부 빈 행 번호다 — `_cell`이 같게 뭉갠다."""
        for token in ["—", "-", "–", "없음", "``"]:
            text = HEAD + f"| {token} | 파견 | 행/2.d/2.md | 2 | b.md | opus low | 미착수 |\n"
            self.assertTrue(dag_check.check_shape(text), f"토큰 {token!r}")

    def test_separator_line_is_still_not_a_row(self):
        """구분선은 전 칸이 대시다 — 첫 칸만 대시인 행과 구별된다."""
        for sep in ["|---|---|---|---|---|---|---|", "|:--|---|--:|---|---|---|---|"]:
            self.assertEqual(dag_check.check_shape(HEAD + sep + "\n"), [], sep)

    def test_blank_row_number_does_not_hide_its_own_violation(self):
        """번호가 빈 자식 행은 부모 서브트리를 탈출한다 — 탈출 자체가 발견이다."""
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="2"),
            row("—", deps="2"),  # 원래 2.2였어야 하는 행
            row("2.z", kind="싱크", deps="2.1"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            found = dag_check.run(text, Path(tmp))
            self.assertTrue(any("행 번호가 비어 있다" in f for f in found), found)

    def test_malformed_row_does_not_hide_its_own_violation(self):
        """훼손 행이 진 위반이 행과 함께 사라지지 않는다."""
        text = table(
            row("2", kind="전개", signal="행/2.d/"),
            row("2.1", deps="2"),
            "| 2.2 | 파견 | 행/2.d/2.md | 2 | b.md | 미착수 |\n",
            row("2.z", kind="싱크", deps="2.1"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            found = dag_check.run(text, Path(tmp))
            self.assertTrue(any("행 2.2의 칸이 6개다" in f for f in found), found)


class MultiSignalTest(unittest.TestCase):
    def test_every_listed_signal_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "기준선.md").write_text("x", encoding="utf-8")
            (run_dir / "결정").mkdir()
            (run_dir / "결정" / "1.md").write_text("y", encoding="utf-8")
            text = table(row("1", signal="기준선.md, 결정/1.md", state="완"))
            self.assertEqual(dag_check.check_signals(dag_check.parse_rows(text), run_dir), [])

    def test_missing_one_of_several_signals_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "기준선.md").write_text("x", encoding="utf-8")
            text = table(row("1", signal="기준선.md, 결정/1.md", state="완"))
            found = dag_check.check_signals(dag_check.parse_rows(text), run_dir)
            self.assertTrue(any("결정/1.md" in f for f in found), found)
            self.assertFalse(any("기준선.md" in f for f in found), found)


class BriefTest(unittest.TestCase):
    def test_missing_brief_file_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(row("1", brief="행/1.md"))
            found = dag_check.check_briefs(dag_check.parse_rows(text), Path(tmp))
            self.assertTrue(any("행/1.md" in f for f in found), found)

    def test_existing_brief_file_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "행").mkdir()
            (run_dir / "행" / "1.md").write_text(
                valid_brief_body(run_dir), encoding="utf-8"
            )
            text = table(row("1", brief="행/1.md"))
            self.assertEqual(dag_check.check_briefs(dag_check.parse_rows(text), run_dir), [])

    def test_row_without_a_brief_is_not_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(row("g1", kind="게이트", brief="—"))
            self.assertEqual(dag_check.check_briefs(dag_check.parse_rows(text), Path(tmp)), [])


class ContractSlotTest(unittest.TestCase):
    """⑦의 계약 축 — 슬롯의 존재와 좌표의 실재까지 본다.

    역할에 맞는 계약이 실렸는지는 보지 않는다 — 파견표가 역할을 담지 않는다
    (`KINDS`는 넷, `references/서식.md` 「계약 자산」 표의 파견 대상 줄은 일곱).
    """

    def _found(self, body: str, run_dir: Path, state: str = "미착수") -> list[str]:
        """계약 축만 흔든다 — 배정 근거는 언제나 채워 둔다."""
        (run_dir / "행").mkdir(exist_ok=True)
        valid = valid_brief_body(run_dir).replace(CONTRACT_LINE, "")
        (run_dir / "행" / "1.md").write_text(body + valid, encoding="utf-8")
        text = table(row("1", brief="행/1.md", state=state))
        return dag_check.check_briefs(dag_check.parse_rows(text), run_dir)

    def test_brief_without_the_slot_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found("- 정본: 어디\n", Path(tmp))
            self.assertTrue(any("`계약:` 슬롯이 없다" in f for f in found), found)

    def test_empty_slot_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found("- 계약:\n", Path(tmp))
            self.assertTrue(any("`계약:` 슬롯이 없다" in f for f in found), found)

    def test_absolute_coordinate_that_exists_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._found(CONTRACT_LINE, Path(tmp)), [])

    def test_missing_coordinate_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found("- 계약: 계약/없는것.md\n", Path(tmp))
            self.assertTrue(any("실재하지 않는다" in f for f in found), found)

    def test_completed_legacy_lens_contracts_are_historical(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = "- 계약: 계약/판정.md, 계약/렌즈.md\n"
            self.assertEqual(self._found(body, Path(tmp), state="완"), [])

    def test_unfinished_legacy_lens_contracts_are_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = "- 계약: 계약/판정.md, 계약/렌즈.md\n"
            found = self._found(body, Path(tmp))
            self.assertEqual(len(found), 2, found)

    def test_other_missing_contract_stays_invalid_when_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found("- 계약: 계약/없는것.md\n", Path(tmp), state="완")
            self.assertTrue(any("실재하지 않는다" in f for f in found), found)

    def test_every_listed_coordinate_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "계약").mkdir()
            (run_dir / "계약" / "있는것.md").write_text("x", encoding="utf-8")
            found = self._found("- 계약: 계약/있는것.md · 계약/없는것.md\n", run_dir)
            self.assertEqual(len(found), 1, found)
            self.assertIn("없는것", found[0])

    def test_a_longer_slot_name_is_not_the_contract_slot(self):
        # 콜론 앞에 낱말이 더 붙은 슬롯은 걸리지 않는다 — 정규식의 경계다.
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found("- 계약 디렉토리: /어딘가/계약\n", Path(tmp))
            self.assertTrue(any("`계약:` 슬롯이 없다" in f for f in found), found)

    def test_a_missing_brief_is_not_double_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(row("1", brief="행/1.md"))
            found = dag_check.check_briefs(dag_check.parse_rows(text), Path(tmp))
            self.assertEqual(len(found), 1, found)
            self.assertIn("파견문이 없다", found[0])


class AssignmentSlotTest(unittest.TestCase):
    """⑦의 배정 축 — 슬롯이 채워졌는지까지 본다.

    도출의 내용이 배정표 문언에 서는지는 보지 않는다. 이 검사가 막는 것은
    슬롯이 통째로 없거나 서식 그대로 남은 파견문이다.
    """

    def _found(self, body: str, run_dir: Path) -> list[str]:
        """배정 축만 흔든다 — 계약 좌표는 언제나 실재하는 것으로 채운다."""
        (run_dir / "행").mkdir(exist_ok=True)
        valid = valid_brief_body(run_dir).replace(ASSIGN_LINE, "")
        (run_dir / "행" / "1.md").write_text(valid + body, encoding="utf-8")
        text = table(row("1", brief="행/1.md"))
        return dag_check.check_briefs(dag_check.parse_rows(text), run_dir)

    def test_brief_without_the_slot_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found("- 정본: 어디\n", Path(tmp))
            self.assertTrue(any("`모델 배정 근거:` 슬롯이 없다" in f for f in found), found)

    def test_empty_slot_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found("- 모델 배정 근거:\n", Path(tmp))
            self.assertTrue(any("`모델 배정 근거:` 슬롯이 없다" in f for f in found), found)

    def test_untouched_template_is_an_empty_slot(self):
        # 서식을 그대로 복사해 온 파견문 — 도출이 없다.
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found("- 모델 배정 근거: {이 행의 모델·노력이 어떻게 도출됐는가}\n", Path(tmp))
            self.assertTrue(any("`모델 배정 근거:` 슬롯이 없다" in f for f in found), found)

    def test_a_filled_slot_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._found(ASSIGN_LINE, Path(tmp)), [])

    def test_a_deviation_derivation_is_clean(self):
        # 이탈도 도출만 실려 있으면 검산은 통과한다 — 도출의 내용은 전개 뒤 검증런의 몫이다.
        with tempfile.TemporaryDirectory() as tmp:
            body = "- 모델 배정 근거: 판단의 질이 한 컨텍스트에 달려 fable로 올린다\n"
            self.assertEqual(self._found(body, Path(tmp)), [])

    def test_a_longer_slot_name_is_not_the_assignment_slot(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found("- 모델 배정 근거 표: 서식.md\n", Path(tmp))
            self.assertTrue(any("`모델 배정 근거:` 슬롯이 없다" in f for f in found), found)


class ReturnSlotTest(unittest.TestCase):
    """⑦의 반환 축 — 공통 첫 줄과 역할 확장의 결선 자리를 요구한다."""

    def test_brief_without_the_slot_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "행").mkdir()
            body = valid_brief_body(run_dir).replace(RETURN_LINE, "")
            (run_dir / "행" / "1.md").write_text(body, encoding="utf-8")
            text = table(row("1", brief="행/1.md"))
            found = dag_check.check_briefs(dag_check.parse_rows(text), run_dir)
            self.assertTrue(any("`반환:` 슬롯이 없다" in f for f in found), found)

    def test_a_completed_legacy_brief_without_the_slot_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "행").mkdir()
            body = valid_brief_body(run_dir).replace(RETURN_LINE, "")
            (run_dir / "행" / "1.md").write_text(body, encoding="utf-8")
            (run_dir / "행" / "1-보고.md").write_text("DONE\n", encoding="utf-8")
            text = table(row("1", brief="행/1.md", signal="행/1-보고.md", state="완"))
            found = dag_check.check_briefs(dag_check.parse_rows(text), run_dir)
            self.assertEqual(found, [])


class InvariantSlotTest(unittest.TestCase):
    """⑦의 불변식 축 — 불변식 파일과 상위 승계·실제 적재를 함께 본다."""

    def _found(self, run_dir: Path, body: str, *, rid: str = "1", rows: list[str] | None = None):
        brief = run_dir / "행" / f"{rid.split('.')[-1]}.md"
        if "." in rid:
            brief = run_dir / "행"
            for part in rid.split(".")[:-1]:
                brief /= f"{part}.d"
            brief /= f"{rid.split('.')[-1]}.md"
        brief.parent.mkdir(parents=True, exist_ok=True)
        brief.write_text(CONTRACT_LINE + ASSIGN_LINE + RETURN_LINE + body, encoding="utf-8")
        table_rows = rows or [row(rid, brief=str(brief.relative_to(run_dir)).replace("\\", "/"))]
        parsed = dag_check.parse_rows(table(*table_rows))
        for other in parsed:
            if other.id == rid or not other.dispatched:
                continue
            other_brief = run_dir / other.brief
            other_brief.parent.mkdir(parents=True, exist_ok=True)
            other_brief.write_text(valid_brief_body(run_dir), encoding="utf-8")
        return dag_check.check_briefs(parsed, run_dir)

    def test_missing_slot_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = self._found(Path(tmp), "- 읽기 목록: 없음\n- 예산: 없음\n")
            self.assertTrue(any("`불변식:` 슬롯이 없다" in f for f in found), found)

    def test_missing_file_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            coord = invariant_path(run_dir)
            body = f"- 불변식: {coord}\n- 읽기 목록: {coord}\n- 예산: --files {coord}\n"
            found = self._found(run_dir, body)
            self.assertTrue(any("불변식 좌표가 파일로 실재하지 않는다" in f for f in found), found)

    def test_empty_file_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            coord = invariant_path(run_dir)
            coord.parent.mkdir(parents=True)
            coord.write_text("", encoding="utf-8")
            body = f"- 불변식: {coord}\n- 읽기 목록: {coord}\n- 예산: --files {coord}\n"
            found = self._found(run_dir, body)
            self.assertTrue(any("불변식 파일이 비어 있다" in f for f in found), found)

    def test_ancestor_invariant_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            root = invariant_path(run_dir, "0")
            parent = invariant_path(run_dir, "2")
            for coord in (root, parent):
                coord.parent.mkdir(parents=True, exist_ok=True)
                coord.write_text("x", encoding="utf-8")
            body = f"- 불변식: {root}\n- 읽기 목록: {root}\n- 예산: --files {root}\n"
            rows = [
                row("2", kind="전개", brief="행/2.md", signal="행/2-보고.md", state="진행"),
                row("2.1", brief="행/2.d/1.md", deps="2", signal="행/2.d/1-보고.md"),
            ]
            found = self._found(run_dir, body, rid="2.1", rows=rows)
            self.assertTrue(any("상위 불변식을 승계하지 않았다" in f and str(parent) in f for f in found), found)

    def test_invariant_must_be_in_read_list_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            coord = invariant_path(run_dir)
            coord.parent.mkdir(parents=True)
            coord.write_text("x", encoding="utf-8")
            found = self._found(run_dir, f"- 불변식: {coord}\n- 읽기 목록: 없음\n- 예산: 없음\n")
            self.assertTrue(any("읽기 목록" in f for f in found), found)
            self.assertTrue(any("예산" in f for f in found), found)

    def test_valid_invariant_chain_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            body = valid_brief_body(run_dir, "0", "2").replace(CONTRACT_LINE + ASSIGN_LINE, "")
            rows = [
                row("2", kind="전개", brief="행/2.md", signal="행/2-보고.md", state="진행"),
                row("2.1", brief="행/2.d/1.md", deps="2", signal="행/2.d/1-보고.md"),
            ]
            self.assertEqual(self._found(run_dir, body, rid="2.1", rows=rows), [])

    def test_invariant_outside_the_run_is_found(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
            run_dir = Path(tmp)
            coord = Path(other) / "불변식.md"
            coord.write_text("x", encoding="utf-8")
            root = invariant_path(run_dir)
            root.parent.mkdir(parents=True)
            root.write_text("x", encoding="utf-8")
            joined = f"{root} · {coord}"
            body = f"- 불변식: {joined}\n- 읽기 목록: {joined}\n- 예산: --files {joined}\n"
            found = self._found(run_dir, body)
            self.assertTrue(any("현재 런 밖" in f and str(coord) in f for f in found), found)

    def test_versioned_invariant_is_allowed_for_a_later_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            root = invariant_path(run_dir)
            revision = invariant_path(run_dir, suffix="-2")
            for coord in (root, revision):
                coord.parent.mkdir(parents=True, exist_ok=True)
                coord.write_text("x", encoding="utf-8")
            joined = f"{root} · {revision}"
            body = f"- 불변식: {joined}\n- 읽기 목록: {joined}\n- 예산: --files {joined}\n"
            self.assertEqual(self._found(run_dir, body), [])

    def test_another_subtrees_invariant_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            root = invariant_path(run_dir)
            foreign = invariant_path(run_dir, "9")
            for coord in (root, foreign):
                coord.parent.mkdir(parents=True, exist_ok=True)
                coord.write_text("x", encoding="utf-8")
            joined = f"{root} · {foreign}"
            body = f"- 불변식: {joined}\n- 읽기 목록: {joined}\n- 예산: --files {joined}\n"
            found = self._found(run_dir, body)
            self.assertTrue(any("적용 서브트리의 불변식이 아니다" in f for f in found), found)


class TableEndTest(unittest.TestCase):
    """`<!-- 행 끝 -->`까지가 행이 사는 범위다. 뒤 산문의 예시 표를 행으로 읽지 않는다."""

    AFTER = "\n\n아래는 설명용 예시다.\n\n| 9 | 파견 | | | | | |\n"

    def test_rows_after_the_sentinel_are_not_parsed(self):
        text = table(row("1", brief="행/1.md", signal="기준선.md")) + self.AFTER
        self.assertEqual([r.id for r in dag_check.parse_rows(text)], ["1"])

    def test_shape_findings_stop_at_the_sentinel(self):
        text = table(row("1", brief="행/1.md", signal="기준선.md")) + self.AFTER
        self.assertEqual(dag_check.check_shape(text), [])

    def test_a_table_without_the_sentinel_is_still_read(self):
        """센티널이 없는 표는 전문을 행 범위로 읽는다."""
        text = table(row("1", brief="행/1.md", signal="기준선.md")).replace(
            dag_check.TABLE_END, ""
        )
        self.assertEqual([r.id for r in dag_check.parse_rows(text)], ["1"])


class SettlementStageTest(unittest.TestCase):
    """완결된 싱크의 결산 단계가 `종결`인가 — 실재만으로는 어디까지 갔는지 알 수 없다."""

    SIGNAL = "행/2.d/z-결산.md"

    def _run_dir(self, tmp, stage_line, *, status="DONE"):
        run_dir = Path(tmp)
        (run_dir / "행" / "2.d").mkdir(parents=True)
        (run_dir / "행" / "2.d" / "z.md").write_text("x", encoding="utf-8")
        (run_dir / self.SIGNAL).write_text(
            f"---\n유형: 결산\n행: 2.z\n상태: {status}\n{stage_line}---\n\n## 판정\nx\n",
            encoding="utf-8",
        )
        return run_dir

    def _rows(self, state="완"):
        return dag_check.parse_rows(table(
            row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2",
                signal=self.SIGNAL, model="opus low", state=state),
        ))

    def test_settled_stage_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, "단계: 종결\n")
            self.assertEqual(dag_check.check_signals(self._rows(), run_dir), [])

    def test_a_sink_stuck_at_commit_is_found(self):
        """`커밋완료`에서 죽은 싱크의 결산도 실재하고 비어 있지 않다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, "단계: 커밋완료 abc1234\n")
            found = dag_check.check_signals(self._rows(), run_dir)
            self.assertTrue(any("커밋완료 abc1234" in f for f in found), found)

    def test_done_at_the_judgment_stage_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, "단계: 판정완료\n")
            found = dag_check.check_signals(self._rows(), run_dir)
            self.assertTrue(any("판정완료" in f for f in found), found)

    def test_done_with_an_incomplete_frontmatter_status_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, "단계: 종결\n", status="완료미충족")
            found = dag_check.check_signals(self._rows(), run_dir)
            self.assertTrue(any("완료미충족" in f for f in found), found)

    def test_return_and_frontmatter_status_mismatch_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, "단계: 종결\n", status="DONE")
            found = dag_check.check_signals(self._rows("비준"), run_dir)
            self.assertTrue(any("DONE-비준" in f for f in found), found)

    def test_a_missing_stage_key_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, "")
            found = dag_check.check_signals(self._rows(), run_dir)
            self.assertTrue(any("'없음'" in f for f in found), found)

    def test_an_unfinished_sink_is_not_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, "단계: 병합완료\n")
            self.assertEqual(dag_check.check_signals(self._rows("진행"), run_dir), [])

    def test_a_dispatch_row_signal_is_not_a_settlement(self):
        """결산 단계는 싱크의 계약이다. 파견 행의 보고에 걸지 않는다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "행").mkdir()
            (run_dir / "행" / "1-보고.md").write_text("---\n유형: 보고\n---\nx\n", encoding="utf-8")
            rows = dag_check.parse_rows(table(
                row("1", brief="행/1.md", signal="행/1-보고.md", state="완"),
            ))
            (run_dir / "행" / "1.md").write_text("x", encoding="utf-8")
            self.assertEqual(dag_check.check_signals(rows, run_dir), [])


class SinkReturnTest(unittest.TestCase):
    """오케가 받은 실제 반환 낱말을 표 상태로 바꾸기 전에 결산과 대조한다."""

    SIGNAL = "행/2.d/z-결산.md"

    def _case(self, tmp: str, *, status: str, stage: str = "판정완료"):
        run_dir = Path(tmp)
        target = run_dir / self.SIGNAL
        target.parent.mkdir(parents=True)
        target.write_text(
            f"---\n유형: 결산\n행: 2.z\n상태: {status}\n단계: {stage}\n---\n",
            encoding="utf-8",
        )
        rows = dag_check.parse_rows(table(
            row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2",
                signal=self.SIGNAL, model="opus low", state="진행"),
        ))
        return rows, run_dir

    def test_done_at_the_judgment_stage_is_found_at_return_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows, run_dir = self._case(tmp, status="DONE")
            found = dag_check.check_sink_return(rows, run_dir, "2.z", "DONE")
            self.assertTrue(any("판정완료" in item for item in found), found)

    def test_done_with_an_incomplete_status_is_found_at_return_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows, run_dir = self._case(tmp, status="완료미충족")
            found = dag_check.check_sink_return(rows, run_dir, "2.z", "DONE")
            self.assertTrue(any("완료미충족" in item for item in found), found)

    def test_old_sink_specific_return_word_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows, run_dir = self._case(tmp, status="병합충돌")
            found = dag_check.check_sink_return(
                rows, run_dir, "2.z", "완료미충족"
            )
            self.assertTrue(any("닫힌 목록 밖" in item for item in found), found)

    def test_exception_return_accepts_each_noncompletion_settlement_status(self):
        for status in dag_check.SINK_EXCEPTION_STATUSES:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                rows, run_dir = self._case(tmp, status=status)
                self.assertEqual(
                    dag_check.check_sink_return(rows, run_dir, "2.z", "예외"),
                    [],
                )

    def test_exception_return_rejects_a_completion_settlement_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows, run_dir = self._case(tmp, status="DONE", stage="종결")
            found = dag_check.check_sink_return(rows, run_dir, "2.z", "예외")
            self.assertTrue(any("비완결 상태여야 한다" in item for item in found), found)

    def test_submitted_return_matches_a_submitted_settlement(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows, run_dir = self._case(tmp, status="상신")
            self.assertEqual(
                dag_check.check_sink_return(rows, run_dir, "2.z", "상신"),
                [],
            )

    def test_unknown_sink_return_word_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows, run_dir = self._case(tmp, status="완료기준미충족")
            found = dag_check.check_sink_return(
                rows, run_dir, "2.z", "완료기준미충족"
            )
            self.assertTrue(any("닫힌 목록 밖" in item for item in found), found)

    def test_cli_runs_only_the_sink_return_gate(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            _, run_dir = self._case(tmp, status="완료미충족")
            table_path = run_dir / "파견표.md"
            table_path.write_text(
                table(row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2",
                          signal=self.SIGNAL, model="opus low", state="진행")),
                encoding="utf-8",
            )
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = dag_check.main([
                    "--table", str(table_path),
                    "--sink-return", "2.z", "예외",
                ])
            self.assertEqual(code, 0, out.getvalue())
            self.assertIn("싱크 반환: 2.z · 예외", out.getvalue())


class GateTest(unittest.TestCase):
    DECIDED = (
        "---\n유형: 결정\n상태: 결정됨\n---\n\n## 브리핑\n선택지 A/B\n\n"
        "## 결정 (메인 기입 — 사용자 발화 축자)\nA로 간다\n\n## 메인 결정\n\n"
    )
    WAITING = (
        "---\n유형: 결정\n상태: 대기\n---\n\n## 브리핑\n선택지 A/B\n\n"
        "## 결정 (메인 기입 — 사용자 발화 축자)\n\n## 메인 결정\n\n"
    )

    def _run_dir(self, tmp, body):
        run_dir = Path(tmp)
        (run_dir / "결정").mkdir()
        (run_dir / "결정" / "g.md").write_text(body, encoding="utf-8")
        return run_dir

    def test_empty_decision_section_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, self.WAITING)
            text = table(row("g1", kind="게이트", brief="—", signal="결정/g.md", state="완"))
            found = dag_check.check_gates(dag_check.parse_rows(text), run_dir, "partial")
            self.assertTrue(any("결정/g.md" in f for f in found), found)

    def test_filled_decision_section_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, self.DECIDED)
            text = table(row("g1", kind="게이트", brief="—", signal="결정/g.md", state="완"))
            self.assertEqual(dag_check.check_gates(dag_check.parse_rows(text), run_dir, "partial"), [])

    def test_unfinished_gate_is_not_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, self.WAITING)
            text = table(row("g1", kind="게이트", brief="—", signal="결정/g.md"))
            self.assertEqual(dag_check.check_gates(dag_check.parse_rows(text), run_dir, "partial"), [])

    def test_main_decision_section_does_not_count(self):
        body = (
            "---\n유형: 결정\n상태: 결정됨\n---\n\n"
            "## 결정 (메인 기입 — 사용자 발화 축자)\n\n## 메인 결정\n메인이 판정했다\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, body)
            text = table(row("g1", kind="게이트", brief="—", signal="결정/g.md", state="완"))
            self.assertTrue(dag_check.check_gates(dag_check.parse_rows(text), run_dir, "partial"))

    def test_placeholder_only_decision_section_is_found(self):
        """브리핑 행이 서식대로 만든 파일의 결정 절은 플레이스홀더만 담는다."""
        body = (
            "---\n유형: 결정\n상태: 결정됨\n---\n\n"
            "## 결정 (메인 기입 — 사용자 발화 축자)\n"
            "{해석·요약 금지. 축자가 정본이고 해석은 하류 몫이다. 불가침이다}\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, body)
            text = table(row("g1", kind="게이트", brief="—", signal="결정/g.md", state="완"))
            found = dag_check.check_gates(dag_check.parse_rows(text), run_dir, "partial")
            self.assertTrue(any("결정 절이 비어 있다" in f for f in found), found)

    def test_multiline_placeholder_is_found(self):
        body = (
            "---\n유형: 결정\n상태: 결정됨\n---\n\n"
            "## 결정 (메인 기입 — 사용자 발화 축자)\n{첫 줄\n둘째 줄}\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, body)
            text = table(row("g1", kind="게이트", brief="—", signal="결정/g.md", state="완"))
            found = dag_check.check_gates(dag_check.parse_rows(text), run_dir, "partial")
            self.assertTrue(any("결정 절이 비어 있다" in f for f in found), found)

    def test_verbatim_beside_leftover_placeholder_is_clean(self):
        body = (
            "---\n유형: 결정\n상태: 결정됨\n---\n\n"
            "## 결정 (메인 기입 — 사용자 발화 축자)\n{서식 잔여}\nA로 간다\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, body)
            text = table(row("g1", kind="게이트", brief="—", signal="결정/g.md", state="완"))
            self.assertEqual(dag_check.check_gates(dag_check.parse_rows(text), run_dir, "partial"), [])

    def test_waiting_frontmatter_is_found_even_when_filled(self):
        """축자가 채워져 있어도 상태가 결정됨이 아니면 게이트를 통과하지 않았다."""
        body = (
            "---\n유형: 결정\n상태: 대기\n---\n\n"
            "## 결정 (메인 기입 — 사용자 발화 축자)\nA로 간다\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, body)
            text = table(row("g1", kind="게이트", brief="—", signal="결정/g.md", state="완"))
            found = dag_check.check_gates(dag_check.parse_rows(text), run_dir, "partial")
            self.assertTrue(any("상태가 '대기'" in f for f in found), found)

    def test_missing_frontmatter_is_found(self):
        body = "## 결정 (메인 기입 — 사용자 발화 축자)\nA로 간다\n"
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, body)
            text = table(row("g1", kind="게이트", brief="—", signal="결정/g.md", state="완"))
            found = dag_check.check_gates(dag_check.parse_rows(text), run_dir, "partial")
            self.assertTrue(any("상태가 '없음'" in f for f in found), found)


class GateBriefingTest(unittest.TestCase):
    """게이트의 결정 파일은 선행 사슬의 어느 행이 낳는다 — 아무도 안 낳으면 영원히 기다린다."""

    def test_gate_whose_decision_file_nobody_produces_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(
                row("1", brief="행/1.md", signal="기준선.md", model="opus high"),
                row("g1", kind="게이트", deps="1", signal="결정/1-프레임.md", model="—"),
            )
            found = dag_check.check_gates(dag_check.parse_rows(text), Path(tmp))
            self.assertTrue(any("낳는 행이 선행 사슬에 없다" in f for f in found), found)

    def test_gate_fed_by_its_predecessor_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(
                row("1", brief="행/1.md", signal="기준선.md, 결정/1-프레임.md", model="opus high"),
                row("g1", kind="게이트", deps="1", signal="결정/1-프레임.md", model="—"),
            )
            self.assertEqual(dag_check.check_gates(dag_check.parse_rows(text), Path(tmp)), [])

    def test_a_transitive_ancestor_counts(self):
        """게이트 결정 파일은 직선행이 아니라 선행 사슬 위의 행이 낳아도 통과한다."""
        with tempfile.TemporaryDirectory() as tmp:
            text = table(
                row("2", kind="전개", brief="행/2.md", signal="행/2.d/", model="fable med"),
                row("2.4", brief="행/2.d/4.md", deps="2",
                    signal="행/2.d/4-보고.md, 결정/2-작업DAG.md", model="fable med"),
                row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2.4",
                    signal="행/2.d/z-결산.md", model="opus low"),
                row("g2", kind="게이트", deps="2.z", signal="결정/2-작업DAG.md", model="—"),
            )
            self.assertEqual(dag_check.check_gates(dag_check.parse_rows(text), Path(tmp)), [])


class GateConsumerTest(unittest.TestCase):
    """게이트 결정에 소비자가 배정됐는가 — 후행은 전개여야 하고 그 파견문이 좌표를 싣는다."""

    DECISION = "결정/1-프레임.md"

    def _table(self, kind, brief="행/2.md"):
        return table(
            row("1", brief="행/1.md", signal=f"기준선.md, {self.DECISION}", model="opus high"),
            row("g1", kind="게이트", deps="1", signal=self.DECISION, model="—"),
            row("2", kind=kind, brief=brief, deps="g1", signal="행/2.d/", model="fable med"),
        )

    def _run_dir(self, tmp, brief_body):
        run_dir = Path(tmp)
        (run_dir / "행").mkdir()
        (run_dir / "행" / "2.md").write_text(brief_body, encoding="utf-8")
        return run_dir

    def test_dispatch_row_after_gate_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, f"- 정본: {self.DECISION}\n")
            found = dag_check.check_gates(dag_check.parse_rows(self._table("파견")), run_dir)
            self.assertTrue(any("유형이 '파견'이다" in f for f in found), found)

    def test_expand_row_without_the_coordinate_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, "- 정본: 기준선.md\n")
            found = dag_check.check_gates(dag_check.parse_rows(self._table("전개")), run_dir)
            self.assertTrue(
                any("`정본:` 슬롯에 없다" in f and self.DECISION in f for f in found), found
            )

    def test_coordinate_only_in_the_reading_list_is_found(self):
        """소비가 서는 자리는 `정본:` 슬롯 하나다 — 읽기 목록의 언급은 소비가 아니다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(
                tmp, f"- 읽기 목록: {self.DECISION}\n- 정본: 기준선.md\n"
            )
            found = dag_check.check_gates(dag_check.parse_rows(self._table("전개")), run_dir)
            self.assertTrue(
                any("`정본:` 슬롯에 없다" in f and self.DECISION in f for f in found), found
            )

    def test_coordinate_only_in_prose_is_found(self):
        """임무 절의 산문 언급도 소비가 아니다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(
                tmp,
                "- 정본: 기준선.md\n\n## 임무\n"
                f"예전 게이트의 {self.DECISION}는 이 행이 소비하지 않는다.\n",
            )
            found = dag_check.check_gates(dag_check.parse_rows(self._table("전개")), run_dir)
            self.assertTrue(
                any("`정본:` 슬롯에 없다" in f and self.DECISION in f for f in found), found
            )

    def test_brief_without_a_canon_slot_is_found(self):
        """슬롯 자체가 없으면 실을 자리가 없다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, f"- 겨냥: {self.DECISION}\n")
            found = dag_check.check_gates(dag_check.parse_rows(self._table("전개")), run_dir)
            self.assertTrue(any("`정본:` 슬롯에 없다" in f for f in found), found)

    def test_expand_row_carrying_the_coordinate_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, f"- 정본: {self.DECISION}\n")
            self.assertEqual(
                dag_check.check_gates(dag_check.parse_rows(self._table("전개")), run_dir), []
            )

    def test_absolute_path_with_backslashes_counts(self):
        """파견문은 좌표를 런 디렉토리 절대 경로로 내보낸다."""
        with tempfile.TemporaryDirectory() as tmp:
            body = "- 정본: C:\\repo\\.sdd\\dag\\demo\\" + self.DECISION.replace("/", "\\") + "\n"
            run_dir = self._run_dir(tmp, body)
            self.assertEqual(
                dag_check.check_gates(dag_check.parse_rows(self._table("전개")), run_dir), []
            )

    def test_partial_defers_the_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp, "- 정본: 기준선.md\n")
            self.assertEqual(
                dag_check.check_gates(dag_check.parse_rows(self._table("파견")), run_dir, "partial"),
                [],
            )

    def test_sink_after_gate_is_exempt(self):
        """⑤가 최상위 게이트에 국면 싱크 도달을 요구한다 — 수렴 간선은 소비가 아니다."""
        with tempfile.TemporaryDirectory() as tmp:
            text = table(
                row("1", brief="행/1.md", signal=f"기준선.md, {self.DECISION}", model="opus high"),
                row("g1", kind="게이트", deps="1", signal=self.DECISION, model="—"),
                row("z", kind="싱크", brief="행/z.md", deps="g1",
                    signal="행/z-결산.md", model="opus low"),
            )
            self.assertEqual(dag_check.check_gates(dag_check.parse_rows(text), Path(tmp)), [])

    def test_missing_brief_is_left_to_the_coordinate_check(self):
        """파견문 부재는 ⑦의 발견이다. 여기서 겹쳐 세지 않는다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            self.assertEqual(
                dag_check.check_gates(dag_check.parse_rows(self._table("전개")), run_dir), []
            )


class IdTest(unittest.TestCase):
    def test_duplicate_row_number_is_found(self):
        text = table(row("2.1", deps="2"), row("2.1", deps="2"))
        found = dag_check.check_ids(dag_check.parse_rows(text))
        self.assertTrue(any("유일" in f for f in found), found)

    def test_legal_shapes_are_clean(self):
        text = table(
            row("1"), row("2.1"), row("2.z"), row("g1"), row("z"), row("2.10.3"), row("2.g1")
        )
        self.assertEqual(dag_check.check_ids(dag_check.parse_rows(text)), [])

    def test_sink_marker_in_the_middle_is_found(self):
        """싱크·게이트는 자식을 두지 않는다 — 마지막 마디에만 온다."""
        for rid in ["2.z.1", "g1.2", "2.x", "2..1"]:
            found = dag_check.check_ids(dag_check.parse_rows(table(row(rid))))
            self.assertTrue(any("문법 밖" in f for f in found), rid)


class ColumnContractTest(unittest.TestCase):
    """행 유형별 칸 계약. 누락(빈 칸)과 해당 없음(`—`)은 다른 사실이다."""

    def _check(self, *rows):
        return dag_check.check_columns(dag_check.parse_rows(table(*rows)))

    def test_dispatch_row_needs_brief_signal_and_model(self):
        found = self._check(row("2.1", deps="2", model="—"))
        self.assertEqual(len(found), 3, found)
        self.assertTrue(all("[계약]" in f for f in found), found)

    def test_complete_dispatch_row_is_clean(self):
        self.assertEqual(
            self._check(row("2.1", brief="행/2.d/1.md", deps="2",
                            signal="행/2.d/1-보고.md", model="opus low")),
            [],
        )

    def test_unfinished_expander_requires_its_completion_report(self):
        found = self._check(
            row("2", kind="전개", brief="행/2.md", signal="행/2.d/", model="fable med")
        )
        self.assertTrue(any("완료보고가 없다" in f for f in found), found)

    def test_unfinished_expander_with_its_completion_report_is_clean(self):
        self.assertEqual(
            self._check(
                row(
                    "2",
                    kind="전개",
                    brief="행/2.md",
                    signal="행/2-보고.md",
                    model="fable med",
                )
            ),
            [],
        )

    def test_gate_row_wants_dashes_and_a_decision_file(self):
        self.assertEqual(
            self._check(row("g1", kind="게이트", deps="1",
                            signal="결정/1-프레임.md", model="—")),
            [],
        )

    def test_gate_row_with_a_brief_is_found(self):
        found = self._check(row("g1", kind="게이트", brief="행/g1.md", deps="1",
                                signal="결정/1.md", model="—"))
        self.assertTrue(any("파견문" in f for f in found), found)

    def test_gate_signal_outside_the_decision_directory_is_found(self):
        found = self._check(row("g1", kind="게이트", deps="1",
                                signal="행/1-보고.md", model="—"))
        self.assertTrue(any("결정 파일이 아니다" in f for f in found), found)

    def test_idle_sink_is_clean(self):
        self.assertEqual(self._check(row("2.z", kind="싱크", deps="2.1", model="—")), [])

    def test_working_sink_wants_a_settlement_signal(self):
        self.assertEqual(
            self._check(row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2.1",
                            signal="행/2.d/z-결산.md", model="opus low")),
            [],
        )

    def test_working_sink_with_a_foreign_signal_is_found(self):
        found = self._check(row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2.1",
                                signal="행/2.d/z-보고.md", model="opus low"))
        self.assertTrue(any("결산이 아니다" in f for f in found), found)

    def test_settlement_from_another_subtree_is_found(self):
        """이름만 맞는 남의 결산은 결산이 아니다 — 좌표는 파견문에서 파생한다."""
        found = self._check(row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2.1",
                                signal="행/9.d/z-결산.md", model="opus low"))
        self.assertTrue(any("결산이 아니다" in f for f in found), found)

    def test_half_filled_sink_is_found(self):
        found = self._check(row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2.1",
                                signal="—", model="—"))
        self.assertTrue(any("반쪽" in f for f in found), found)

    def test_blank_cell_is_not_read_as_none(self):
        """`—`는 판단의 기록이고 빈 칸은 그 판단이 없다는 증거다."""
        text = HEAD + "| 2.z | 싱크 |  |  |  |  | 미착수 |\n"
        found = dag_check.check_columns(dag_check.parse_rows(text))
        self.assertTrue(found)
        self.assertTrue(all("빈 칸" in f for f in found), found)


class DriveTest(unittest.TestCase):
    """파견 직전 행의 실행 좌표 — 오케가 모델·노력 두 낱말로 Agent 인자를 만든다."""

    def test_ready_row_without_a_usable_model_is_found(self):
        text = table(
            row("1", brief="행/1.md", signal="기준선.md", model="opus high", state="완"),
            row("2", brief="행/2.md", deps="1", signal="행/2-보고.md", model="opus"),
        )
        found = dag_check.check_drive(dag_check.parse_rows(text))
        self.assertTrue(any("행 2" in f for f in found), found)

    def test_ready_row_with_model_and_effort_is_clean(self):
        text = table(
            row("1", brief="행/1.md", signal="기준선.md", model="opus high", state="완"),
            row("2", brief="행/2.md", deps="1", signal="행/2-보고.md", model="fable med"),
        )
        self.assertEqual(dag_check.check_drive(dag_check.parse_rows(text)), [])

    def test_ready_codex_row_with_xhigh_effort_is_clean(self):
        """행별 근거로 최상급 노력을 배정한 Codex 행은 운전할 수 있다."""
        text = table(
            row("1", brief="행/1.md", signal="기준선.md", model="opus high", state="완"),
            row(
                "2",
                brief="행/2.md",
                deps="1",
                signal="행/2-보고.md",
                model="gpt-5.6-sol xhigh",
            ),
        )
        self.assertEqual(dag_check.check_drive(dag_check.parse_rows(text)), [])

    def test_blocked_row_is_not_yet_checked(self):
        text = table(
            row("1", brief="행/1.md", signal="기준선.md", model="opus high"),
            row("2", brief="행/2.md", deps="1", signal="행/2-보고.md", model="—"),
        )
        self.assertEqual(dag_check.check_drive(dag_check.parse_rows(text)), [])

    def test_idle_sink_is_never_dispatched(self):
        text = table(row("z", kind="싱크", model="—"))
        self.assertEqual(dag_check.check_drive(dag_check.parse_rows(text)), [])

    def test_partial_mode_defers_the_drive_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(row("1", brief="행/1.md", signal="기준선.md", model="opus"))
            self.assertFalse(
                any("[운전]" in f for f in dag_check.run(text, Path(tmp), "partial"))
            )

    def test_partial_mode_does_not_claim_the_drive_check(self):
        """0번 전개는 무발견 문면으로 자기검사 완료를 판정한다 — 재지 않은 것을 열거하지 않는다."""
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "행").mkdir()
            (run_dir / "행" / "1.md").write_text(
                valid_brief_body(run_dir), encoding="utf-8"
            )
            (run_dir / "파견표.md").write_text(
                table(row("1", brief="행/1.md", signal="기준선.md", model="opus low")),
                encoding="utf-8",
            )
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                dag_check.main(["--table", str(run_dir / "파견표.md"), "--mode", "partial"])
            self.assertIn("무발견 (partial:", out.getvalue())
            self.assertNotIn("운전", out.getvalue())


class StateTest(unittest.TestCase):
    def test_unknown_state_is_found(self):
        found = dag_check.check_states(dag_check.parse_rows(table(row("1", state="완료"))))
        self.assertTrue(any("완료" in f for f in found), found)

    def test_known_states_are_clean(self):
        rows = [row(str(i), state=s) for i, s in enumerate(dag_check.STATES, start=1)]
        self.assertEqual(dag_check.check_states(dag_check.parse_rows(table(*rows))), [])

    def test_blank_kind_is_found(self):
        """오케는 유형 칸으로 행동을 고른다 — 빈 유형은 지시가 아니라 해석 요구다."""
        found = dag_check.check_states(dag_check.parse_rows(table(row("1", kind="—"))))
        self.assertTrue(any("유형" in f for f in found), found)

    def test_known_kinds_are_clean(self):
        rows = [row(str(i), kind=k) for i, k in enumerate(dag_check.KINDS, start=1)]
        self.assertEqual(dag_check.check_states(dag_check.parse_rows(table(*rows))), [])


class RunTest(unittest.TestCase):
    def _run_dir(self, tmp):
        run_dir = Path(tmp)
        (run_dir / "기준선.md").write_text("x", encoding="utf-8")
        (run_dir / "행" / "2.d").mkdir(parents=True)
        briefs = {
            "행/1.md": ("0",),
            "행/2.md": ("0",),
            "행/z.md": ("0",),
            "행/2.d/1.md": ("0", "2"),
            "행/2.d/z.md": ("0", "2"),
        }
        for rel, owners in briefs.items():
            (run_dir / rel).write_text(valid_brief_body(run_dir, *owners), encoding="utf-8")
        return run_dir

    def test_clean_table_returns_nothing(self):
        """서식·대응표가 보이는 정상 표 — 아홉 검사 전건을 통과한다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp)
            text = table(
                row("1", brief="행/1.md", signal="기준선.md", model="opus high", state="완"),
                row("2", kind="전개", brief="행/2.md", deps="1",
                    signal="행/2-보고.md", model="fable med"),
                row("2.1", brief="행/2.d/1.md", deps="2",
                    signal="행/2.d/1-보고.md", model="opus low"),
                row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2.1",
                    signal="행/2.d/z-결산.md", model="opus low"),
                row("z", kind="싱크", brief="행/z.md", deps="2.z",
                    signal="행/z-결산.md", model="opus low"),
            )
            self.assertEqual(dag_check.run(text, run_dir), [])

    def test_ready_flag_lists_drive_information(self):
        """--ready는 무발견 뒤에 파견 직전 행의 표 줄과 진행·상신중·예외 목록을 덧낸다."""
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp)
            text = table(
                row("1", brief="행/1.md", signal="기준선.md", model="opus high", state="완"),
                row("2", kind="전개", brief="행/2.md", deps="1",
                    signal="행/2-보고.md", model="fable med"),
                row("2.1", brief="행/2.d/1.md", deps="2",
                    signal="행/2.d/1-보고.md", model="opus low"),
                row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2.1",
                    signal="행/2.d/z-결산.md", model="opus low"),
                row("z", kind="싱크", brief="행/z.md", deps="2.z",
                    signal="행/z-결산.md", model="opus low"),
            )
            (run_dir / "파견표.md").write_text(text, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = dag_check.main(
                    ["--table", str(run_dir / "파견표.md"), "--ready"]
                )
            printed = out.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("ready 1행", printed)
            self.assertIn(row("2", kind="전개", brief="행/2.md", deps="1",
                              signal="행/2-보고.md", model="fable med").strip(), printed)
            self.assertNotIn("| 2.1 |", printed)
            self.assertIn("진행 0행", printed)
            self.assertIn("상신중 0행", printed)
            self.assertIn("예외 0행", printed)

    def test_ready_flag_prints_live_rows_verbatim(self):
        """진행 행의 표 줄 전문이 나온다 — 교대로 온 새 오케의 감시 좌표가 이 줄이다."""
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp)
            live = row("2", kind="전개", brief="행/2.md", deps="1",
                       signal="행/2-보고.md", model="fable med", state="진행")
            text = table(
                row("1", brief="행/1.md", signal="기준선.md", model="opus high", state="완"),
                live,
                row("2.1", brief="행/2.d/1.md", deps="2",
                    signal="행/2.d/1-보고.md", model="opus low"),
                row("2.z", kind="싱크", brief="행/2.d/z.md", deps="2.1",
                    signal="행/2.d/z-결산.md", model="opus low"),
                row("z", kind="싱크", brief="행/z.md", deps="2.z",
                    signal="행/z-결산.md", model="opus low"),
            )
            (run_dir / "파견표.md").write_text(text, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = dag_check.main(
                    ["--table", str(run_dir / "파견표.md"),
                     "--mode", "partial", "--ready"]
                )
            printed = out.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("ready 0행", printed)
            self.assertIn("진행 1행", printed)
            self.assertIn(live.strip(), printed)

    def test_idle_sinks_and_gates_pass_with_dashes(self):
        """`—` 사용례는 통과한다 — 무작업 싱크와 게이트가 그 자리다."""
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run_dir(tmp)
            text = table(
                row("1", brief="행/1.md",
                    signal="기준선.md, 결정/1-프레임.md", model="opus high", state="완"),
                row("g1", kind="게이트", deps="1",
                    signal="결정/1-프레임.md", model="—", state="완"),
                row("2", kind="전개", brief="행/2.md", deps="g1",
                    signal="행/2-보고.md", model="fable med"),
                row("2.1", brief="행/2.d/1.md", deps="2",
                    signal="행/2.d/1-보고.md", model="opus low"),
                row("2.z", kind="싱크", deps="2.1", model="—"),
                row("z", kind="싱크", brief="행/z.md", deps="2.z",
                    signal="행/z-결산.md", model="opus low"),
            )
            (run_dir / "결정").mkdir()
            (run_dir / "결정" / "1-프레임.md").write_text(
                "---\n유형: 결정\n상태: 결정됨\n---\n\n"
                "## 결정 (메인 기입 — 사용자 발화 축자)\n프레임을 확정한다\n",
                encoding="utf-8",
            )
            # 게이트 후행 전개의 파견문은 그 결정 좌표를 싣는다(⑧ 소비 계약).
            (run_dir / "행" / "2.md").write_text(
                "- 정본: 결정/1-프레임.md\n" + valid_brief_body(run_dir),
                encoding="utf-8",
            )
            self.assertEqual(dag_check.run(text, run_dir), [])

    def test_findings_are_aggregated(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = table(row("1", deps="9", state="완료"))
            self.assertGreaterEqual(len(dag_check.run(text, Path(tmp))), 2)


class DocExampleTest(unittest.TestCase):
    """문면이 보여 주는 표는 검산을 통과해야 한다.

    좌표 실재 검사가 걸리지 않도록 표가 지목한 파일을 그대로 만들어 준 뒤 잰다.
    """

    SKILL = SCRIPTS.parent
    HEADER = "| 행 | 유형 | 파견문 |"

    def _table(self, path: Path) -> str:
        blocks, cur, inside = [], [], False
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("```"):
                if inside and any(self.HEADER in x for x in cur):
                    blocks.append("\n".join(cur))
                cur, inside = [], not inside
                continue
            if inside:
                cur.append(line)
        self.assertEqual(len(blocks), 1, f"{path.name}의 파견표 예시가 하나가 아니다")
        return blocks[0] + "\n"

    def _materialize(self, text: str, run_dir: Path) -> None:
        rows = dag_check.parse_rows(text)
        gates = {r.id: r.signals for r in rows if r.kind == "게이트"}
        by_id = {r.id: r for r in rows}
        for r in rows:
            # 게이트 후행의 파견문에는 그 게이트의 결정 좌표가 실린다(⑧ 소비 계약).
            parts = r.id.split(".")
            owners = ["0"] + [
                owner
                for depth in range(1, len(parts))
                if (owner := ".".join(parts[:depth])) in by_id
                and by_id[owner].kind == "전개"
            ]
            body = "x\n" + valid_brief_body(run_dir, *owners) + "".join(
                f"- 정본: {s}\n" for d in r.deps for s in gates.get(d, [])
            )
            for rel in ([r.brief] if r.dispatched else []) + r.signals:
                target = run_dir / rel
                if rel.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                    (target / "채움.md").write_text("x", encoding="utf-8")
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(
                        body if rel == r.brief else "x", encoding="utf-8"
                    )

    def _assert_clean(self, name: str):
        text = self._table(self.SKILL / name)
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            self._materialize(text, run_dir)
            self.assertEqual(dag_check.run(text, run_dir), [], name)

    def test_daeungpyo_example(self):
        self._assert_clean("대응표.md")

    def test_row_zero_first_edition(self):
        self._assert_clean("행_0.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)

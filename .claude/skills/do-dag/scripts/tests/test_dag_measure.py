"""dag_measure 실측기 7종의 시험. 직접 실행이 정본이다: python .claude/skills/do-dag/scripts/tests/test_dag_measure.py"""

from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dag_measure as m  # noqa: E402


def _write(root: Path, rel: str, body: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


class TestCount(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_계수와_문맥(self):
        _write(self.root, "a.md", "명세 칸을 채운다\n다른 줄\n")
        _write(self.root, "b.md", "무관한 내용\n")
        lines = m.run_count("명세 칸", m._expand("*.md", self.root)[0], self.root, regex=False)
        joined = "\n".join(lines)
        self.assertIn("a.md: 1", joined)
        self.assertIn("b.md: 0", joined)
        self.assertIn(":1: 명세 칸을 채운다", joined)  # 히트 문맥이 보인다
        self.assertIn("합계: 1", joined)

    def test_자기_규칙문이_문맥에_드러난다(self):
        # 규칙문이 패턴을 담으면 계수에 들되 문맥으로 보인다.
        _write(self.root, "z.md", "ⓒ 「자칭하지 않는다」류의 부정 언급\n")
        lines = m.run_count("자칭하지 않는다", m._expand("z.md", self.root)[0], self.root, regex=False)
        self.assertIn("합계: 1", "\n".join(lines))
        self.assertTrue(any("류의 부정 언급" in ln for ln in lines))


class TestExpandUnresolved(unittest.TestCase):
    """해석되지 않은 조각은 증거 블록에 뜬다 — 무언의 과소 견적을 막는다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_typo_among_hits_is_reported(self):
        _write(self.root, "a.md", "x\n")
        paths, missing = m._expand("a.md, 없는파일.md", self.root)
        self.assertEqual([p.name for p in paths], ["a.md"])
        self.assertEqual(missing, ["없는파일.md"])
        self.assertEqual(m._unresolved(missing), ["미해석: 없는파일.md"])

    def test_all_resolved_adds_no_line(self):
        _write(self.root, "a.md", "x\n")
        paths, missing = m._expand("a.md, *.md", self.root)
        self.assertEqual(missing, [])
        self.assertEqual(m._unresolved(missing), [])

    def test_the_block_carries_the_notice(self):
        _write(self.root, "a.md", "명세 칸\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = m.main(["count", "--pattern", "명세 칸",
                           "--files", "a.md,없는파일.md", "--root", str(self.root)])
        self.assertEqual(code, 0)
        self.assertIn("미해석: 없는파일.md", out.getvalue())


class TestAnchor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_유일_다중_부재(self):
        p = _write(self.root, "a.md", "하나\n반경 확대 3건\n둘\n반경 확대 3건\n")
        lines = m.run_anchor("반경 확대 3건", p, self.root)
        self.assertIn("다중 2", lines[0])
        p2 = _write(self.root, "b.md", "반경 확대 3건\n")
        self.assertIn("유일", m.run_anchor("반경 확대 3건", p2, self.root)[0])
        self.assertIn("부재", m.run_anchor("없는 문자열", p2, self.root)[0])


class TestTable(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_이스케이프_파이프는_열이_아니다(self):
        # 명세 안 \| 4개는 순진한 split에서 11열이 된다.
        body = (
            "| ID | 명세 | 처분 | 노출 | 연결 | 상태 | 증거 |\n"
            "|---|---|---|---|---|---|---|\n"
            "| S-11 | 표면 `\\| a \\| b \\| c \\| d`의 예외 | fail | N-8 | — | 미착수 | — |\n"
        )
        p = _write(self.root, "이음새.md", body)
        joined = "\n".join(m.run_table(p, self.root))
        self.assertIn("머리 7열", joined)
        self.assertIn("불일치 행은 위에 열거", joined)
        self.assertTrue("불일치" not in joined.split("판정")[0].split("머리 7열")[1])

    def test_열_불일치가_잡힌다(self):
        body = "| a | b | c |\n|---|---|---|\n| 1 | 2 |\n"
        p = _write(self.root, "t.md", body)
        joined = "\n".join(m.run_table(p, self.root))
        self.assertIn("2열 — 머리와 불일치", joined)


class TestSame(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_동문과_갈림(self):
        _write(self.root, "1.md", "같은 내용\n")
        _write(self.root, "2.md", "같은 내용\n")
        lines = m.run_same(m._expand("*.md", self.root)[0], self.root, normalize=True)
        self.assertIn("판정: 동문", "\n".join(lines))
        _write(self.root, "3.md", "다른 내용\n")
        lines = m.run_same(m._expand("*.md", self.root)[0], self.root, normalize=True)
        self.assertIn("갈림 2군", "\n".join(lines))

    def test_정규화가_개행_차이를_흡수한다(self):
        (self.root / "a.md").write_bytes(b"x\r\ny\r\n")
        (self.root / "b.md").write_bytes(b"x\ny\n")
        lines = m.run_same(m._expand("*.md", self.root)[0], self.root, normalize=True)
        self.assertIn("판정: 동문", "\n".join(lines))


class TestAttrib(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"],
                    ["git", "config", "user.name", "t"],
                    ["git", "config", "commit.gpgsign", "false"]):
            subprocess.run(cmd, cwd=self.root, check=True, capture_output=True)
        _write(self.root, "base.md", "기저\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "base"], cwd=self.root, check=True, capture_output=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_미귀속이_잡히고_전건_귀속이_선다(self):
        _write(self.root, "base.md", "수정\n")
        _write(self.root, "새파일.md", "신설\n")
        lines = m.run_attrib(self.root, ["base.md"], allow_untracked=False)
        joined = "\n".join(lines)
        self.assertIn("미귀속 잔존", joined)
        self.assertIn("새파일.md", joined)
        lines = m.run_attrib(self.root, ["base.md", "새파일.md"], allow_untracked=False)
        self.assertIn("전건 귀속", "\n".join(lines))


class TestChanges(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"],
                    ["git", "config", "user.name", "t"],
                    ["git", "config", "commit.gpgsign", "false"]):
            subprocess.run(cmd, cwd=self.root, check=True, capture_output=True)
        _write(self.root, "미스테이지.md", "기저\n")
        _write(self.root, "스테이지.md", "기저\n")
        _write(self.root, "삭제.md", "기저\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "base"], cwd=self.root, check=True, capture_output=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_현존은_스테이지_미스테이지_미추적을_모두_센다(self):
        _write(self.root, "미스테이지.md", "수정\n")
        _write(self.root, "스테이지.md", "수정\n")
        subprocess.run(["git", "add", "스테이지.md"], cwd=self.root, check=True, capture_output=True)
        _write(self.root, "새파일.md", "신설\n")

        lines, has_deleted = m.run_changes(self.root, "HEAD")

        self.assertFalse(has_deleted)
        joined = "\n".join(lines)
        self.assertIn("현존 3", joined)
        for path in ("미스테이지.md", "스테이지.md", "새파일.md"):
            self.assertIn(f"  {path}", joined)

    def test_삭제는_현존과_분리되고_fail_closed다(self):
        (self.root / "삭제.md").unlink()

        lines, has_deleted = m.run_changes(self.root, "HEAD")

        self.assertTrue(has_deleted)
        joined = "\n".join(lines)
        self.assertIn("삭제 1", joined)
        self.assertIn("  삭제.md", joined)
        self.assertIn("판정: 삭제대상", joined)


class TestBudget(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_예산_판정(self):
        _write(self.root, "소.md", "x" * 400)
        lines = m.run_budget(m._expand("소.md", self.root)[0], self.root, "opus")
        self.assertIn("예산 안", "\n".join(lines))
        big = self.root / "대.md"
        big.write_text("x" * 1_000_000, encoding="utf-8")  # 좁은문자 ~200k tok
        lines = m.run_budget([big], self.root, "opus")
        self.assertIn("예산 초과", "\n".join(lines))
        lines = m.run_budget([big], self.root, "fable")
        self.assertIn("예산 초과", "\n".join(lines))

    def test_예산_초과_판정이_모델_상향을_안내하지_않는다(self):
        """양적 초과의 처분은 분할 하나다.

        규율은 네 자리에서 모델 상향을 금지한다(`references/서식.md` 「배정표 (모델·노력)」의
        `전거 예산` 블록 · `전거/파견단위.md` 「예산」 항목 · `references/분해_원리.md`
        「크기와 경계」 · `행_0.md` 「행 `2`의 전개 지시에 담을 것」) — 모델을
        올리는 근거는 질적 난이도뿐이다. 이 출력을 읽는 것은 파견 단위를 자르는
        전개이므로, 실측기가 금지된 처분을 대등한 선택지로 내밀면 규율이 그
        자리에서 진다.
        """
        big = self.root / "대.md"
        big.write_text("x" * 1_000_000, encoding="utf-8")
        joined = "\n".join(m.run_budget([big], self.root, "opus"))
        self.assertIn("예산 초과", joined)
        self.assertNotIn("상향", joined)
        self.assertIn("쪼갠다", joined)

    def test_하네스_기저와_출력_유보가_합에_든다(self):
        # 읽기 목록만으로는 견적이 서지 않는다 — 하네스 기저와 출력 재유입이 함께 든다.
        _write(self.root, "빈.md", "")
        lines = m.run_budget(m._expand("빈.md", self.root)[0], self.root, "opus")
        joined = "\n".join(lines)
        for term in ("하네스 기저", "도구 왕복", "출력 유보"):
            self.assertIn(term, joined)
        self.assertEqual(m.est_required(0, 0),
                         m.HARNESS_FLOOR + m.TOOL_TRAFFIC + m.OUTPUT_FLOOR)

    def test_미존재_정본이_읽기에_든다(self):
        _write(self.root, "빈.md", "")
        paths = m._expand("빈.md", self.root)[0]
        lines = m.run_budget(paths, self.root, "opus", pending=83_474)
        joined = "\n".join(lines)
        self.assertIn("미존재 정본", joined)
        self.assertIn("83,474바이트", joined)
        self.assertGreater(m.est_pending(83_474), 40_000)

    def test_실측_3기를_재현한다(self):
        """실측 3기에 대한 견적의 회귀 가드.

        계약은 방향이 있다 — 과소는 금지고 과다는 허용 폭이 넓다.
        """
        구조 = [
            ("행 2 전개(저작 83,474바이트)", m.est_required(71_612, 83_474), 185_647),
            ("2.1 운전성 렌즈", m.est_required(39_719 + m.est_pending(78_271), 0), 158_232),
            ("2.2 정합성 렌즈", m.est_required(60_707 + m.est_pending(78_271), 0), 154_332),
        ]
        for 이름, 견적, 실측 in 구조:
            self.assertGreater(견적, 실측 * 0.95, f"{이름}: 낙관 {견적:,} < 실측 {실측:,}")
            self.assertLess(견적, 실측 * 1.25, f"{이름}: 과다 {견적:,}")

    def test_저작량이_출력_유보를_올린다(self):
        _write(self.root, "빈.md", "")
        paths = m._expand("빈.md", self.root)[0]
        floor = m.run_budget(paths, self.root, "opus")
        heavy = m.run_budget(paths, self.root, "opus", writes=200_000)
        self.assertIn("하한", "\n".join(floor))
        self.assertNotIn("하한", "\n".join(heavy))
        self.assertGreater(m.est_required(0, 200_000), m.est_required(0, 0))

class TestCli(unittest.TestCase):
    def test_블록_구조와_대상해시(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "a.md", "패턴 하나\n")
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).resolve().parents[1] / "dag_measure.py"),
                 "count", "--pattern", "패턴", "--files", "a.md", "--root", str(root)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("[실측기 count]", proc.stdout)
            self.assertIn("명령: python dag_measure.py count", proc.stdout)
            self.assertIn("대상해시: sha1:", proc.stdout)
            self.assertIn("[/실측기]", proc.stdout)

    def test_budget_블록이_항을_전부_보인다(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "정본.md", "한글 본문\n" * 100)
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).resolve().parents[1] / "dag_measure.py"),
                 "budget", "--files", "정본.md", "--model", "fable",
                 "--writes", "40000", "--root", str(root)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            for term in ("읽기 합계", "하네스 기저", "출력 유보", "소요 견적", "판정"):
                self.assertIn(term, proc.stdout)
            self.assertIn("40,000바이트", proc.stdout)

    def test_대상_0파일은_실패다(self):
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parents[1] / "dag_measure.py"),
             "count", "--pattern", "x", "--files", "없는경로*.md"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("대상 0파일", proc.stdout)

    def test_changes는_삭제가_있으면_exit_1이다(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"],
                        ["git", "config", "user.name", "t"],
                        ["git", "config", "commit.gpgsign", "false"]):
                subprocess.run(cmd, cwd=root, check=True, capture_output=True)
            _write(root, "삭제.md", "기저\n")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True, capture_output=True)
            (root / "삭제.md").unlink()

            proc = subprocess.run(
                [sys.executable, str(Path(__file__).resolve().parents[1] / "dag_measure.py"),
                 "changes", "--worktree", str(root), "--base", "HEAD"],
                capture_output=True, text=True, encoding="utf-8",
            )

            self.assertEqual(proc.returncode, 1)
            self.assertIn("판정: 삭제대상", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)

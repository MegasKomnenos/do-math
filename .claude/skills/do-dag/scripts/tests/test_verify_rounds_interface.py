"""do-dag가 verify-rounds에 내리는 접속면의 회귀 시험."""

from __future__ import annotations

import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[2]


class TestVerifyRoundsInterface(unittest.TestCase):
    PRESETS = ("claude-full", "mixed", "codex-full")

    def test_파견재료가_기준원문을_불변식과_분리한다(self):
        body = (SKILL / "references" / "검증_체제.md").read_text(encoding="utf-8")
        self.assertIn("기준 원문 재료", body)
        invariant = body.split("**불변식 재료**", 1)[1].split("\n- **", 1)[0]
        self.assertNotIn("상위 문서의 원문 경로", invariant)

    def test_검증런은_worktree에서_실행하고_여덟절을_조립한다(self):
        body = (SKILL / "계약" / "검증런.md").read_text(encoding="utf-8")
        self.assertIn("**기준 원문**", body)
        self.assertIn("메인 체크아웃을 실행 좌표로 쓰지 않는다", body)
        self.assertIn("저장소 상대 경로 하나를 `- <경로>`", body)

    def test_누적변경은_changes_실측기를_쓴다(self):
        body = (SKILL / "전거" / "검증.md").read_text(encoding="utf-8")
        self.assertIn("dag_measure.py changes", body)
        self.assertNotIn("git -C <worktree> diff --name-only", body)

    def test_폐지된_verify_rounds_자산을_참조하지_않는다(self):
        body = "\n".join(
            p.read_text(encoding="utf-8")
            for p in SKILL.rglob("*.md")
        )
        for fossil in (
            "계약/발견.md",
            "계약/수리기안.md",
            "계약/조립.md",
            "references/파견문/수리.md",
            "배제·폐기·무처분 잔여",
        ):
            self.assertNotIn(fossil, body)

    def test_모델_프리셋_어휘가_닫혀_있다(self):
        assignment = (SKILL / "전거" / "파견단위.md").read_text(encoding="utf-8")
        for preset in self.PRESETS:
            self.assertIn(preset, assignment)
        main = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("Codex 오케", main)
        self.assertNotIn("오케 모델이 Codex", main)

    def test_검증런_모델_프리셋은_명시값이_없으면_do_dag를_상속한다(self):
        contract = (SKILL / "계약" / "검증런.md").read_text(encoding="utf-8")
        self.assertIn("검증런_모델_프리셋", contract)
        self.assertIn("`모델_프리셋`을 상속", contract)
        self.assertIn("명시값이 있으면 상속값을 덮는다", contract)
        self.assertIn("`mixed`에서 검증런 행 자체는 Claude", contract)

    def test_codex_완료_대기_스크립트와_절차가_verify_rounds와_같다(self):
        local_wait = SKILL / "scripts" / "wait_outputs.py"
        verify_wait = SKILL.parent / "verify-rounds" / "scripts" / "wait_outputs.py"
        self.assertTrue(local_wait.is_file())
        self.assertEqual(local_wait.read_bytes(), verify_wait.read_bytes())

        procedure = (SKILL / "references" / "배정.md").read_text(encoding="utf-8")
        self.assertIn(
            "python .claude/skills/do-dag/scripts/wait_outputs.py <반환 절대 경로 ...>",
            procedure,
        )
        self.assertIn("exit 0", procedure)
        self.assertIn("exit 3", procedure)
        self.assertIn("같은 호출을 다시", procedure)


if __name__ == "__main__":
    unittest.main(verbosity=1)

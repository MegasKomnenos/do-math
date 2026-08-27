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

    def test_검증런은_파견문_작업디렉토리에서_실행한다(self):
        body = (SKILL / "계약" / "검증런.md").read_text(encoding="utf-8")
        self.assertIn("**기준 원문**", body)
        self.assertIn("제품 산출물을 검증하면 노드 worktree", body)
        self.assertIn("설계 자산을\n검증하면 메인 체크아웃", body)
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

    def test_내용_선택은_복수의_적합한_결과가_남을_때만_상신한다(self):
        main = (SKILL / "전거" / "실행.md").read_text(encoding="utf-8")
        contract = (SKILL / "계약" / "검증런.md").read_text(encoding="utf-8")
        self.assertIn("현행 정본에 맞는 비동등한 결과가 둘 이상", main)
        self.assertIn("정확성·완전성 결함이라는 사실만으로 4항이 성립하지 않는다", main)
        self.assertNotIn("산출물의 내용 품질(논증·정확성·완전성 등 실질)", main)
        self.assertIn("정확성·완전성 결함이라는 사실만으로 사용자에게", contract)

    def test_전달_발견만_검토전개를_생성한다(self):
        contract = (SKILL / "계약" / "검증런.md").read_text(encoding="utf-8")
        self.assertIn("「호출자에게 전달」이 확정된", contract)
        self.assertIn("기각·무처분 발견은 검토전개 생성 수에 포함하지 않는다", contract)
        self.assertIn("### 발견의 호출자 후속", contract)

    def test_심사자에게_검토전개_전체의_최소_규모를_알린다(self):
        contract = (SKILL / "계약" / "검증런.md").read_text(encoding="utf-8")
        flat = " ".join(contract.split())
        self.assertIn("검토전개 행 하나의 비용만 뜻하지 않는다", contract)
        self.assertIn("전개 뒤 검증런", contract)
        self.assertIn("작업자 행 하나 이상", contract)
        self.assertIn("각 검증런은 수리자·심사자 여러 기", flat)

    def test_산출물_구현_누락의_뜻이_지급문에_보존된다(self):
        body = (SKILL / "references" / "검증_체제.md").read_text(encoding="utf-8")
        self.assertIn("원자료가 요구하지만 산출물에 구현되어 있지 않은", body)
        self.assertNotIn("산출물 밖 공백", body)

    def test_노드는_싱크_앞에_기각보관_검토전개를_둔다(self):
        system = (SKILL / "references" / "검증_체제.md").read_text(encoding="utf-8")
        contract = (SKILL / "계약" / "검증런.md").read_text(encoding="utf-8")
        template = (SKILL / "기각보관_검토전개.md").read_text(encoding="utf-8")
        self.assertIn("기각 보관", system)
        self.assertIn("노드 싱크 직전", system)
        self.assertIn("기각 보관:", contract)
        self.assertIn("역할: 기각보관검토", template)
        self.assertIn("기각·병합·타당", template)
        self.assertIn("다음 검토전개를 반복할 실익", template)

    def test_선택지_설명문은_사용자_확정_문면이_아니다(self):
        duty = (SKILL / "전거" / "의무.md").read_text(encoding="utf-8")
        form = (SKILL / "references" / "서식.md").read_text(encoding="utf-8")
        self.assertIn("선택지의 「결정 효과」 전문은 확정 문면", duty)
        self.assertIn("선택지 설명문을 사용자 발화로 기록하지 않는다", duty)
        self.assertIn("응답 방식: {직접 규범을 담은 자유 입력 | 선택}", form)
        self.assertIn("구현 세부는 사용자 확정 문면이 아니다", form)

    def test_codex_완료_대기_스크립트와_절차가_verify_rounds와_같다(self):
        local_wait = SKILL / "scripts" / "wait_outputs.py"
        verify_wait = SKILL.parent / "verify-rounds" / "scripts" / "wait_outputs.py"
        self.assertTrue(local_wait.is_file())
        self.assertEqual(local_wait.read_bytes(), verify_wait.read_bytes())

        procedure = (SKILL / "references" / "배정.md").read_text(encoding="utf-8")
        self.assertIn(
            "python .agents/skills/do-dag/scripts/wait_outputs.py <반환 절대 경로 ...>",
            procedure,
        )
        self.assertIn("exit 0", procedure)
        self.assertIn("exit 3", procedure)
        self.assertIn("같은 호출을 다시", procedure)


if __name__ == "__main__":
    unittest.main(verbosity=1)

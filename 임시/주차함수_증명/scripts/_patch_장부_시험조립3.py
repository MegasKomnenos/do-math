# -*- coding: utf-8 -*-
"""작업 장부: 셋째 시험 조립(열세 조각 전부)과 잔존 정리의 재개들을 적는다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "작업_장부.md")
s = io.open(P, encoding="utf-8").read()

ENTRY = (
    "- 2026-11-13 01:2x **셋째 시험 조립**(열세 조각 전부; `대조v2/_시험조립_0113.md`): 라벨 432 전부 해소(중복 0), 부록 D 47항목, [todo] 0. 불변식 실패 3 — 5B 머리 둘 「증명됨, 계산 보조(방향 반올림 구간)」(함께 둘 수 없음; 5B 재개에 포함), 부록 B 부재(생성 전). 예약 글자 잔존: 10장 705행 가족 매개변수 $a$($ak^{2/3}$ 등)와 문턱 $h_0$(old-8-14 증명 (5)) → 10장 집필자(a35b8fce3db7355bd) 재개; 5A 94행 $\\mathcal Y(a)$ 하나 → 세션 패치($\\mathrm{sh}'$); 5B 266행 $a:=Y+j+1$(41회)·766행 $b$·부록 D 104행 $a$ → 5B 재개에 포함; 7B 33행 $\\min(h,k)$·868행 $b$·부록 D 5행 $(c,Y,R,\\ast)$의 $b$·$c$ → 7B 재개(회수: $h_i$ 꼴, $i$, $\\mathrm{cf}$·$\\mathrm{wt}$ + 「코드의 변수」 대응); 7A 부록 D5 보충분의 $h$·$a$·$b$·$c$·$l$ → 7A 재개 중. 부록 A 예행: 본문 미출현 1.2 행 2($\\mathrm{Gr}(x)$, $\\mathrm{km}_N$; 최종 정리에서 삭제), 식별자 83개. "
    "다음: 5B·7A·10장 마무리 회수 → 설계 에이전트 최종 정리(`파견/장부v2_최종정리_지시.md`) → `_patch_9장_2차대조.py` 재적용·4절 재생성 → `명세v2_빌드.py --check --briefs` → 조립·불변식·부록 A·B·C·자료 묶음 → 11장 → 일관성 검토."
)
old = "\n## 재개 기록\n"
assert s.count(old) == 1
if "**셋째 시험 조립**" not in s:
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
s = s.replace("(열세 조각 전부 2차 대조·반영 완료; 5B의 5A 전역 글자 회피 한 번만 진행)", "(열세 조각 전부 2차 대조·반영 완료; 잔존 정리 — 5B 글자·지위, 7A 부록 D5 글자, 10장 $a$·$h_0$ — 진행)")
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 작업_장부.md (셋째 시험 조립)")

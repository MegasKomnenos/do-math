# -*- coding: utf-8 -*-
"""작업_장부.md 「현재 상태」에 18:2x 줄(6차 수리 회수·파이프라인·7차 파견)을 17:2x 줄 뒤에 넣고, 「기록」 절 끝에 항목을 더한다."""
import io, sys
P = r"C:\math\임시\주차함수_증명\작업_장부.md"
with io.open(P, encoding="utf-8") as f:
    lines = f.read().split("\n")
idx = None
for i, ln in enumerate(lines[:40]):
    if ln.startswith("- 17:2x 6차 독립 검토 회수"):
        idx = i
if idx is None:
    print("17:2x 줄 없음"); sys.exit(1)
if not any(ln.startswith("- 18:2x 6차 수리 회수") for ln in lines[:40]):
    new = ("- 18:2x 6차 수리 회수·파이프라인·7차 파견(이 세션): W1–W10·WD(두 단계)·W11·WL 열셋 회수(보고·인계 `대조v2/수학검사2/수리_전체6_*.md`·`인계_전체6_*.md`; 사안별 결정과 큰 변경은 결정 110 — 정리 5-1 머리에 column-lemma 의존, psi-two-sided 두 단계 상계, 7A 범위 「행 n≥16」, 2-38·2-39 첫째 증명 고유 입력, 「띠 전파」→「비 전파」·「비 비교」, 「깊은 자식」 7.7절, jensen-lower 인용·fb(λ), lemma-ell 6.2절 이동, 4.3절 z·σ→τ, 5B old-5-23·𝒥_j, 7B 연쇄 명시·국소 N, 부록 D 수치·서식·자료 사실, 부록 A·C 이력 문구 삭제). "
           "파이프라인 18:24: 4절 이름 1(「비 전파」), 11.2 5열 1·6열 4, 재실행표 42, 조립 2,306,175바이트·11,074행·라벨 404·부록 D 42, 의존지도 404·뺌 47·입력 379·순환 0·상호 인용 13, 불변식·괄호·지위·조사 0, 자리표시자 0, 잔재 의존지도 옛 기록 둘, 자료묶음 554·1094·문제 0(r690be93의 `published_algebra.py`·`certify_concavity.py` 새로 복사), README 재생성, `_재실행표_여유.json` 0.21347·「비 비교」 정정 뒤 재실행표 재생성, 스냅샷 27조각 18:25, KaTeX 배경(`_katex_1824.log`). "
           "7차 독립 검토 M1–M14(열다섯; 이력 비공개; `파견/전체_독립검토7_파견문_1115.md`) 18:3x 파견. 회수되면 같은 방식(판정 없이 수리자 직접 판단)으로 X 물결 수리 → 파이프라인 → 8차 … 바꿀 것이 없을 때까지.")
    lines.insert(idx + 1, new)
try:
    j = lines.index("## 재개 기록")
except ValueError:
    print("재개 기록 없음"); sys.exit(1)
key = "**전체 독립 검토 6차 수리 회수·파이프라인·7차 검토 파견(M1–M14)**"
if not any(key in ln for ln in lines):
    entry = ("- 2026-11-15 17:2x–18:3x " + key + ": 열셋 회수(W1 5자리, W2 6, W3 4, W4 6, W5 7, W6 6, W7 23, W8 8, W9 4, W10 6, WD 26, W11 6, WL 75). 결정 110. 파이프라인·검사·스냅샷·README는 「현재 상태」 18:2x 줄. 7차 M1–M14 파견.")
    k = j
    while k > 0 and lines[k - 1].strip() == "":
        k -= 1
    lines.insert(k, entry)
with io.open(P, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))
print("장부 갱신 완료")

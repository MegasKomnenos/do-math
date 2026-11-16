# -*- coding: utf-8 -*-
"""작업_장부.md 「현재 상태」에 17:2x 줄(6차 검토 회수·W 파견)을 16:3x 줄 뒤에 넣고, 「기록」 절 끝에 항목을 더한다."""
import io, sys
P = r"C:\math\임시\주차함수_증명\작업_장부.md"
with io.open(P, encoding="utf-8") as f:
    lines = f.read().split("\n")
idx = None
for i, ln in enumerate(lines[:40]):
    if ln.startswith("- 16:3x 5차 수리 회수"):
        idx = i
if idx is None:
    print("16:3x 줄 없음"); sys.exit(1)
if not any(ln.startswith("- 17:2x 6차 독립 검토 회수") for ln in lines[:40]):
    new = ("- 17:2x 6차 독립 검토 회수·수리 파견(이 세션): L1–L14(열다섯; L7a·L7b) 16:5x–17:2x 전부 회수(`대조v2/수학검사2/검토전체6_L*.md`) — 수학 0; 검토자 셈으로 사실 5·정합 25·문면 24; 사용자 판단으로 올린 것 아홉. "
           "큰 것: 7A 머리말·236행의 범위 서술이 행 $n\\le15$에서 거짓(L6); head-sum-1이 부르는 psi-two-sided 상계의 꼴이 상수 $0.85108$에 닿음(L9); 정리 2-38·2-39의 입력 귀속 세 자리 어긋남(L1); jensen-lower †가 정리 chain-expansion(가)의 중복 증명(L8); 부록 A·C의 편집 이력 문구(L11); 「띠」 낱말(L13); 8.4 되먹임 인자의 임시 변수 $\\theta$(L8); D.5 숫자는 계산 세션의 잠정 채움(L12 1항 — WD 손대지 않음). "
           "사용자 지시대로 판정 문서 없이 `파견/전체검토6_수리_공통_1115.md`(1절 방식·선호 원문·선례, 2절 배정표, 3절 서식, 4절 임자·주의 메모)로 W1–W10·WD 열하나 17:2x 병행 파견(gp-fable-high; WD 두 단계). 뒤 단계 안내 `_W11_`·`_WL_` 작성, 7차 파견문 `파견/전체_독립검토7_파견문_1115.md`(태그 M) 준비. "
           "세션 직접: `_sync_4절이름.py`를 「기록의 이름」 열까지 맞추도록 넓힘(L14-2·3: critical-front·2-38 행), 의존지도 생성기는 이미 패치. 회수 뒤 W11·WL → 파이프라인 → 7차.")
    lines.insert(idx + 1, new)
try:
    j = lines.index("## 재개 기록")
except ValueError:
    print("재개 기록 없음"); sys.exit(1)
key = "**전체 독립 검토 6차 회수·수리 파견(W1–W10·WD)**"
if not any(key in ln for ln in lines):
    entry = ("- 2026-11-15 16:4x–17:2x " + key + ": L1–L14 열다섯 회수(수학 0, 사실 5·정합 25·문면 24). 판정 문서 없이 작업자가 보고를 직접 판단하는 6차 수리 공통 안내(배정 메모 4절 포함)로 W1–W10·WD 파견; W11·WL 안내와 7차 파견문 준비; 4절 동기화 스크립트 확장.")
    k = j
    while k > 0 and lines[k - 1].strip() == "":
        k -= 1
    lines.insert(k, entry)
with io.open(P, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))
print("장부 갱신 완료")

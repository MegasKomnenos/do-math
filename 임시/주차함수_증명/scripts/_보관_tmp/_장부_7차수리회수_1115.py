# -*- coding: utf-8 -*-
"""작업_장부.md 「현재 상태」에 20:3x 줄(7차 수리 회수·파이프라인·8차 파견)을 19:3x 줄 뒤에 넣고, 「기록」 절 끝에 항목을 더한다."""
import io, sys
P = r"C:\math\임시\주차함수_증명\작업_장부.md"
with io.open(P, encoding="utf-8") as f:
    lines = f.read().split("\n")
idx = None
for i, ln in enumerate(lines[:40]):
    if ln.startswith("- 19:3x 7차 독립 검토 회수"):
        idx = i
if idx is None:
    print("19:3x 줄 없음"); sys.exit(1)
if not any(ln.startswith("- 20:3x 7차 수리 회수") for ln in lines[:40]):
    new = ("- 20:3x 7차 수리 회수·파이프라인·8차 파견(이 세션): X1–X10·XD(두 단계)·X11·XL 열셋 회수(보고·인계 `대조v2/수학검사2/수리_전체7_*.md`·`인계_전체7_*.md`; 결정과 큰 변경은 결정 111 — 수학 둘의 근거 보강(analytic-transfer $k$-단조성, D.xcert $\\varsigma$ 하계), 2-30 모든 $n$ 부등식·blocked-majorant † 제거, 1.5절 지위 표 둘로(X1; 결정 9·86과 글자로 어긋남 — 사용자 알림), hermite-nu 범위 좁힘·둘째 판정 삭제, 8장·6장 머리 부분 표지, 10장 「작성자 판단」 둘, 「기록의 첫째/둘째 작성자·검토」 낱말, 「점질량」·「귀납의 출발」·「내림 몫」 등). "
           "파이프라인 20:32–20:33: 11.2 5열 3·6열 21, 재실행표 42, 조립 2,316,726바이트·11,072행·라벨 404·부록 D 42, 의존지도 404·입력 380·머리 순환 0(hermite-nu 머리의 analytic-transfer 라벨 참조를 풀어 해소)·상호 인용 13, 불변식·괄호·지위·조사 0, 자리표시자 0, 자료묶음 559·1120·문제 0, README 재생성(SHA: `xcert_iv/summarize.py`·`summary.json`·`summary.txt` 갱신 — `min_interior_sL` 기록), 스냅샷 27조각 20:33, KaTeX 배경(`_katex_2032.log`). "
           "세션 직접: 장9 564행 centroid-stop(나) 라벨 인용, README 635행 「내림·올림」, `xcert_iv/summarize.py` 안쪽 하계 기록·재실행. "
           "8차 독립 검토 N1–N14(열다섯; 이력 비공개; `파견/전체_독립검토8_파견문_1115.md`) 20:3x 파견. 회수되면 같은 방식으로 Y 물결(`파견/전체검토8_수리_공통_1115.md` 준비됨) → 파이프라인 → 9차 … 바꿀 것이 없을 때까지.")
    lines.insert(idx + 1, new)
try:
    j = lines.index("## 재개 기록")
except ValueError:
    print("재개 기록 없음"); sys.exit(1)
key = "**전체 독립 검토 7차 수리 회수·파이프라인·8차 검토 파견(N1–N14)**"
if not any(key in ln for ln in lines):
    entry = ("- 2026-11-15 19:3x–20:3x " + key + ": 열셋 회수(X1 7자리, X2 5, X3 7, X4 7, X5 6, X6 4, X7 13, X8 11, X9 3, X10 7, XD 66, X11 9, XL 53). 결정 111. 파이프라인·검사·스냅샷·README는 「현재 상태」 20:3x 줄. 8차 N1–N14 파견.")
    k = j
    while k > 0 and lines[k - 1].strip() == "":
        k -= 1
    lines.insert(k, entry)
with io.open(P, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))
print("장부 갱신 완료")

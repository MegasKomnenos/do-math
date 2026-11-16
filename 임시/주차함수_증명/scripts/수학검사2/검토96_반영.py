# -*- coding: utf-8 -*-
"""결정 96 반영의 독립 검토 넷(보고 `대조v2/수학검사2/검토_결정96_{A,B,C,D}.md`)에서 받아들인 지적의 반영. 새 문장이 이미 있으면 건너뛰고,
없을 때만 앵커가 한 번 맞는 자리를 치환한다(멱등). 코드 쪽(ivio.dec 바깥 넓힘 H2, summarize.py 라벨, 패치 스크립트 논리)은 따로 고쳤다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D5A = "장v2/부록D_장5A.md"
D8 = "장v2/부록D_장8.md"
DEC = "대조v2/장부_설계_세션결정.md"
RM = "원고_자료/README.md"

EDITS = [
    # ---- A: D.15 ----
    (D5A, "양 끝 $1.4$·$10$도 $10^{-15}$ 안쪽까지만 덮는다($k=125j^3$인 정수 입력은 그 틈에 정확히 든다).",
     "양 끝 $1.4$·$10$도 $2\\times10^{-15}$ 안쪽까지만 덮는다($k=125j^3$, $r+1=5j^2(7+i)$인 정수 입력이 틈이 난 $18$개 격자점에 정확히 놓인다)."),
    (D5A, "같은 다섯 상자의 첫 셀을 기록과 같은 방식($\\hat{\\mathrm{Wr}}_j$·$\\hat{\\mathfrak J}$를 $\\mathrm{ku}$ 반쪽 상자 둘의 합집합으로 좁히고 $\\mathrm{cw}=0.1$, A29는 $[1.4,1.8]$)으로도 다시 인증했다(최소 여유 각각 [D15:재인증여유]; [D15:재인증시간]).",
     "같은 다섯 상자의 첫 셀을 기록의 재인증 방식($\\hat{\\mathrm{Wr}}_j$·$\\hat{\\mathfrak J}$를 $\\mathrm{ku}$ 반쪽 상자 둘의 합집합으로 좁힘)으로도 다시 인증했다(셀 폭 $0.1$, A29는 $[1.4,1.8]$; 기록의 재인증은 셀 폭 $0.08$·$0.067$; 최소 여유 각각 [D15:재인증여유]; [D15:재인증시간])."),
    (D5A, "**산술 등급.** 방향 반올림 구간(mpmath.iv, 30자리). 급수는 명시적 꼬리와 함께 자른다.",
     "**산술 등급.** 방향 반올림 구간(mpmath.iv, 30자리). 급수는 명시적 꼬리와 함께 자른다. 상자 자료는 상자별 캐시(JSON, 17자리 십진 문자열)에 저장해 재사용하며, 읽을 때 양 끝을 상대 $2^{-48}$ 바깥으로 넓혀 둘러싸기를 유지한다."),
    (D5A, "`verify_exact_cover.py`, `verify_exact_cover_out.txt`: 검증기(정확 유리수); `launch_rerun.py`: 작업자 기동기).",
     "`verify_exact_cover.py`, `verify_exact_cover_out.txt`: 검증기(정확 유리수); `launch_rerun.py`, `rerun_launches.txt`: 작업자 기동기와 기동 기록; `_test_exact_grid.py`: 두 셀 시험; `v1_floatgrid/`: binary64 격자로 돌린 앞선 실행의 인증서·로그·검증기)."),
    # ---- B: D.35, D.36, D.37 ----
    (D8, "$\\varsigma$ ($\\varsigma\\ge0.1$)를 곱한 표를 왼쪽부터의",
     "$\\varsigma$ ($\\varsigma\\ge0.1$)(상수 $0.04$, $0.12$와 $\\mathfrak e$의 $0.1$은 binary64 값)를 곱한 표를 왼쪽부터의"),
    (D8, "($p_i'\\le0$의 끝값과 꼭짓점 검사)", "($p_i'\\le0$의 끝값·꼭짓점 검사; 3차 계수의 괄호가 $0$을 걸치는 조각은 보수적 상계)"),
    (D8, "$\\Omega$의 하계는 기록의 binary64 함수보다 최대 $1.1\\times10^{-14}$ 낮다(`test_lib_out.txt`).",
     "$2\\times10^5$개 표본점에서 $\\Omega$의 하계는 기록의 binary64 함수보다 $1.1\\times10^{-14}$ 이내로 낮다(`test_lib_out.txt`)."),
    (D8, "출력 `bprime_result.txt`, `tail_out.txt`, `checks_out.txt`, `test_lib_out.txt`(기록의 binary64 $\\Omega$·$\\hat{\\mathcal T}$와의 대조),",
     "출력 `bprime_result.txt`, `tail_out.txt`, `checks_out.txt`, `test_lib.py`→`test_lib_out.txt`(기록의 binary64 $\\Omega$·$\\hat{\\mathcal T}$와의 대조), 재실행 순서 `세션_재계산/rerun_omega_h1.sh`, 앞선 판(binary64 PCHIP을 읽던 $\\Omega$)의 라이브러리와 출력 `ivbox_lib_v1_binary64omega.py`·`v1_binary64omega/`,"),
    (D8, "`box_N_…`), 기록 대조 `compare_record.py`, `compare_record_out.txt`.",
     "`box_N_…`), 기록 대조 `compare_record.py`, `compare_record_out.txt`; 재실행 순서 `세션_재계산/rerun_omega_h1.sh`, 앞선 판의 출력 `v1_binary64omega/`."),
    # ---- C: 5.73 †, 장3, 장9 ----
    ("장v2/장5B.md", "피적분함수와 그 $\\eta$-도함수들은 공통 지배함수 $\\varrho^{2m+2j}\\min(1,8\\varrho^{-2})e^{-\\eta_0\\varrho^2/2}$($j\\ge0$; 원점에서 유계, 꼬리에서 Gauss 감쇠)를 가져",
     "피적분함수의 $j$차 $\\eta$-도함수($j\\ge0$)는 $\\eta$에 무관한 지배함수 $\\varrho^{2m+2j}\\min(1,8\\varrho^{-2})e^{-\\eta_0\\varrho^2/2}$(원점에서 유계, 꼬리에서 Gauss 감쇠)를 가져"),
    ("장v2/장3.md", "을 만족하고, 이 하한은 $n^{1/3}/4$ 규모로", "을 만족하고, 이 하계는 $n^{1/3}/4$ 규모로"),
    ("장v2/장9.md", "대신 그 상한 $\\mathfrak e\\bigl((1+2\\vartheta)/(1+\\vartheta)\\bigr)^{3/2}$", "대신 그 상계 $\\mathfrak e\\bigl((1+2\\vartheta)/(1+\\vartheta)\\bigr)^{3/2}$"),
    # ---- 결정 96 본문 ----
    (DEC, "$k=125j^3$의 정수 입력이 틈에 정확히 든다.", "$k=125j^3$, $r+1=5j^2(7+i)$인 정수 입력이 틈이 난 18개 격자점에 정확히 놓인다."),
    (DEC, "그대로 둔다(상자 자료 캐시 재사용).", "그대로 둔다. 상자 자료 캐시(17자리 십진으로 저장)는 그대로 읽으면 끝이 안쪽으로 $10^{-16}$ 들어올 수 있어, 읽을 때 양 끝을 상대 $2^{-48}$ 바깥으로 넓혀 재사용한다(H2; 검토 A의 지적)."),
    (DEC, "D.17·D.19·D.39의 하계 뜻 「하한」→「하계」", "D.17·D.19의 하계 뜻 「하한」→「하계」"),
    (DEC, "7.6의 「꼭대기 거리 지표의 상한」→「상계」.", "7.6의 「꼭대기 거리 지표의 상한」→「상계」. 검토 뒤 보충(18:5x): 3장 「이 하계는 $n^{1/3}/4$ 규모」, 9.4 「그 상계」; 부록 B의 기록 제목 「명시적 하한」은 그대로."),
    # ---- README ----
    (RM, "(그 격자는 격자점 18곳에서 폭 $10^{-15}$ 이하의 틈을 남긴다)", "(그 격자는 격자점 18곳에서 폭 $1.1\\times10^{-15}$ 이하의 틈을 남긴다)"),
    (RM, "아직 끝나지 않은 계산이 걸린 항목(지금은 `D.{{D:xcert-partAB}}` 하나)의 칸은 「(진행 중)」이다.",
     "아직 끝나지 않은 계산이 걸린 항목이 있으면 그 칸을 「(진행 중)」으로 둔다(지금은 없다; 끝나야 아는 값은 `[Dn:이름]` 자리표시자)."),
    ("scripts/_patch_README_세션파일.py", "(그 격자는 격자점 18곳에서 폭 $10^{-15}$ 이하의 틈을 남긴다)", "(그 격자는 격자점 18곳에서 폭 $1.1\\\\times10^{-15}$ 이하의 틈을 남긴다)"),
]

n = 0
for rel, old, new in EDITS:
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    if new in s:
        continue
    c = s.count(old)
    if c == 1:
        s = s.replace(old, new)
        io.open(p, "w", encoding="utf-8", newline="\n").write(s)
        n += 1
    else:
        print("앵커 수", c, rel, old[:60])
print("치환", n)

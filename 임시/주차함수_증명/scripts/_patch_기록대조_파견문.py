# -*- coding: utf-8 -*-
"""기록 대조 파견문에 세션 결정 뒤의 입력 셋과 확인 요 셋을 더한다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "파견", "장부v2_기록대조_파견문.md")
s = io.open(P, encoding="utf-8").read()

old1 = "- `C:\\math\\임시\\주차함수_증명\\파견\\명세v2_출처목록.md`:"
new1 = (
    "- `C:\\math\\임시\\주차함수_증명\\대조v2\\장부_설계_세션결정.md`와 `대조v2\\장부_설계_반영.md`: 결정록 4절에 대한 세션의 답(열셋)과 세션이 더한 결정 다섯(나무 크기 변수 $t$, $A^{(t)}_N$, 5.5의 국소 수준 좌표, 1장 전역 기호의 국소 재사용 금지, $\\mathrm{flat}_k(t)$), 그리고 반영 결과. 사전의 현행은 이 결정이 반영된 `장부_v2.md`다.\n"
    + old1
)
assert s.count(old1) == 1
s = s.replace(old1, new1)

old2 = "$F_m(x)$·$\\sigma_\\ell(m)$, $W_x(C)$, $B_N$, $P_{<k}$)은 빠짐없이 판정을 적는다."
new2 = (
    "$F_m(x)$·$\\sigma_\\ell(m)$, $W_x(C)$, $B_N$, $P_{<k}$)은 빠짐없이 판정을 적는다. "
    "이 가운데 셋은 사전 설계가 기록 원문을 열지 않아 판정하지 못하고 1.3에 「확인 요」로 남긴 것이다: [r79ee9e0]의 $F_m(x)$·$\\sigma_\\ell(m)$(2.8의 분포함수인가, 머묾 질량 $\\varsigma$의 첨자를 바꾼 것인가), 조사3·6의 $W_x(C)$(첫 판 5.28 증명의 $W_v$와 같은 양인가), [r37c204b]의 $P_{<k}$(첫 판 6.4의 $P_k$와 같은 양인가). 이 셋은 기록 원문으로 반드시 판정한다. "
    "또 사전이 허용한 두 예외(바탕 글자 $d$: 변수 $d$·$d_i$·$d_{n,k}$; 바탕 글자 $x$: 좌표 $x$·$\\hat x$와 함수 $x_t(y)$)는 설계 결정이므로 어긋남으로 적지 않는다."
)
assert s.count(old2) == 1
s = s.replace(old2, new2)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched", P)

# -*- coding: utf-8 -*-
"""외부 피드백(2026-11-14 둘째 묶음) 본문 셋: 명제 10.5 부호 문장의 조건화(정리 6.62는 k>=3131), 보조정리 5.73 (다)의 지배함수,
D.30 (7)(ㄱ) 작은 기울기 대체의 정당화. 앵커가 한 번만 맞을 때 치환, 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EDITS = [
    ("장v2/장10.md",
     "정리 {{6:V-all}}의 (V), 곧 모든 $m\\in[k,2k]$에서 $\\mathcal V_k(m)\\ge0$으로 $\\mathcal X_n\\ge0$이고, $N<m\\le2k$에서",
     "판정 $\\mathsf V$, 곧 모든 $m\\in[k,2k]$에서 $\\mathcal V_k(m)\\ge0$이 성립하면 $\\mathcal X_n\\ge0$이고(정리 {{6:V-all}}에 따라 $k\\ge3131$에서 성립한다), $N<m\\le2k$에서"),
    ("장v2/장5B.md",
     "† (나)에서 피적분함수가 $8\\varrho^{2m-2}e^{-\\eta\\varrho^2/2}$로 지배되므로 $\\eta$에 대해 적분 기호 안에서 미분할 수 있고, ",
     "† (가)에서 $|1-\\varrho\\mathcal D|\\le1$이고 (나)에서 $|1-\\varrho\\mathcal D|\\le8\\varrho^{-2}$이므로, $\\eta\\ge\\eta_0>0$에서 피적분함수와 그 $\\eta$-도함수들은 공통 지배함수 $\\varrho^{2m+2j}\\min(1,8\\varrho^{-2})e^{-\\eta_0\\varrho^2/2}$($j\\ge0$; 원점에서 유계, 꼬리에서 Gauss 감쇠)를 가져 $\\eta$에 대해 적분 기호 안에서 미분할 수 있고, "),
    ("장v2/부록D_장7A.md",
     "($|\\mathfrak s_\\ell|\\le10^{-14}$이면 비 대신 $\\mathrm{st}$; $\\varsigma$가 구간이면",
     "($|\\mathfrak s_\\ell|\\le10^{-14}$이면 비 대신 $\\mathrm{st}$를 쓴다. $\\mathfrak s_\\ell>0$이면 비가 $\\mathrm{st}$보다 크지만 그 차는 상대 $\\mathfrak s_\\ell\\mathrm{st}\\,e^{\\mathfrak s_\\ell\\mathrm{st}}/2<2\\times10^{-15}$(인수 $\\varsigma\\le12$, $\\mathrm{st}\\le0.3$)이고, 기록 코드가 이 항에 곱하는 인자 $(1+10^{-12})^2$에 든다. 이 글의 구간 재계산은 $(e^z-1)/z$의 둘러싸기로 평가해 이 분기가 없다. $\\varsigma$가 구간이면"),
]

n = 0
for rel, old, new in EDITS:
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    c = s.count(old)
    if c == 1:
        s = s.replace(old, new)
        io.open(p, "w", encoding="utf-8", newline="\n").write(s)
        n += 1
        print("고침", rel, old[:40])
    elif new in s:
        print("이미", rel, old[:40])
    else:
        print("앵커 수", c, rel, old[:40])
print("치환", n)

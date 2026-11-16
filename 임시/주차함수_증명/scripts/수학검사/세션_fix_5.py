# -*- coding: utf-8 -*-
"""외부 지적(보조정리 5.41/조립 5.77의 C_I 대 부록 D.21): 부록 식 줄의 음의 항이 υ^5·υ^6으로 적혀 있으나 본문 정의(646행)에
u=ρ^2(ρ^3dρ=u du/2)를 넣으면 ½(υ^10 I_1+υ^12/4 I_2)이다. 수치: 본문 정의 C_I(1)=√π(6−23√2)=−47.0177, 부록 표기대로면 +6.6924,
고친 식이면 −47.0177(세션 mpmath 재계산; 기록 r5f5cf73 §6 「−N_0C_1(1)=46√2−12」와 일치). 또 I_i의 적분 변수를 ρ로 적어 원래 ρ와 섞이던 것을 u로 적고,
수식 안의 한글(「(ㄴ)으로 적분한」)을 밖으로 뺀다(KaTeX 경고 1건 해소). 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "장v2", "부록D_장5B.md")
OLD = ("$\\mathfrak C_{\\mathrm I}(\\eta)=8\\sqrt{2\\pi}\\,\\eta^{-3}(1+\\eta)^{-3/2}-\\frac{2(1+\\eta)}3\\bigl[\\text{(ㄴ)으로 적분한 } \\upsilon^4\\cdot\\tfrac12(\\upsilon\\,\\mathfrak I_1(\\upsilon)+\\tfrac{\\upsilon^2}4\\mathfrak I_2(\\upsilon))\\bigr]$, "
       "$\\mathfrak I_i(\\upsilon)=\\int_0^1\\rho(1-\\rho)^ie^{-\\upsilon^2\\rho/2}d\\rho$.")
NEW = ("$\\mathfrak C_{\\mathrm I}(\\eta)=8\\sqrt{2\\pi}\\,\\eta^{-3}(1+\\eta)^{-3/2}-\\frac{2(1+\\eta)}3\\int_0^\\infty\\tfrac12\\bigl(\\upsilon^{10}\\,\\mathfrak I_1(\\upsilon)+\\tfrac{\\upsilon^{12}}4\\mathfrak I_2(\\upsilon)\\bigr)e^{-\\eta\\upsilon^2/2}d\\upsilon$, "
       "$\\mathfrak I_i(\\upsilon)=\\int_0^1u(1-u)^ie^{-\\upsilon^2u/2}du$($u=\\rho^2$; 둘째 항은 (ㄴ)으로 적분한다).")
s = io.open(P, encoding="utf-8").read()
c = s.count(OLD)
if c == 1:
    s = s.replace(OLD, NEW); io.open(P, "w", encoding="utf-8", newline="\n").write(s); print("고침 1")
elif NEW in s:
    print("이미")
else:
    print("앵커 수", c)

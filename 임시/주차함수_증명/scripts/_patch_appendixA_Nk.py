# -*- coding: utf-8 -*-
"""부록 A의 3장·4장 표에 4.3절 정규화 상수 N_k·N_∞ 행을 더한다(독해 3 수리 A (4))."""
import io

p = "임시/주차함수_증명/장/부록A.md"
lines = io.open(p, encoding="utf-8").read().split("\n")
idx = None
for i, ln in enumerate(lines):
    if ln.startswith(r"| $\mathcal A_{k,n}$, $\mathcal M_r$, $\mathcal I_k$"):
        idx = i
        break
assert idx is not None
row = r"| $N_k$, $N_\infty$ | 4.3절 중앙 틈 증명의 정규화 상수 $N_k=\frac{n!}{p_n}\cdot(\dots)$와 그 극한 $N_\infty=2/\sqrt\pi$. 6.2절의 열별 증가 문턱 $N_k$, 정리 {{old:정리 3.4}}의 비명시 문턱 $N_0$과 다른 양(구별 문장은 4.3절) | 4.3 | 기록 [rce3dc75]는 극한을 $N_0$으로 적음 |"
lines.insert(idx + 1, row)
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("부록 A: N_k·N_∞ 행 추가")

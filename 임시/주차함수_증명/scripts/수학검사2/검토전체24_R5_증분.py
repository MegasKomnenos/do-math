# 검토전체24 R5: 6.5절 721행의 설명 "두 계수의 차 inc^- - inc^+ 는 각 계수보다 작다" 확인
from math import log
def g(x): return (x - 1) * log(1 + 1 / x)
worst = 0.0; arg = None
for y0 in range(2, 301):
    for d in range(2, y0 + 2):
        for q in range(1, d):
            im = g(y0 - 1 + d) - g(y0 - 1 + q)
            ip = g(y0 + d) - g(y0 + q)
            r = (im - ip) / ip
            if r > worst: worst = r; arg = (y0, d, q)
print("max (inc^- - inc^+)/inc^+ =", worst, arg)

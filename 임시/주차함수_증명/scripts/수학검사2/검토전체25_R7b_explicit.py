# -*- coding: utf-8 -*-
# 검토전체25 R7b: 보조정리 explicit-bounds 두 상계와 sg_m 상계, 증명 속 로그 항등식의 수치 검산
from math import log, exp, lgamma
def logP(m, j):
    return (log(j) + lgamma(m) - lgamma(j) - lgamma(m - j + 1) + ((j - 2) * log(j) if j > 1 else 0.0)
            + ((m - j - 1) * log(m - j + 1) if m - j > 0 else 0.0) - (m - 1) * log(m + 1))
logBor = lambda d: -d + (d - 1) * log(d) - lgamma(d + 1)
logRen = lambda j: -j + (j - 1) * log(j) - lgamma(j)
worst1 = worst2 = worst3 = -1e9; idfail = 0
for m in list(range(1, 80)) + [150, 400, 904, 3000]:
    J = 1 / (m + 1)
    sg = m * log(m / (m + 1)) + 1
    worst3 = max(worst3, sg - (1 / (2 * (m + 1)) + 1 / (6 * m * (m + 1))))
    for U in range(0, m):
        lhs = logP(m, m - U) - logBor(U + 1)
        ident = (U + 1) + sum(log(1 - i * J) for i in range(2, U + 2)) + (m - U - 1) * log(1 - (U + 1) * J)
        if abs(lhs - ident) > 1e-8 * max(1, abs(lhs)):
            idfail += 1
        worst1 = max(worst1, lhs - (sg + log((m + 1) / (m - U))))
    for j in range(1, m + 1):
        lhs = logP(m, j) - logRen(j)
        ident = -log(m + 1) + j + sum(log(1 - i * J) for i in range(2, j + 1)) + (m - j - 1) * log(1 - j * J)
        if abs(lhs - ident) > 1e-8 * max(1, abs(lhs)):
            idfail += 1
        worst2 = max(worst2, lhs - (sg + log(m + 1) - 2 * log(m + 1 - j)))
print("max(log lhs - log rhs): first=%.3e second=%.3e sg-bound=%.3e  identity failures=%d" % (worst1, worst2, worst3, idfail))

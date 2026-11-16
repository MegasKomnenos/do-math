# K7a: 명제 pair-check-10000 검산 — (7.11) 우변, k=10000, q+q'+j<=50, 경우 수와 최솟값
from fractions import Fraction as F
k = 10000
def pis(q): return F(q*(q-1), 2*(k+1))
def exbar(q):
    p = pis(q); return q + (k+q)*p/(1-p)
cnt = 0; best = None
for q in range(1, 50):
    for qp in range(q, 50):
        for j in range(0, 51-q-qp):
            if q+qp+j > 50: break
            cnt += 1
            rhs = 1 - F(j,k)*(exbar(q)+exbar(qp)) - (exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if best is None or rhs < best[0]: best = (rhs, (q,qp,j))
print("cases", cnt)
print("min", float(best[0]), best[1], "positive:", best[0] > 0)

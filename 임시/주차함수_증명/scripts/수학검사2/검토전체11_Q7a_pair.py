# 검토전체11 Q7a: 명제 pair-check-10000 — 경우 수 10725, (7.11) 우변 최솟값 자리 (1,33,16), 값 > 0.0492 를 정확 유리수로 확인
from fractions import Fraction as F
k = 10000
def pis(q): return F(q*(q-1), 2*(k+1))
def exbar(q):
    p = pis(q); return q + (k+q)*p/(1-p)
cnt = 0; best = None
for q in range(1, 50):
    for qp in range(q, 50):
        for j in range(0, 51-q-qp):
            cnt += 1
            rhs = 1 - F(j,k)*(exbar(q)+exbar(qp)) - (exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if best is None or rhs < best[0]: best = (rhs, q, qp, j)
print("count (q<=q'):", cnt)
print("min rhs:", float(best[0]), "at (q,q',j)=", best[1:], " > 0.0492 ?", best[0] > F(492,10000))
# 모든 경우 양수?

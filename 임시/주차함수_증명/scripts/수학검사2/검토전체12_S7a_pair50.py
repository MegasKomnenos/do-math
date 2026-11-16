# (7.11) 우변을 k=10000, q+q'+j<=50 에서 정확 유리수로 평가; 경우 수와 최솟값
from fractions import Fraction as F
k=10000
def pish(q): return F(q*(q-1),2*(k+1))
def exbar(q):
    p=pish(q); return q+(k+q)*p/(1-p)
cnt=0; mn=None; arg=None
for q in range(1,50):
    for qp in range(q,50):
        for j in range(0,51-q-qp):
            cnt+=1
            v=1-F(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if mn is None or v<mn: mn=v; arg=(q,qp,j)
print(cnt, arg, float(mn))

# 명제 pair-check-10000: k=10000, q+q'+j<=50, (7.11) 우변 양수인지와 개우 수·최솟값 확인(배정밀도 근사)
from fractions import Fraction as Fr
k=10000
def pis(q): return Fr(q*(q-1),2*(k+1))
def exbar(q):
    p=pis(q); return q+(k+q)*p/(1-p)
cnt=0; mn=None; arg=None
for q in range(1,49):
    for qp in range(q,51-q):
        jmax=50-q-qp
        for j in range(0,jmax+1):
            cnt+=1
            rhs=1-Fr(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if mn is None or rhs<mn: mn=rhs; arg=(q,qp,j)
print("count",cnt,"min",float(mn),"at",arg)

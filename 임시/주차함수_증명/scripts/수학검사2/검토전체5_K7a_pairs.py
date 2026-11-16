# K7a 검산: 7.4절 쌍별 판정 (7.11)의 경우 수와 최솟값(k=10000, 껍질 50), 꼬리 삼중 (7.12), 표의 nu_P(K_1)
from fractions import Fraction as F
import math

def pi_sharp(q,k): return F(q*(q-1), 2*(k+1))
def ex_bar(q,k):
    p=pi_sharp(q,k); return q+(k+q)*p/(1-p)
def rhs711(q,qp,j,k):
    return 1-F(j,k)*(ex_bar(q,k)+ex_bar(qp,k))-(ex_bar(q,k)*(qp-1)+ex_bar(qp,k)*(q-1))/(2*k)

k=10000; cnt=0; mn=None; arg=None
for q in range(1,51):
    for qp in range(q,51):
        for j in range(0,51-q-qp):
            cnt+=1
            v=rhs711(q,qp,j,k)
            if mn is None or v<mn: mn=v; arg=(q,qp,j)
print("cases",cnt,"min",float(mn),arg, "all positive:", mn>0)

# Borel mass
def Bor(m): return math.exp(-m+(m-1)*math.log(m)-math.lgamma(m+1))
def kebar(M,K1):
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
def F712(q,C,kb):
    s=sum(Bor(s1+1)*((q-1-s1)+C*(q-1-s1)**1.5) for s1 in range(0,q-1))
    return C*q**1.5-math.exp(kb)*s
triples=[(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]
for K1,M,C in triples:
    kb=kebar(M,K1)
    worst=min(F712(q,C,kb) for q in range(2,M+1))
    print("triple",K1,M,C,"kebar",round(kb,6),"min F",worst, "C*M^1.5",C*M**1.5)

# nu_P table
def lb(q,qp,j,k,M,C):
    def nhat(q): return 0.0 if q==1 else C*q**1.5/k
    def exh(q): n=nhat(q); return q+(k+q)*n/(1-n)
    return 1-j/k*(exh(q)+exh(qp))-(exh(q)*(qp-1)+exh(qp)*(q-1))/(2*k)
table={12000:(120,0.54),13000:(120,0.54),14000:(120,0.54),15000:(120,0.54),20000:(120,0.54),30000:(250,0.593),50000:(250,0.593),100000:(300,0.522),200000:(450,0.548),500000:(450,0.548),10**6:(700,0.519)}
for K1,(M,C) in table.items():
    nu=1
    while True:
        ok=True
        if nu-1>M: ok=False
        else:
            for q in range(1,nu):
                qp_max=nu-q
                for qp in range(1,qp_max+1):
                    j=nu-q-qp
                    if lb(q,qp,j,K1,M,C)<=0: ok=False;break
                if not ok: break
        if not ok: break
        nu+=1
    print("K1",K1,"nu_P",nu-1)

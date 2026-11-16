# L13: D.band102-integer (ㄱ)(ㄷ) 재계산
from fractions import Fraction as F
import math
k=10000
def pish(q): return F(q*(q-1),2*(k+1))
def exb(q): p=pish(q); return q+(k+q)*p/(1-p)
best=None
for q in range(1,51):
    for qp in range(q,51):
        for j in range(0,51-q-qp):
            v=1-F(j,k)*(exb(q)+exb(qp))-(exb(q)*(qp-1)+exb(qp)*(q-1))/(2*k)
            if best is None or v<best[0]: best=(v,(q,qp,j))
print("(ㄱ) min", float(best[0]), best[1])
# (ㄷ) lb_K1 with nhat_q = C q^{3/2}/K1
def nuP(K1,M,C):
    def nh(q): return 0.0 if q==1 else C*q**1.5/K1
    def ex(q): n=nh(q); return q+(K1+q)*n/(1-n)
    ex_cache={q:ex(q) for q in range(1,M+2)}
    nu=2; prev=None
    while True:
        mn=None
        for q in range(1,min(M,nu-1)+1):
            for qp in range(q,min(M,nu-q)+1):
                j=nu-q-qp
                if j<0: continue
                v=1-(j/K1)*(ex_cache[q]+ex_cache[qp])-(ex_cache[q]*(qp-1)+ex_cache[qp]*(q-1))/(2*K1)
                if mn is None or v<mn[0]: mn=(v,(q,qp,j))
        if mn is not None and mn[0]<=0: return nu-1, prev, mn
        prev=mn; nu+=1
for K1,M,C in ((12000,120,0.54),(15000,120,0.54),(20000,120,0.54),(30000,250,0.593)):
    print(K1, nuP(K1,M,C))

# (ㄴ) F_C(q)
import math
def Bor(m): return math.exp((m-1)*math.log(m)-m-math.lgamma(m+1))
def keb(K1,M): 
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
for K1,M,C in ((10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)):
    ke=keb(K1,M); mn=None
    for q in range(2,M+1):
        s=sum(Bor(s+1)*((q-1-s)+C*(q-1-s)**1.5) for s in range(0,q-1))
        Fq=C*q**1.5-math.exp(ke)*s
        rel=Fq/(C*q**1.5)
        if mn is None or rel<mn[0]: mn=(rel,q)
    print("(ㄴ)",K1,M,C,"ke=%.4f"%ke,"min rel %.3e at q=%d"%mn)

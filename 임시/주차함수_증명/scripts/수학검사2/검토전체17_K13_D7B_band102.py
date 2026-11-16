# K13: recompute (ㄱ)(ㄴ)(ㄷ) of D.band102-integer
from fractions import Fraction as F
from math import factorial, exp, sqrt
import numpy as np
# (ㄱ) k=10000 exact
k=10000
def exq(q):
    pi=F(q*(q-1),2*(k+1)); return q+(k+q)*pi/(1-pi)
EX={q:exq(q) for q in range(1,51)}
best=None;cnt=0
for q in range(1,50):
    for qp in range(q,51-q):
        for j in range(0,51-q-qp):
            cnt+=1
            v=1-F(j,k)*(EX[q]+EX[qp])-(EX[q]*(qp-1)+EX[qp]*(q-1))/(2*k)
            if best is None or v<best[0]: best=(v,(q,qp,j))
print('(ㄱ) count',cnt,'min',float(best[0]),best[1])
# (ㄴ) F_tf
from math import lgamma, log
def Bor(m): return exp(-m+(m-1)*log(m)-lgamma(m+1))
for K1,M,tf in [(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]:
    ke=3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
    mins=min((tf*q**1.5-exp(ke)*sum(Bor(s+1)*((q-1-s)+tf*(q-1-s)**1.5) for s in range(q-1)))/(tf*q**1.5) for q in range(2,M+1))
    argm=min(range(2,M+1),key=lambda q:(tf*q**1.5-exp(ke)*sum(Bor(s+1)*((q-1-s)+tf*(q-1-s)**1.5) for s in range(q-1)))/(tf*q**1.5))
    print('(ㄴ)',K1,M,tf,'ke=%.4f'%ke,'min rel=%.3e at q=%d'%(mins,argm))
# (ㄷ) nu_P scan with floats
def hat_ex(q,K1,tf):
    q=np.asarray(q,dtype=float); n=np.where(q>=2,tf*q**1.5/K1,0.0); return q+(K1+q)*n/(1-n)
for K1,M,tf in [(12000,120,.54),(13000,120,.54),(14000,120,.54),(15000,120,.54),(20000,120,.54),(30000,250,.593),(50000,250,.593),(100000,300,.522),(200000,450,.548),(500000,450,.548),(1000000,700,.519)]:
    nuP=None; prev=None
    for nu in range(2,M*2+2):
        q=np.arange(1,nu); qp=nu-q  # j=0 shell? lb decreasing in j, worst at max j for given (q,qp) sum... scan all j
        worst=(1e9,None)
        for j in range(0,nu-1):
            qs=np.arange(1,nu-j); qps=nu-j-qs
            m=qs<=qps
            qs=qs[m]; qps=qps[m]
            if len(qs)==0: continue
            if qs.max()>M or qps.max()>M: continue
            lb=1-j/K1*(hat_ex(qs,K1,tf)+hat_ex(qps,K1,tf))-(hat_ex(qs,K1,tf)*(qps-1)+hat_ex(qps,K1,tf)*(qs-1))/(2*K1)
            i=lb.argmin()
            if lb[i]<worst[0]: worst=(lb[i],(int(qs[i]),int(qps[i]),j))
        if worst[0]<0: nuP=nu-1; print('(ㄷ)',K1,'nu_P=',nuP,'worst at nu_P',prev,'min at nu_P+1 %.4f'%worst[0]); break
        prev=('%.4f'%worst[0],worst[1])

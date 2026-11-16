from fractions import Fraction as Fr
import math
from mpmath import mp, mpf, e as E, sqrt as msqrt, exp as mexp, factorial as mfac
mp.dps=40
# (ㄱ) k=10000 shell<=50
k=10000
def exbar(q): 
    p=Fr(q*(q-1),2*(k+1)); return q+(k+q)*p/(1-p)
best=None;cnt=0;ordered=0
for q in range(1,50):
    for qp in range(q,50):
        for j in range(0,50-q-qp+1):
            cnt+=1; ordered+= 1 if q==qp else 2
            v=1-Fr(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/Fr(2*k)
            if best is None or v<best[0]: best=(v,(q,qp,j))
print("(ㄱ) count",cnt,"ordered",ordered,"min",float(best[0]),best[1])
# (ㄴ) five triples
def Bor(m): return mexp(-m)*mpf(m)**(m-1)/mfac(m)
for K1,M,tf in ((10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)):
    tf=mpf(tf); ke=mpf(3*(M-1))/(2*(K1+1))+mpf((M-1)*(3*M-4))/(12*(K1+1)**2)+mpf((M-1)**2)/(2*(K1+1)*(K1+2-M))+mpf((M-1)**4)/(12*(K1+1)**2*(K1+2-M))
    worst=None
    for q in range(2,M+1):
        F=tf*mpf(q)**1.5-mexp(ke)*sum(Bor(s+1)*((q-1-s)+tf*mpf(q-1-s)**1.5) for s in range(0,q-1))
        r=F/(tf*mpf(q)**1.5)
        if worst is None or r<worst[0]: worst=(r,q)
    print("(ㄴ)",K1,M,float(tf),"ke=%.4f"%ke,"min rel margin %.3e at q=%d"%(float(worst[0]),worst[1]))
# (ㄷ) lb at listed worst points and shells
def lb(K1,M,tf,q,qp,j):
    def nh(q): return mpf(0) if q==1 else tf*mpf(q)**1.5/K1
    def exh(q): return q+(K1+q)*nh(q)/(1-nh(q))
    return 1-mpf(j)/K1*(exh(q)+exh(qp))-(exh(q)*(qp-1)+exh(qp)*(q-1))/(2*K1)
tab=[(12000,120,0.54,93,(36,36,21)),(13000,120,0.54,96,(37,37,22)),(14000,120,0.54,99,(38,38,23)),(15000,120,0.54,102,(39,40,23)),(20000,120,0.54,115,(44,45,26)),(30000,250,0.593,132,(51,52,29)),(50000,250,0.593,164,(64,64,36)),(100000,300,0.522,228,(89,89,50)),(200000,450,0.548,298,(117,117,64)),(500000,450,0.548,435,(171,171,93)),(10**6,700,0.519,590,(232,233,125))]
for K1,M,tf,nu,w in tab:
    tf=mpf(tf)
    def shellmin(nu):
        m=None
        for q in range(1,min(M,nu-1)+1):
            for qp in range(q,min(M,nu-q)+1):
                j=nu-q-qp
                if j<0: continue
                v=lb(K1,M,tf,q,qp,j)
                if m is None or v<m[0]: m=(v,(q,qp,j))
        return m
    a=shellmin(nu); b=shellmin(nu+1)
    print("(ㄷ)",K1,"shell",nu,"min lb %.4f at %s"%(float(a[0]),a[1]),"| listed",w,"%.4f"%float(lb(K1,M,tf,*w)),"| shell+1 min %.4f"%float(b[0]))

# E13: D.band102-integer (ㄱ)(ㄴ)(ㄷ)(ㅁ)의 수 재계산
from fractions import Fraction as F
import math
# (ㄱ)
k=10000
def exbar(q):
    pi=F(q*(q-1),2*(k+1)); return q+(k+q)*pi/(1-pi)
cnt=0; cnt_ord=0; mn=(10,None)
for q in range(1,51):
    for qp in range(q,51):
        for j in range(0,51-q-qp):
            cnt+=1; cnt_ord+= 1 if q==qp else 2
            v=1-F(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if v<mn[0]: mn=(v,(q,qp,j))
print('(ㄱ)',cnt,cnt_ord,float(mn[0]),mn[1])
# (ㄴ)
def Bor(m): return math.exp((m-1)*math.log(m)-m-math.lgamma(m+1))
def kebar(K1,M):
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
for K1,M,tf in [(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]:
    ke=kebar(K1,M); worst=(1,None)
    for q in range(2,M+1):
        Fq=tf*q**1.5-math.exp(ke)*sum(Bor(s+1)*((q-1-s)+tf*(q-1-s)**1.5) for s in range(0,q-1))
        r=Fq/(tf*q**1.5)
        if r<worst[0]: worst=(r,q)
    print('(ㄴ)',K1,M,tf,'ke=%.4f'%ke,'minrel=%.3e at q=%d'%worst, 'tfM^1.5=%.0f'%(tf*M**1.5))
# (ㄷ)
def nuP(K1,M,tf):
    k=K1
    def exh(q):
        if q==1: return 1.0
        n=tf*q**1.5/k; return q+(k+q)*n/(1-n)
    def lb(q,qp,j): return 1-j/k*(exh(q)+exh(qp))-(exh(q)*(qp-1)+exh(qp)*(q-1))/(2*k)
    def shell_min(nu):
        best=(10,None)
        for q in range(1,min(M,nu-1)+1):
            for qp in range(q,min(M,nu-q)+1):
                j=nu-q-qp
                if j<0: continue
                v=lb(q,qp,j)
                if v<best[0]: best=(v,(q,qp,j))
        return best
    nu=2
    while True:
        m=shell_min(nu)
        if m[0]<=0: return nu-1, shell_min(nu-1), m
        nu+=1
tab=[(12000,120,0.54),(13000,120,0.54),(14000,120,0.54),(15000,120,0.54),(20000,120,0.54),(30000,250,0.593),(50000,250,0.593),(10**5,300,0.522),(2*10**5,450,0.548),(5*10**5,450,0.548),(10**6,700,0.519)]
for K1,M,tf in tab:
    nP,a,b=nuP(K1,M,tf)
    print('(ㄷ)',K1,'nuP=',nP,'worst',a[1],'%.4f'%a[0],'next min %.4f'%b[0])
# (ㅁ)
r2=sum(2*k+40-max(20001,2*k+1)+1 for k in range(9981,11100))
r3=sum(max(0,58-max(41,20001-2*k)+1) for k in range(9972,12000))
r4=sum(max(0,102-max(59,20001-2*k)+1) for k in range(9950,12000))
r4b=sum(max(0,102-max(41,20001-2*k)+1) for k in range(9950,12000))
print('(ㅁ)',r2,r3,r4,r4b, 11099-9981+1, 11999-9972+1, 11999-9950+1)

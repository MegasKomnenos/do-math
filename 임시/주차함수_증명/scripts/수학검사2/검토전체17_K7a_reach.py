# K7a: 명제 pair-reach-table 검산 — (7.12) 꼬리 삼중과 nu_P(K1) (부동소수점 점검; 정본은 부록 D의 정확 유리수)
import math
def Bor(j): return math.exp(-j+(j-1)*math.log(j)-math.lgamma(j+1))
def kebar(K1,M):
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
def tail_ok(K1,M,tf):
    kb=math.exp(kebar(K1,M)); worst=None
    for q in range(2,M+1):
        v=tf*q**1.5-kb*sum(Bor(s+1)*((q-1-s)+tf*(q-1-s)**1.5) for s in range(0,q-1))
        if worst is None or v<worst[0]: worst=(v,q)
    return worst
triples=[(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]
for t in triples: print("tail", t, "min F =", tail_ok(*t), "tf*M^1.5 =", round(t[2]*t[1]**1.5))
def nuP(K1,M,tf):
    k=K1
    def exh(q):
        if q==1: return 1.0
        n=tf*q**1.5/k; return q+(k+q)*n/(1-n)
    def lb(q,qp,j): return 1-j/k*(exh(q)+exh(qp))-(exh(q)*(qp-1)+exh(qp)*(q-1))/(2*k)
    nu=1
    while True:
        nxt=nu+1
        if nxt>M+1: return nu
        ok=True
        for q in range(1,nxt):
            for qp in range(1,nxt-q+1):
                j=nxt-q-qp
                if lb(q,qp,j)<=0: ok=False;break
            if not ok: break
        if not ok: return nu
        nu=nxt
cols=[(12000,120,0.54),(13000,120,0.54),(14000,120,0.54),(15000,120,0.54),(20000,120,0.54),(30000,250,0.593),(50000,250,0.593),(10**5,300,0.522),(2*10**5,450,0.548),(5*10**5,450,0.548),(10**6,700,0.519)]
print([ (c[0],nuP(*c)) for c in cols])

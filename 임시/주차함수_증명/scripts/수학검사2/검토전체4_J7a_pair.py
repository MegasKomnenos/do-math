# J7a: 7.4절 쌍별 판정·꼬리 삼중·닿은 껍질의 수치 재계산 (부동소수점; 부호와 자릿수 확인용)
import math
def rhs711(k,q,qp,j):
    def exbar(q):
        ps=q*(q-1)/(2*(k+1)); return q+(k+q)*ps/(1-ps)
    return 1-(j/k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
k=10000; cnt=0; best=(9,None)
for q in range(1,50):
    for qp in range(q,50):
        for j in range(0,51-q-qp):
            cnt+=1; v=rhs711(k,q,qp,j)
            if v<best[0]: best=(v,(q,qp,j))
print("count q<=q' :",cnt," min:",best)
# ordered count
print("ordered count:", sum(1 for q in range(1,50) for qp in range(1,50) for j in range(0,51-q-qp)))
def Bor(w): return math.exp(-w+(w-1)*math.log(w)-math.lgamma(w+1))
def kebar(K1,M):
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
def F(C,q,ke):
    return C*q**1.5-math.exp(ke)*sum(Bor(s+1)*((q-1-s)+C*(q-1-s)**1.5) for s in range(0,q-1))
triples=[(9950,120,0.54),(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]
for K1,M,C in triples:
    ke=kebar(K1,M); mn=min(F(C,q,ke)/(C*q**1.5) for q in range(2,M+1))
    print("triple",K1,M,C," kebar=%.4f"%ke," min rel margin=%.3e"%mn," C*M^1.5=%.0f"%(C*M**1.5))
def lb(k,M,C,q,qp,j):
    def exhat(q):
        if q==1: return 1.0
        n=C*q**1.5/k; return q+(k+q)*n/(1-n)
    return 1-(j/k)*(exhat(q)+exhat(qp))-(exhat(q)*(qp-1)+exhat(qp)*(q-1))/(2*k)
cols=[(12000,120,0.54),(13000,120,0.54),(14000,120,0.54),(15000,120,0.54),(20000,120,0.54),(30000,250,0.593),(50000,250,0.593),(10**5,300,0.522),(2*10**5,450,0.548),(5*10**5,450,0.548),(10**6,700,0.519)]
for K1,M,C in cols:
    nu=1; last=0; worst=None
    while True:
        ok=True; w=(9,None)
        for q in range(1,nu):
            for qp in range(q,nu-q+1):
                j=nu-q-qp
                if j<0: continue
                if q>M or qp>M: ok=False; break
                v=lb(K1,M,C,q,qp,j)
                if v<w[0]: w=(v,(q,qp,j))
                if v<=0: ok=False
            if not ok: break
        if not ok: break
        last=nu; worst=w; nu+=1
    print("K1",K1,"nuP",last,"worst",worst)

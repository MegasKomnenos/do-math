# (7.12) 꼬리 삼중 확인(배정밀도)과 pair-reach-table의 nu_P 재현(배정밀도 훑기; 표의 열 셋)
import math
def Bor(m): return math.exp(-m+(m-1)*math.log(m)-math.lgamma(m+1))
def kebar(K1,M):
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
def F(tf,q,kb):
    return tf*q**1.5-math.exp(kb)*sum(Bor(s+1)*((q-1-s)+tf*(q-1-s)**1.5) for s in range(0,q-1))
triples=[(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]
for K1,M,tf in triples:
    kb=kebar(K1,M); mn=min(F(tf,q,kb)/(tf*q**1.5) for q in range(2,M+1))
    print('triple',K1,M,tf,'kebar=%.4f'%kb,'min rel margin=%.3g'%mn, 'tf*M^1.5=%.0f'%(tf*M**1.5))
def nuP(K1,M,tf):
    def nh(q): return 0.0 if q==1 else tf*q**1.5/K1
    def exh(q): n=nh(q); return q+(K1+q)*n/(1-n)
    def lb(q,qp,j): return 1-j/K1*(exh(q)+exh(qp))-(exh(q)*(qp-1)+exh(qp)*(q-1))/(2*K1)
    nu=2
    while True:
        ok=True
        for q in range(1,nu):
            for qp in range(q,nu-q+1):
                j=nu-q-qp
                if q>M or qp>M or lb(q,qp,j)<=0: ok=False;break
            if not ok: break
        if not ok: return nu-1
        nu+=1
for K1,(M,tf) in [(12000,(120,0.54)),(15000,(120,0.54)),(20000,(120,0.54)),(30000,(250,0.593)),(10**5,(300,0.522)),(10**6,(700,0.519))]:
    print('K1',K1,'nu_P',nuP(K1,M,tf))

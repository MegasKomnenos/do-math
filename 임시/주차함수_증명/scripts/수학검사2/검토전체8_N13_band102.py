# D.band102-integer (ㄱ)(ㄴ)(ㄷ)의 수치를 정확 유리수/고정밀로 다시 센다.
import sys, io, math
from fractions import Fraction as F
from decimal import Decimal, getcontext
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
getcontext().prec = 50
# (ㄱ) k=10000, pi#_q = q(q-1)/(2(k+1)), ex_q = q+(k+q)pi/(1-pi), rhs = 1 - j/k(ex_q+ex_q') - [ex_q(q'-1)+ex_q'(q-1)]/(2k)
k = 10000
def exbar(q):
    pi = F(q*(q-1), 2*(k+1)); return q + (k+q)*pi/(1-pi)
best = None; cnt=0
for q in range(1,51):
    for qp in range(q,51):
        for j in range(0, 51-q-qp):
            cnt+=1
            v = 1 - F(j,k)*(exbar(q)+exbar(qp)) - (exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if best is None or v < best[0]: best=(v,(q,qp,j))
print("(ㄱ) cases", cnt, "min", float(best[0]), best[1])
# (ㄴ) F_C(q) with Bor(s+1) = (s+1)^(s-1) e^{-(s+1)}/s!
def kebar(K1,M):
    return F(3*(M-1),2*(K1+1)) + F((M-1)*(3*M-4),12*(K1+1)**2) + F((M-1)**2,2*(K1+1)*(K1+2-M)) + F((M-1)**4,12*(K1+1)**2*(K1+2-M))
E = Decimal(1).exp()
def Bor(m):  # Decimal
    return Decimal(m)**(m-1) * (-Decimal(m)).exp() / Decimal(math.factorial(m))
import functools
@functools.lru_cache(None)
def borD(m): return Bor(m)
for (K1,M,C) in [(10**4,120,Decimal('0.54')),(2*10**4,250,Decimal('0.593')),(10**5,300,Decimal('0.522')),(10**5,450,Decimal('0.548')),(10**6,700,Decimal('0.519'))]:
    kb = kebar(K1,M); ekb = (Decimal(kb.numerator)/Decimal(kb.denominator)).exp()
    minrel=None
    for q in range(2,M+1):
        s_ = sum(borD(s+1)*(Decimal(q-1-s)+C*Decimal(q-1-s)**Decimal('1.5')) for s in range(0,q-1))
        Fq = C*Decimal(q)**Decimal('1.5') - ekb*s_
        rel = Fq/(C*Decimal(q)**Decimal('1.5'))
        if minrel is None or rel<minrel[0]: minrel=(rel,q)
    print("(ㄴ)",K1,M,C,"kebar=%.4f"%float(kb),"min rel margin %.3e at q=%d"%(float(minrel[0]),minrel[1]))
# (ㄷ) lb_K1 for the eleven K1 at shells nu_P and nu_P+1
tbl=[(12000,120,F(54,100),93),(13000,120,F(54,100),96),(14000,120,F(54,100),99),(15000,120,F(54,100),102),(20000,120,F(54,100),115),(30000,250,F(593,1000),132),(50000,250,F(593,1000),164),(10**5,300,F(522,1000),228),(2*10**5,450,F(548,1000),298),(5*10**5,450,F(548,1000),435),(10**6,700,F(519,1000),590)]
getcontext().prec = 40
def q32(q): return Decimal(q)**Decimal('1.5')
for (K1,M,C,nuP) in tbl:
    Cd = Decimal(C.numerator)/Decimal(C.denominator)
    def exhat(q):
        if q==1: return Decimal(1)
        n = Cd*q32(q)/Decimal(K1); return Decimal(q)+(Decimal(K1)+q)*n/(1-n)
    def lb(q,qp,j):
        return 1 - Decimal(j)/Decimal(K1)*(exhat(q)+exhat(qp)) - (exhat(q)*(qp-1)+exhat(qp)*(q-1))/(2*Decimal(K1))
    res=[]
    for nu in (nuP, nuP+1):
        worst=None
        for q in range(1, min(M,nu-1)+1):
            for qp in range(q, min(M,nu-q)+1):
                j = nu-q-qp
                if j<0: continue
                v = lb(q,qp,j)
                if worst is None or v<worst[0]: worst=(v,(q,qp,j))
        res.append((nu, float(worst[0]), worst[1]))
    print("(ㄷ)",K1,res)

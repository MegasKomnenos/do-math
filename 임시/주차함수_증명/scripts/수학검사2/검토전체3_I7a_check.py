from fractions import Fraction as Fr
import math
# (1) pair-check-10000 count and min of (7.12) RHS
k=10000
def pish(q): return Fr(q*(q-1),2*(k+1))
def exbar(q):
    p=pish(q); return q+(k+q)*p/(1-p)
cnt=0; best=None
for q in range(1,51):
    for qp in range(q,51):
        for j in range(0,51-q-qp):
            cnt+=1
            v=1-Fr(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if best is None or v<best[0]: best=(v,q,qp,j)
print("pair-check count",cnt,"min",float(best[0]),best[1:])
# (2) n_X(2002), n_M ratios
print("nX(2002)=",math.ceil(2002**(4/3)), 2002**(4/3))
print("nM ratios",20507/841**1.5, 73032/2000**1.5)
# (3) tail triple check (float) for (9950,120,0.54) and (10^6,700,0.519)
def Bor(m): return math.exp(-m+(m-1)*math.log(m)-math.lgamma(m+1))
def kebar(K1,M):
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
for (K1,M,C) in [(9950,120,0.54),(10**6,700,0.519),(10**5,300,0.522)]:
    kb=kebar(K1,M); mn=1e9
    for q in range(2,M+1):
        F=C*q**1.5-math.exp(kb)*sum(Bor(s+1)*((q-1-s)+C*(q-1-s)**1.5) for s in range(0,q-1))
        mn=min(mn,F)
    print("tail triple",K1,M,C,"min F",mn)
# (4) lb reach for K1=15000 with (120,0.54) and K1=12000
def reach(K1,M,C):
    k=K1
    def nh(q): return 0 if q==1 else C*q**1.5/k
    def exh(q): return q+(k+q)*nh(q)/(1-nh(q))
    nu=1
    while True:
        ok=True
        for q in range(1,nu):
            for qp in range(q,nu-q+1):
                j=nu-q-qp
                if j<0: continue
                if q>M or qp>M: ok=False; break
                lb=1-j/k*(exh(q)+exh(qp))-(exh(q)*(qp-1)+exh(qp)*(q-1))/(2*k)
                if lb<=0: ok=False; break
            if not ok: break
        if not ok: return nu-1
        nu+=1
for K1,M,C in [(12000,120,0.54),(15000,120,0.54),(20000,120,0.54),(10**6,700,0.519)]:
    print("reach",K1,reach(K1,M,C))
# (5) integer-strips counts
a=sum(max(0,2*k+40-max(20001,2*k+1)+1) for k in range(9981,11100))
b=sum(max(0,2*k+102-max(2*k+41,20001)+1) for k in range(9950,12000))
c=1000*(102-59+1)+1000*(102-80+1)+1000*(102-96+1)
print("strips",a,b+c)
# (6) pole-PD numbers
print(2*math.exp(-5.3146*0.6996), 0.3**1.5/2, 0.0821*math.exp(-3/25233), 0.7*2001/2002)

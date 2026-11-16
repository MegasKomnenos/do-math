from fractions import Fraction as F
import math
k=10000
def pish(q): return F(q*(q-1),2*(k+1))
def exbar(q):
    p=pish(q); return q+(k+q)*p/(1-p)
cnt=0; mn=None; arg=None
for q in range(1,50):
    for qp in range(q,50):
        for j in range(0,51-q-qp):
            cnt+=1
            v=1-F(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if mn is None or v<mn: mn=v; arg=(q,qp,j)
print("count",cnt,"min",float(mn),arg)
# ordered count
print("ordered", sum(1 for q in range(1,50) for qp in range(1,50) for j in range(0,51-q-qp)))
# ke-bar values
def kebar(K1,M):
    return 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
for K1,M,C in [(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]:
    print(K1,M,C,"kebar",round(kebar(K1,M),5),"C M^1.5",round(C*M**1.5,1))
# tail triple check (float) for first triple
def Bor(m): return math.exp(-m+(m-1)*math.log(m)-math.lgamma(m+1))
for K1,M,C in [(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]:
    kb=math.exp(kebar(K1,M)); worst=None
    for q in range(2,M+1):
        s=sum(Bor(s+1)*((q-1-s)+C*(q-1-s)**1.5) for s in range(0,q-1))
        Fq=C*q**1.5-kb*s
        rel=Fq/(C*q**1.5)
        if worst is None or rel<worst[0]: worst=(rel,q)
    print("triple",K1,M,C,"min rel margin",worst)
print("nX(2002)=",math.ceil(2002**(4/3)), 2002**(4/3))
print("0.8165*841^1.5",0.8165*841**1.5, "20507/841^1.5",20507/841**1.5,"73032/2000^1.5",73032/2000**1.5)
print("2e^{-5.3146*0.6996}",2*math.exp(-5.3146*0.6996),"0.3^1.5/2",0.3**1.5/2,"0.0821*e^{-3/25233}",0.0821*math.exp(-3/25233))
print("0.7*2001/2002",0.7*2001/2002)
print("nM>2k+1 check k=841:",0.8165*841**1.5,2*841+1)

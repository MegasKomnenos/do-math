from fractions import Fraction as F
from math import exp, factorial
k=10000
def ex(q):
    p=F(q*(q-1),2*(k+1)); return q+(k+q)*p/(1-p)
cnt=0; cnt_ord=0; mn=(10,None)
for q in range(1,51):
    for qp in range(q,51):
        for j in range(0,51-q-qp):
            cnt+=1; cnt_ord+= 1 if q==qp else 2
            v=1-F(j,k)*(ex(q)+ex(qp))-(ex(q)*(qp-1)+ex(qp)*(q-1))/(2*k)
            if v<mn[0]: mn=(v,(q,qp,j))
print("count unordered",cnt,"ordered",cnt_ord,"min",float(mn[0]),mn[1])
# (ㄴ) approximate with given ke values
def Bor(m): return exp(-m)*m**(m-1)/factorial(m)
for (K1,M,C,ke) in ((10**4,120,0.54,0.0180),(2*10**4,250,0.593,0.0188),(10**5,300,0.522,0.0045),(10**5,450,0.548,0.0068),(10**6,700,0.519,0.0010)):
    best=None
    for q in range(2,M+1):
        Fq=C*q**1.5-exp(ke)*sum(Bor(s+1)*((q-1-s)+C*(q-1-s)**1.5) for s in range(0,q-1))
        r=Fq/(C*q**1.5)
        if best is None or r<best[0]: best=(r,q)
    print(K1,M,C,"min rel margin",best)

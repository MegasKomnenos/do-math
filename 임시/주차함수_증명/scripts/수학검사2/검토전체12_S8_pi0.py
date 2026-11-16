# pi^0_n(y)=Pr_n(G<=y) 가 n에 비증가인지 소규모 확인 (해석 문단 점검)
from fractions import Fraction
from math import factorial
def pi0(n,y):
    # EGF exp(sum_{t<=y} t^{t-1} x^t/t!) 의 x^n 계수 * n! / p_n
    T=[Fraction(0)]*(n+1)
    for t in range(1,min(y,n)+1): T[t]=Fraction(t**(t-1),factorial(t))
    E=[Fraction(0)]*(n+1); E[0]=Fraction(1)
    # E' = T' E
    for m in range(1,n+1):
        s=Fraction(0)
        for t in range(1,m+1): s+=t*T[t]*E[m-t]
        E[m]=s/m
    pn=(n+1)**(n-1)
    return E[n]*factorial(n)/pn
for y in (3,5,8):
    vals=[pi0(n,y) for n in range(1,2*y+3)]
    mono=all(vals[i]>=vals[i+1] for i in range(len(vals)-1))
    print(y, mono, [float(v) for v in vals])

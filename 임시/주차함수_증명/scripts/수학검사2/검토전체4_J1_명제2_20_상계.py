# J1 검산: 명제 2-20의 유한 n 상계값 (n=17,100,1000,10^4). 정확 유리수(n<=1000)와 mpmath(10^4).
from fractions import Fraction as Fr
from math import comb, factorial
import mpmath as mp
mp.mp.dps = 40

def vk(k,Z,H):
    return (1+Fr(1,k))**Z + (1-Fr(1,k))**(Z+H) - 2

def bound_exact(n):
    best=None
    pn = (n+1)**(n-1)
    cs = [c for c in range(n//2+1, n+1)]  # c > n/2
    for b in range(3, n+1):
        # 조건: 3<=i<=b, n/2<k<=n 에서 v_k(i-1,1)<0
        ok = all(vk(k,i-1,1) < 0 for i in range(3,b+1) for k in cs)
        if not ok: break
        s1=Fr(0); s2=Fr(0)
        for c in cs:
            kap = n-c-b+1
            if kap<0: continue
            pref = Fr(factorial(n)*c**(c-1), factorial(c)*pn)
            s1 += pref*b*Fr(n-c+1)**(n-c-b)/factorial(kap)
            s2 += pref*2*Fr(n-c-b+3)**(n-c-b)/factorial(kap)
        val = 1 - s1 + s2
        if best is None or val<best[0]: best=(val,b)
    return best

def bound_mp(n):
    best=None
    lnpn = (n-1)*mp.log(n+1)
    cs = range(n//2+1, n+1)
    for b in range(3, 60):
        ok = all(((1+mp.mpf(1)/k)**(i-1) + (1-mp.mpf(1)/k)**i - 2) < 0 for i in range(3,b+1) for k in (n//2+1, n))
        # v_k(Z,1)는 k에 대해 단조? 안전하게 전 범위 검사 (느리면 끝점만) -> 전 범위 검사
        ok = all(((1+mp.mpf(1)/k)**(i-1) + (1-mp.mpf(1)/k)**i - 2) < 0 for i in range(3,b+1) for k in cs) if ok else False
        if not ok: break
        s1=mp.mpf(0); s2=mp.mpf(0)
        for c in cs:
            kap=n-c-b+1
            if kap<0: continue
            lpref = mp.loggamma(n+1)+(c-1)*mp.log(c)-mp.loggamma(c+1)-lnpn - mp.loggamma(kap+1)
            s1 += mp.e**(lpref + mp.log(b) + (n-c-b)*mp.log(n-c+1))
            s2 += mp.e**(lpref + mp.log(2) + (n-c-b)*mp.log(n-c-b+3))
        val = 1-s1+s2
        if best is None or val<best[0]: best=(val,b)
    return best

for n in (17,100,1000):
    v,b = bound_exact(n); print(n, "b*=",b, "상계=", float(v))
v,b = bound_mp(10000); print(10000, "b*=",b, "상계=", mp.nstr(v,6))

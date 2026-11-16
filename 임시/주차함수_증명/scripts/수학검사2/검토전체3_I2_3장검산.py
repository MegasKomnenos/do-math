# 검토전체3 I2: 3장 수치 검산
from fractions import Fraction as Fr
from math import gamma, sqrt, pi
import math

# (1) 멜린 변환 식의 독립 검증: E[B] = 2/3 sqrt(2/pi) (B = int_0^1 sup B), 꼬리 상수 3/sqrt(2pi)
def mellin(s):
    return (1.5)**(s/3)*gamma(1+2*s/3)*gamma(5/6-s/3)/gamma(5/6)*gamma(0.5-s/3)*gamma(2/3)/(gamma(0.5)*gamma(2/3-s/3))
# E X^sigma = Gamma(1+2sigma/3) E B^{-2sigma/3}  -> E B^s at s=1 : sigma=-3/2 ... 극 근처라 직접 못 씀; 대신 s=1 은 sigma=-3/2 인데 Gamma(1+2sigma/3)=Gamma(0) 극.
# 그래서 E B^s = mellin(-3s/2)/gamma(1-s) 로 극한 처리: s=1에서 gamma(1-s) 극이 상쇄. s->1 극한을 수치로.
for s in (0.999999, 0.9999999):
    sig=-1.5*s
    val=mellin(sig)/gamma(1+2*sig/3)
    print("E[B^s] s=",s, val, " 참값 2/3*sqrt(2/pi)=", 2/3*sqrt(2/pi))
# 꼬리 상수: (3/2-sigma) E X^sigma -> 3/sqrt(2pi) as sigma->3/2
for sig in (1.4999, 1.499999):
    print("(3/2-s)EX^s=", (1.5-sig)*mellin(sig), " 참값 3/sqrt(2pi)=", 3/sqrt(2*pi))
print("mellin(0)=", mellin(0))
# Legendre: Gamma(1/3)Gamma(5/6) = 2^{1/3} sqrt(pi) Gamma(2/3)
print("Legendre:", gamma(1/3)*gamma(5/6), 2**(1/3)*sqrt(pi)*gamma(2/3))
# (3/4)^{3/2}
print("(3/4)^1.5=", 0.75**1.5, " 2^-3*3^1.5=", 3**1.5/8)

# (2) 정리 3-6의 유리수
lam=Fr(751,1000); J=8
val=lam**J + Fr(1,31)*sum(i*lam**(i-1) for i in range(1,J+1)) + Fr(1,1000)*sum((i-1)*lam**(i-1) for i in range(1,J+1))
print("s_n(k) 상계 =", val, float(val), val==Fr(7309649993107890414228499,15500000000000000000000000))
# lambda <= 3/4 + 3/(4n) 검사 n>=1000
assert all(Fr(math.ceil(3*n/4),n) <= Fr(3,4)+Fr(3,4*n) for n in range(1,5000))
assert all(Fr(-(-3*n//4),n) <= Fr(751,1000) for n in range(1000,20000))
print("lambda 상계 OK")
# 9n^2-48n-32 at n=6 ; 16(n+1)(n+2)<=25n^2 for n>=6
print("9*36-48*6-32=", 9*36-288-32)
# E_n omega_n small n
def p(n): return (n+1)**(n-1) if n>=1 else 1
from math import comb
for n in range(1,6):
    s=sum(Fr(comb(n,j)*j**j*p(n-j),p(n)) for j in range(1,n//2+1))
    print(n, s, float(s), "<= sqrt n:", float(s)<=sqrt(n))
# n>=6: check inequality sqrt(2/pi) sqrt((n+1)(n+2)/n) <= sqrt n for n=6..30 and the exact E_n omega_n for n=6..60
for n in range(6,61):
    bound=sqrt(2/pi)*sqrt((n+1)*(n+2)/n)
    exact=sum(Fr(comb(n,j)*j**j*p(n-j),p(n)) for j in range(1,n//2+1))
    assert bound<=sqrt(n)+1e-12 and float(exact)<=bound+1e-12, (n,bound,float(exact))
print("E_n omega_n <= bound <= sqrt n for 6..60 OK")
# per-term inequality check: binom(n,j) j^j p_{n-j}/p_n < eta(j/(n+1))/sqrt(2pi(n+1))
eta=lambda ph: ph**-0.5*(1-ph)**-1.5
for n in range(1,80):
    for j in range(1,n//2+1):
        lhs=comb(n,j)*j**j*p(n-j)/p(n); rhs=eta(j/(n+1))/sqrt(2*pi*(n+1))
        assert lhs<rhs,(n,j,lhs,rhs)
print("항별 부등식 OK")
# integral of eta: 2 sqrt(phi/(1-phi))
import random
# numeric check of the sum bound (1/(n+1)) sum eta <= 2 sqrt((floor(n/2)+1)/(n-floor(n/2)))
for n in range(1,200):
    S=sum(eta(j/(n+1)) for j in range(1,n//2+1))/(n+1)
    B=2*sqrt((n//2+1)/(n-n//2))
    assert S<=B,(n,S,B)
print("합-적분 상계 OK")
# 3.4 머리: ceil(3n/4) <= n-1 for n>=4; 2k >= 3n/2
assert all(math.ceil(3*n/4)<=n-1 for n in range(4,1000))
print("k<=n-1 for n>=4 OK; n=3:", math.ceil(9/4), "n=2:", math.ceil(6/4))

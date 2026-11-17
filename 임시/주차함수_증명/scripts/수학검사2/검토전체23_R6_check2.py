# 7.3 검산: k=2,3,5에서 극, 갱신열 극한 1/(k rho_k), 문턱 밀도 극한 P_k(inf)=k a_{k-1} K(rho)/rho 를 mpmath로 본다.
import sys, io
from mpmath import mp, mpf, factorial, log, exp, findroot, quad, e as E
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
mp.dps = 40
def run(k, N=400):
    # a_m = A_{m,k-1}/m!  (7.1): n a_n = sum_j min(j,k) a_{j-1} a_{n-j}
    a = [mpf(1)]
    for n in range(1, N+2):
        a.append(sum(min(j,k)*a[j-1]*a[n-j] for j in range(1,n+1))/n)
    ao = [mpf(1)] + [mpf(m+1)**(m-1)/factorial(m) for m in range(1, N+2)]
    for m in range(0,k+1): assert abs(a[m]-ao[m]) < mpf(10)**-30
    Q = lambda x: sum((k-t)*ao[t-1]*x**t/t for t in range(1,k))   # p_{t-1}/t! = ao_{t-1}/t
    Hk = lambda x: exp(Q(x))*(1 - k*quad(lambda s: exp(-Q(s)), [0,x]))  # 1/A_{k-1} = 1-C_k
    rho = findroot(Hk, mpf(1)/2 + mpf(1)/(2*E))
    K = [mpf(0)]*(N+3)
    for j in range(1, N+3):
        s = sum((k-m)*ao[m-1]*K[j-m] for m in range(1,k) if j-m>=0)
        if j == k+1: s += 1
        K[j] = s/j
    Krho = exp(Q(rho))*quad(lambda s: s**k*exp(-Q(s)), [0,rho])
    Kser = sum(K[j]*rho**j for j in range(N+3))
    Pinf = k*a[k-1]*Krho/rho
    n = N
    EH = (n+1)*a[k-1]*sum(K[j]*a[n+1-j] for j in range(k+1, n+2))/a[n]
    print("k=%d rho=%s (1/e=%s) a^rho_N=%s 1/(k rho)=%s" % (k, mp.nstr(rho,12), mp.nstr(1/E,6), mp.nstr(a[N]*rho**N,12), mp.nstr(1/(k*rho),12)))
    print("   K(rho) 적분=%s 급수=%s  P_k(N)=%s  P_k(inf)=%s  (1+1/N)P_inf=%s" % (mp.nstr(Krho,12), mp.nstr(Kser,12), mp.nstr(k*EH/n,12), mp.nstr(Pinf,12), mp.nstr((1+mpf(1)/n)*Pinf,12)))
    print("   max a^rho_m =", mp.nstr(max(a[m]*rho**m for m in range(N+1)),12), " C_k'(rho)=k 확인: ", mp.nstr(-mp.diff(Hk, rho),12))
for k in (2,3,5): run(k)
print("log 2 =", mp.nstr(log(2),12))

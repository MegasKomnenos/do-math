# -*- coding: utf-8 -*-
"""수학검사2 태그 10: 10.1-10.3절 항등식을 정확한 유리수로 검산한다.
A_{m,l}은 정리 2:old-2-6의 마지막 차 재귀로 정확히 계산한다.
검사: 보조정리 10:old-8-2(장부), 10:old-8-3(a)(d)(e), 10:old-8-4(i)(ii)(iii), 명제 10:old-8-5, 10:old-8-6,
      10:old-8-8(가)(나)(다), 따름정리 6:V-core-identity, 정리 10:old-8-10 증명의 Stem 식, 명제 10:old-8-15의 부등식."""
from fractions import Fraction as Fr
from math import comb, factorial
import sys

def p(n): return (n+1)**(n-1) if n>=1 else 1

def make_A(M, L):
    A = [[0]*(L+2) for _ in range(M+1)]
    for l in range(L+2):
        A[0][l] = 1
    for m in range(1, M+1):
        for l in range(L+2):
            A[m][l] = sum(comb(m-1,j-1)*min(j,l+1)*A[j-1][l]*A[m-j][l] for j in range(1,m+1))
    return A

def run(k):
    M = 3*k+2
    A = make_A(M, k+2)
    def Aml(m,l):
        if l < 0: return 0
        return A[m][l]
    def s(m,l):  # s_m(l) = Pr(M <= l-1) = A_{m,l-1}/p_m
        return Fr(Aml(m,l-1), p(m))
    def b(m,l): return Aml(m,l)-Aml(m,l-1)
    def c(m,l): return Fr(b(m,l), p(m))
    def vs(m,l): return s(m+1,l+1)-s(m,l)   # 머묾 질량
    def d(m): return b(m,k)-b(m,k-1)
    def c2(m): return c(m,k)+c(m,k-1)
    def cl(m,sign):
        if m<=k-1: return Fr(0)
        return c(m,k if sign>0 else k-1)/s(m,k)
    def mu(m):
        return Fr(d(m), Aml(m,k-1))
    def P(n,j):
        return Fr(min(j,k)*comb(n-1,j-1)*Aml(j-1,k-1)*Aml(n-j,k-1), Aml(n,k-1))
    ok = True
    for n in range(2*k+1, 3*k+1):
        nu = n-2*k; N = k+nu
        # (star)(n) = src + inh (7:old-6-14 / 7:old-6-15)
        src = Fr(0); inh = Fr(0); Quad = Fr(0); Stem = Fr(0)
        for j in range(1,n+1):
            L_, R_ = j-1, n-j
            hv = 1 if j>k else 0
            chi = Fr(1,k)*(-(1 if j==k else 0)*(1-cl(R_,-1)) + hv*(cl(L_,1)+cl(L_,-1)+cl(R_,1)+cl(R_,-1))) \
                  + (1+Fr(hv,k))*cl(L_,1)*cl(R_,1) + (1-Fr(hv,k))*cl(L_,-1)*cl(R_,-1)
            src += P(n,j)*chi
            inh += P(n,j)*((mu(L_) if k<=L_<=2*k else 0)+(mu(R_) if k<=R_<=2*k else 0))
            Quad += P(n,j)*((1+Fr(hv,k))*cl(L_,1)*cl(R_,1)+(1-Fr(hv,k))*cl(L_,-1)*cl(R_,-1))
            Stem += P(n,j)*Fr(hv,k)*((cl(L_,1)+cl(L_,-1))*(1 if L_>2*k else 0)+(cl(R_,1)+cl(R_,-1))*(1 if R_>2*k else 0))
        star = src+inh
        w = {m: Fr(comb(n-1,m)*p(m)*Aml(n-1-m,k-1), Aml(n,k-1)) for m in range(k-1, n)}
        u_n = w[N]*s(N,k+1)
        def f(m):
            if m<=N: return 2*((k+1)*c(m,k)-(k-1)*c(m,k-1))
            return (k+n-m+1)*c(m,k)-(k+n-m-1)*c(m,k-1)
        # old-8-2
        rhs = sum(w[m]*f(m) for m in range(k,2*k+1)) - u_n + Quad + Stem
        t1 = (star == rhs)
        # Stem formula (10.1) and old-8-10 identity
        t2 = (Stem == sum(w[m]*c2(m) for m in range(2*k+1, n)))
        t3 = (Aml(n,k-1)*Stem == sum(comb(n-1,m)*p(n-1-m)*(b(m,k)+b(m,k-1)) for m in range(2*k+1,n)))
        # old-8-3 (a),(d),(e)
        def g_exp(x):  # e^{g(x)} = (1+1/x)^{x-1} exact rational for integer x
            return Fr(x+1,x)**(x-1)
        def r_(m): return Fr(Aml(m+1,k-1), (m+1)*Aml(m,k-1))
        t4 = all(w[m+1]/w[m] == g_exp(m+1)/r_(n-2-m) for m in range(k, n-1))
        # (d): w_m/w_N = Bor(m+1)Bor(n-m)/(Bor(N+1)Bor(k)); Bor(j)=e^{-j} j^{j-1}/j! -> ratio rational: e-powers cancel ((m+1)+(n-m) = (N+1)+k = n+1)
        def Bor_noexp(j): return Fr(j**(j-1), factorial(j))
        t5 = all(w[m]/w[N] == Bor_noexp(m+1)*Bor_noexp(n-m)/(Bor_noexp(N+1)*Bor_noexp(k)) for m in range(N, n))
        # (e): w_m/w_k = gL_m * s_{n-1-m}(k)/s_{N-1}(k); u_n/w_k = e^{g(N)-g(k)} s_N(k+1)/s_{N-1}(k)
        def gL(m):
            v = Fr(1)
            for i in range(k, m): v *= g_exp(i+1)/g_exp(n-1-i)
            return v
        t6 = all(w[m]/w[k] == gL(m)*s(n-1-m,k)/s(N-1,k) for m in range(k, N+1))
        t7 = (u_n/w[k] == g_exp(N)/g_exp(k)*s(N,k+1)/s(N-1,k))
        # old-8-4
        Lnu = sum((m-N)*Fr(d(m),p(m))+c2(m) for m in range(N+1,2*k+1))
        t8 = (Lnu == sum((m-N+1)*c(m,k)-(m-N-1)*c(m,k-1) for m in range(N+1,2*k+1)))
        t9 = all(sum(c(m,l) for m in range(np_,2*k+1)) == s(np_,l+1)-s(2*k+1,l+1)+sum(vs(m,l) for m in range(np_,2*k+1)) for np_ in range(k,2*k+1) for l in (k-1,k,k+1))
        t10 = all(c(m,k)-c(m-1,k-1) == vs(m-1,k)-vs(m-1,k-1) for m in range(k+1,2*k+2))
        BdL = -(2*s(2*k+1,k+1)+s(2*k+1,k)+(2*k-N)*c(2*k+1,k))
        t11 = (Lnu == 2*s(N+1,k+1)+s(N+1,k)+sum(2*vs(m,k)+vs(m,k-1) for m in range(N+1,2*k+1))+sum((m-N)*(c(m+1,k)-c(m,k-1)) for m in range(N+1,2*k+1))+BdL) and BdL<=0
        # old-8-5
        V = lambda m: sum((k+1)*c(mm,k)-(k-1)*c(mm,k-1) for mm in range(m,2*k+1))
        Xn = 2*sum((w[m]-w[m-1])*V(m) for m in range(k+1,N+1))
        Yn = sum((w[m]-w[N])*((k+n-m)*Fr(d(m),p(m))+c2(m)) for m in range(N+1,2*k+1))
        t12 = (star == 2*w[k]*V(k)+Xn+Yn-w[N]*(Lnu+s(N,k+1))+Quad+Stem)
        # old-8-6
        T = lambda m: sum(f(i) for i in range(m,2*k+1)) if m<=2*k else Fr(0)
        wkm1 = Fr(0)
        t13 = (sum(w[m]*f(m) for m in range(k,2*k+1)) == w[k]*T(k)+sum((w[m]-w[m-1])*T(m) for m in range(k+1,2*k+1))) and (T(k) == 2*V(k)-Lnu)
        t13b = (T(k+1) == T(k)+2*(k-1)*c(k,k-1))
        # old-8-8
        DD = lambda m: (k+1)*s(m+1,k+1)-2*k*s(m,k)+(k-1)*s(m-1,k-1)
        t14 = all(DD(m) == (k+1)*vs(m,k)-(k-1)*vs(m-1,k-1) for m in range(k+1,2*k+1))
        om = lambda m: Fr(2) if m<=N+1 else 2-Fr(m-N,k)
        Stays = 2*vs(N+1,k)+sum((2-Fr(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(N+2,2*k+1))
        BdS = -(k+nu)*(vs(2*k,k)+c(2*k,k-1))-s(2*k,k-1)
        t15 = True
        if nu <= k-1:
            for m0 in range(k, N+1):
                lhs = 2*k*c(m0,k)+2*s(m0,k+1)+2*s(m0,k)+(2*k+2)*vs(m0,k)-2*s(N+1,k+1)-s(N+2,k+1)+BdS+sum(om(m)*DD(m) for m in range(m0+1,2*k+1))-Stays
                if lhs != T(m0): t15 = False
            for m0 in range(N+1, 2*k+1):
                mS = 3*k+nu-m0
                lhs = mS*c(m0,k)+s(m0,k)+(s(m0,k+1)-s(m0+1,k+1))+(mS+1)*vs(m0,k)+BdS+sum(om(m)*DD(m) for m in range(m0+1,2*k+1))-sum((2-Fr(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(m0+1,2*k+1))
                if lhs != T(m0): t15 = False
            lhsL = 2*s(N+1,k+1)+s(N+2,k+1)+Stays+sum(Fr(m-N,k)*DD(m) for m in range(N+2,2*k+1))-4*s(2*k+1,k+1)+s(2*k,k-1)-(k-nu-2)*(vs(2*k,k)+c(2*k,k-1))
            if lhsL != Lnu: t15 = False
        # V-core identity (6)
        BdV = 2-2*s(2*k+1,k+1)-(k-1)*(vs(2*k,k)+c(2*k,k-1))
        t16 = (V(k) == BdV+sum(DD(m) for m in range(k+1,2*k+1)))
        # old-8-15 (window survival upper bound): s_N(k+1) <= s^W_{nu-1}(N,k+1)
        import math
        Bor = lambda j: math.exp(-j)*j**(j-1)/math.factorial(j)
        sW = 1-sum(Bor(r+1)*(nu-1-r)/(k+nu-r) for r in range(0,nu-1))
        t17 = float(s(N,k+1)) <= sW+1e-12
        res = [t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t13b,t14,t15,t16,t17]
        if not all(res):
            ok = False
            print("k=%d n=%d FAIL" % (k,n), res)
    return ok

if __name__ == '__main__':
    for k in (3,4,5,6,7):
        print("k=%d: 모든 항등식(old-8-2, old-8-3(a)(d)(e), old-8-4(i)-(iii), old-8-5, old-8-6, old-8-8(가)(나)(다), V-core-identity, Stem 식, old-8-15) 성립:" % k, run(k))

# -*- coding: utf-8 -*-
# R9 검산: 9.1~9.3의 정확 항등식을 작은 k에서 유리수 산술로 확인한다.
#  - 보조정리 old-8-2 (장부 항등식): (★)(n) = Σ w_m f_m - u_n + Quad_n + Stem_n  (7장 정의로 (★) 직접 계산)
#  - 따름정리 old-8-3 (a)(c)(d) 닫힌 꼴, (b) 비감소
#  - 명제 old-8-6 (Abel 꼴), 명제 old-8-8 (머묾 꼴 (가)(나))
#  - 9.3 FLQ 정의 뒤의 T_{k+1} = T_k + 2(k-1)c_k(k-1), 정리 old-8-10 증명의 Θ_n·Stem_n 식
from fractions import Fraction as Fr
from math import comb
import sys

def park(m): return (m+1)**(m-1) if m>=1 else 1  # p_0 = 1

# A[m][l] : 최대 변위 <= l 인 길이 m 주차함수 수 (마지막 차 재귀, 정리 2:old-2-6). A[m][-1]=0 처리.
def build_A(M, L):
    A = [[0]*(L+2) for _ in range(M+1)]  # 인덱스 l+1 로 저장 (l=-1 → 0)
    for l in range(-1, L+1):
        A[0][l+1] = 1 if l>=0 else 0
    for l in range(0, L+1):
        for m in range(1, M+1):
            s = 0
            for j in range(1, m+1):
                s += comb(m-1, j-1)*min(j, l+1)*A[j-1][l+1]*A[m-j][l+1]
            A[m][l+1] = s
    return A

def main():
    ok_all = True
    for k in range(3, 8):
        M = 3*k
        A = build_A(M, k+2)
        def Acnt(m, l):
            if m < 0: return 0
            if l < 0: return 0
            if l > k+2: raise ValueError
            return A[m][l+1]
        def s(m, y):  # s_m(y) = A_{m,y-1}/p_m
            return Fr(Acnt(m, y-1), park(m))
        def c(m, Y):  # c_m(Y) = b_{m,Y}/p_m
            return Fr(Acnt(m, Y)-Acnt(m, Y-1), park(m))
        def b(m, Y): return Acnt(m, Y)-Acnt(m, Y-1)
        def d(m): return b(m, k)-b(m, k-1)
        def cl_plus(m): return Fr(b(m, k), Acnt(m, k-1)) if m>=0 else Fr(0)
        def cl_minus(m): return Fr(b(m, k-1), Acnt(m, k-1)) if m>=0 else Fr(0)
        def mu(m): return Fr(d(m), Acnt(m, k-1))
        def vs(m, l): return s(m+1, l+1)-s(m, l)  # ς_m(ℓ)
        # 상수 확인: p_m
        for n in range(2*k+1, 3*k+1):
            nu = n-2*k; N = n-k
            An = Acnt(n, k-1)
            def P(j): return Fr(min(j, k)*comb(n-1, j-1)*Acnt(j-1, k-1)*Acnt(n-j, k-1), An)
            # 7.5절 원천 함수
            def chi(j):
                lin = Fr(1, k)*(-(1 if j==k else 0)*(1-cl_minus(n-j)) + (1 if j>k else 0)*(cl_plus(j-1)+cl_minus(j-1)+cl_plus(n-j)+cl_minus(n-j)))
                ind = Fr(1 if j>k else 0, k)
                quad = (1+ind)*cl_plus(j-1)*cl_plus(n-j) + (1-ind)*cl_minus(j-1)*cl_minus(n-j)
                return lin+quad
            src = sum(P(j)*chi(j) for j in range(1, n+1))
            inh = sum(P(j)*(mu(j-1)*(1 if k<=j-1<=2*k else 0) + mu(n-j)*(1 if k<=n-j<=2*k else 0)) for j in range(1, n+1))
            star = src+inh
            # 정리 7:old-6-21 (7.14) 확인
            KD = sum((k+n-m)*comb(n-1, m)*park(n-1-m)*d(m) for m in range(2*k+1, n))
            if An*star != d(n)-KD:
                print("(7.14) 불일치", k, n); ok_all = False
            # 9.1 장부
            def w(m): return Fr(comb(n-1, m)*park(m)*Acnt(n-1-m, k-1), An)
            def c2(m): return c(m, k)+c(m, k-1)
            def f(m):
                kap = Fr(2) if m <= N else 1+Fr(n-m, k)
                return kap*k*Fr(d(m), park(m)) + (2-(1 if m>N else 0))*c2(m)
            # 장부 항의 닫힌 꼴 확인
            for m in range(k, 2*k+1):
                if m <= N:
                    alt = 2*((k+1)*c(m,k)-(k-1)*c(m,k-1))
                else:
                    alt = (k+n-m+1)*c(m,k)-(k+n-m-1)*c(m,k-1)
                if alt != f(m): print("f_m 닫힌 꼴 불일치", k, n, m); ok_all=False
            u = w(N)*s(N, k+1)
            Quad = sum(P(j)*((1+Fr(1,k))*cl_plus(j-1)*cl_plus(n-j) + (1-Fr(1,k))*cl_minus(j-1)*cl_minus(n-j)) for j in range(k+1, n+1))
            Stem = sum(P(j)*Fr(1,k)*((cl_plus(j-1)+cl_minus(j-1))*(1 if j-1>2*k else 0) + (cl_plus(n-j)+cl_minus(n-j))*(1 if n-j>2*k else 0)) for j in range(k+1, n+1))
            Stem2 = sum(w(m)*c2(m) for m in range(2*k+1, n))
            if Stem != Stem2: print("Stem 식 불일치", k, n); ok_all=False
            lhs = star; rhs = sum(w(m)*f(m) for m in range(k, 2*k+1)) - u + Quad + Stem
            if lhs != rhs: print("old-8-2 불일치", k, n, lhs, rhs); ok_all = False
            # old-8-3
            def g_exp(x):  # e^{g(x)} = (1+1/x)^{x-1} for integer x>=1
                return Fr(x+1, x)**(x-1)
            def r_res(m): return Fr(Acnt(m+1, k-1), (m+1)*Acnt(m, k-1))
            for m in range(k, n-1):
                if w(m+1)/w(m) != g_exp(m+1)/r_res(n-2-m): print("old-8-3(a) 첫 등식 불일치", k, n, m); ok_all=False
                if w(m+1)/w(m) != g_exp(m+1)/g_exp(n-1-m)*s(n-2-m, k)/s(n-1-m, k): print("old-8-3(a) 둘째 등식 불일치", k, n, m); ok_all=False
            if k >= 43:
                pass
            # (c): w_m = π_n(m+1)/(n s_n(k)) with π_n(t) = C(n,t) t^{t-1} p_{n-t}/p_n  (정리 2:chain-law(라)의 정의)
            def pi_n(t): return Fr(comb(n, t)*t**(t-1)*park(n-t), park(n))
            for m in range(N, n):
                if w(m) != pi_n(m+1)/(n*s(n, k)): print("old-8-3(c) 불일치", k, n, m); ok_all=False
            # (d)
            for m in range(k, N+1):
                gL = Fr(1)
                for i in range(k, m): gL *= g_exp(i+1)/g_exp(n-1-i)
                if w(m)/w(k) != gL*s(n-1-m, k)/s(N-1, k): print("old-8-3(d) 불일치", k, n, m); ok_all=False
            if u/w(k) != g_exp(N)/g_exp(k)*s(N, k+1)/s(N-1, k): print("old-8-3(d) u_n 식 불일치", k, n); ok_all=False
            # old-8-6
            def T(m): return sum(f(i) for i in range(m, 2*k+1)) if m <= 2*k else Fr(0)
            abel = w(k)*T(k)+sum((w(m)-w(m-1))*T(m) for m in range(k+1, 2*k+1))
            if abel != sum(w(m)*f(m) for m in range(k, 2*k+1)): print("old-8-6 불일치", k, n); ok_all=False
            # 9.3: T_{k+1} = T_k + 2(k-1)c_k(k-1)
            if T(k+1) != T(k)+2*(k-1)*c(k, k-1): print("T_{k+1} 식 불일치", k, n); ok_all=False
            # old-8-8 (ν ≤ k-1)
            if nu <= k-1:
                def DD(m): return (k+1)*s(m+1, k+1)-2*k*s(m, k)+(k-1)*s(m-1, k-1)
                for m in range(k+1, 2*k+1):
                    if DD(m) != (k+1)*vs(m, k)-(k-1)*vs(m-1, k-1): print("DD 머묾 식 불일치", k, n, m); ok_all=False
                def om(m): return Fr(2) if m <= N+1 else 2-Fr(m-N, k)
                Stays = 2*vs(N+1, k)+sum((2-Fr(m-N, k))*(vs(m, k)+vs(m-1, k-1)) for m in range(N+2, 2*k+1))
                Bd = -(k+nu)*(vs(2*k, k)+c(2*k, k-1))-s(2*k, k-1)
                for m0 in range(k, N+1):
                    rhs = 2*k*c(m0, k)+2*s(m0, k+1)+2*s(m0, k)+(2*k+2)*vs(m0, k)-2*s(N+1, k+1)-s(N+2, k+1)+Bd+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-Stays
                    if T(m0) != rhs: print("old-8-8(가) 불일치", k, n, m0, T(m0), rhs); ok_all=False
                for m0 in range(N+1, 2*k+1):
                    mf = 3*k+nu-m0
                    rhs = mf*c(m0, k)+s(m0, k)+(s(m0, k+1)-s(m0+1, k+1))+(mf+1)*vs(m0, k)+Bd+sum(om(m)*DD(m) for m in range(m0+1, 2*k+1))-sum((2-Fr(m-N, k))*(vs(m, k)+vs(m-1, k-1)) for m in range(m0+1, 2*k+1))
                    if T(m0) != rhs: print("old-8-8(나) 불일치", k, n, m0, T(m0), rhs); ok_all=False
                # 정리 old-8-10 증명: Θ_n = (n/k) A_{n,k-1} u_n A_{N,k-1}/A_{N,k};  A_{n,k-1} Stem_n = Σ_{m>2k} C(n-1,m) p_{n-1-m} b2_m
                Theta = comb(n, k)*k**(k-2)*Acnt(N, k-1)
                if Fr(Theta) != Fr(n, k)*An*u*Fr(Acnt(N, k-1), Acnt(N, k)): print("Θ_n 식 불일치", k, n); ok_all=False
                if An*Stem != sum(comb(n-1, m)*park(n-1-m)*(b(m,k)+b(m,k-1)) for m in range(2*k+1, n)): print("A Stem 식 불일치", k, n); ok_all=False
                # FLQ 꼴: (★) ≥ w_{k+1}T_k - u + Stem  when T_m ≥0 (m≥k+2)?  (단지 분해 확인) 생략
        print("k =", k, "검사 끝")
    print("모두 일치" if ok_all else "불일치 있음")

main()

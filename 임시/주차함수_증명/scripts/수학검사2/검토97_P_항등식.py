# -*- coding: utf-8 -*-
"""결정 97 점검 P: 10.1–10.3절의 남은 진술과 6.5절의 (6.41)을 정확한 유리수로 검산한다.
A_{m,l}은 정리 2:old-2-6의 마지막 차 재귀로 계산한다(scripts/수학검사2/10_검산_항등식.py와 같은 길).
검사: 보조정리 10:old-8-4(열 꼬리; 경계 n'=2k+1의 빈 합까지), 명제 10:old-8-6(Abel 항등식; w_{k-1} 없이),
      명제 10:old-8-8 (가)(나)와 m_0=k 특수화, 10.3 도입의 T_{k+1}=T_k+2(k-1)c_k(k-1), DD_m 항등식,
      정리 6:old-6-19 증명 첫째 단계의 (6.41), n=3k에서 T_m=2V_k(m). 가볍게(k<=8)."""
from fractions import Fraction as Fr
from math import comb

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
    for m in range(1, k+4):
        assert A[m][m-1] == p(m), ("A sanity", m)
    def Aml(m,l): return 0 if l < 0 else A[m][l]
    def s(m,l): return Fr(Aml(m,l-1), p(m))          # s_m(l) = Pr(M <= l-1)
    def c(m,l): return Fr(Aml(m,l)-Aml(m,l-1), p(m))  # c_m(l) = Pr(M = l)
    def vs(m,l): return s(m+1,l+1)-s(m,l)             # 머묾 질량
    res = {}
    # 보조정리 10.4 (열 꼬리): k>=2, n'<=2k, l>=1. 경계 n'=2k+1(빈 합)도 함께.
    ok = True
    for l in range(1, k+2):
        for n1 in range(1, 2*k+2):
            lhs = sum(c(m,l) for m in range(n1, 2*k+1))
            rhs = s(n1,l+1)-s(2*k+1,l+1)+sum(vs(m,l) for m in range(n1,2*k+1))
            ok &= (lhs == rhs)
    res["10.4 열 꼬리(n'=1..2k+1)"] = ok
    # 분해 항등식 c_m(l) = [s_m(l+1)-s_{m+1}(l+1)] + vs_m(l)
    res["c=[..]+vs"] = all(c(m,l) == (s(m,l+1)-s(m+1,l+1))+vs(m,l) for m in range(1,2*k+2) for l in range(1,k+2))
    # DD_m 항등식과 (6.41)
    def DD(m, y): return (y+2)*s(m+2,y+2)-2*(y+1)*s(m+1,y+1)+y*s(m,y)  # DD(m,y) with capacity y: (k+1)s_{m+2}(k+1)-2k s_{m+1}(k)+(k-1)s_m(k-1), y=k-1
    def DDm(m): return DD(m-1, k-1)
    res["DD_m=(k+1)vs_m(k)-(k-1)vs_{m-1}(k-1)"] = all(DDm(m) == (k+1)*vs(m,k)-(k-1)*vs(m-1,k-1) for m in range(k+1, 2*k+1))
    V = lambda m: sum((k+1)*c(i,k)-(k-1)*c(i,k-1) for i in range(m, 2*k+1))
    BdV = 2-2*s(2*k+1,k+1)-(k-1)*vs(2*k,k)-(k-1)*c(2*k,k-1)
    res["(6.41) V_k(k)=Bd^V+sum DD(m,k-1)"] = (V(k) == BdV + sum(DD(m,k-1) for m in range(k,2*k)))
    res["c_k(k)=0"] = (c(k,k) == 0)
    okA = okS1 = okS2 = okT = ok3k = True
    for n in range(2*k+1, 3*k+1):
        nu = n-2*k; N = k+nu
        w = {m: Fr(comb(n-1,m)*p(m)*Aml(n-1-m,k-1), Aml(n,k-1)) for m in range(k, n)}
        def f(m):
            if m<=N: return 2*((k+1)*c(m,k)-(k-1)*c(m,k-1))
            return (k+n-m+1)*c(m,k)-(k+n-m-1)*c(m,k-1)
        T = {m: sum(f(i) for i in range(m,2*k+1)) for m in range(k,2*k+2)}
        assert T[2*k+1] == 0
        # 명제 10.6: Abel 항등식 (w_{k-1} 없이)
        okA &= (sum(w[m]*f(m) for m in range(k,2*k+1)) == w[k]*T[k]+sum((w[m]-w[m-1])*T[m] for m in range(k+1,2*k+1)))
        # 10.3 도입: T_{k+1} = T_k + 2(k-1)c_k(k-1)
        okT &= (T[k+1] == T[k] + 2*(k-1)*c(k,k-1))
        if n == 3*k:
            ok3k &= all(T[m] == 2*V(m) for m in range(k,2*k+1))
            continue  # 명제 10.7은 nu<=k-1
        # 명제 10.7
        def om(m): return Fr(2) if m <= N+1 else 2-Fr(m-N,k)
        Stays = 2*vs(N+1,k)+sum((2-Fr(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(N+2,2*k+1))
        BdS = -(k+nu)*(vs(2*k,k)+c(2*k,k-1))-s(2*k,k-1)
        for m0 in range(k, N+1):
            rhs = 2*k*c(m0,k)+2*s(m0,k+1)+2*s(m0,k)+(2*k+2)*vs(m0,k)-2*s(N+1,k+1)-s(N+2,k+1)+BdS \
                  + sum(om(m)*DDm(m) for m in range(m0+1,2*k+1)) - Stays
            okS1 &= (T[m0] == rhs)
        rhs_k = 4-2*s(N+1,k+1)-s(N+2,k+1)+BdS+sum(om(m)*DDm(m) for m in range(k+1,2*k+1))-Stays
        okS1 &= (T[k] == rhs_k)
        for m0 in range(N+1, 2*k+1):
            mS = 3*k+nu-m0
            rhs = mS*c(m0,k)+s(m0,k)+(s(m0,k+1)-s(m0+1,k+1))+(mS+1)*vs(m0,k)+BdS \
                  + sum(om(m)*DDm(m) for m in range(m0+1,2*k+1)) \
                  - sum((2-Fr(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(m0+1,2*k+1))
            okS2 &= (T[m0] == rhs)
    res["10.6 Abel"] = okA
    res["10.3 T_{k+1}=T_k+2(k-1)c_k(k-1)"] = okT
    res["10.7(가) incl. m0=k"] = okS1
    res["10.7(나)"] = okS2
    res["n=3k: T_m=2V_k(m)"] = ok3k
    return res

if __name__ == "__main__":
    allok = True
    for k in range(3, 9):
        r = run(k)
        allok &= all(r.values())
        print(k, {a: ("OK" if b else "FAIL") for a, b in r.items()})
    print("ALL OK" if allok else "FAIL")

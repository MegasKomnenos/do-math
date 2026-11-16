# 검토전체16 E2: 4.3절 상쇄 분해 (4.7) 의 수치 일관성 검사 (중간 k) 와 (4.14), F0/F1 적분
import mpmath as mp
from fractions import Fraction as Fr
from math import comb, factorial
mp.mp.dps = 40

def p(n): return (n + 1) ** (n - 1) if n >= 1 else 1

def e_n_exact(k, n):
    # K_{m,k}(y) 와 1,2계 도함수를 y=k 에서 정확 정수로: 재귀 K_m = sum_j C(m-1,j) W(j+1) K_j K_{m-1-j}
    K0 = [0] * (n + 1); K1 = [0] * (n + 1); K2 = [0] * (n + 1)
    K0[0] = 1
    for m in range(1, n + 1):
        s0 = s1 = s2 = 0
        for j in range(m):
            c = comb(m - 1, j)
            a0, a1, a2 = K0[j], K1[j], K2[j]
            b0, b1, b2 = K0[m - 1 - j], K1[m - 1 - j], K2[m - 1 - j]
            # 곱 P = K_j K_{m-1-j}
            P0 = a0 * b0; P1 = a1 * b0 + a0 * b1; P2 = a2 * b0 + 2 * a1 * b1 + a0 * b2
            if j + 1 <= k:
                W0, W1 = j + 1, 0
            else:
                W0, W1 = k, 1   # W = y, at y=k
            s0 += c * W0 * P0
            s1 += c * (W1 * P0 + W0 * P1)
            s2 += c * (2 * W1 * P1 + W0 * P2)
        K0[m], K1[m], K2[m] = s0, s1, s2
    return K0, K1, K2

def J_exact(k, n, z):
    J = [0] * (n + 1)
    for m in range(0, n):
        if m + 1 < k: continue
        s = sum(comb(m, i) * (z + i + 1) * p(i) * J[m - i] for i in range(m + 1))
        if m >= k - 1:
            s += comb(m, k - 1) * p(k - 1) * p(m - k + 1)
        J[m + 1] = s
    return J[n]

def hermite(N_, y, n):
    He = [Fr(1), Fr(N_)]
    for j in range(2, n + 1):
        He.append(N_ * He[j - 1] - (j - 1) * y * He[j - 2])
    return He
def M_r(r, n, y):
    N_ = n + y + 1
    He = hermite(N_, y, n)
    c = sum((-1) ** i * comb(r + 1, i) * He[n - i] / factorial(n - i) for i in range(r + 2) if n - i >= 0)
    # M_r^{(y,n)} = n!/p_n * e^{-y/2} * c
    return mp.mpf(factorial(n)) / mp.mpf(p(n)) * mp.e ** (-mp.mpf(y) / 2) * (mp.mpf(c.numerator) / mp.mpf(c.denominator))

def Bor(j): return mp.e ** (-j) * mp.mpf(j) ** (j - 1) / mp.factorial(j)
def Bor_z(j, Z): return mp.e ** (-j * Z) * (j * Z) ** (j - 1) / mp.factorial(j)
def Bor_tail(k, Z): return 1 - mp.fsum(Bor_z(j, Z) for j in range(1, k + 1))

def Wi(k, j):
    return mp.quad(lambda v: mp.e ** (k * v**2 / 2) * v**2 * Bor_tail(k, 1 - v) * (v**2 / 2) ** j, [0, 0.2, 0.5, 1])
def I_k(k):
    eta = lambda v: -mp.log(1 - v) - v - v**2 / 2
    return mp.quad(lambda v: v / (1 - v) * mp.e ** (-v**2 / 2) * mp.e ** (-k * eta(v)), [0, 0.3, 0.7, 1])

print("== (4.7) 분해의 수치 일관성 (y=k, n=2k) ==")
for k in [20, 40, 80]:
    n = 2 * k
    K0, K1, K2 = e_n_exact(k, n)
    assert K0[n] == None or True
    e_n = K2[n]
    Jn = J_exact(k, n, k - 1)
    pn = p(n)
    M0, M2, M4 = M_r(0, n, k), M_r(2, n, k), M_r(4, n, k)
    M0m = M_r(0, n, k - 1)
    W0, W1, W2 = Wi(k, 0), Wi(k, 1), Wi(k, 2)
    A = (2 * W1 + k * W2) * M0 - (W0 + k * W1) * M2 + mp.mpf(k) / 4 * W0 * M4
    bD = mp.mpf(e_n) / pn - A
    Ik = I_k(k)
    bJ = mp.mpf(Jn) / pn - Bor(k) * Ik * M0m
    gk = 2 - k * M2 / M0
    R = k * W2 + gk * W1 - Bor(k) * Ik
    print(f"k={k}: M0={mp.nstr(M0,8)} (4sqrt2={mp.nstr(4*mp.sqrt(2),8)}), kM2/M0={mp.nstr(k*M2/M0,6)}, k^2M4/M0={mp.nstr(k*k*M4/M0,6)}, g_k={mp.nstr(gk,6)}")
    print(f"      k^3 bD={mp.nstr(k**3*bD,6)} (46sqrt2-12={mp.nstr(46*mp.sqrt(2)-12,6)}),  k^2.5 bJ={mp.nstr(mp.mpf(k)**2.5*bJ,6)},  kR/Bor={mp.nstr(k*R/Bor(k),6)},  k^2.5 (e-J)/p_n={mp.nstr(mp.mpf(k)**2.5*(mp.mpf(e_n)-Jn)/pn,6)}")
    # 정리 4-7 하계 (omega = g_k)
    a0 = mp.mpf(3) ** (-mp.mpf(2)/3) * mp.gamma(mp.mpf(1)/3); a1 = mp.mpf(3) ** (-mp.mpf(1)/3) * mp.gamma(mp.mpf(2)/3)
    lb = gk - mp.mpf(7)/2 - (4*gk + mp.mpf(1)/2) * a0 * mp.mpf(k) ** (-mp.mpf(1)/3) - mp.mpf(13)/2 * gk * a1 * mp.mpf(k) ** (-mp.mpf(2)/3) - 12 * gk / k
    print(f"      정리4-7 하계 (omega=g_k): {mp.nstr(lb,6)} <= kR/Bor: {lb <= k*R/Bor(k)}")

print("== (4.14) 수치 확인 k=30000 ==")
k = 30000; eps = 1 / mp.sqrt(k)
def Bor_ld(phi):
    return 2 + mp.quad(lambda w: w ** (-mp.mpf(3)/2) * (1 - mp.e ** (-phi * w)), [0, 1])
def Bor_ldR(beta): return Bor_ld(-beta**2 / 2)
for beta in [mp.mpf('0.5'), mp.mpf(1), mp.mpf(2), mp.mpf(4)]:
    Z = 1 + 1j * beta * eps
    val = mp.sqrt(k) * Bor_tail(k, Z)
    TR = mp.mpf(3)/5 + mp.mpf(12)/5 * beta**2 + mp.mpf(3)/2 * beta**4 + beta**6 / 25
    TI = mp.mpf(1)/100 + mp.mpf(201)/100 * beta + mp.mpf(7)/10 * beta**3 + beta**4/500 + beta**5/50000 + beta**7/500000
    errR = abs(mp.re(val) - (2*mp.pi) ** (-mp.mpf(1)/2) * Bor_ldR(beta) - mp.mpf(4)/3 * beta**2 * eps)
    errI = abs(mp.im(val) - beta)
    bR = (2*mp.pi) ** (-mp.mpf(1)/2) * eps**2 * mp.e ** (beta**2/2) * TR
    bI = (2*mp.pi) ** (-mp.mpf(1)/2) * eps * mp.e ** (beta**2/2) * TI
    print(f"beta={beta}: Re err {mp.nstr(errR,4)} <= {mp.nstr(bR,4)} {errR<=bR};  Im err {mp.nstr(errI,4)} <= {mp.nstr(bI,4)} {errI<=bI}")
# Dawson 항등식
for beta in [mp.mpf('0.7'), mp.mpf(2)]:
    Daw = mp.e ** (-beta**2/2) * mp.quad(lambda v: mp.e ** (v**2/2), [0, beta])
    print("Dawson 항등식:", mp.nstr(Bor_ldR(beta) * mp.e ** (-beta**2/2), 12), mp.nstr(2 - 2*beta*Daw, 12))

print("== F0, F1 적분 ==")
ninf = 2 / mp.sqrt(mp.pi)
def F0(z):
    inner = mp.quad(lambda r: r**2 * mp.e ** ((1-r**2)*z**2/2) * ((1-r**2)*z**2 + (1-r**2)**2*z**4/4) * (2*mp.pi) ** (-mp.mpf(1)/2) * Bor_ldR(r*z), [0, 1])
    return -ninf * z**4 * mp.e ** (-z**2) * inner
def F1(z):
    inner = mp.quad(lambda r: r**2 * mp.e ** ((1-r**2)*z**2/2) * ((1-r**2)*z**2 + (1-r**2)**2*z**4/4) * (mp.mpf(4)/3 * r**2 * z**2 - mp.mpf(2)/3 * r * z**4), [0, 1])
    return -ninf * z**4 * mp.e ** (-z**2) * inner
mp.mp.dps = 20
I0 = mp.quad(F0, [-8, -4, -2, 0, 2, 4, 8]); I1 = mp.quad(F1, [-8, -4, -2, 0, 2, 4, 8])
print("int F0 =", mp.nstr(I0, 8), " int F1 =", mp.nstr(I1, 8), " 46sqrt2-12 =", mp.nstr(46*mp.sqrt(2)-12, 8))

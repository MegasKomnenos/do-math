# 검토전체20 N7a: 7.4-7.5절 수치·항등식 검산 (1)
# 실행: python -I 검토전체20_N7a_check1.py > 검토전체20_N7a_check1_out.txt
from fractions import Fraction as F
from itertools import permutations
from math import comb, factorial, exp, log, sqrt
import mpmath as mp

mp.mp.dps = 40

def A_table(N, lmax):
    # A[n][l] = A_{n,l}, l from -1..lmax ; A_{n,-1}=0, A_{0,l}=1
    A = [[0]*(lmax+2) for _ in range(N+1)]
    for l in range(-1, lmax+1):
        A[0][l+1] = 1 if l >= 0 else 0
    for n in range(1, N+1):
        for l in range(0, lmax+1):
            s = 0
            for j in range(0, n):
                s += comb(n-1, j)*min(j+1, l+1)*A[j][l+1]*A[n-1-j][l+1]
            A[n][l+1] = s
    return A

def Aget(A, n, l):
    if l < 0: return 0
    return A[n][l+1]

def p(n): return (n+1)**(n-1) if n >= 1 else 1

def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        j = i-1
        while j >= 0 and sig[j] < sig[i]: j -= 1
        h.append(i-j)  # i - (j) with 0-based: position index i+1 minus (j+1) ; j=-1 -> i+1
    return h

print("== 1. 모멘트 재귀 (7.2)(7.3), 전분산 (7.4), mom_k 전수 대조 (n<=7) ==")
for k in (2, 3):
    N = 7
    A = A_table(N, k+1)
    # brute force moments under Pr^sigma_{n,k}
    Zf = {0: F(0)}; ZH = {0: F(0)}; ZZ = {0: F(0)}
    Varb = {}
    for n in range(1, N+1):
        tot = 0; sZ = 0; sH = 0; sZZ = 0; sZ2 = 0
        for sig in permutations(range(1, n+1)):
            h = caps(sig)
            w = 1
            for hi in h: w *= min(hi, k)
            Z = sum(1 for hi in h if hi > k); H = sum(1 for hi in h if hi == k)
            tot += w; sZ += w*Z; sH += w*H; sZZ += w*Z*(Z-1); sZ2 += w*Z*Z
        assert tot == Aget(A, n, k-1)
        Zf[n] = F(sZ, tot); ZH[n] = F(sH, tot); ZZ[n] = F(sZZ, tot)
        Varb[n] = F(sZ2, tot) - Zf[n]**2
    # recursion (7.2)
    a = {n: F(Aget(A, n, k-1), factorial(n)) for n in range(N+1)}
    ok72 = all(n*a[n] == sum(min(pp, k)*a[pp-1]*a[n-pp] for pp in range(1, n+1)) for n in range(1, N+1))
    def P(n, pp): return min(pp, k)*a[pp-1]*a[n-pp]/(n*a[n])
    ok73 = True
    for n in range(1, N+1):
        r1 = sum(P(n, pp)*((1 if pp > k else 0)+Zf[pp-1]+Zf[n-pp]) for pp in range(1, n+1))
        r2 = sum(P(n, pp)*((1 if pp == k else 0)+ZH[pp-1]+ZH[n-pp]) for pp in range(1, n+1))
        r3 = sum(P(n, pp)*(ZZ[pp-1]+ZZ[n-pp]+2*Zf[pp-1]*Zf[n-pp]+2*(1 if pp > k else 0)*(Zf[pp-1]+Zf[n-pp])) for pp in range(1, n+1))
        ok73 &= (r1 == Zf[n] and r2 == ZH[n] and r3 == ZZ[n])
    # cnt and variance formula
    cnt = {}
    for n in range(0, N+1):
        for m in range(0, N+1):
            if m > n: cnt[(n, m)] = F(0)
            elif m == n: cnt[(n, m)] = F(1)
            else:
                cnt[(n, m)] = sum(P(n, pp)*(cnt[(pp-1, m)]+cnt[(n-pp, m)]) for pp in range(1, n+1)) if n >= 1 else F(0)
    def g(m, pp): return (1 if pp > k else 0)+Zf[pp-1]+Zf[m-pp]
    def y(m): return sum(P(m, pp)*g(m, pp)**2 for pp in range(1, m+1)) - Zf[m]**2 if m >= 1 else F(0)
    ok74 = True
    for n in range(1, N+1):
        v = sum(cnt[(n, m)]*y(m) for m in range(1, n+1))
        ok74 &= (v == Varb[n])
        lhsH = k*ZH[n]; rhsH = sum(cnt[(n, m)]*k*P(m, k) for m in range(k, n+1))
        ok74 &= (lhsH == rhsH)
        T = ZZ[n]-k*ZH[n]
        rhsT = Zf[n]*(Zf[n]-1)+sum(cnt[(n, m)]*(y(m)-k*P(m, k)) for m in range(k, n+1))
        ok74 &= (T == rhsT)
        def mom(m):
            return 2*sum(P(m, pp)*Zf[pp-1]*Zf[m-pp] for pp in range(1, m+1))+2*sum(P(m, pp)*(Zf[pp-1]+Zf[m-pp]) for pp in range(k+1, m+1))-k*P(m, k)
        ok74 &= (T == sum(cnt[(n, m)]*mom(m) for m in range(k, n+1)))
        if n == k:
            xk = F(k, k+1)**(k-1)
            ok74 &= (mom(k) == -k*xk)
    print(f"k={k}: (7.2) {ok72}, (7.3) {ok73}, (7.4)+mom+mom_k {ok74}")

print("== 2. 한 걸음 항등식 (7.13), fold-A, fold-R, fold-T, fold-L1, fold-DIP (mpmath) ==")
for k in (3, 4, 6):
    N = 3*k+6
    A = A_table(N, k)
    e = mp.e
    def at(m, y):  # tilde a^{(y)}_m = e^{-m} A_{m,y-1}/m!
        return mp.mpf(Aget(A, m, y-1))/mp.factorial(m)*mp.e**(-m)
    def Bor(m): return mp.e**(-m)*mp.mpf(m)**(m-1)/mp.factorial(m)
    def cl(m, sgn):
        Am = Aget(A, m, k-1)
        return mp.mpf(Aget(A, m, k)-Am)/Am if sgn > 0 else mp.mpf(Am-Aget(A, m, k-2))/Am
    def mu(m): return mp.mpf(Aget(A, m, k)-2*Aget(A, m, k-1)+Aget(A, m, k-2))/Aget(A, m, k-1)
    def Pk(m, j): return mp.mpf(min(j, k)*comb(m-1, j-1)*Aget(A, j-1, k-1)*Aget(A, m-j, k-1))/Aget(A, m, k-1)
    def chi(m, j):
        ind_gt = 1 if j > k else 0; ind_eq = 1 if j == k else 0
        return (mp.mpf(1)/k)*(-ind_eq*(1-cl(m-k, -1)) if j == k else ind_gt*(cl(j-1, 1)+cl(j-1, -1)+cl(m-j, 1)+cl(m-j, -1))/k*0+0) if False else \
            (1/mp.mpf(k))*(-(ind_eq)*(1-cl(m-k, -1) if m-k >= 0 else 0)+ind_gt*(cl(j-1, 1)+cl(j-1, -1)+cl(m-j, 1)+cl(m-j, -1))) \
            + (1+mp.mpf(ind_gt)/k)*cl(j-1, 1)*cl(m-j, 1)+(1-mp.mpf(ind_gt)/k)*cl(j-1, -1)*cl(m-j, -1)
    def src(m): return sum(Pk(m, j)*chi(m, j) for j in range(1, m+1))
    ok13 = True; okA = True; okR = True; okT = True; okL1 = True; okDIP = True
    for n in range(1, N+1):
        rhs = src(n)+sum(Pk(n, j)*(mu(j-1)+mu(n-j)) for j in range(1, n+1))
        ok13 &= abs(rhs-mu(n)) < mp.mpf(10)**-25
        if n >= k:
            Eu = mp.e**-1/(n*at(n, k))
            thr = -mp.e*Bor(k)*at(n-k, k-1)
            heavy = sum(at(n-1-m, k)*(at(m, k+1)-at(m, k-1))*(1+(1 if n-1-m >= k else 0)) for m in range(k, n))
            quad = sum(min(j, k+1)*(at(j-1, k+1)-at(j-1, k))*(at(n-j, k+1)-at(n-j, k))+min(j, k-1)*(at(j-1, k)-at(j-1, k-1))*(at(n-j, k)-at(n-j, k-1)) for j in range(1, n+1))
            okA &= abs(src(n)-Eu*(thr+heavy+quad)) < mp.mpf(10)**-25
            okA &= quad >= 0 and heavy >= 0
        if n >= 2*k+1:
            nu = n-2*k
            def sib(q): return mp.e*Bor(n-k-q)
            for B in range(nu+1, n-k):
                l = n-1-k-B
                lhs = sum(sib(q)*(at(k+q, k+1)-at(k+q, k-1)) for q in range(nu-1, B+1))
                ed1 = mp.e*Bor(k+1)*at(n-1-k, k+1); ed2 = mp.e*Bor(k)*at(n-k, k+1)
                up = mp.e*Bor(l+2)*at(n-2-l, k-1)+mp.e*Bor(l+1)*at(n-1-l, k-1)
                inn = sum(sib(q+1)*at(k+q+1, k+1)-sib(q-1)*at(k+q-1, k-1) for q in range(nu, B))
                okR &= abs(lhs-(ed1+ed2+inn-up)) < mp.mpf(10)**-25
            # fold-L1 (7.15) for all l in [0,k-2]
            for l in range(0, k-1):
                rhs15 = mp.e*Bor(k+1)*at(n-1-k, k+1)+mp.e*Bor(k)*(at(n-k, k+1)-at(n-k, k-1))-mp.e*Bor(l+2)*at(n-2-l, k-1)-mp.e*Bor(l+1)*at(n-1-l, k-1)
                okL1 &= (mp.e*n*at(n, k)*src(n) >= rhs15 - mp.mpf(10)**-25)
                # fold-DIP: if (7.16) holds then src>0
                O = Bor(k+1)*Bor(n-k)/(Bor(l+2)*Bor(n-1-l)+Bor(l+1)*Bor(n-l))
                ratio = (mp.mpf(Aget(A, n-l, k))/p(n-l))/(mp.mpf(Aget(A, n-1-k, k))/p(n-1-k))
                if ratio < O: okDIP &= (src(n) > 0)
        # fold-T
        for m in range(1, n-1):
            if 2*m >= n-1 and n >= 3:
                okT &= (at(n-2-m, k)*at(m+1, k+1) >= at(n-m, k)*at(m-1, k-1) - mp.mpf(10)**-30)
    print(f"k={k}, n<={N}: (7.13) {ok13}; fold-A {okA}; fold-R {okR}; fold-T {okT}; fold-L1 {okL1}; fold-DIP {okDIP}")

print("== 3. heavy-block (7.10), (라) pi^sharp 상계; ex_t >= q ==")
k = 6; N = 2*k+3
A = A_table(N, k)
def s(m, y): return F(Aget(A, m, y-1), p(m))
def pi(m, j): return F(comb(m, j)*j**(j-1)*p(m-j), p(m))
ok10 = True; okra = True
for q in range(2, k+3):
    m = k+q-1
    lhs = 1-s(m, k)
    rhs = sum(pi(m, j)*(F(j-k, j)+F(k, j)*(1-s(j-k+k-1, k))) for j in range(k+1, k+q))
    ok10 &= (lhs == rhs)
    pis = F(q*(q-1), 2*(k+1))
    okra &= (lhs <= pis)
    ex = F(k+q)*p(m)/Aget(A, m, k-1)-k
    okra &= (ex >= q)
    if pis < 1:
        okra &= (ex <= q+(k+q)*pis/(1-pis))
print(f"k={k}: (7.10) {ok10}; (라) {okra}")

print("== 4. kernel-bound 수치 (m<=80) ==")
def Borf(m): return exp(-m)*m**(m-1)/factorial(m)
okkb = True; worst = 0
for m in range(1, 81):
    for sv in range(0, m):
        pim = comb(m, sv)*(m-sv)**(m-sv-1)*(sv+1)**(sv-1)/(m+1)**(m-1)
        ke = 3*(sv+1)/(2*(m+1))+(sv+1)*(3*sv+2)/(12*(m+1)**2)+(sv+1)**2/(2*(m+1)*(m-sv))+(sv+1)**4/(12*(m+1)**2*(m-sv))
        bound = Borf(sv+1)*exp(ke)
        if pim > bound*(1+1e-12): okkb = False
        worst = max(worst, pim/bound)
print(f"kernel-bound holds: {okkb}; max ratio pi/bound = {worst:.6f}")

print("== 5. pair-check-10000: 개수와 최솟값 ==")
k = 10000
def pish(q): return F(q*(q-1), 2*(k+1))
def exbar(q):
    ps = pish(q); return q+(k+q)*ps/(1-ps)
cnt_cases = 0; mn = None; arg = None
for q in range(1, 50):
    for qp in range(q, 50):
        for j in range(0, 51-q-qp):
            cnt_cases += 1
            val = 1-F(j, k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if mn is None or val < mn: mn = val; arg = (q, qp, j)
print(f"cases (q<=q') = {cnt_cases}; min = {float(mn):.5f} at {arg}; ordered pairs = {sum(1 for q in range(1,50) for qp in range(1,50) for j in range(0,51-q-qp))}")

print("== 6. 꼬리 삼중 (7.12) float 점검, ke-bar ==")
for (K1, M, tf) in [(10**4, 120, 0.54), (2*10**4, 250, 0.593), (10**5, 300, 0.522), (10**5, 450, 0.548), (10**6, 700, 0.519)]:
    keb = 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
    Bo = [0]+[mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j) for j in range(1, M+2)]
    minrel = None
    for q in range(2, M+1):
        Fq = tf*mp.mpf(q)**1.5-mp.e**keb*sum(Bo[sv+1]*((q-1-sv)+tf*mp.mpf(q-1-sv)**1.5) for sv in range(0, q-1))
        rel = Fq/(tf*mp.mpf(q)**1.5)
        if minrel is None or rel < minrel: minrel = rel
    print(f"({K1},{M},{tf}): ke-bar={keb:.4f}, min rel margin={mp.nstr(minrel,3)}, tf*M^1.5={tf*M**1.5:.0f}")

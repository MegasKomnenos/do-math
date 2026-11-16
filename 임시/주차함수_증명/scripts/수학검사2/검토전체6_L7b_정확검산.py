# 7.6-7.7절 항등식·부등식의 정확 유리수 검산 (L7b). python -I 로 실행.
from fractions import Fraction as Fr
from math import comb, ceil, log, exp, sqrt, pi

def build(k, M):
    A = {}
    for l in (k-2, k-1, k):
        A[l] = [Fr(1)]
        for m in range(1, M+1):
            A[l].append(sum(Fr(comb(m-1, j-1))*min(j, l+1)*A[l][j-1]*A[l][m-j] for j in range(1, m+1)))
    return A

def p(m): return Fr((m+1)**(m-1)) if m >= 1 else Fr(1)

def run(k, M):
    A = build(k, M)
    Ak = A[k-1]
    def s(m, y):  # y in {k-1,k,k+1}
        return A[y-1][m]/p(m)
    def c(m, Y):  # Y in {k-1,k}
        return (A[Y][m]-A[Y-1][m])/p(m)
    def Pn(n, j): return Fr(j*comb(n-1, j-1))*p(j-1)*p(n-j)/p(n)
    def Pk(n, j): return Fr(min(j, k)*comb(n-1, j-1))*Ak[j-1]*Ak[n-j]/Ak[n]
    def clp(m): return (A[k][m]-Ak[m])/Ak[m]
    def clm(m): return (Ak[m]-A[k-2][m])/Ak[m]
    def chi(n, j):
        L, R = j-1, n-j
        lin = Fr(0)
        if j == k: lin -= (1-clm(R))
        if j > k: lin += clp(L)+clm(L)+clp(R)+clm(R)
        h = 1 if j > k else 0
        return lin/k + (1+Fr(h, k))*clp(L)*clp(R) + (1-Fr(h, k))*clm(L)*clm(R)
    def src(n): return sum(Pk(n, j)*chi(n, j) for j in range(1, n+1))
    def mu(m): return (A[k][m]-2*Ak[m]+A[k-2][m])/Ak[m]
    def d(m): return A[k][m]-2*Ak[m]+A[k-2][m]
    def inh(n): return sum(Pk(n, j)*(mu(j-1)*(k <= j-1 <= 2*k) + mu(n-j)*(k <= n-j <= 2*k)) for j in range(1, n+1))
    def inhlin(n): return sum(Pk(n, j)*((clp(j-1)+clm(j-1))*(k <= j-1 <= 2*k)+(clp(n-j)+clm(n-j))*(k <= n-j <= 2*k)) for j in range(1, n+1))/k
    def w(n, m): return Fr(comb(n-1, m))*p(m)*Ak[n-1-m]/Ak[n]
    def pfrak(m): return ((k+1)*(A[k][m]-Ak[m])-(k-1)*(Ak[m]-A[k-2][m]))/p(m)
    def Left(n): return sum(w(n, m)*pfrak(m) for m in range(k, 2*k+1))
    def KDp(n): return sum(Fr((k+n-m)*comb(n-1, m))*p(n-1-m)*d(m) for m in range(2*k+1, n))
    def Quad(n): return sum(Pk(n, j)*((1+Fr(1, k))*clp(j-1)*clp(n-j)+(1-Fr(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
    def Stem(n): return sum(Pk(n, j)*((clp(j-1)+clm(j-1))*(j-1 > 2*k)+(clp(n-j)+clm(n-j))*(n-j > 2*k)) for j in range(k+1, n+1))/k
    def rw(n, q): return Fr(k, k+1+q)*Pn(n, k+1+q)/Pn(n, k)
    def eg(x): return Fr(x+1, x)**(x-1)  # e^{g(x)}
    ok = True
    def chk(name, cond, info=""):
        nonlocal ok
        if not cond:
            ok = False; print("  FAIL", name, info)
    nPD = ceil((k+1)**(4/3))+k+1
    for n in range(2*k+1, M+1):
        nu = n-2*k
        # root-symmetry
        chk("rw(nu)=1", rw(n, nu) == 1, (n,))
        for q in range(0, k+nu-1):
            j = k+1+q
            chk("rw ratio", rw(n, q+1)/rw(n, q) == eg(j)/eg(n-j), (n, q))
        chk("rw>=1 for q>=nu", all(rw(n, q) >= 1 for q in range(nu, k+nu)), (n,))
        # (7.22)
        lhs = k*s(n, k)*src(n)
        r722 = sum(Fr(k, j)*Pn(n, j)*((c(j-1, k-1)+c(j-1, k))*s(n-j, k)+s(j-1, k)*(c(n-j, k-1)+c(n-j, k))) for j in range(k+1, n+1)) - Pn(n, k)*s(n-k, k-1)
        chk("(7.22)", lhs >= r722, (n,))
        br1 = sum(rw(n, q)*(c(k+q, k-1)+c(k+q, k)) for q in range(nu, k+nu)) - s(k+nu, k-1)
        br2 = c(k+nu, k-1)+s(k+nu, k+1)-s(n, k)-s(n, k+1)
        chk("(7.23a)", r722 >= Pn(n, k)*br1, (n,))
        chk("(7.23b)", br1 >= br2, (n,))
        # top-roots with U0=min(3,k-1)
        U0 = min(3, k-1)
        brT = br2 + sum((rw(n, k+nu-1-U)-1)*(s(n-1-U, k)-s(n-U, k)) for U in range(0, U0+1))
        chk("top-roots 1st", br1 >= brT, (n,))
        hz = lambda N: 1-s(N+1, k)/s(N, k)
        chk("top-roots 2nd", brT >= s(n, k)*(sum((rw(n, k+nu-1-U)-1)*hz(n-1-U) for U in range(0, U0+1))-1), (n,))
        # apex identity: k s_n apex^H = P_n(k) * br1
        apex = (sum(Pk(n, j)*(clp(j-1)+clm(j-1)) for j in range(n-k+1, n+1)) - Pk(n, k)*(1-clm(n-k)))/k
        chk("apex identity", k*s(n, k)*apex == Pn(n, k)*br1, (n,))
        # Fold/Eu identity (common factor e^{1-n} removed)
        l_ = ceil(0.3*k)
        if l_ <= k-2 and n-l_ >= n-k:
            Fold = (sum(Pk(n, j)*(clp(j-1)+clm(j-1)) for j in range(n-k, n-l_+1)) - Pk(n, k)*(1-clm(n-k)))/k
            # Fold/Eu = e n atil_n Fold ; atil_n = e^{-n} A_n/n!  -> times e^{n-1}: n A_n Fold / n!
            lhsF = Fr(n)*Ak[n]*Fold/Fr(__import__('math').factorial(n))
            thr = -Fr(k**(k-1))*A[k-2][n-k]/(Fr(__import__('math').factorial(k))*__import__('math').factorial(n-k))
            B = n-1-k-l_
            fac = __import__('math').factorial
            S = sum(Fr((n-k-q)**(n-k-q-2) if n-k-q >= 1 else 1)/fac(n-1-k-q)*(A[k][k+q]-A[k-2][k+q])/fac(k+q) for q in range(nu-1, B+1))
            chk("Fold/Eu identity", lhsF == thr+S, (n,))
            if n >= 3*k+1:
                chk("src>=inhlin+Fold", src(n) >= inhlin(n)+Fold, (n,))
        if n >= 3*k+1:
            chk("src>=inhlin+apex", src(n) >= inhlin(n)+apex, (n,))
            chk("(7.24)", inhlin(n)+inh(n) == 2*Left(n), (n,))
        if n <= 3*k:
            chk("(7.25)", Ak[n]*(src(n)+inh(n)) == d(n)-KDp(n), (n,))
        # w nondecreasing on [k,2k]
        chk("w nondecr", all(w(n, m+1) >= w(n, m) for m in range(k, 2*k)), (n,))
    n = 3*k
    if n <= M:
        u3k = w(n, 2*k)*s(2*k, k+1)
        chk("(7.26)", src(n)+inh(n) == 2*Left(n)-u3k+Quad(n)+Stem(n), (n,))
        rthr = s(2*k, k+1)/s(2*k-1, k)
        chk("thr-unit-ratio eq", u3k/w(n, k) == eg(2*k)/eg(k)*rthr, (n,))
        print(f"  k={k}: u_3k/w_k = {float(u3k/w(n,k)):.5f}, r_thr = {float(rthr):.5f}, 2Left/w_k = {float(2*Left(n)/w(n,k)):.4f}")
    print(f"k={k}, n<= {M}, n_PD={nPD}: {'all checks passed' if ok else 'SOME FAILED'}")

for k, M in [(3, 20), (4, 24), (5, 26), (6, 28)]:
    run(k, M)

# explicit-bounds (나) and old-2-32(ㄱ) numeric check
print("--- explicit-bounds (나) numeric check m<=80 ---")
def Bor(d): return exp(-d)*d**(d-1)/__import__('math').factorial(d)
def Ren(j): return j*Bor(j) if j >= 1 else 1.0
bad = 0
for m in range(2, 81):
    im = m*log(m/(m+1))+1
    assert 0 <= im <= 1/(2*(m+1))+1/(6*m*(m+1))+1e-15
    for U in range(0, m):
        P = (m-U)*comb(m-1, m-U-1)*float(p(m-U-1))*float(p(U))/float(p(m))
        if P > Bor(U+1)*exp(im)*(m+1)/(m-U)*(1+1e-12): bad += 1
        if P < Bor(U+1)*(1-1e-12): bad += 1
    for j in range(1, m+1):
        P = j*comb(m-1, j-1)*float(p(j-1))*float(p(m-j))/float(p(m))
        if P > Ren(j)*exp(im)*(m+1)/(m+1-j)**2*(1+1e-12): bad += 1
print("violations:", bad)

# R7a: 보조정리 green-atom과 (7.5)를 작은 크기에서 정확 유리수로 검사
from fractions import Fraction as Fr
from math import comb, factorial
def p_(m): return Fr((m+1)**(m-1)) if m >= 1 else Fr(1)
def mul(a, b, N):
    c = [Fr(0)]*(N+1)
    for i, ai in enumerate(a):
        if ai == 0: continue
        for j in range(0, N+1-i):
            c[i+j] += ai*b[j]
    return c
def integ(a, N): return [Fr(0)] + [a[i]/(i+1) for i in range(N)]
def expo(a, N):
    e = [Fr(1)] + [Fr(0)]*N
    for n in range(1, N+1):
        e[n] = sum(i*a[i]*e[n-i] for i in range(1, n+1))/n
    return e
def A_table(N, ell):
    A = [1]
    for n in range(1, N+1):
        A.append(sum(comb(n-1, j)*min(j+1, ell+1)*A[j]*A[n-1-j] for j in range(n)) if ell >= 0 else 0)
    return A
def wpart(N, wg):   # 가중 분배함수 A_n[wg], wg(t) -> Fraction
    A = [Fr(1)]
    for n in range(1, N+1):
        A.append(sum(comb(n-1, j)*wg(j+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
ok = True
for k in (2, 3, 4, 5):
    N = 3*k+2
    T = [Fr(0)] + [Fr(t**(t-1), factorial(t)) for t in range(1, N+1)]
    eT = [p_(n)/factorial(n) for n in range(N+1)]
    T2 = mul(T, T, N)
    Gr = [T[i]-T2[i]/2 for i in range(N+1)]
    z = Fr(k-1)
    ep = expo([z*g for g in Gr], N); em = expo([-z*g for g in Gr], N)
    mono = [Fr(0)]*(N+1); mono[k-1] = Fr(1, factorial(k-1))
    ser = mul(mul(eT, ep, N), integ(mul(em, mono, N), N), N)
    JG = [p_(k-1)*factorial(n)*ser[n] for n in range(N+1)]
    # J_n(k-1) = d/deta K_{n,k}(eta, k-1) at eta=k : 유한 차분 대신 eta의 다항식 보간 (차수 <= n/k <= 3)
    def Kn(eta, y): return wpart(N, lambda t: Fr(t) if t < k else (Fr(eta) if t == k else Fr(y)))
    # eta 차수 <= 3: 네 점 보간으로 도함수
    import sympy as sp
    e_ = sp.symbols('e')
    pts = [k-1, k, k+1, k+2, k+3]
    vals = [Kn(pt, k-1) for pt in pts]
    Am2 = A_table(N, k-2); Am1 = A_table(N, k-1); A0 = A_table(N, k)
    Ky = [wpart(N, lambda t, yy=yy: Fr(t) if t <= k else Fr(yy)) for yy in (k-1, k, k+1, k+2, k+3)]
    for n in range(1, N+1):
        poly = sp.interpolate([(pt, sp.Rational(v[n].numerator, v[n].denominator)) for pt, v in zip(pts, vals)], e_)
        J = sp.diff(poly, e_).subs(e_, k)
        B = vals[1][n] - vals[0][n]          # K(k,k-1) - K(k-1,k-1)
        assert vals[0][n] == Am2[n]
        d = A0[n] - 2*Am1[n] + Am2[n]
        # K''_{n,k}(k): y 다항식 보간(차수 <= n-k <= 2k+2; 작은 크기이므로 충분한 점을 쓴다)
        deg = max(0, n-k)
        ypts = list(range(k-1, k+deg+2))
        yv = [wpart(n, lambda t, yy=yy: Fr(t) if t <= k else Fr(yy))[n] for yy in ypts]
        ypoly = sp.interpolate([(a, sp.Rational(b.numerator, b.denominator)) for a, b in zip(ypts, yv)], e_)
        K2 = sp.diff(ypoly, e_, 2).subs(e_, k)
        jg = sp.Rational(JG[n].numerator, JG[n].denominator)
        c1 = (B <= J); c2 = (J <= jg); c3 = (J == jg) if n <= 2*k else True; c4 = (d >= K2 - jg)
        if not (c1 and c2 and c3 and c4): ok = False; print("FAIL", k, n, c1, c2, c3, c4)
    print("k =", k, "n<=", N, ": B<=J<=J^G, 등호(n<=2k), d>=K''-J^G 확인")
print("all ok:", ok)

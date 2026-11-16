# K2 검산 2: 4.3절의 생성함수 항등식 (4.2)·(4.1)·명제 4.6·(4.9)·M_4/M_0 식을 정확 유리수 멱급수로 검산한다.
from fractions import Fraction as Fr
from math import comb, factorial

def ser_mul(a, b, N):
    c = [Fr(0)] * (N + 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j in range(0, N + 1 - i):
            c[i + j] += ai * b[j]
    return c

def ser_exp(a, N):
    # exp of series a (a[0] may be nonzero only if rational exp... require a[0]==0 here)
    assert a[0] == 0
    e = [Fr(0)] * (N + 1)
    e[0] = Fr(1)
    # e' = a' e  => n e_n = sum_{j=1}^n j a_j e_{n-j}
    for n in range(1, N + 1):
        s = Fr(0)
        for j in range(1, n + 1):
            s += j * a[j] * e[n - j]
        e[n] = s / n
    return e

def ser_int(a, N):
    r = [Fr(0)] * (N + 1)
    for i in range(0, N):
        r[i + 1] = a[i] / (i + 1)
    return r

def poly(coeffs, N):
    r = [Fr(0)] * (N + 1)
    for i, c in enumerate(coeffs):
        if i <= N:
            r[i] = Fr(c)
    return r

def scal(a, c):
    return [x * c for x in a]

def add(a, b):
    return [x + y for x, y in zip(a, b)]

def exp_lin(c, N):
    # e^{c Y}
    return ser_exp(poly([0, c], N), N)

def bor_tail(k, N):
    # Bor^tail_k(Y) = 1 - sum_{j=1}^k e^{-jY} (jY)^{j-1}/j!
    t = poly([1], N)
    for j in range(1, k + 1):
        term = scal(ser_mul(exp_lin(-j, N), poly([0] * (j - 1) + [Fr(j) ** (j - 1)], N), N), Fr(1, factorial(j)))
        t = add(t, scal(term, -1))
    return t

def V(N):
    return poly([Fr(1, 2), -1, Fr(1, 2)], N)  # (1-Y)^2/2

def lagrange_coeff(g, n, N):
    # [x^n] g(T(x)) = [Y^n] g(Y)(1-Y)e^{nY}
    h = ser_mul(ser_mul(g, poly([1, -1], N), N), exp_lin(n, N), N)
    return h[n]

p = lambda m: Fr((m + 1) ** (m - 1)) if m >= 1 else Fr(1)

def K_poly(n, k):
    # K_{n,k}(y) as polynomial in y (list of Fractions), via last-car recursion
    memo = {0: [Fr(1)]}
    def pmul(a, b):
        c = [Fr(0)] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                c[i + j] += x * y
        return c
    def padd(a, b):
        m = max(len(a), len(b))
        return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(m)]
    for m in range(1, n + 1):
        tot = [Fr(0)]
        for j in range(m):
            w = [Fr(j + 1)] if j + 1 <= k else [Fr(0), Fr(1)]
            tot = padd(tot, pmul([Fr(comb(m - 1, j))], pmul(w, pmul(memo[j], memo[m - 1 - j]))))
        memo[m] = tot
    return memo

def peval(a, y):
    return sum(c * y ** i for i, c in enumerate(a))

def pder(a):
    return [i * a[i] for i in range(1, len(a))]

out = []
for k in (3, 4):
    N = 2 * k + 6
    Kp = K_poly(2 * k + 3, k)
    # (4.2) with y rational
    y = Fr(7, 3)
    BT = bor_tail(k, N)
    Vs = V(N)
    eyV = ser_exp(scal(add(Vs, poly([-Fr(1, 2)], N)), y), N)  # e^{y(V - 1/2)}
    # integrand (1-Z)^2 Bor^tail(Z) e^{yV(Z)} : use e^{y(V-1/2)} and fix constant e^{y/2} cancels with e^{-yV(Y)} = e^{-y(V(Y)-1/2)} e^{-y/2}
    inner = ser_int(ser_mul(ser_mul(poly([1, -2, 1], N), BT, N), eyV, N), N)
    emyV = ser_exp(scal(add(Vs, poly([-Fr(1, 2)], N)), -y), N)
    Psi = add(add(poly([1], N), scal(ser_mul(poly([0, 1], N), BT, N), -1)), scal(ser_mul(emyV, inner, N), y))
    g = ser_mul(exp_lin(1, N), Psi, N)  # e^Y Psi(Y)
    ok42 = []
    for n in range(0, 2 * k + 3):
        lhs = peval(Kp[n], y) / factorial(n)
        rhs = lagrange_coeff(g, n, N)
        ok42.append((n, lhs == rhs))
    out.append("k=%d (4.2) y=7/3: n<=2k+1 all equal: %s ; n=2k+2 equal: %s" % (k, all(e for n, e in ok42 if n <= 2 * k + 1), ok42[2 * k + 2][1]))
    # (4.1): e_n = K''_{n,k}(k)
    kk = Fr(k)
    ekV = ser_exp(scal(add(Vs, poly([-Fr(1, 2)], N)), kk), N)
    emkV = ser_exp(scal(add(Vs, poly([-Fr(1, 2)], N)), -kk), N)
    base = ser_mul(ser_mul(poly([1, -2, 1], N), BT, N), ekV, N)
    V2 = ser_mul(Vs, Vs, N)
    Ia = ser_int(ser_mul(base, add(scal(Vs, 2), scal(V2, kk)), N), N)
    Ib = ser_int(ser_mul(base, add(poly([2], N), scal(Vs, 2 * kk)), N), N)
    Ic = ser_int(base, N)
    bracket = add(add(Ia, scal(ser_mul(Vs, Ib, N), -1)), scal(ser_mul(V2, Ic, N), kk))
    Phi = ser_mul(ser_mul(exp_lin(1, N), emkV, N), bracket, N)
    ok41 = []
    for n in range(0, 2 * k + 3):
        en = peval(pder(pder(Kp[n])), kk) if len(Kp[n]) >= 3 else Fr(0)
        rhs = lagrange_coeff(Phi, n, N) * factorial(n)
        ok41.append((n, en == rhs, en))
    out.append("k=%d (4.1) e_n for n<=2k+1 all equal: %s ; e_n values: %s ; n=2k+2 equal: %s" % (k, all(e for n, e, _ in ok41 if n <= 2 * k + 1), [str(v) for _, _, v in ok41[: 2 * k + 2]], ok41[2 * k + 2][1]))
    # 명제 4.6 / J-egf: J_n(k-1) recursion vs Lagrange coefficient
    z = Fr(k - 1)
    J = [Fr(0)] * (2 * k + 1)
    for n in range(0, 2 * k):
        s = sum(comb(n, i) * (z + i + 1) * p(i) * J[n - i] for i in range(0, n + 1))
        if n >= k - 1:
            s += comb(n, k - 1) * p(k - 1) * p(n - k + 1)
        J[n + 1] = s
    # RHS: (k^{k-1}/k!) e^Y e^{-(k-1)V(Y)} int_0^Y (1-Z) Z^{k-1} e^{-kZ} e^{(k-1)V(Z)} dZ   (Bor(k) e^{k(1-Z)} = k^{k-1}/k! e^{-kZ})
    ek1V = ser_exp(scal(add(Vs, poly([-Fr(1, 2)], N)), z), N)   # e^{(k-1)(V-1/2)}
    emk1V = ser_exp(scal(add(Vs, poly([-Fr(1, 2)], N)), -z), N)
    integrand = ser_mul(ser_mul(ser_mul(poly([1, -1], N), poly([0] * (k - 1) + [1], N), N), exp_lin(-k, N), N), ek1V, N)
    G = scal(ser_mul(ser_mul(exp_lin(1, N), emk1V, N), ser_int(integrand, N), N), Fr(k ** (k - 1), factorial(k)))
    ok46 = [(n, J[n] == lagrange_coeff(G, n, N) * factorial(n)) for n in range(0, 2 * k + 1)]
    out.append("k=%d Prop 4.6 / J-egf: J_n(k-1) n<=2k all equal: %s ; J values: %s" % (k, all(e for _, e in ok46), [str(x) for x in J]))

# (4.9) and M_4/M_0 via Hermite numbers
def He_list(n, y):
    Nn = n + y + 1
    He = [Fr(1), Nn]
    for j in range(2, n + 1):
        He.append(Nn * He[j - 1] - (j - 1) * y * He[j - 2])
    return He

def M_ratio(n, y, i):
    # numerator n! [Y^n] (1-Y)^{i+1} B(Y)  with B = sum He_j Y^j/j!  (common factors cancel in ratios)
    He = He_list(n, y)
    def num(ii):
        s = Fr(0)
        for m in range(0, ii + 2):
            if n - m >= 0:
                s += Fr(comb(ii + 1, m)) * (-1) ** m * He[n - m] * Fr(factorial(n), factorial(n - m))
        return s
    return num(i) / num(0)

for (n, y) in [(10, Fr(3)), (11, Fr(7, 2)), (20, Fr(10)), (19, Fr(10)), (20, Fr(19, 2))]:
    He = He_list(n, y)
    theta = He[n] / He[n - 1] - n
    lhs = M_ratio(n, y, 2)
    rhs = (theta * ((n - y) ** 2 + n) - n * (n + 1)) / (y ** 2 * theta)
    out.append("(4.9) n=%d y=%s: equal %s" % (n, y, lhs == rhs))
for k in (5, 6, 7, 8):
    for nu in (0, -1):
        n = 2 * k + nu
        y = Fr(k)
        He = He_list(n, y)
        th = He[n] / He[n - 1] - n
        kk = Fr(k)
        if nu == 0:
            f = 1 + 16 / kk + 18 / kk ** 2 + 2 / kk ** 3 - (4 + 38 / kk + 22 / kk ** 2 + 2 / kk ** 3) / th
        else:
            f = 1 + 12 / kk - 6 / kk ** 2 - (4 + 26 / kk - 14 / kk ** 2) / th
        out.append("M4/M0 k=%d nu=%d: formula equal %s" % (k, nu, M_ratio(n, y, 4) == f))
# M_0 = e^{-y/2}(He_n - n He_{n-1})/p_n  (sanity on i=0 numerator)
with open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체17_K2_series_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))

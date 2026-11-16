"""부록 D 열 인증 「식」(5-15행)의 세 재귀를 정확 유리수로 검산한다.

(1) g, h, e 세 재귀를 Fraction으로 돌려 e_n n!/x^n == A_{n,y-1}(마지막 차 재귀) 인지,
(2) g_n == a°_n x^n (n<=y) 인지, g == exp(Q_{y-1}) 인지(장2의 Q), h_n >= 0 인지,
(3) T_y' + Q_{y-1}' == y * sum_{j<y} a°_j x^j (둘째 재귀 유도의 핵심 항등식),
(4) 척도화한 마지막 차 재귀 n e_n = x sum min(j+1,y) e_j e_{n-1-j} 가 같은 e_n 을 주는지,
(5) 13행 두 식: e^(k+1)-2e^(k)+e^(k-1) == x^n/n! d_{n,k}, 10e^(k+1)>=17e^(k) <=> 10A_{n,k}>=17A_{n,k-1}.
"""
from fractions import Fraction as F
from math import comb, factorial


def a0(m):  # a°_m = (m+1)^{m-1}/m!
    return F((m + 1) ** (m - 1), factorial(m)) if m else F(1)


def lastcar(y, nmax):  # A_{n,y-1}
    a = [1]
    for n in range(1, nmax + 1):
        a.append(sum(comb(n - 1, j) * min(j + 1, y) * a[j] * a[n - 1 - j] for j in range(n)))
    return a


def three_recurrences(y, nmax, x):
    g = [F(1)]
    for n in range(1, nmax + 1):
        g.append(sum(F(j * j ** (j - 1), factorial(j)) * x ** j * g[n - j] for j in range(1, min(y, n) + 1)) / n)
    h = [F(0)]
    for n in range(1, nmax + 1):
        s = y * x * sum(a0(j - 1) * x ** (j - 1) * h[n - j] for j in range(1, min(y, n) + 1))
        if n >= y + 1:
            s += y * x * g[n - 1]
        h.append(s / n)
    e = [F(1)]
    for n in range(1, nmax + 1):
        e.append(g[n] + sum(h[j] * e[n - j] for j in range(1, n + 1)))
    return g, h, e


def scaled_lastcar(y, nmax, x):
    e = [F(1)]
    for n in range(1, nmax + 1):
        e.append(x * sum(min(j + 1, y) * e[j] * e[n - 1 - j] for j in range(n)) / n)
    return e


def series_exp(c, nmax):  # exp of series c (c[0]=0), via n f_n = sum j c_j f_{n-j}
    f = [F(1)]
    for n in range(1, nmax + 1):
        f.append(sum(j * c[j] * f[n - j] for j in range(1, min(n, len(c) - 1) + 1)) / n)
    return f


def main():
    NMAX = 30
    ok_all = True
    for x in (F(3, 8), F(1), F(416066935374, 1 << 40)):
        for y in range(1, 9):
            A = lastcar(y, NMAX)
            g, h, e = three_recurrences(y, NMAX, x)
            e2 = scaled_lastcar(y, NMAX, x)
            c1 = all(e[n] * factorial(n) / x ** n == A[n] for n in range(NMAX + 1))
            c2 = all(g[n] == a0(n) * x ** n for n in range(min(y, NMAX) + 1))
            c3 = all(h[n] >= 0 for n in range(NMAX + 1))
            c4 = e == e2
            # exp(Q_{y-1}) with 장2's Q_{l}(x)=sum_{j<l}(l-j)p_j x^{j+1}/(j+1)!, l=y-1 (scaled by x)
            l = y - 1
            Q = [F(0)] * (NMAX + 1)
            for j in range(l):
                Q[j + 1] = F((l - j) * (j + 1) ** (j - 1 if j else 0) if j else (l - j), factorial(j + 1)) * x ** (j + 1)
            eQ = series_exp(Q, NMAX)
            same_as_expQ = (eQ == g)
            ok = c1 and c2 and c3 and c4
            ok_all &= ok
            print(f"x={x} y={y}: e*n!/x^n==A {c1}; g_n==a_n x^n (n<=y) {c2}; h>=0 {c3}; scaled lastcar==e {c4}; g==exp(Q_(y-1))? {same_as_expQ}")
    # (3) identity T_y' + Q_{y-1}' == y sum_{j<y} a_j x^j  (x=1 suffices: polynomial identity in coefficients)
    for y in range(1, 12):
        Tp = {j: F((j + 1) ** j, factorial(j)) for j in range(y)}  # [x^j] T_y' = (j+1)^j/j!
        Qp = {j: F((y - 1 - j) * ((j + 1) ** (j - 1) if j else 1), factorial(j)) for j in range(y - 1)}
        lhs = {j: Tp.get(j, 0) + Qp.get(j, 0) for j in range(y)}
        rhs = {j: y * a0(j) for j in range(y)}
        assert lhs == rhs, y
    print("T_y' + Q_{y-1}' == y*sum_{j<y} a_j x^j : True for y=1..11")
    # (5) line 13 identities, exact
    x = F(7, 19)
    for k in (2, 3, 5, 8):
        A = {c: lastcar(c, NMAX) for c in (k - 1, k, k + 1)}
        E = {c: three_recurrences(c, NMAX, x)[2] for c in (k - 1, k, k + 1)}
        ok1 = all(E[k + 1][n] - 2 * E[k][n] + E[k - 1][n] == x ** n / factorial(n) * (A[k + 1][n] - 2 * A[k][n] + A[k - 1][n]) for n in range(NMAX + 1))
        ok2 = all((10 * E[k + 1][n] >= 17 * E[k][n]) == (10 * A[k + 1][n] >= 17 * A[k][n]) for n in range(NMAX + 1))
        ok_all &= ok1 and ok2
        print(f"k={k}: line-13 difference identity {ok1}; band equivalence {ok2}")
    print("ALL OK" if ok_all else "SOME CHECK FAILED")


if __name__ == '__main__':
    main()

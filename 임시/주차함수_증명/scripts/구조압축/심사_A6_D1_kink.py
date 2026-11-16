# 심사 A6 — D1(7.5)·R5 검산: 볼록–꺾임 분해(명제 7:old-6-5)와 경계 다항식의 관계.
# 확인(정확 산술, n<=7 전수): (a) Kink_{n,k} := A_{n,k-1} E[H_k]/k = J_n(k)  (J_n(z) := sum_sigma H_k k^{H_k-1} z^{Z_k} prod_{h_i<k} h_i, 2장 정의)
#                              (b) Conv_{n,k} - Kink_{n,k} = d_{n,k} = A_{n,k}-2A_{n,k-1}+A_{n,k-2}
#                              (c) 섬유 부호식: A^sigma_k - 2A^sigma_{k-1} + A^sigma_{k-2} = A^sigma_{k-1} v_k(Z,H)  (2:old-2-14 = 7.2의 재유도)
import itertools, io
from fractions import Fraction as F
from pathlib import Path
ROOT = Path(r"C:\math\임시\주차함수_증명")
def caps(sigma):
    n = len(sigma); h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and sigma[j] < sigma[i]:
            j -= 1
        h.append(i - j)  # distance to nearest larger on the left (position i+1 - position of larger), capacity h_i
    return h
def Abar_piece_poly(perms_h, lo_cap):
    """polynomial in y on [lo_cap, lo_cap+1]: sum_sigma (prod_{h_i<=lo_cap} h_i) y^{#{h_i>lo_cap}} as dict deg->coef"""
    P = {}
    for h in perms_h:
        c = 1; d = 0
        for hi in h:
            if hi <= lo_cap: c *= hi
            else: d += 1
        P[d] = P.get(d, 0) + c
    return P
def poly_eval(P, y):
    return sum(c * F(y) ** d for d, c in P.items())
def poly_d2(P):
    return {d - 2: c * d * (d - 1) for d, c in P.items() if d >= 2}
def integral_weighted(P2, a, sgn):
    """ integral_0^1 (1-f) * P2(a + sgn*f) df exactly, P2 polynomial dict """
    # expand P2(a + sgn f) as polynomial in f via binomial
    from math import comb
    Q = {}
    for d, c in P2.items():
        for j in range(d + 1):
            Q[j] = Q.get(j, 0) + c * comb(d, j) * F(a) ** (d - j) * (sgn ** j)
    # integral_0^1 (1-f) f^j df = 1/(j+1) - 1/(j+2)
    return sum(c * (F(1, j + 1) - F(1, j + 2)) for j, c in Q.items())
out = []
bad_a = bad_b = bad_c = 0; cases = 0
for n in range(1, 8):
    perms = list(itertools.permutations(range(1, n + 1)))
    hs = [caps(s) for s in perms]
    for k in range(2, n + 1):
        A = lambda y: sum(F(1) * __import__("math").prod(min(hi, y) for hi in h) for h in hs)
        # A_{n,y} = sum_sigma prod min(h_i, y+1), so d_{n,k} = Abar(k+1) - 2 Abar(k) + Abar(k-1)
        Ak, Akm1, Akm2 = A(k + 1), A(k), A(k - 1)
        d = Ak - 2 * Akm1 + Akm2
        # Kink
        kink = F(0); J = F(0)
        for h in hs:
            Z = sum(1 for hi in h if hi > k); H = sum(1 for hi in h if hi == k)
            w = __import__("math").prod(min(hi, k) for hi in h)
            kink += F(w * H, k)
            if H >= 1:
                J += H * F(k) ** (H - 1) * F(k) ** Z * __import__("math").prod(hi for hi in h if hi < k)
            # (c) fiber sign formula
            wk = __import__("math").prod(min(hi, k + 1) for hi in h); wm = __import__("math").prod(min(hi, k - 1) for hi in h)
            v = (1 + F(1, k)) ** Z + (1 - F(1, k)) ** (Z + H) - 2
            if F(wk) - 2 * w + wm != w * v:
                bad_c += 1
        if kink != J: bad_a += 1
        # Conv
        P1 = Abar_piece_poly(hs, k)        # on [k, k+1]
        P0 = Abar_piece_poly(hs, k - 1)    # on [k-1, k]
        conv = integral_weighted(poly_d2(P1), k, +1) + integral_weighted(poly_d2(P0), k, -1)
        if conv - kink != d: bad_b += 1
        cases += 1
out.append(f"cases (n<=7, 2<=k<=n): {cases}")
out.append(f"(a) Kink_{{n,k}} == J_n(k): violations = {bad_a}")
out.append(f"(b) Conv - Kink == d_{{n,k}}: violations = {bad_b}")
out.append(f"(c) fiber sign formula per sigma (2.14 == 7.2 derivation): violations = {bad_c}")
txt = "\n".join(out)
print(txt)
io.open(ROOT / "scripts" / "구조압축" / "심사_A6_D1_kink_out.txt", "w", encoding="utf-8").write(txt + "\n")

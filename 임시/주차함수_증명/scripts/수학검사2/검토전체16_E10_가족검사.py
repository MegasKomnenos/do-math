# -*- coding: utf-8 -*-
"""E10 (장10) 독립 검토: 명제 check-ga (a)(b)의 하계를 사슬 재귀로 다시 센다(배정밀도, 검산 목적)."""
import math, sys

def logBor(m):
    return -m + (m - 1) * math.log(m) - math.lgamma(m + 1)

def Bor(m):
    return math.exp(logBor(m))

def chain_s(y, Q):
    """s[q] = frak s_q(y) for 1<=q<=Q via first-step recursion (deficit coordinates)."""
    s = [0.0] * (Q + 2)
    s[1] = 1.0
    lb = [0.0] + [logBor(j) for j in range(1, Q + 2)]
    lby = [logBor(y + q) for q in range(0, Q + 2)]
    for q in range(2, Q + 1):
        tot = 0.0
        acc = 0.0
        for qp in range(1, q):
            pr = math.exp(lb[q - qp] + lby[qp] - lby[q])
            tot += pr
            acc += pr * (y / (y + qp)) * s[qp]
        s[q] = (1.0 - tot) + acc
    return s

def prBorGe(q):
    return 1.0 - sum(Bor(j) for j in range(1, q))

def Ren_star(j):
    return (2 * math.pi) ** -0.5 * j ** -0.5 * math.exp(-1.0 / (12 * j))

def A_up(q0, q):
    return math.sqrt(2 * math.pi) / 4 * math.exp(1.0 / (12 * (q0 - q))) * (q0 + q) * math.sqrt(q0 - q)

def e_low_R(k0, q0, s_y):
    y = k0 + 1
    zR = sum(Ren_star(q0 - q) * math.exp(-(q + A_up(q0, q)) / y) * s_y[q] for q in range(1, q0))
    return k0 / (k0 + 1) * (1 - q0 / (2 * k0)) * (max(zR, s_y[q0] - prBorGe(q0)) + Bor(q0))

f1 = 4 / (3 * math.sqrt(2 * math.pi))
cR = math.sqrt(2 * math.pi) / 2 * math.exp(1 / 12)

def s_low(d, y):
    return math.exp(-f1 * ((y + d - 1) / y) ** 1.5 * d ** 1.5 / y)

def Qfun(y, xi):
    k = y - 1
    q0 = xi * y ** (2 / 3)
    pref = k / (k + 1) * (1 - q0 / (2 * k)) * 2 * (2 * math.pi) ** -0.5 * math.exp(-1 / 12) * y / (cR * q0)
    t1 = math.exp(-q0 / y) * s_low(q0, y) * (math.exp(-cR * q0 / y) - math.exp(-cR * q0 * math.sqrt(q0 / 2) / y))
    t2 = math.exp(-q0 / (2 * y)) * s_low(q0 / 2, y) * (math.exp(-cR * q0 * math.sqrt(q0 / 2 + 1) / y) - math.exp(-cR * q0 ** 1.5 / y))
    return pref * (t1 + t2)

# R# and R#' from the first script (mpmath run); copied values
R = {"bulk": (6668, 2.32368819872827, None, 2 ** (2 / 3)),
     "2": (8065, 3.64244929904270, None, 2 ** (2 / 3)),
     "1b": (9551, 4.27896427450323, 1.81460440307666, 2 ** (2 / 3)),
     "1a": (9705, 4.77025926479757, 1.77025926479757, 1.3)}

for fam, (k0, Rs, Rsp, xicap) in R.items():
    eps0 = math.floor(2 ** (2 / 3) * (k0 + 1) ** (2 / 3))
    s_y = chain_s(k0 + 1, eps0 + 1)
    s_k = chain_s(k0, eps0 + 2)
    best = None; bestq = None
    bestp = None; bestpq = None
    for q0 in range(2, eps0 + 1):
        eR = e_low_R(k0, q0, s_y)
        val = 4 * s_k[q0 + 1] + 2 * eR - Rs
        if best is None or val < best:
            best, bestq = val, q0
        if Rsp is not None and q0 >= 104:
            valp = eR + s_k[q0 + 1] - Rsp
            if bestp is None or valp < bestp:
                bestp, bestpq = valp, q0
    # (b) edge
    y = k0 + 1
    edge = 4 * s_low(xicap * y ** (2 / 3) + 1, k0) + 2 * Qfun(y, xicap) - Rs
    out = "%s k0=%d eps0=%d  (a) min margin %.6f at q0=%d; (b) edge margin %.6f (xi=%.4f)" % (fam, k0, eps0, best, bestq, edge, xicap)
    if Rsp is not None:
        edgep = Qfun(y, 2 ** (2 / 3)) + s_low(2 ** (2 / 3) * y ** (2 / 3) + 1, k0) - Rsp
        out += "; m0>N: (a) min %.6f at q0=%d, (b) edge %.6f" % (bestp, bestpq, edgep)
    print(out)
    # sanity: s_2 value and e_low at q0=2
    print("   s_2(y)=%.8f  s_3(k0)=%.8f  e_low_R(q0=2)=%.6f" % (s_y[2], s_k[3], e_low_R(k0, 2, s_y)))

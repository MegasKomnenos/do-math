# -*- coding: utf-8 -*-
"""Q10 float checks part 2: DDL_2 vs DDL^natural, Thm old-8-22 at moderate k, Lemma old-8-31(i) and
Thm old-8-28 at k=9705, bulk constant r_* vs true u_n/w_{k+1}."""
import numpy as np
from math import log, exp, sqrt, pi, lgamma
import importlib.util, sys, os

spec = importlib.util.spec_from_file_location("q10f", os.path.join(os.path.dirname(os.path.abspath(__file__)), "검토전체11_Q10_float.py"))
q10 = importlib.util.module_from_spec(spec); spec.loader.exec_module(q10)

def g(x): return (x - 1) * log(1 + 1 / x)
def gp(x): return log(1 + 1 / x) - (x - 1) / (x * (x + 1))

def DDL2(k):
    """DDL_2(k) = 2 sum_{d=2}^{k+1} H_d, with H_d per Thm old-8-22 (y0=k)."""
    y0 = k
    ds = np.arange(2, k + 2, dtype=float)
    H = np.zeros(k + 2)
    # precompute g at integers up to 2k+2
    xs = np.arange(1, 2 * k + 3, dtype=float)
    G = (xs - 1) * np.log1p(1 / xs)   # g(x)
    LBor = q10.LB
    for q in range(1, k + 1):
        dd = np.arange(q + 1, k + 2)          # d > q
        j = dd - q
        incp = G[y0 + dd - 1] - G[y0 + q - 1]            # g(y0+d)-g(y0+q)
        incm = G[y0 - 1 + dd - 1] - G[y0 - 1 + q - 1]    # g(y0-1+d)-g(y0-1+q)
        kap = np.exp(incm) + np.exp(-incp) - 2
        tilt = np.exp(LBor[y0 + q] - LBor[y0 + dd])
        Bor_j = np.exp(LBor[j])
        Acrit = (y0 - 1) * kap / (2 * (1 - np.exp(-incp)))
        nq = Acrit * (y0 + 1 + q) / q
        t = (y0 - 1) / (y0 - 1 + q)
        Zmax = int(np.ceil(nq.max())) + 1
        z = np.arange(0, Zmax + 1, dtype=float)
        tz = t ** z
        P1 = np.cumsum(z * tz); P2 = np.cumsum(z * z * tz)
        Z = np.ceil(nq).astype(int) - 1
        Z = np.clip(Z, 0, Zmax)
        inner = P1[Z] - P2[Z] / nq
        term = q * kap * tilt * Bor_j * np.minimum(j, inner)
        H[dd] += term
    return 2 * H.sum(), H

def chain_G_and_E(y, q0):
    """forward DP under Pr^y from q0: G(q)=E[Pi_{j(q)}; pass q]; returns E[Pi_L * L] and E[Pi_L 1_ch] and s_{q0}(y)."""
    LB = q10.LB
    S = q10.s_all(y, q0 + 1)
    Gv = np.zeros(q0 + 1); Gv[q0] = 1.0
    EL = 0.0; Ech = 0.0
    for q in range(q0, 0, -1):
        if q < q0:
            pass
        # stop at q with child of size exactly y: pi_{y+q-1}(y) = Bor(y)Bor(q)/Bor(y+q)
        pich = exp(LB[y] + LB[q] - LB[y + q])
        Ech += Gv[q] * pich
        if q > 1:
            qp = np.arange(1, q)
            pr = np.exp(LB[q - qp] + LB[y + qp] - LB[y + q])
            Gv[qp] += Gv[q] * pr * (y / (y + qp))
    for q in range(1, q0):
        EL += Gv[q] * S[q]
    return EL, Ech, S[q0]

def main():
    # ---- DDL_2 vs DDL^natural ----
    j1, j2 = q10.j_integrals()
    for k in (6667, 8065):
        q10.prep_logBor(3 * k + 10)
        d2, H = DDL2(k)
        print(f"k={k}: DDL_2(k)={d2:.6f}  DDL^nat(k)={q10.DDLnat(k, j1, j2):.6f}  DDL(k)=2*50.62/sqrt(k-1)={2*50.62/sqrt(k-1):.6f}")
    # ---- Thm old-8-22: DD_m >= -H_d at moderate k (exact DD via chain DP, valid d<=y+2) ----
    for k in (40, 80, 200):
        q10.prep_logBor(3 * k + 10)
        S = {y: q10.s_all(y, k + 3) for y in (k - 1, k, k + 1)}
        _, H = DDL2(k)
        worst = 1e9
        for d in range(2, k + 2):
            DD = (k + 1) * S[k + 1][d] - 2 * k * S[k][d] + (k - 1) * S[k - 1][d]
            worst = min(worst, DD + H[d])
        print(f"k={k}: min_d (DD_m + H_d) = {worst:.3e} (>=0 means Thm old-8-22 holds numerically); sum_d DD_m = {sum((k+1)*S[k+1][d]-2*k*S[k][d]+(k-1)*S[k-1][d] for d in range(2,k+2)):.5f}, DDL_2={2*H.sum():.5f}")
    # ---- Lemma old-8-31(i) and Thm old-8-28 at k=9705 ----
    k = 9705; y = k + 1
    q10.prep_logBor(3 * k + 10)
    Sy = q10.s_all(y, k + 3); Sk = q10.s_all(k, k + 3)
    cumBor = np.cumsum(np.concatenate(([0.0], np.exp(q10.LB[1:k + 5]))))
    worst = 1e9; wq = None
    for q0 in range(2, k + 2):
        kc = k * (Sy[q0] - Sk[q0 + 1])
        lb = q10.e_low_R(k, q0, Sy, cumBor)
        if kc - lb < worst: worst, wq = kc - lb, q0
    print(f"k={k}: Lemma old-8-31(i): min_{{q0}} (k c - lower bound) = {worst:.3e} at q0={wq}")
    for q0 in (2, 50, 300, 722, 3000, 9706):
        EL, Ech, s = chain_G_and_E(y, q0)
        kc = k * (Sy[q0] - Sk[q0 + 1])
        bound = (y - 1) / y * (1 - q0 / (2 * y)) * (EL + Ech)
        print(f"   q0={q0}: k c={kc:.6f}  Thm old-8-28 bound={bound:.6f}  ratio={kc/bound if bound>0 else float('nan'):.4f}")
    # ---- bulk r_* at k=6668, nu=0.48k+1 ----
    k = 6668
    q10.prep_logBor(3 * k + 10)
    S = {yy: q10.s_all(yy, k + 3) for yy in (k - 1, k, k + 1)}
    nu = int(0.48 * k) + 1; N = k + nu
    u_over_wk = exp(g(N) - g(k)) * S[k + 1][nu] / S[k][nu]
    wk1_over_wk = exp(g(k + 1) - g(N - 1)) * S[k][nu - 1] / S[k][nu]
    true = u_over_wk / wk1_over_wk
    # r_* with j0 = m_hit
    mh = int(np.ceil(sqrt(5 * k * log(k))))
    pitwo = exp(q10.LB[k] + q10.LB[nu - 1] - 1 - q10.LB[N])
    Piup = np.prod([(k + 1) / (k + i) for i in range(1, mh + 2)])
    rstar_mh = (1 + 1 / k) ** min(mh, nu - 1) + (Piup / pitwo if mh < nu - 1 else 0)
    print(f"k={k} nu={nu}: true u_n/w_(k+1) = {true:.6f}; e^(3/2k) r_*(j0=m_hit) = {exp(1.5/k)*rstar_mh:.6f}; ebar(k)={q10.ebar(k):.6f}; pi_two={pitwo:.3e} >= 0.41508 k^-1.5={0.41508*k**-1.5:.3e}")
    # also check threshold-unit ratio at n=3k: u_3k/w_k < 1.3502
    u3 = exp(g(2 * k) - g(k)) * S[k + 1][k] / S[k][k]
    print(f"   u_(3k)/w_k = {u3:.5f} (<1.3502), 2 v(k) lower bound: T_k(3k)=2V_k(k) = {2*sum((k+1)*(S[k+1][m-k]-S[k][m-k+1])-(k-1)*(S[k][m-k+1]-S[k-1][m-k+2]) for m in range(k+1,2*k)):.4f} (partial, m<2k)")

if __name__ == "__main__":
    main()

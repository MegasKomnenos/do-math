---
weight: unit
short: raising the threshold of a chain sum by two
---
## Description

With $N = k + r + 1$ and $\mu_{\mathrm{mid}}$ the mean number of cuts under the homogeneous law with parameter $k/(k+1+r/2)$ on the compositions of $r$, raising the threshold of the chain sum from $k$ to $k+2$ multiplies it by at least $(1+2/k)^{\mu_{\mathrm{mid}}}$.

## Statement

Let $k \ge 1$ and $r \ge 1$ be natural numbers, and put $N = k + r + 1$, $h_{\mathrm{mid}} = k/(k + 1 + r/2)$ and $\mu_{\mathrm{mid}} = \mu_r(h_{\mathrm{mid}})$. Then

$$\Bigl(1 + \frac2k\Bigr)^{\mu_{\mathrm{mid}}}\ \Lambda_r(k;N) \ \le\ \Lambda_r(k+2;N).$$

Here $\Lambda_m(y;N)$ is the chain sum, the total weight of the compositions of $m$ for the threshold profile $s \mapsto y/(N-s)$ (`Parking.Lam`, `Parking.thr`), $\mu_r(h)$ is the mean number of cuts of a composition of $r$ under the homogeneous law with parameter $h$ (`Parking.muh`), and the power is a real power with the real exponent $\mu_{\mathrm{mid}}$.

## Explanation

The statement bounds the boundary term $B_+ = (a_{k+1}/(k+1))\,\Lambda_r(k+2;N)$ of column $k+1$ in `Parking.dq_frozen` from below by a multiple of the chain sum $\Lambda_r(k;N)$, the same chain sum by which `Parking.Lam_shorten` bounds the boundary term of column $k$ from above.

The chain sum is a polynomial in the threshold, $\Lambda_r(y;N) = \sum_q y^{q-1} V_q$ with $V_q = V_q(r;\lambda^{1,N})$ (`Parking.Lam_thr`). Passing from $y = k$ to $y = k + 2$ multiplies the term of $q$ parts by $c^{q-1}$, $c = 1 + 2/k$. So $\Lambda_r(k+2;N)/\Lambda_r(k;N)$ is the mean of $c^{Q-1}$ under the law of the number of parts $Q$ given by the threshold profile with $y = k$. By Jensen's inequality this mean is at least $c$ to the power of the mean of $Q - 1$. The mean number of cuts under the threshold profile is not known explicitly, however, and the statement replaces it by the mean under a homogeneous law, for which `Parking.mu0_le_muh` gives an explicit lower bound. This replacement is the content of the comparison `Parking.Vc_thr_ratio_ge`: the law of $Q$ under the threshold profile dominates, in the likelihood-ratio order, the homogeneous law whose constant cut weight is the value $h_{\mathrm{mid}} = k/(N - r/2)$ of the threshold profile at the midpoint $s = r/2$ of the segment.

## Proof

Put $c = 1 + 2/k \ge 1$, $h = h_{\mathrm{mid}} > 0$, and for $1 \le q \le r$

$$u_q = T_{r,q}\,h^{q-1}, \qquad v_q = k^{q-1}\,V_q, \qquad V_q = V_q(r;\lambda^{1,N}),$$

with the weights $T_{r,q}$ of the constant profile $1$ (`Parking.Tq`) and the weights of `Parking.Vc` for the profile $s \mapsto 1/(N-s)$. By `Parking.tau_eq`, $\sum_q u_q = \tau_r(h)$. By `Parking.Lam_thr`, $\sum_q v_q = \Lambda_r(k;N)$ and, since $k c = k + 2$, $\sum_q v_q\,c^{q-1} = \Lambda_r(k+2;N)$. The $u_q$ are nonnegative (`Parking.Tq_nonneg`) and the $v_q$ are positive (`Parking.Vc_pos`, the profile being positive at the cut points because $r < N$).

**Likelihood-ratio order.** For $1 \le q$ and $q + 1 \le r$,

$$u_{q+1}\,v_q \le u_q\,v_{q+1}.$$

Indeed `Parking.Tq_ratio` gives $q\,r\,T_{r,q+1} = (q+1)(r-q)\,T_{r,q}$, and `Parking.Vc_thr_ratio_ge`, applicable because $r < N$, gives $(q+1)(r-q)\,V_q \le q\,r\,(N - r/2)\,V_{q+1}$. Hence

$$q\,r\,u_{q+1}\,v_q = (q+1)(r-q)\,T_{r,q}\,h^{q}\,k^{q-1}\,V_q \le q\,r\,T_{r,q}\,h^{q-1}\,k^{q-1}\,\bigl(h\,(N - r/2)\bigr)\,V_{q+1} = q\,r\,u_q\,v_{q+1},$$

because $h\,(N - r/2) = k$ by the choice of $h$. Dividing by $q\,r > 0$ gives the claim. By `Parking.lr_of_consecutive` the inequality extends to all pairs: $u_{q'}\,v_q \le u_q\,v_{q'}$ for $1 \le q \le q' \le r$.

**Monotone test function.** The function $q \mapsto c^{q-1}$ is nondecreasing because $c \ge 1$. The weighted Chebyshev inequality `Parking.lr_sum_le`, for two sequences in likelihood-ratio order and a nondecreasing function, gives

$$\Bigl(\sum_q u_q\,c^{q-1}\Bigr)\Bigl(\sum_q v_q\Bigr) \le \Bigl(\sum_q v_q\,c^{q-1}\Bigr)\Bigl(\sum_q u_q\Bigr), \quad\text{that is,}\quad \Bigl(\sum_q u_q\,c^{q-1}\Bigr)\Lambda_r(k;N) \le \Lambda_r(k+2;N)\,\tau_r(h).$$

**Jensen's inequality.** Let $\mu = \mu_r(h)$. By `Parking.muh_mul_tau`, $\mu\,\tau_r(h) = \sum_q (q-1)\,u_q$. For each $q$, $c^{q-1} = c^{\mu} e^{(\log c)(q-1-\mu)} \ge c^{\mu}\bigl(1 + (\log c)(q-1-\mu)\bigr)$ by $e^t \ge 1 + t$. Multiplying by $u_q \ge 0$ and summing,

$$\sum_q u_q\,c^{q-1} \ \ge\ c^{\mu}\Bigl(\sum_q u_q + (\log c)\Bigl(\sum_q (q-1)u_q - \mu \sum_q u_q\Bigr)\Bigr) = c^{\mu}\,\tau_r(h).$$

**Conclusion.** Since $\Lambda_r(k;N) \ge 0$, the last two displays give $c^{\mu}\,\tau_r(h)\,\Lambda_r(k;N) \le \Lambda_r(k+2;N)\,\tau_r(h)$, and $\tau_r(h) > 0$ (`Parking.tau_pos`) can be cancelled.

---
weight: unit
short: harmonic decay of the tilted prime kernel beyond the threshold
---
## Description

Let $y \ge 2$ and $x \ge 0$. If the tilted free prime kernel $\varepsilon_m x^m$ does not increase on $1 \le m \le y$, then the tilted prime kernel $q_m = \kappa^{(y)}_m x^m$ satisfies $(m+1)\,q_{m+1} \le m\,q_m$ for every $m \ge y$.

## Statement

Let $y \ge 2$ be a natural number and $x \ge 0$ a real number. Suppose that
$$\varepsilon_{m+1}\, x^{m+1} \;\le\; \varepsilon_m\, x^m \qquad \text{for all } 1 \le m < y,$$
where $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`, tilted: `Parking.epsT`). Then, with $q_m = \kappa^{(y)}_m x^m$ the tilted prime kernel of the threshold $y$ (`Parking.kqT`, `Parking.kq`),
$$(m+1)\, q_{m+1} \;\le\; m\, q_m \qquad \text{for all } m \ge y .$$

## Explanation

The conclusion says that $m\,q_m$ does not increase from the threshold on, so that $q_m \le (y/m)\, q_y$ for $m \ge y$: beyond its free range the tilted kernel decays at least like $1/m$. The word harmonic refers to this rate.

The reason is the shape of the recursion `Parking.kqT_rec`, $N q_N = \sum_{\gamma=1}^{y-1} w_\gamma\, q_{N-\gamma}$ with fixed nonnegative weights $w_\gamma = (y-\gamma)\, a_\gamma x^\gamma$, $a_\gamma = \gamma^{\gamma-1}/\gamma!$ (`Parking.cay`). The right-hand sides for $N = m+1$ and $N = m$ involve the same weights and kernel values shifted by one index. If the kernel does not increase on the indices involved, the right-hand side for $m+1$ is at most that for $m$, which is the conclusion. So the harmonic decay at $m$ follows from the monotonicity of the kernel before $m$, and the monotonicity at $m$ follows in turn from the harmonic decay at $m$; the two statements are proved together by one induction, started by the hypothesis on the free range. The hypothesis is a condition on the tilt: it holds at the critical tilt $x_k = (k/(k+1))^{k-1}$ (`Parking.xcrit`) for $y = k$ (`Parking.epsT_succ_le`).

In the proof of the positive signs beyond the first layer for the columns $k\ge82$ (`Parking.step_pos_large`) the statement is used at the critical tilt, in the form $L\,q_L \le k\,q_k$ for $L \ge k$ (`Parking.kap_K3a`), to bound the feedback of distant rows.

## Proof

Write $w_\gamma = (y-\gamma)^+ a_\gamma x^\gamma$, with $(y-\gamma)^+ = \max(y-\gamma,0)$, for the tilted weights (`Parking.kqWT`); they are nonnegative (`Parking.kqWT_nonneg`) and vanish for $\gamma \ge y$. We prove by strong induction on $m \ge 1$ the two statements

- (A$_m$) $q_{m+1} \le q_m$;
- (B$_m$) if $m \ge y$, then $(m+1)\, q_{m+1} \le m\, q_m$.

The theorem is (B$_m$) for $m \ge y$.

Let $m \ge 1$ and suppose (A$_i$) for all $1 \le i < m$.

*Case $m + 1 \le y$.* Both indices lie in the free range, where $q = \varepsilon x^{\cdot}$ (`Parking.kqT_eq_epsT`), and (A$_m$) is the hypothesis on the free kernel. (B$_m$) is void.

*Case $m \ge y$.* The recursion `Parking.kqT_rec` at $N = m+1$ and at $N = m$, written with the sums up to $\gamma = N$ as in its Lean form (the terms with $\gamma \ge y$ are zero), reads
$$(m+1)\, q_{m+1} = \sum_{\gamma=1}^{m+1} w_\gamma\, q_{m+1-\gamma}, \qquad m\, q_m = \sum_{\gamma=1}^{m} w_\gamma\, q_{m-\gamma} .$$
In the first sum the term $\gamma = m+1$ vanishes, since $m+1 \ge y$. Compare the remaining terms for each $1 \le \gamma \le m$. If $\gamma \ge y$, both terms are zero. If $\gamma < y$, then $i = m - \gamma$ satisfies $1 \le i < m$ (because $m \ge y > \gamma$), so (A$_i$) gives $q_{m+1-\gamma} \le q_{m-\gamma}$, and multiplication by $w_\gamma \ge 0$ gives the inequality of the two terms. Summing, $(m+1)\, q_{m+1} \le m\, q_m$, which is (B$_m$).

For (A$_m$): $q_{m+1} \ge 0$ by `Parking.kqT_nonneg`, hence $m\, q_{m+1} \le (m+1)\, q_{m+1} \le m\, q_m$, and division by $m > 0$ gives $q_{m+1} \le q_m$.

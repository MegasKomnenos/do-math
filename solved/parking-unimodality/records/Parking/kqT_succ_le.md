---
weight: unit
short: monotonicity of the tilted prime kernel
---
## Description

Let $y \ge 2$ and $x \ge 0$. If the tilted free prime kernel $\varepsilon_m x^m$ does not increase on $1 \le m \le y$, then the tilted prime kernel $q_m = \kappa^{(y)}_m x^m$ does not increase on $m \ge 1$.

## Statement

Let $y \ge 2$ be a natural number and $x \ge 0$ a real number. Suppose that
$$\varepsilon_{m+1}\, x^{m+1} \;\le\; \varepsilon_m\, x^m \qquad \text{for all } 1 \le m < y,$$
where $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`, tilted: `Parking.epsT`). Then, with $q_m = \kappa^{(y)}_m x^m$ the tilted prime kernel of the threshold $y$ (`Parking.kqT`, `Parking.kq`),
$$q_{m+1} \;\le\; q_m \qquad \text{for all } m \ge 1 .$$

## Explanation

On the free range the tilted kernel is the tilted free kernel, so there the conclusion is the hypothesis. The content is that the monotonicity continues beyond the threshold, for every $m$, although the kernel is no longer explicit there. The mechanism is described in the record of `Parking.kqT_harmonic`, which is the stronger statement on $m \ge y$ and is proved by the same induction.

The range starts at $m = 1$ and not at $m = 0$, because $q_0 = 0$ (`Parking.kq_zero`). At the critical tilt $x_k = (k/(k+1))^{k-1}$ (`Parking.xcrit`) the hypothesis holds for $y = k$ (`Parking.epsT_succ_le`), and the left half of the argument uses the resulting monotonicity of $\kappa^{(k)}_m x_k^m$ to order the weights with which earlier rows feed back into a row.

## Proof

The Lean proof establishes this statement and `Parking.kqT_harmonic` together, by the strong induction on $m$ that is written out in the record of `Parking.kqT_harmonic`; the present statement is the part (A$_m$) of that induction. Its two cases are as follows.

If $m + 1 \le y$, then $q_{m+1} = \varepsilon_{m+1} x^{m+1}$ and $q_m = \varepsilon_m x^m$ by `Parking.kqT_eq_epsT`, and the inequality is the hypothesis.

If $m \ge y$, the harmonic inequality $(m+1)\, q_{m+1} \le m\, q_m$ holds (`Parking.kqT_harmonic`, whose proof at the index $m$ uses the present statement only at indices smaller than $m$). Since $q_{m+1} \ge 0$ by `Parking.kqT_nonneg`, $m\, q_{m+1} \le (m+1)\, q_{m+1} \le m\, q_m$, and division by $m > 0$ gives $q_{m+1} \le q_m$.

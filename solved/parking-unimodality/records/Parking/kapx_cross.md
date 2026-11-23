---
weight: step
short: cross form of the log-convexity of the tilted kernel
---
## Description

At the diagonal tilt, the tilted kernel $\kappa_m = x^m\varepsilon_m$ satisfies $\kappa_{m+t}\,\kappa_r \le \kappa_{r+t}\,\kappa_m$ for $1 \le m \le r$ and every $t \ge 0$.

## Statement

Let $k$, $m$, $r$, $t$ be natural numbers with $1 \le m \le r$. Then $\kappa_{m+t}\,\kappa_r \le \kappa_{r+t}\,\kappa_m$, where $\kappa_m = x^m\varepsilon_m$ is the tilted kernel of `Parking.kapx` at the diagonal tilt $x = 1/\gamma_k$ of `Parking.xk`.

## Explanation

The inequality is the cross form of log-convexity, and it does not depend on the tilt: both sides carry the factor $x^{m+r+t}$. In the two-point argument `Parking.two_point` it is the hypothesis that lets the memory of the nonpositive rows be compared at two rows: with $r$ the offset of the crossing row and $t$ the distance to the target row, the weight $\kappa_{m+t}$ that a nonpositive row has at the target row, relative to the weight $\kappa_m$ it has at the crossing row, is at most $\kappa_{r+t}/\kappa_r$. `Parking.caseA` supplies it in this form.

## Proof

By `Parking.eps_cross`, $\varepsilon_{m+t}\varepsilon_r \le \varepsilon_m\varepsilon_{r+t}$. Multiply both sides by $x^{m+t}x^{r} = x^{r+t}x^{m} \ge 0$.

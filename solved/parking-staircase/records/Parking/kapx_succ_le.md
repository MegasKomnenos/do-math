---
weight: step
short: the tilted kernel does not increase up to 3k/5
---
## Description

At the diagonal tilt $x = 1/\gamma_k$ the tilted kernel $\kappa_m = x^m\varepsilon_m$ satisfies $\kappa_{m+1} \le \kappa_m$ for $1 \le m$, $m + 1 \le \frac35k$ ($k \ge 2$).

## Statement

Let $k \ge 2$ and $m \ge 1$ be natural numbers with $5(m+1) \le 3k$. Then $\kappa_{m+1} \le \kappa_m$, where $\kappa_m = x^m\varepsilon_m$ is the tilted kernel of `Parking.kapx` at the diagonal tilt $x = 1/\gamma_k$ of `Parking.xk`.

## Explanation

The diagonal tilt is the scale in which the diagonal lower bound $\gamma_k\,\beta^{(k-1)}_{j-1} \le \beta^{(k)}_j$ (`Parking.bq_diag_lower`) loses its factor $\gamma_k$. In that scale the feedback kernel of the column equation is $\kappa$, and the two-point argument `Parking.two_point` needs it to be nonincreasing on the range of indices that occur, which `Parking.caseA` restricts to $m \le 0.47k$. The statement is `Parking.eps_succ_le_gam` multiplied by $x^{m+1}$; the range $\frac35k$ is the one of that statement.

## Proof

By `Parking.eps_succ_le_gam`, $\varepsilon_{m+1} \le \gamma_k\varepsilon_m$. Multiply by $x^{m+1} \ge 0$ and use $x\gamma_k = 1$ (`Parking.CrossCrit.xk_mul_gam`): $\kappa_{m+1} = x^{m+1}\varepsilon_{m+1} \le x^m(x\gamma_k)\varepsilon_m = \kappa_m$.

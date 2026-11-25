---
weight: step
short: the tilted prime kernel in the free range
---
## Description

In the free range $1 \le m \le y$ the tilted prime kernel of the threshold $y$ is the tilted free prime kernel: $\kappa^{(y)}_m x^m = \varepsilon_m x^m$.

## Statement

For every natural number $y \ge 1$, every real number $x$ and every natural number $m$ with $1 \le m \le y$,
$$\kappa^{(y)}_m\, x^m \;=\; \varepsilon_m\, x^m ,$$
where $\kappa^{(y)}_m x^m$ is the tilted prime kernel of the threshold $y$ (`Parking.kqT`, `Parking.kq`) and $\varepsilon_m x^m$, $\varepsilon_m = (m-1)^{m-1}/m!$, is the tilted free prime kernel (`Parking.epsT`).

## Explanation

This is `Parking.kq_eq_eps` in tilted form. It supplies the explicit initial values from which the recursion `Parking.kqT_rec` produces the tilted kernel beyond the threshold.

## Proof

$\kappa^{(y)}_m = \varepsilon_m$ for $1 \le m \le y$ by `Parking.kq_eq_eps`; multiply by $x^m$.

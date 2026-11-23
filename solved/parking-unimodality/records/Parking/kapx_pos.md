---
weight: step
short: positivity of the tilted kernel
---
## Description

At the diagonal tilt $x = 1/\gamma_k$ the tilted kernel $\kappa_m = x^m\varepsilon_m$ is positive for every $m \ge 1$.

## Statement

For every natural number $k$ and every natural number $m \ge 1$, $\kappa_m > 0$, where $\kappa_m = x^m\varepsilon_m$ is the tilted kernel of `Parking.kapx`, $x = 1/\gamma_k$ is the diagonal tilt of `Parking.xk`, $\gamma_k = (1+1/k)^{k-2}$, and $\varepsilon_m = (m-1)^{m-1}/m!$.

## Explanation

This is the positivity hypothesis on the kernel in the two-point argument `Parking.two_point`, where it is supplied by `Parking.caseA`. For $m = 0$ the kernel vanishes because $\varepsilon_0 = 0$.

## Proof

$x > 0$ by `Parking.CrossCrit.xk_pos` and $\varepsilon_m > 0$ by `Parking.eps_pos`.

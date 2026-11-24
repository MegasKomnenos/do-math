---
weight: unit
short: nonnegativity of the tilted prime kernel
---
## Description

For a threshold $y \ge 2$ and a tilt $x \ge 0$ the tilted prime kernel is nonnegative: $\kappa^{(y)}_m x^m \ge 0$ for every $m$. With $x = 1$ this is the nonnegativity of the prime kernel itself.

## Statement

For every natural number $y \ge 2$, every real number $x \ge 0$ and every natural number $m$,
$$\kappa^{(y)}_m\, x^m \;\ge\; 0 ,$$
where $\kappa^{(y)}_m = [X^m](1 - 1/Z_y)$ is the prime kernel of the threshold $y$ (`Parking.kq`; $Z_y$ is the series `Parking.Zs`) and $\kappa^{(y)}_m x^m$ its tilted form (`Parking.kqT`).

## Explanation

The prime kernel is defined as a coefficient of $1 - 1/Z_y$ (`Parking.Ks`), and the coefficients of an inverse series have no evident sign. The sign comes from the recursion `Parking.kq_rec`: beyond the free range each value of the kernel is a combination, with nonnegative coefficients, of earlier values, and in the free range the kernel is $\varepsilon_m = (m-1)^{m-1}/m! \ge 0$ (`Parking.eps`). (Under the combinatorial interpretation the kernel counts prime parking functions and is nonnegative for that reason; the library does not use this.)

Nonnegativity is what makes the kernel usable in inequalities. In the proof of the diagonal lower bound `Parking.bq_diag_lower` an induction passes through the sum $\sum_m \kappa^{(k)}_m (\cdot)_{n-m}$, and in the proof of `Parking.step_pos_large` the feedback terms $\kappa^{(k)}_{n-j} x^{n-j}$ of the tilted column inequality are estimated from above and below. The case $x = 1$ gives $\kappa^{(y)}_m \ge 0$.

## Proof

By strong induction on $m$.

For $m = 0$, $\kappa^{(y)}_0 = 0$ (`Parking.kq_zero`).

For $1 \le m \le y$, $\kappa^{(y)}_m x^m = \varepsilon_m x^m$ (`Parking.kqT_eq_epsT`), and $\varepsilon_m \ge 0$ (`Parking.eps_nonneg`), $x^m \ge 0$.

For $m > y$, the recursion `Parking.kqT_rec` gives $m\, \kappa^{(y)}_m x^m = \sum_{\gamma=1}^{m} (y-\gamma)^+ a_\gamma x^\gamma \cdot \kappa^{(y)}_{m-\gamma} x^{m-\gamma}$, where $(y-\gamma)^+ = \max(y-\gamma,0)$ and $a_\gamma = \gamma^{\gamma-1}/\gamma!$ (`Parking.cay`). The weights are nonnegative (`Parking.kqWT_nonneg`), and the kernel values on the right have indices smaller than $m$ and are nonnegative by the induction hypothesis. So the right-hand side is nonnegative, and division by $m > 0$ gives the claim.

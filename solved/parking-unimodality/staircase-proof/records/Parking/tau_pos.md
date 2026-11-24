---
weight: step
short: positivity of the homogeneous total weight
---
## Description

The total weight $\tau_m(h)$ of the compositions of $m \ge 1$ with constant cut weight $h \ge 0$ is positive.

## Statement

For every natural number $m \ge 1$ and every real number $h \ge 0$, $\tau_m(h) > 0$. Here $\tau_m(h)$ (`Parking.tau`) is the total weight of all compositions of $m$ in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and every cut weighs $h$; by `Parking.tau_eq`, $\tau_m(h) = \sum_{q=1}^{m} T_{m,q}\,h^{q-1}$ with $T_{m,q}$ from `Parking.Tq`.

## Explanation

The composition with one part has no cut and weight $a_m > 0$, whatever $h$ is; this is why $h = 0$ is allowed. The positivity makes $\tau_m(h)$ a valid normalisation: the mean number of cuts $\mu_m(h)$ (`Parking.muh`) is a quotient by it (`Parking.muh_mul_tau`, `Parking.muh_nonneg`), and the proofs of `Parking.mu0_le_muh` and `Parking.Lam_gain` use its sign: the first to obtain the positivity of a sum of which $\tau_m(h)$ is a positive multiple, the second when it divides an inequality by $\tau_m(h)$.

## Proof

By `Parking.tau_eq`, $\tau_m(h) = \sum_{q=1}^{m} T_{m,q}\,h^{q-1}$. Every term is nonnegative, by `Parking.Tq_nonneg` and $h \ge 0$. The term with $q = 1$, which occurs because $m \ge 1$, is $T_{m,1}\,h^{0} = T_{m,1}$, and $T_{m,1} > 0$ by `Parking.Tq_pos`.

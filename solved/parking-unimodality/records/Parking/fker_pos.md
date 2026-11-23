---
weight: step
short: positivity of the frozen kernel
---
## Description

The frozen kernel is positive: $f_i > 0$ for every $i \ge 1$.

## Statement

For every natural number $i \ge 1$, $f_i > 0$, where $f$ is the frozen kernel of `Parking.fker` ($f_1 = \frac32e^{-1}$, $f_i = e^{-i}\varepsilon_i$ for $i \ge 2$).

## Explanation

The hypothesis $i \ge 1$ is needed since $f_0 = 0$. Positivity of the kernel on the indices $i \ge 1$ is a hypothesis of `Parking.renewal_pos`, of `Parking.renewal_logConvex` and of `Parking.extreme_column_le`, which are applied to $f$ and its renewal sequence $G$ (`Parking.Gres`).

## Proof

$f_i$ is the sum of $e^{-i}\varepsilon_i$, which is positive by `Parking.eps_pos`, and of a term that is $\frac12e^{-1}$ or $0$.

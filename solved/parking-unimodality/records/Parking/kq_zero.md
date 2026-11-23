---
weight: step
short: the prime kernel at index zero
---
## Description

For a threshold $y \ge 1$, the prime kernel vanishes at the index $0$: $\kappa^{(y)}_0 = 0$.

## Statement

For every natural number $y \ge 1$, $\kappa^{(y)}_0 = 0$, where $\kappa^{(y)}_m = [X^m] K_y$ is the prime kernel of the threshold $y$ (`Parking.kq`) and $K_y = 1 - Z_y^{-1}$ (`Parking.Ks`, with $Z_y$ the series `Parking.Zs` of the threshold $y$).

## Explanation

The prime kernel series has no constant term, so the kernel is a sequence indexed from $1$; the renewal sums $\sum_{m=1}^{n} \kappa^{(y)}_m (\cdot)_{n-m}$ start at $m = 1$ for this reason.

## Proof

The constant coefficient of the inverse of a power series is the inverse of its constant coefficient. The constant coefficient of $Z_y$ is $z^{(y)}_0 = 1$ (`Parking.coeff_Zs`, `Parking.zr_zero`), so the constant coefficient of $K_y = 1 - Z_y^{-1}$ is $1 - 1 = 0$.

---
weight: step
short: constant coefficient of one minus the prime kernel series
---
## Description

For a threshold $y \ge 1$, the constant coefficient of $1 - K_y$ is $1$.

## Statement

For every natural number $y \ge 1$, $[X^0]\,(1 - K_y) = 1$, where $K_y$ is the prime kernel series of the threshold $y$ (`Parking.Ks`).

## Explanation

Together with `Parking.coeff_one_sub_Ks_of_pos` this gives all coefficients of $1 - K_y = 1/Z_y$ ($Z_y$ is the series `Parking.Zs` of the threshold, and $\kappa^{(y)}_m = [X^m] K_y$ is the prime kernel `Parking.kq`): the constant coefficient is $1$ and the coefficient of $X^m$, $m \ge 1$, is $-\kappa^{(y)}_m$. With them the coefficient of $X^n$ in a product $F\,(1-K_y)$ is $F_n - \sum_{m=1}^{n} \kappa^{(y)}_m F_{n-m}$.

## Proof

The constant coefficient of $K_y$ is $\kappa^{(y)}_0$ by the definition of `Parking.kq`, and $\kappa^{(y)}_0 = 0$ by `Parking.kq_zero`. Hence the constant coefficient of $1 - K_y$ is $1 - 0 = 1$.

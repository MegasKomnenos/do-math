---
weight: step
short: the series of a threshold times one minus its prime kernel
---
## Description

For a threshold $y \ge 1$, $Z_y\,(1 - K_y) = 1$: the series of the threshold and one minus its prime kernel series are inverse to each other.

## Statement

For every natural number $y \ge 1$, $Z_y\,(1 - K_y) = 1$ as formal power series, where $Z_y$ is the series of the threshold $y$ (`Parking.Zs`) and $K_y = 1 - Z_y^{-1}$ is its prime kernel series (`Parking.Ks`).

## Explanation

The identity is the relation between the two series in the form in which it is used. Its coefficient of $X^n$, $n \ge 1$, is the renewal equation $z^{(y)}_n = \sum_{m=1}^{n} \kappa^{(y)}_m z^{(y)}_{n-m}$ between the environment $z^{(y)}$ (`Parking.zr`) and the prime kernel $\kappa^{(y)}$ (`Parking.kq`). In the proofs about a column it is the relation by which a product with $Z_k$ and a product with $1 - K_k$ cancel.

## Proof

By definition $1 - K_y = Z_y^{-1}$. A power series over a field whose constant coefficient is not zero satisfies $F \cdot F^{-1} = 1$. The constant coefficient of $Z_y$ is $z^{(y)}_0$ (`Parking.coeff_Zs`), which equals $1$ for $y \ge 1$ (`Parking.zr_zero`).

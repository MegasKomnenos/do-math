---
weight: step
short: the inverse of the series of a threshold
---
## Description

The inverse of the series $Z_y$ of a threshold is $1 - K_y$, where $K_y$ is the prime kernel series.

## Statement

For every natural number $y$, $Z_y^{-1} = 1 - K_y$, where $Z_y$ is the series of the threshold $y$ (`Parking.Zs`) and $K_y = 1 - Z_y^{-1}$ is its prime kernel series (`Parking.Ks`).

## Explanation

This is the definition of $K_y$ solved for the inverse. It is used to replace a division by $Z_y$ with a multiplication by $1 - K_y$; the quotients $Z_{k-1}/Z_k$ and $Z_{k+1}/Z_k$ of the series of a column are handled in that form. That $Z_y^{-1}$ is a two-sided inverse of $Z_y$ is the separate statement `Parking.Zs_mul_one_sub_Ks`, which needs $y \ge 1$.

## Proof

By definition $K_y = 1 - Z_y^{-1}$, so $1 - K_y = Z_y^{-1}$.

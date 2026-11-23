---
weight: step
short: nonnegativity of the flow sum
---
## Description

For $k\ge2$ and every $R$, the sum $\Sigma_\omega=\sum_{i=k+1}^{k+R-1}(i-k+1)\,\omega_i$ of the flow factors of the column $k$ is nonnegative.

## Statement

Let $k\ge2$ and $R$ be natural numbers. Then $\Sigma_\omega\ge0$, where $\Sigma_\omega=\sum_{i=k+1}^{k+R-1}(i-k+1)\,\omega_i$ is the sum `Parking.Somg` and $\omega_i=1-i/((i+1)\,x\gamma_i)$ is the factor `Parking.omg` of the column $k$ ($x$ is the diagonal tilt `Parking.xk`, $\gamma_i$ is `Parking.gam`).

## Explanation

The sign is used at the end of the proof of the crossing criterion `Parking.cross_criterion`, where $\Sigma_\omega$ multiplies a positive quantity, and in `Parking.cross_of_bounds`, where the product of two factors is bounded by the product of their upper bounds, which requires both factors to be nonnegative.

## Proof

Each term is a product of two nonnegative numbers. For $i\ge k+1$ the weight $i-k+1$ is positive. For $i\ge k$, $x\gamma_i\ge1$ (`Parking.CrossCrit.one_le_xk_mul_gam`), hence $(i+1)\,x\gamma_i\ge i+1\ge i$, so $i/((i+1)x\gamma_i)\le1$ and $\omega_i\ge0$.

---
weight: step
short: the tilted ratios are at least one
---
## Description

For $i\ge k\ge2$, $x\,\gamma_i\ge1$, where $x=1/\gamma_k$ is the diagonal tilt of the column $k$ and $\gamma_i=(1+1/i)^{i-2}$.

## Statement

Let $k\ge2$ and $i\ge k$ be natural numbers. Then $1\le x\,\gamma_i$, where $x$ is the diagonal tilt of the column $k$ (`Parking.xk`) and $\gamma_i$ is `Parking.gam`.

## Explanation

The number $x\gamma_n$ is the ratio $\pi_{n+1}/\pi_n$ of two consecutive weights of the column $k$ (`Parking.CrossCrit.pix_succ`). The statement therefore says that the weights $\pi_n$ are nondecreasing from the index $k$ on, which gives the nonnegativity of the corrections $\mathsf e_j$ (`Parking.CrossCrit.ecor_nonneg`) and $\omega_i$ (`Parking.omg`). Equality holds at $i=k$ (`Parking.CrossCrit.xk_mul_gam`).

## Proof

$\gamma$ is nondecreasing on the indices $\ge2$ (`Parking.gam_mono`), so $\gamma_k\le\gamma_i$. Multiplying by $x>0$ (`Parking.CrossCrit.xk_pos`) and using $x\gamma_k=1$ (`Parking.CrossCrit.xk_mul_gam`) gives $1\le x\gamma_i$.

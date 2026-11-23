---
weight: step
short: monotonicity of the factor of the diagonal bound
---
## Description

The factor $\gamma_k=(1+1/k)^{k-2}$ is nondecreasing for $k\ge2$.

## Statement

For all natural numbers $2\le i\le j$, $\gamma_i\le\gamma_j$, where $\gamma_k=(1+1/k)^{k-2}$ (`Parking.gam`).

## Explanation

The diagonal tilt of the column $k$ is $x=1/\gamma_k$ (`Parking.xk`). Where the argument for the column $k$ meets the factor $\gamma_i$ of a later index $i\ge k$, the monotonicity gives $x\,\gamma_i\ge1$ (`Parking.CrossCrit.one_le_xk_mul_gam`); it is also used in the proof of the diagonal lower bound `Parking.bq_diag_lower`.

## Proof

Write $\psi_m=(1+1/m)^{m-1}$. By `Parking.psi_mono`, $\psi_i\le\psi_j$. By `Parking.psi_eq_gam`, $\psi_i=\gamma_i(1+1/i)$ and $\psi_j=\gamma_j(1+1/j)$. Since $i\le j$, $1+1/j\le1+1/i$, and $\gamma_j\ge0$, so
$$\gamma_i\Bigl(1+\frac1i\Bigr)\le\gamma_j\Bigl(1+\frac1j\Bigr)\le\gamma_j\Bigl(1+\frac1i\Bigr).$$
Dividing by $1+1/i>0$ gives $\gamma_i\le\gamma_j$.

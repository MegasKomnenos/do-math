---
weight: step
short: nonnegativity of the tilt correction
---
## Description

For $j\ge k\ge2$ the correction $\mathsf e_j=(j-k+2)-\Pi_{j+1}/\pi_{j+1}$ of the column $k$ is nonnegative.

## Statement

Let $k\ge2$ and $j\ge k$ be natural numbers. Then $\mathsf e_j\ge0$, where $\mathsf e_j=(j-k+2)-\Pi_{j+1}/\pi_{j+1}$ is the correction `Parking.ecor` of the column $k$, $\pi_n$ are the weights `Parking.pix`, and $\Pi_i=\sum_{n=k}^{i}\pi_n$ (`Parking.pixSum`).

## Explanation

The statement says that the sum of the $j-k+2$ weights $\pi_k,\dots,\pi_{j+1}$ is at most $j-k+2$ times the last one. In the crossing criterion `Parking.cross_criterion` it is needed for two signs. The coefficients $\bar\kappa_{N-j}+x\,\mathsf e_j/(j+1)$ of the summed column equation ($\bar\kappa$ is the kernel deficit `Parking.kbar`, $x$ the diagonal tilt `Parking.xk`, $N=k+R$) must be nonnegative before the values $u_j$ of the tilted profile (`Parking.profD`) can be replaced by the largest one. And the factor $\mathsf e_{N-1}+\Sigma_\omega$ on the right side of the criterion must be nonnegative when the criterion is passed to its closed-form version `Parking.cross_of_bounds`.

## Proof

For $n\ge k$, $\pi_{n+1}=x\gamma_n\pi_n$ (`Parking.CrossCrit.pix_succ`, applicable since $n\ge2$) with $x\gamma_n\ge1$ (`Parking.CrossCrit.one_le_xk_mul_gam`) and $\pi_n>0$ (`Parking.CrossCrit.pix_pos`); so $\pi_n\le\pi_{n+1}$, and by induction $\pi_n\le\pi_{j+1}$ for $k\le n\le j+1$. Summing over these $j-k+2$ indices gives $\Pi_{j+1}\le(j-k+2)\,\pi_{j+1}$, and dividing by $\pi_{j+1}>0$ gives $\Pi_{j+1}/\pi_{j+1}\le j-k+2$, which is the claim.

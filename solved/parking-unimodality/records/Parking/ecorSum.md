---
weight: unit
short: accumulated tilt correction
---
## Description

The sum $\mathsf E=\sum_{j=k}^{N-2}\mathsf e_j/(j+1)$, $N=k+R$, of the tilt corrections $\mathsf e_j$ of the column $k$ over the rows below the last two.

## Statement

For natural numbers $k\ge2$ and $R$, with $N=k+R$,
$$\mathsf E=\mathsf E(k,R)=\sum_{j=k}^{N-2}\frac{\mathsf e_j}{j+1},$$
where $\mathsf e_j=(j-k+2)-\Pi_{j+1}/\pi_{j+1}$ is the correction `Parking.ecor` of the column $k$. For $R\le1$ the sum is empty and $\mathsf E=0$.

## Explanation

In the proof of the crossing criterion `Parking.cross_criterion`, the tilted column equation of the column $k-1$ is summed over the rows $k,\dots,N$. After the summation by parts, the coefficient of the tilted profile $u_j=x^j\beta^{(k-1)}_j$ (`Parking.profD`), for $k\le j\le N-2$, is $\bar\kappa_{N-j}+x\,\mathsf e_j/(j+1)$, with $\bar\kappa$ the kernel deficit `Parking.kbar` and $x$ the diagonal tilt `Parking.xk`. When every $u_j$ is replaced by the largest value $u_N$, the second parts of these coefficients add up to $x\,\mathsf E$. So $\mathsf E$ is the total cost, on the left side of the criterion, of the weights $\pi_n$ (`Parking.pix`) not being constant; it is subtracted there from the main term $R(R+1)/N$.

The sum is nonnegative for $k\ge2$ since each $\mathsf e_j$ is (`Parking.CrossCrit.ecor_nonneg`), and it is small: $\mathsf E\le\bar{\mathsf E}=5(R-2)(R-1)R(R+1)/(24k^3)$ (`Parking.Ebar`), which for $R$ of order $k^{2/3}$ is of order $k^{-1/3}$.

In Lean, `ecorSum k R = ∑ j ∈ Icc k (k + R - 2), ecor k j / ((j : ℝ) + 1)`. The upper end $k+R-2$ is a subtraction of natural numbers; for $k\ge2$ it is the ordinary one.

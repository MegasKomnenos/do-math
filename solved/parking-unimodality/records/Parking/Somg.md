---
weight: unit
short: weighted sum of the flow factors
---
## Description

The sum $\Sigma_\omega=\sum_{i=k+1}^{N-1}(i-k+1)\,\omega_i$, $N=k+R$, of the flow factors $\omega_i=1-i/((i+1)x\gamma_i)$ of the column $k$, each weighted by its distance from the row $k$ plus one.

## Statement

For natural numbers $k$ and $R$, with $N=k+R$,
$$\Sigma_\omega=\Sigma_\omega(k,R)=\sum_{i=k+1}^{N-1}(i-k+1)\,\omega_i,$$
where $\omega_i$ is the factor `Parking.omg` of the column $k$. For $R\le1$ the sum is empty and $\Sigma_\omega=0$.

## Explanation

In the proof of the crossing criterion `Parking.cross_criterion` the summed column equation contains the flow term $\sum_{i=k}^{N-1}\Pi_iJ_i$, where $\Pi_i$ are the partial sums `Parking.pixSum` of the weights $\pi_n$ (`Parking.pix`) and $J_i=F_i-F^-_{i-1}$ is the flow described in the record of `Parking.omg` ($F_n$ and $F^-_n$ are the proportions of parking functions of length $n$ with maximum displacement at most $k-1$ and at most $k-2$). Three bounds turn it into $\Sigma_\omega$: $J_k=0$; $J_i\le\omega_i/2$ for $k<i<N$ (the flow bound $J_i\le\omega_i(1-F^-_{i-1})$, together with the budget of that proof, which says that under its hypotheses at most half of the parking functions of length $i-1$ have maximum displacement at least $k-1$); and $\Pi_i\le(i-k+1)\pi_i\le(i-k+1)\pi_N$. Together, under the hypotheses of that proof,
$$\sum_{i=k}^{N-1}\Pi_i\,J_i\le\frac{\pi_N}{2}\,\Sigma_\omega .$$
The weight $i-k+1$ is thus the number of terms of $\Pi_i$. On the right side of the criterion $\Sigma_\omega$ stands next to $\mathsf e_{N-1}$ (`Parking.ecor`).

For $k\ge2$ the sum is nonnegative (`Parking.CrossCrit.Somg_nonneg`). It is the larger of the two terms on the right side of the criterion: by the bound for $\omega_i$ it is at most $\bar H+\frac{5}{2k}\bar G$ (`Parking.Hbar`, `Parking.Gbar`), and its leading part $\sum_{i}(i-k+1)/(i+1)$ is of order $R^2/k$.

In Lean, `Somg k R = ∑ i ∈ Icc (k + 1) (k + R - 1), ((i : ℝ) - k + 1) * omg k i`; the upper end $k+R-1$ is a subtraction of natural numbers, which is the ordinary one except for $k=R=0$.

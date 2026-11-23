---
weight: step
short: ratio of consecutive weights
---
## Description

The weights $\pi_n=x^na_n/n$ of a column $k$ satisfy $\pi_{n+1}=x\,\gamma_n\,\pi_n$ for $n\ge2$, where $\gamma_n=(1+1/n)^{n-2}$.

## Statement

For every natural number $k$ and every natural number $n\ge2$,
$$\pi_{n+1}=x\,\gamma_n\,\pi_n,$$
where $\pi_n$ is the weight `Parking.pix` of the column $k$, $x$ is the diagonal tilt of the column $k$ (`Parking.xk`), and $\gamma_n$ is `Parking.gam` at the index $n$ (not at $k$).

## Explanation

The ratio of consecutive weights is the product of the tilt, which belongs to the column $k$, and the factor $\gamma_n$, which belongs to the row. At $n=k$ the product is $1$, so $\pi_{k+1}=\pi_k$; for $n\ge k$ it is at least $1$ (`Parking.CrossCrit.one_le_xk_mul_gam`). All statements about the size of the corrections $\mathsf e_j$ (`Parking.ecor`) rest on this recursion: it yields $\mathsf e_k=0$ and the recursion for $\mathsf e_j$ given in that record.

## Proof

By `Parking.cay_ratio`, $a_{n+1}=(1+1/n)^{n-1}a_n$ for $n\ge1$, and for $n\ge2$ the factor is $(1+1/n)^{n-1}=\gamma_n\,(1+1/n)=\gamma_n\,(n+1)/n$. Hence
$$\pi_{n+1}=\frac{x^{n+1}a_{n+1}}{n+1}=x\,\gamma_n\cdot\frac{n+1}{n}\cdot\frac{x^n a_n}{n+1}=x\,\gamma_n\,\pi_n .$$

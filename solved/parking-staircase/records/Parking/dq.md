---
weight: unit
short: normalised step of a column
---
## Description

The normalised step of the column $k$ in the row $n$: $\delta^{(k)}_n=\beta^{(k)}_n-\beta^{(k-1)}_n=(b(n,k)-b(n,k-1))/n!$.

## Statement

For natural numbers $k\ge1$ and $n$,
$$\delta^{(k)}_n=\beta^{(k)}_n-\beta^{(k-1)}_n=\frac{b(n,k)-b(n,k-1)}{n!},$$
a real number, where $\beta^{(k)}_n=b(n,k)/n!$ (`Parking.bq`). When the column $k$ is fixed, the other records write $\delta_n$ for $\delta^{(k)}_n$. The Lean definition `dq k n` is also defined for $k=0$, where the subtraction of natural numbers gives $k-1=0$ and hence the value $0$.

## Explanation

The step $d_{n,k}=b(n,k)-b(n,k-1)$ is the difference of two neighbouring entries of the row $n$, and the main theorem says that in every row the steps are first nonnegative and then nonpositive. $\delta^{(k)}_n=d_{n,k}/n!$ has the same sign as $d_{n,k}$; the four records `Parking.dq_nonneg_iff`, `Parking.dq_pos_iff`, `Parking.dq_nonpos_iff`, `Parking.dq_neg_iff` pass between an inequality for the real number $\delta^{(k)}_n$ and the comparison of the natural numbers $b(n,k-1)$ and $b(n,k)$.

The proof studies the step along a column: for fixed $k$, the sequence $n\mapsto\delta^{(k)}_n$. For $k\ge2$ it is the second difference of the environments in the threshold, $\delta^{(k)}_n=z^{(k+1)}_n-2z^{(k)}_n+z^{(k-1)}_n$ (by `Parking.bq_eq`; compare `Parking.d_eq_A`). It vanishes for $n<k$ (`Parking.dq_eq_zero`), starts with the negative value $\delta^{(k)}_k=-a_k/k$ (`Parking.dq_base`), and in the rows $k+1\le n\le2k-1$ it satisfies the column equation `Parking.dq_col`.

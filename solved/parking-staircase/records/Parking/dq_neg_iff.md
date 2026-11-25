---
weight: step
short: negative step, in real and natural form
---
## Description

The normalised step is negative exactly when the count decreases strictly: $\delta^{(k)}_n<0$ if and only if $b(n,k)<b(n,k-1)$.

## Statement

For all natural numbers $k$ and $n$: $\delta^{(k)}_n<0$ if and only if $b(n,k)<b(n,k-1)$. Here $\delta^{(k)}_n=(b(n,k)-b(n,k-1))/n!$ (`Parking.dq`) and $b$ is `Parking.b`. The statement includes $k=0$ with $k-1$ read as $0$, as in the Lean definition; both sides are then false.

## Explanation

One of the four conversions between the sign of the real number $\delta^{(k)}_n$ and the comparison of the counts; see `Parking.dq_nonneg_iff` for their purpose.

## Proof

The statement is the negation of both sides of `Parking.dq_nonneg_iff`: $\delta^{(k)}_n<0$ is the negation of $0\le\delta^{(k)}_n$, and $b(n,k)<b(n,k-1)$ is the negation of $b(n,k-1)\le b(n,k)$.

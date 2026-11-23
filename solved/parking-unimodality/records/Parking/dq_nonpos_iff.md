---
weight: step
short: nonpositive step, in real and natural form
---
## Description

The normalised step is nonpositive exactly when the count does not increase: $\delta^{(k)}_n\le0$ if and only if $b(n,k)\le b(n,k-1)$.

## Statement

For all natural numbers $k$ and $n$: $\delta^{(k)}_n\le0$ if and only if $b(n,k)\le b(n,k-1)$. Here $\delta^{(k)}_n=(b(n,k)-b(n,k-1))/n!$ (`Parking.dq`) and $b$ is `Parking.b`. The statement includes $k=0$ with $k-1$ read as $0$, as in the Lean definition; both sides then hold trivially.

## Explanation

One of the four conversions between the sign of the real number $\delta^{(k)}_n$ and the comparison of the counts; see `Parking.dq_nonneg_iff` for their purpose.

## Proof

The statement is the negation of both sides of `Parking.dq_pos_iff`: $\delta^{(k)}_n\le0$ is the negation of $0<\delta^{(k)}_n$, and $b(n,k)\le b(n,k-1)$ is the negation of $b(n,k-1)<b(n,k)$.

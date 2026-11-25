---
weight: step
short: positive step, in real and natural form
---
## Description

The normalised step is positive exactly when the count increases strictly: $0<\delta^{(k)}_n$ if and only if $b(n,k-1)<b(n,k)$.

## Statement

For all natural numbers $k$ and $n$: $0<\delta^{(k)}_n$ if and only if $b(n,k-1)<b(n,k)$. Here $\delta^{(k)}_n=(b(n,k)-b(n,k-1))/n!$ (`Parking.dq`) and $b$ is `Parking.b`. The statement includes $k=0$ with $k-1$ read as $0$, as in the Lean definition; both sides are then false.

## Explanation

One of the four conversions between the sign of the real number $\delta^{(k)}_n$ and the comparison of the counts; see `Parking.dq_nonneg_iff` for their purpose.

## Proof

$\delta^{(k)}_n=(b(n,k)-b(n,k-1))/n!$ with the difference taken in the real numbers, and $n!>0$. So $0<\delta^{(k)}_n$ if and only if $b(n,k-1)<b(n,k)$ as real numbers, which is the same as the inequality of natural numbers.

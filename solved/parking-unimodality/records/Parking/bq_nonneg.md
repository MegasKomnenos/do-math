---
weight: step
short: nonnegativity of the normalised counts
---
## Description

The normalised counts are nonnegative: $\beta^{(k)}_n=b(n,k)/n!\ge0$.

## Statement

For all natural numbers $k$ and $n$, $0\le\beta^{(k)}_n$, where $\beta^{(k)}_n=b(n,k)/n!$ (`Parking.bq`).

## Explanation

A count divided by a factorial. In the column equation of the step (`Parking.dq_col`) the term $\frac2n\beta^{(k-1)}_{n-1}$ is the source term, and its sign is what the arguments about the sign of the step use.

## Proof

$\beta^{(k)}_n$ is the quotient of the natural number $b(n,k)$ by the positive number $n!$.

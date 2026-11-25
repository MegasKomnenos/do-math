---
weight: step
short: coefficients of the series of a threshold
---
## Description

The coefficient of $X^n$ in the series $Z_y$ of a threshold $y$ is $z^{(y)}_n = A(n,y-1)/n!$.

## Statement

For all natural numbers $y$ and $n$, $[X^n]\, Z_y = z^{(y)}_n$, where $Z_y$ is the series of the threshold $y$ (`Parking.Zs`) and $z^{(y)}_n = A(n,y-1)/n!$ (`Parking.zr`).

## Explanation

This is the definition of $Z_y$ read at one coefficient. It is stated separately because the proofs about the series of a column pass between identities of power series and identities of their coefficients many times.

## Proof

$Z_y$ is defined as the power series whose $n$-th coefficient is $z^{(y)}_n$.

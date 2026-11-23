---
weight: step
short: the tilted environment on the free range
---
## Description

On the free range $N \le y$ of a threshold $y \ge 1$ the tilted environment is the tilted Cayley mass: $z^{(y)}_N x^N = c_N x^N$.

## Statement

For every natural number $y \ge 1$, every real number $x$ and every natural number $N \le y$,
$$z^{(y)}_N\, x^N \;=\; c_N\, x^N ,$$
where $z^{(y)}_N x^N$ is the tilted environment of the threshold $y$ (`Parking.zrT`) and $c_N x^N$, $c_N = (N+1)^{N-1}/N!$, is the tilted Cayley mass (`Parking.ccT`).

## Explanation

A parking function of length $N \le y$ has all displacements smaller than $y$, so the threshold is no restriction there. The identity gives the tilted environment explicitly on its first $y+1$ terms. The conditions on the free range in the monotonicity theorem `Parking.zrT_anti_crit` and the boundary terms of the first-layer recursion in the left half are evaluated through it.

## Proof

$z^{(y)}_N = c_N$ for $N \le y$ by `Parking.zr_eq_cc`; multiply by $x^N$.

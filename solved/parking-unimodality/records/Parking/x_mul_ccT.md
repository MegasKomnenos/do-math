---
weight: step
short: tilted Cayley mass times the tilt
---
## Description

$x \cdot c_N x^N = a_{N+1} x^{N+1}$: a tilted Cayley mass multiplied by the tilt is the tilted tree number of the next index.

## Statement

For every real number $x$ and every natural number $N$,
$$x \cdot c_N\, x^N \;=\; a_{N+1}\, x^{N+1},$$
where $c_N = (N+1)^{N-1}/N!$ (`Parking.cc`, tilted: `Parking.ccT`) and $a_n = n^{n-1}/n!$ (`Parking.cay`, tilted: `Parking.cayT`).

## Explanation

The numbers $c_N$ and $a_{N+1}$ are the same number; the two names index it by the length of a parking function and by the size of a tree. The identity converts between the two tilted forms. With it the Cayley sum $x \sum_{j=1}^{k} c_j x^j$ of `Parking.cayleySum_le_one` is the sum $\sum_{n=2}^{k+1} a_n x^n$ of tilted tree numbers, and the monotonicity of the tilted Cayley masses gives that of the tilted tree numbers in the proof of `Parking.epsT_succ_le`.

## Proof

By definition $c_N = a_{N+1}$, and $x \cdot x^N = x^{N+1}$.

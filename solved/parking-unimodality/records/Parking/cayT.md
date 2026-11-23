---
weight: unit
short: tilted tree numbers
---
## Description

The tilted tree numbers $a_n x^n$ at a tilt $x$, where $a_n = n^{n-1}/n!$ for $n \ge 1$ and $a_0 = 0$.

## Statement

For a real number $x$ and a natural number $n$, the tilted tree number is
$$a_n\, x^n, \qquad a_n = \frac{n^{n-1}}{n!}\ \ (n \ge 1), \quad a_0 = 0$$
(`Parking.cay`).

## Explanation

$n!\,a_n = n^{n-1}$ is the number of rooted labelled trees on $n$ vertices, and $a_n$ is the coefficient of the tree series $T = \sum a_n X^n$. The tilted tree numbers are the tilted Cayley masses (`Parking.ccT`) with the index shifted by one and one more factor $x$: $a_{N+1} x^{N+1} = x \cdot c_N x^N$ (`Parking.x_mul_ccT`). They are given a name of their own because two expressions of this part are naturally written with $a$ and not with $c$: the weights $(y-\gamma)^+ a_\gamma x^\gamma$ of the recursion of the tilted prime kernel (`Parking.kqWT`, `Parking.kqT_rec`), and the comparison $\varepsilon_{m+1} x^{m+1} (1+1/m)^m = a_{m+1} x^{m+1}$, with $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`), between the tilted free prime kernel and the tilted tree numbers, by which `Parking.epsT_succ_le` is proved.

In Lean this is `cayT x n = cay n * x ^ n`.

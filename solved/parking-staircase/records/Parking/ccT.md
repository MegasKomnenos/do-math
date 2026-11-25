---
weight: unit
short: tilted Cayley masses
---
## Description

The tilted Cayley masses $c_N x^N$ at a tilt $x$, where $c_N = (N+1)^{N-1}/N!$ is the number of parking functions of length $N$ divided by $N!$.

## Statement

For a real number $x$ and a natural number $N$, the tilted Cayley mass is
$$c_N\, x^N, \qquad c_N = \frac{(N+1)^{N-1}}{N!}$$
(`Parking.cc`).

## Explanation

The numbers $c_N$ are the normalised counts of all parking functions, without a bound on the displacement. A parking function of length $N \le y$ has all displacements smaller than $y$, so the tilted environment $z^{(y)}_N x^N$ of a threshold $y$ (`Parking.zrT`) coincides with $c_N x^N$ on its free range $N \le y$ (`Parking.zrT_eq_ccT`). The tilted Cayley masses are therefore the explicit beginning of every tilted environment, and the conditions under which a tilted environment behaves well are conditions on them.

The ratio of consecutive masses is $c_{j+1} x^{j+1} / (c_j x^j) = x\,(1 + 1/(j+1))^{j}$ (`Parking.ccT_succ`), which increases with $j$. For a given tilt the masses hence first decrease and then increase, and the critical tilt $x_k$ (`Parking.xcrit`) is the one at which the turning point lies at the indices $k-1$ and $k$ (`Parking.ccT_succ_le`, `Parking.ccT_le_succ`). Multiplied by one more factor $x$, the mass is a tilted tree number: $x \cdot c_N x^N = a_{N+1} x^{N+1}$ (`Parking.x_mul_ccT`, `Parking.cayT`).

In Lean this is `ccT x N = cc N * x ^ N`.

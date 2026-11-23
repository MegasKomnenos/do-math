---
weight: unit
short: tilted environment of a threshold
---
## Description

The tilted environment $z^{(y)}_N x^N$ of a threshold $y$ at a tilt $x$, where $z^{(y)}_N = A(N,y-1)/N!$ is the normalised number of parking functions of length $N$ with all displacements smaller than $y$.

## Statement

For a natural number $y$, a real number $x$ and a natural number $N$, the tilted environment of the threshold $y$ at the tilt $x$ is
$$z^{(y)}_N\, x^N, \qquad z^{(y)}_N = \frac{A(N,y-1)}{N!}$$
(`Parking.zr`; $A(n,k)$ is the number of parking functions of length $n$ with maximum displacement at most $k$).

## Explanation

A tilt is a real number $x$, and to tilt a sequence $(u_N)$ is to pass to $(u_N x^N)$. The recursions of this subject are convolutions: every term of the last-car recursion for $z^{(y)}_{N+1}$ is a product $z^{(y)}_i z^{(y)}_{N-i}$ whose indices add up to $N$. Multiplying the $N$-th term by $x^N$ therefore gives a recursion of the same form, with one extra factor $x$ (`Parking.zrT_succ`). For $x > 0$ the tilt changes no sign, so an inequality between quantities of one row $n$ is the same statement before and after tilting. What the tilt changes is the comparison of different rows: the ratio of consecutive terms is multiplied by $x$. The tilt is a free parameter that is chosen so that the tilted sequence has a property the untilted one lacks. Untilted, the environment increases on its free range $N \le y$, where it equals $c_N = (N+1)^{N-1}/N!$ and $c_{N+1}/c_N = (1+1/(N+1))^N \ge 1$. At the critical tilt $x_k = (k/(k+1))^{k-1}$ (`Parking.xcrit`) the tilted environment of the threshold $k$ never increases (`Parking.zrT_anti_crit`), and sums against it can then be bounded by Abel summation.

The library calls $z^{(y)}$ the environment of the threshold $y$. In the equations of a column it is the sequence against which the quantities of the column are convolved, as in the one-tree bound `Parking.one_tree_bound`. The basic facts about the tilted environment are: it equals $1$ at $N = 0$ (`Parking.zrT_zero`), it is nonnegative for $x \ge 0$ (`Parking.zrT_nonneg`), it does not decrease when the threshold is raised (`Parking.zrT_le_zrT`), and on the free range $N \le y$ it is the tilted Cayley mass $c_N x^N$ (`Parking.zrT_eq_ccT`, `Parking.ccT`). The left half of the argument (the columns $k$ in the rows $n \ge 2k$) is written throughout in terms of the tilted environments of the thresholds $k+1$, $k$, $k-1$ at the critical tilt.

In Lean this is `zrT y x N = zr y N * x ^ N`. All tilted sequences of the library carry the suffix `T` and are written as value times power.

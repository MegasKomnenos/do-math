---
weight: step
short: nonnegativity of the tilted environment
---
## Description

For a tilt $x \ge 0$ the tilted environment of a threshold is nonnegative: $z^{(y)}_N x^N \ge 0$.

## Statement

For every natural number $y$, every real number $x \ge 0$ and every natural number $N$, $z^{(y)}_N\, x^N \ge 0$, where $z^{(y)}_N x^N$ is the tilted environment of the threshold $y$ (`Parking.zrT`; $z^{(y)}_N = A(N,y-1)/N!$).

## Explanation

The tilted environments serve as weights in the sums of the step bound `Parking.step_bound` and of the arguments for the rows $n \ge 2k$ of the columns $k \ge 82$ (`Parking.step_pos_large`, `Parking.DeltaPsi_nonneg`, `Parking.DeltaId_nonneg`), and their nonnegativity is what allows an inequality to be multiplied by them.

## Proof

$z^{(y)}_N \ge 0$ by `Parking.zr_nonneg` (it is a count divided by a factorial), and $x^N \ge 0$ for $x \ge 0$.

---
weight: step
short: the tilted environment at length zero
---
## Description

For a threshold $y \ge 1$ and any tilt $x$, the tilted environment equals $1$ at $N = 0$.

## Statement

For every natural number $y \ge 1$ and every real number $x$, $z^{(y)}_0\, x^0 = 1$, where $z^{(y)}_N x^N$ is the tilted environment of the threshold $y$ (`Parking.zrT`).

## Explanation

This is the initial value of the tilted last-car recursion `Parking.zrT_succ`. It is one of the hypotheses under which the monotonicity of the tilted environment is proved (`Parking.zrT_anti_crit`).

## Proof

$z^{(y)}_0 = 1$ by `Parking.zr_zero`, and $x^0 = 1$.

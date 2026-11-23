---
weight: step
short: positivity of the tilted Cayley masses
---
## Description

For a tilt $x > 0$ the tilted Cayley masses are positive: $c_N x^N > 0$.

## Statement

For every real number $x > 0$ and every natural number $N$, $c_N x^N > 0$, where $c_N = (N+1)^{N-1}/N!$ (`Parking.cc`) and $c_N x^N$ is the tilted Cayley mass (`Parking.ccT`).

## Explanation

The positivity is used wherever an inequality between tilted Cayley masses is multiplied or divided by one of them, for example when the ratio formula `Parking.ccT_succ` is turned into the monotonicity statements `Parking.ccT_succ_le` and `Parking.ccT_le_succ`.

## Proof

$c_N > 0$ by `Parking.cc_pos`, and $x^N > 0$ for $x > 0$.

---
weight: step
short: the tilted environment increases with the threshold
---
## Description

For a tilt $x \ge 0$ and thresholds $y \le y'$, the tilted environment of $y$ is at most that of $y'$: $z^{(y)}_N x^N \le z^{(y')}_N x^N$.

## Statement

For all natural numbers $y \le y'$, every real number $x \ge 0$ and every natural number $N$,
$$z^{(y)}_N\, x^N \;\le\; z^{(y')}_N\, x^N ,$$
where $z^{(y)}_N x^N$ is the tilted environment of the threshold $y$ (`Parking.zrT`; $z^{(y)}_N = A(N,y-1)/N!$).

## Explanation

Raising the threshold admits more parking functions. In the arguments for the rows $n \ge 2k$ of the columns $k \ge 82$ (`Parking.step_pos_large`, `Parking.weighted_debt`, `Parking.DeltaId_nonneg`) the three tilted environments of the thresholds $k-1 \le k \le k+1$ are compared with each other in this way, and the tilted cells (`Parking.Ut`), which are their differences, are nonnegative for this reason.

## Proof

$z^{(y)}_N \le z^{(y')}_N$ by `Parking.zr_mono` (the count $A(N,\ell)$ does not decrease in $\ell$), and the inequality is multiplied by $x^N \ge 0$.

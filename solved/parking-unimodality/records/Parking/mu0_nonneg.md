---
weight: step
short: nonnegativity of the explicit bound for the mean number of cuts
---
## Description

The explicit bound $\mu^0_r(X) = \bigl(\sqrt{(4+X)^2 + 12(r-1)} - (4+X)\bigr)/3$ is nonnegative for $r \ge 1$ and $X \ge 0$.

## Statement

For every natural number $r \ge 1$ and every real number $X \ge 0$,

$$\mu^0_r(X) \;=\; \frac{\sqrt{(4+X)^2 + 12\,(r-1)} - (4+X)}{3} \;\ge\; 0,$$

where $\mu^0_r$ is the function of `Parking.mu0`.

## Explanation

$\mu^0_r(X)$ is the lower bound of `Parking.mu0_le_muh` for a mean number of cuts, so it should be nonnegative, and it is: the square root is at least $4 + X$ because $12(r-1) \ge 0$. The sign is used where $\mu^0_r$ is multiplied by a coefficient that is then bounded or dropped: in the proof of `Parking.step_neg_of_Gfun`, and in the proof of `Parking.Gfun_pos`, which for $2 \le r \le 13$ discards the two terms of the criterion function `Parking.Gfun` that contain $\mu^0_r$, and for $r \ge 14$ bounds $\mu^0_r$ from below by a linear function of $\sqrt r$ that may be negative.

The hypothesis $X \ge 0$ is how the proof knows that $4 + X$ is positive. The inequality itself holds for every real $X$, since a square root is nonnegative; the library does not need that.

## Proof

Since $r \ge 1$, $(4+X)^2 \le (4+X)^2 + 12(r-1)$, and since $4 + X > 0$, taking square roots gives $4 + X \le \sqrt{(4+X)^2 + 12(r-1)}$. The numerator of $\mu^0_r(X)$ is therefore nonnegative.

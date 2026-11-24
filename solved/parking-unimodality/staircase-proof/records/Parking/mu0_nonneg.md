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

$\mu^0_r(X)$ is the lower bound of `Parking.mu0_le_muh` for a mean number of cuts, so it should be nonnegative, and it is: the square root is at least $4 + X$ because $12(r-1) \ge 0$. The sign is used in the proof of `Parking.ledger`, where $\mu^0_q$ occurs in the exponent $E_0 = \frac{q+2}{2q}\,\mu^0_q\bigl(q^2/(k-1)\bigr)$ that multiplies a logarithm: because $E_0 \ge 0$, the logarithm may be replaced by a lower bound, and for $q \le 36$ the product is dropped.

The hypothesis $X \ge 0$ is how the proof knows that $4 + X$ is positive. The inequality itself holds for every real $X$, since a square root is nonnegative; the library does not need that.

## Proof

Since $r \ge 1$, $(4+X)^2 \le (4+X)^2 + 12(r-1)$, and since $4 + X > 0$, taking square roots gives $4 + X \le \sqrt{(4+X)^2 + 12(r-1)}$. The numerator of $\mu^0_r(X)$ is therefore nonnegative.

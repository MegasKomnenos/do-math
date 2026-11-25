---
weight: unit
short: explicit lower bound for the mean number of cuts
---
## Description

$\mu^0_r(X) = \bigl(\sqrt{(4+X)^2 + 12(r-1)} - (4+X)\bigr)/3$, the explicit function that bounds from below the mean number of cuts of a composition of $r$ under a homogeneous law.

## Statement

For a natural number $r$ and a real number $X$,

$$\mu^0_r(X) = \frac{\sqrt{(4+X)^2 + 12(r-1)} - (4+X)}{3}.$$

## Explanation

For $r \ge 1$ the number $\mu^0_r(X)$ is the nonnegative root $\mu$ of the quadratic equation $3\mu^2 + 2(4+X)\mu = 4(r-1)$. It is the lower bound of `Parking.mu0_le_muh`: for $0 < h \le 1$ the mean number of cuts $\mu_r(h)$ under the homogeneous law with parameter $h$ (`Parking.muh`) satisfies $\mu^0_r(X) \le \mu_r(h)$ with $X = r(1/h - 1)$. The record of `Parking.mu0_le_muh` explains where the quadratic comes from.

The variable $X$ measures how far the weight $h$ of a cut lies below $1$. At $h = 1$, the birthday law, $X = 0$ and $\mu^0_r(0) = (\sqrt{12r+4} - 4)/3$, which grows like $\sqrt{4r/3}$. As $X$ grows the bound decreases, in agreement with the fact that a smaller weight per cut makes cuts rarer. The bound is used at one value of $X$: the gain of the boundary chain sum along a diagonal (`Parking.Lam_gain`) has the exponent $E_0 = \frac{q+2}{2q}\,\mu^0_q\bigl(q^2/(k-1)\bigr)$, where $X = q^2/(k-1)$ belongs to the constant cut weight $h = (k-1)/(k-1+q)$, and with this exponent $\mu^0$ enters the inequality between closed forms `Parking.ledger`.

In Lean the definition is `mu0 r X`. For $r \ge 1$ the number under the square root is nonnegative. For $r = 0$ it can be negative, where the Lean square root is $0$ by convention; the definition is used only for $r \ge 1$.

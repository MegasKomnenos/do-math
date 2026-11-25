---
weight: step
short: lower bound for the tilt exponent
---
## Description

The number $\underline a=5/(2k)-4/(3k^2)$, a lower bound for $1+\log x$ where $x=1/\gamma_k$ is the diagonal tilt of the column $k$.

## Statement

For a natural number $k$, $\underline a=\underline a(k)=\dfrac{5}{2k}-\dfrac{4}{3k^2}$.

## Explanation

With $\alpha=1+\log x$ for the diagonal tilt $x$ (`Parking.xk`), one has $\underline a\le\alpha\le\bar a=5/(2k)$ for $k\ge2$; see `Parking.abar` for the role of $\alpha$ and `Parking.xk_bounds` for the proof. The lower bound is nonnegative for $k\ge2$, since $\underline a=(15k-8)/(6k^2)$; this gives $x\ge e^{-1}$, the lower bound of `Parking.xk_bounds`, and the proof of that statement is where $\underline a$ is used.

The two bounds differ by $4/(3k^2)$ only. The term $-\frac{4}{3k^2}$ is the true second coefficient of the expansion of $\alpha$.

In Lean, `alow k = 5 / (2 * (k : ℝ)) - 4 / (3 * (k : ℝ) ^ 2)`; it is used for $k\ge2$.

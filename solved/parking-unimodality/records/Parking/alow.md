---
weight: step
short: lower bound for the tilt exponent
---
## Description

The number $\underline a=5/(2k)-4/(3k^2)$, a lower bound for $1+\log x$ where $x=1/\gamma_k$ is the diagonal tilt of the column $k$.

## Statement

For a natural number $k$, $\underline a=\underline a(k)=\dfrac{5}{2k}-\dfrac{4}{3k^2}$.

## Explanation

With $\alpha=1+\log x$ for the diagonal tilt $x$ (`Parking.xk`), one has $\underline a\le\alpha\le\bar a=5/(2k)$ for $k\ge2$; see `Parking.abar` for the role of $\alpha$ and `Parking.xk_bounds` for the proof. The lower bound is nonnegative for $k\ge2$, since $\underline a=(15k-8)/(6k^2)$; this gives $x\ge e^{-1}$. It is used where a quantity decreases as $\alpha$ grows, namely in the upper bound $\bar t$ for the kernel deficit (`Parking.tup`): a larger tilt makes the kernel masses larger and the deficit smaller, so an upper bound for the deficit needs a lower bound for the tilt.

The two bounds differ by $4/(3k^2)$ only. What the application needs from the lower bound is its first order: $\underline a$ enters only through the upper bound $\bar t$ of the kernel deficit (`Parking.tup`), and with $\underline a$ replaced by $0$ the main inequality of `Parking.cross_of_bounds` fails at $k=265$, $R=70$, whereas a much cruder second-order term would still serve (evaluation of the closed forms, not part of any proof). The term $-\frac{4}{3k^2}$ is the true second coefficient of the expansion of $\alpha$. The delicate estimate of the kernel deficit is the lower bound $\underline t$ (`Parking.tlow`), which uses $\bar a$ and not $\underline a$.

In Lean, `alow k = 5 / (2 * (k : ℝ)) - 4 / (3 * (k : ℝ) ^ 2)`; it is used for $k\ge2$.

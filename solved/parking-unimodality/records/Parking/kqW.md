---
weight: step
short: weights of the prime-kernel recursion
---
## Description

The weights $(y-\gamma)^+\, a_\gamma$ of the recursion of the prime kernel of a threshold $y$, where $a_\gamma = \gamma^{\gamma-1}/\gamma!$.

## Statement

For natural numbers $y$ and $\gamma$,
$$w^{(y)}_\gamma \;=\; (y-\gamma)^+\, a_\gamma ,$$
where $(y-\gamma)^+ = \max(y-\gamma, 0)$ and $a_\gamma = \gamma^{\gamma-1}/\gamma!$ for $\gamma \ge 1$, $a_0 = 0$ (`Parking.cay`).

## Explanation

These are the coefficients with which the prime kernel $\kappa^{(y)}$ (`Parking.kq`) reproduces itself beyond its free range: `Parking.kq_rec` states $N \kappa^{(y)}_N = \sum_{\gamma=1}^{N} w^{(y)}_\gamma\, \kappa^{(y)}_{N-\gamma}$ for $N \ge y \ge 2$, written with the convolution `Parking.rconv`. The weight vanishes for $\gamma = 0$ and for $\gamma \ge y$, so only the terms $1 \le \gamma \le y-1$ contribute, and all weights are nonnegative. The weights arise as the coefficients of the polynomial $\sum_{j \le y-2} (y-1-j)\, c_j X^j$ with $c_j = a_{j+1}$, which measures how far the weight $\min(j+1,y)$ of the last-car recursion falls short of $y$; the proof of `Parking.kq_rec` shows this.

In Lean the factor $(y-\gamma)^+$ is the natural-number subtraction `y - γ`, which stops at zero, cast to a real number.

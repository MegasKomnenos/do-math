---
weight: step
short: tilted weights of the prime-kernel recursion
---
## Description

The tilted weights $(y-\gamma)^+\, a_\gamma x^\gamma$ of the recursion of the tilted prime kernel of a threshold $y$, where $a_\gamma = \gamma^{\gamma-1}/\gamma!$.

## Statement

For a natural number $y$, a real number $x$ and a natural number $\gamma$,
$$(y-\gamma)^+\; a_\gamma\, x^\gamma ,$$
where $(y-\gamma)^+ = \max(y-\gamma,0)$ and $a_\gamma x^\gamma$ is the tilted tree number (`Parking.cayT`; $a_\gamma = \gamma^{\gamma-1}/\gamma!$, $a_0 = 0$).

## Explanation

This is the weight $(y-\gamma)^+ a_\gamma$ of the recursion of the prime kernel (`Parking.kqW`) multiplied by $x^\gamma$. In the recursion `Parking.kq_rec` the indices $\gamma$ and $N - \gamma$ of each term add up to $N$, so after multiplication by $x^N$ the same recursion holds for the tilted kernel with these tilted weights (`Parking.kqT_rec`). The weights are nonnegative for $x \ge 0$ (`Parking.kqWT_nonneg`) and vanish for $\gamma = 0$ and for $\gamma \ge y$.

In Lean the factor $(y-\gamma)^+$ is the natural-number subtraction `y - γ`, which stops at zero, cast to a real number.

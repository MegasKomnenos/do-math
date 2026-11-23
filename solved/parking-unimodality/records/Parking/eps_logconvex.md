---
weight: unit
short: log-convexity of the prime kernel
---
## Description

The prime kernel $\varepsilon_m = (m-1)^{m-1}/m!$ is log-convex: $\varepsilon_{m+1}^2 \le \varepsilon_m\,\varepsilon_{m+2}$ for every $m \ge 1$.

## Statement

For every natural number $m \ge 1$, $\varepsilon_{m+1}^2 \le \varepsilon_m\,\varepsilon_{m+2}$, where $\varepsilon$ is the sequence of `Parking.eps`. In Lean, with $m = n + 1$: `eps (n + 2) ^ 2 ≤ eps (n + 1) * eps (n + 3)` for every natural number $n$.

## Explanation

The statement concerns the indices $m \ge 1$ only; $\varepsilon_0 = 0$ is outside it. Because $\varepsilon_m > 0$, it says that the ratio $g_m = \varepsilon_{m+1}/\varepsilon_m$ of `Parking.gs` does not decrease.

Both persistence arguments for the columns $k \ge 82$ rest on this property. What else they use about $\varepsilon$ are bounds on the size of $\varepsilon_m$ and the value of the sum $\sum_m e^{-m}\varepsilon_m$. Log-convexity survives a geometric tilt, so the tilted kernel $\kappa_m = x^m\varepsilon_m$ satisfies the same cross inequality (`Parking.kapx_cross`), which is the hypothesis of the two-point argument `Parking.two_point` that compares the memory of the nonpositive rows at two different rows. It also passes to the frozen kernel (`Parking.fker_logconvex`) and from there, by the theorem of Kaluza (`Parking.renewal_logConvex`), to the renewal sequence of that kernel, which is what the extreme-column bound `Parking.extreme_column_le` needs.

## Proof

By `Parking.eps_step`, $\varepsilon_{m+1} = g_m\varepsilon_m$ and $\varepsilon_{m+2} = g_{m+1}\varepsilon_{m+1}$. By `Parking.gs_mono`, $g_m \le g_{m+1}$, and by `Parking.eps_pos` the numbers $\varepsilon_m$, $\varepsilon_{m+1}$ are positive. Therefore

$$\varepsilon_{m+1}^2 = \varepsilon_{m+1}\,g_m\,\varepsilon_m \le \varepsilon_{m+1}\,g_{m+1}\,\varepsilon_m = \varepsilon_m\,\varepsilon_{m+2}.$$

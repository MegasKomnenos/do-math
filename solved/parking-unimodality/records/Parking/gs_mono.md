---
weight: step
short: monotonicity of the step ratio
---
## Description

The step ratio $g_m = \varepsilon_{m+1}/\varepsilon_m$ of the prime kernel is nondecreasing in $m$.

## Statement

For natural numbers $1 \le m \le m'$, $g_m \le g_{m'}$, where $g$ is the step ratio of `Parking.gs`. In Lean: the function `gs` (with `gs i` $= g_{i+1}$) is monotone on the natural numbers.

## Explanation

Since $\varepsilon_{m+1} = g_m\varepsilon_m$ (`Parking.eps_step`) and $\varepsilon_m > 0$, the statement is equivalent to the log-convexity of $\varepsilon$, and `Parking.eps_logconvex` is derived from it. It is used a second time in `Parking.caseFar`: the weights $\theta_m = \max(g_m - \gamma_k, 0)$ of the far feedback inherit the monotonicity of $g$, and the extreme-column bound `Parking.extreme_column_le` requires weights that do not decrease.

## Proof

It suffices to show $g_m \le g_{m+1}$ for every $m \ge 1$. For $m = 1$: $g_1 = \frac12$ and $g_2 = \frac23\cdot 2 = \frac43$. For $m = i + 1$ with $i \ge 1$, $g_{i+1} = \frac{i+1}{i+2}(1+\frac1i)^i$ is a product of two nonnegative factors, and each does not decrease when $i$ is replaced by $i+1$: $\frac{i+1}{i+2} \le \frac{i+2}{i+3}$ because $(i+1)(i+3) \le (i+2)^2$, and $(1+\frac1i)^i \le (1+\frac1{i+1})^{i+1}$ by `Parking.chi_mono`, which states that $(1+1/i)^i$ is nondecreasing in $i \ge 1$.

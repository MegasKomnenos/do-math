---
weight: step
short: the step ratio as a quotient of the prime kernel
---
## Description

Consecutive values of the prime kernel are related by the step ratio: $\varepsilon_{m+1} = g_m\,\varepsilon_m$ for every $m \ge 1$.

## Statement

For every natural number $m \ge 1$, $\varepsilon_{m+1} = g_m\,\varepsilon_m$, where $\varepsilon_m = (m-1)^{m-1}/m!$ is the sequence of `Parking.eps` and $g_m$ is the step ratio of `Parking.gs`. In Lean, with $m = i + 1$: `eps (i + 1 + 1) = gs i * eps (i + 1)` for every natural number $i$.

## Explanation

This is the statement that the explicit formula of `Parking.gs` is the quotient $\varepsilon_{m+1}/\varepsilon_m$. It is written as a product so that no division occurs. Every later estimate of $\varepsilon_{m+1}$ against $\varepsilon_m$ passes through it: the log-convexity `Parking.eps_logconvex`, the comparison with $\gamma_k$ in `Parking.eps_succ_le_gam`, and the monotonicity of $(k+\rho)\kappa_\rho$ in `Parking.Fk_anti`.

## Proof

For $m = 1$: $\varepsilon_2 = 1^1/2! = \frac12$ by `Parking.eps_succ`, $\varepsilon_1 = 1$ by `Parking.eps_one`, and $g_1 = \frac12$ by `Parking.gs_zero`.

For $m = i + 1$ with $i \ge 1$: by `Parking.eps_succ`, $\varepsilon_{i+2} = (i+1)^{i+1}/(i+2)!$ and $\varepsilon_{i+1} = i^i/(i+1)!$. Hence

$$\frac{\varepsilon_{i+2}}{\varepsilon_{i+1}} = \frac{(i+1)^{i+1}}{(i+2)\,i^i} = \frac{i+1}{i+2}\Bigl(1+\frac1i\Bigr)^{i} = g_{i+1},$$

which is a routine calculation with $(i+2)! = (i+2)(i+1)!$.

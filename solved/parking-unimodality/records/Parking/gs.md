---
weight: unit
short: step ratio of the prime kernel
---
## Description

The step ratio $g_m = \varepsilon_{m+1}/\varepsilon_m$ of the prime kernel $\varepsilon_m = (m-1)^{m-1}/m!$, defined by the explicit formula $g_1 = \frac12$, $g_m = \frac{m}{m+1}\bigl(1+\frac1{m-1}\bigr)^{m-1}$ for $m \ge 2$.

## Statement

For a natural number $m \ge 1$ put

$$g_1 = \frac12, \qquad g_m = \frac{m}{m+1}\Bigl(1+\frac1{m-1}\Bigr)^{m-1} \quad (m \ge 2).$$

The Lean function counts from zero: `gs i` is $g_{i+1}$, that is, `gs i` $= \frac{i+1}{i+2}\,(1+1/i)^{i}$ for every natural number $i$. For $i = 0$ the second factor is a zeroth power and equals $1$, which gives the value $\frac12$.

## Explanation

The number $g_m$ is the ratio of two consecutive values of the prime kernel $\varepsilon$ of `Parking.eps`: $\varepsilon_{m+1} = g_m\,\varepsilon_m$ for $m \ge 1$ (`Parking.eps_step`). Indeed $\varepsilon_{m+1}/\varepsilon_m = m^m/\bigl((m+1)(m-1)^{m-1}\bigr)$. The definition is the closed formula and not the quotient, so that the ratio can be estimated directly. In Lean, $1/0 = 0$, so the formula at $i = 0$ is $\frac12 \cdot 1^0$ (`Parking.gs_zero`), in agreement with $\varepsilon_2/\varepsilon_1 = \frac12$.

The ratio does not decrease in $m$ (`Parking.gs_mono`); this is the log-convexity of $\varepsilon$ (`Parking.eps_logconvex`).

The persistence argument for a column $k$ compares $g_m$ with the constant $\gamma_k = (1+1/k)^{k-2}$ of `Parking.gam`. The comparison enters in two ways, which are the same fact. First, the kernel in the diagonal scale, $\kappa_m = \varepsilon_m/\gamma_k^m$ (`Parking.kapx`), does not increase from $m$ to $m+1$ exactly when $g_m \le \gamma_k$. Second, the coefficient $\gamma_k\varepsilon_m - \varepsilon_{m+1} = \varepsilon_m(\gamma_k - g_m)$ of `Parking.persistence_inequality` is nonnegative exactly when $g_m \le \gamma_k$. Since $\log g_m = 1 - \frac{3}{2m} + O(m^{-2})$ and $\log\gamma_k = 1 - \frac{5}{2k} + O(k^{-2})$, the two quantities agree to first order at $m = \frac35 k$. The library proves $g_m \le \gamma_k$ for $m + 1 \le \frac35 k$ (`Parking.eps_succ_le_gam`) and, for larger $m$, only bounds the possible excess $g_m - \gamma_k$ from above (`Parking.theta_f_le`). This is the reason why the offset $\frac35 k$ separates two regimes in `Parking.caseFar`.

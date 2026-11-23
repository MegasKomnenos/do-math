---
weight: step
short: the prime kernel grows by at most the diagonal factor up to 3k/5
---
## Description

For $k \ge 2$ and $1 \le m$ with $m + 1 \le \frac35k$: $\varepsilon_{m+1} \le \gamma_k\,\varepsilon_m$, where $\varepsilon_m = (m-1)^{m-1}/m!$ and $\gamma_k = (1+1/k)^{k-2}$.

## Statement

Let $k \ge 2$ and $m \ge 1$ be natural numbers with $5(m+1) \le 3k$. Then

$$\varepsilon_{m+1} \le \gamma_k\,\varepsilon_m,$$

where $\varepsilon$ is the sequence of `Parking.eps` and $\gamma_k = (1+1/k)^{k-2}$ is the number of `Parking.gam`.

## Explanation

In terms of the step ratio $g_m = \varepsilon_{m+1}/\varepsilon_m$ of `Parking.gs` the statement is $g_m \le \gamma_k$ for $m + 1 \le \frac35k$. Both numbers are a little below $e$: $g_m \le \exp\bigl(1 - \frac{3}{2(m+1)}\bigr)$ and $\gamma_k \ge \exp\bigl(1 - \frac{5}{2k}\bigr)$, and the hypothesis $5(m+1) \le 3k$ is exactly the comparison of the two exponents. The two exponential bounds are proved below and are used again in `Parking.Fk_anti` and `Parking.theta_f_le`.

The statement fixes the range in which the kernel behaves well in the diagonal scale of the column $k$. It has two consequences. The tilted kernel $\kappa_m = \varepsilon_m/\gamma_k^m$ does not increase up to the index $\frac35k$ (`Parking.kapx_succ_le`), which the two-point argument needs. And the coefficients $\gamma_k\varepsilon_m - \varepsilon_{m+1}$ of `Parking.persistence_inequality` are nonnegative for $m + 1 \le \frac35k$, so that in `Parking.caseFar` the rows up to the offset $\frac35k$ need no estimate of those terms, while the rows beyond it do. The bound $\frac35$ cannot be improved by more than a term of lower order, since to first order $g_m$ and $\gamma_k$ agree at $m = \frac35k$ (see `Parking.gs`).

## Proof

Write $m = i + 1$, so that $\varepsilon_{m+1} = g_m\varepsilon_m$ with $g_m = \frac{i+1}{i+2}(1+\frac1i)^i$ by `Parking.eps_step`. Since $\varepsilon_m \ge 0$, it suffices to show $g_m \le \gamma_k$.

*The upper bound of $g$.* For $i \ge 1$, that is $m \ge 2$,

$$g_{i+1} \le \exp\Bigl(1 - \frac{3}{2(i+2)}\Bigr).$$

Indeed $g_{i+1} = \exp\bigl(-\log(1+\frac1{i+1}) + i\log(1+\frac1i)\bigr)$. By `Parking.log_one_add_le3`, $\log(1+u) \le u - \frac{u^2}2 + \frac{u^3}3$ at $u = \frac1i$, and by `Parking.log_one_add_ge2`, $\log(1+u) \ge u - \frac{u^2}{2}$ at $u = \frac1{i+1}$. The difference between $1 - \frac3{2(i+2)}$ and the resulting upper bound of the exponent is

$$\frac{7i^3 + 4i^2 - 4i - 4}{6\,i^2(i+1)^2(i+2)},$$

which is nonnegative for $i \ge 1$.

*The lower bound of $\gamma$.* For $k \ge 2$, $\gamma_k \ge \exp\bigl(1 - \frac{5}{2k}\bigr)$. This is the upper bound $x \le e^{-1}e^{5/(2k)}$ of `Parking.xk_bounds` for the diagonal tilt $x = 1/\gamma_k$ of `Parking.xk`, inverted by means of $x\gamma_k = 1$ (`Parking.CrossCrit.xk_mul_gam`).

*Conclusion.* For $m = 1$: $g_1 = \frac12$ (`Parking.gs_zero`) and $\gamma_k \ge 1$, since $\gamma_k$ is a power of a number at least $1$. For $m = i + 1 \ge 2$: the hypothesis $5(i+2) \le 3k$ is equivalent to $\frac5{2k} \le \frac{3}{2(i+2)}$, hence $g_m \le \exp\bigl(1 - \frac3{2(i+2)}\bigr) \le \exp\bigl(1 - \frac5{2k}\bigr) \le \gamma_k$.

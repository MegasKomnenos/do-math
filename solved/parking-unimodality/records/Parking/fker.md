---
weight: unit
short: the frozen kernel
---
## Description

The frozen kernel $f$: $f_1 = \frac32 e^{-1}$ and $f_i = e^{-i}\varepsilon_i$ for $i \ge 2$, where $\varepsilon_i = (i-1)^{i-1}/i!$. It is the prime kernel in the Borel scale with $\frac12e^{-1}$ added at the index $1$.

## Statement

For a natural number $i$,

$$f_i = e^{-i}\,\varepsilon_i + \begin{cases}\tfrac12 e^{-1} & \text{if } i = 1,\\ 0 & \text{otherwise,}\end{cases}$$

where $\varepsilon$ is the sequence of `Parking.eps`. Thus $f_0 = 0$, $f_1 = \frac32e^{-1}$, and $f_i = e^{-i}\varepsilon_i$ for $i \ge 2$. In Lean: `fker i`.

## Explanation

The kernel is made for one purpose: to write the column of the level $k-1$ as a sequence with nonnegative innovations with respect to a kernel that does not depend on $k$. Let $u_n = b(n,k-1)/n!$. The column equation of the level $k-1$ (`Parking.bq_L0`) reads, on the rows $k \le n \le 2k-1$,

$$u_n = \frac{z_{n-1}}{n} + \frac{k-1}{n}\,u_{n-1} + \sum_{m=1}^{n-k}\varepsilon_m\,u_{n-m},$$

with a nonnegative source term $z_{n-1}/n$. The coefficient $\frac{k-1}{n}$ of the preceding row depends on the row, and it is at least $\frac12$ as long as $n \le 2k-2$. Replacing it by the constant $\frac12$ ("freezing" it) and dropping the source turns the equation into the inequality $u_n \ge (\varepsilon_1 + \frac12)u_{n-1} + \sum_{m\ge2}\varepsilon_mu_{n-m}$. In the Borel scale $v_\sigma = e^{-\sigma}u_{k+\sigma}$ this is $v_\sigma \ge \sum_{i=1}^{\sigma}f_iv_{\sigma-i}$, with exactly the kernel $f$: the summand $\frac12e^{-1}$ at $i = 1$ is the frozen coefficient. The argument is carried out in the proof of `Parking.caseFar`.

The factor $e^{-i}$ is chosen because $e^{-1}$ is the scale at which the prime kernel is summable with total mass below one: $\sum_m e^{-m}\varepsilon_m = 1 - e^{-1}$ (`Parking.hasSum_eps`). Hence every partial sum of $f$ is at most $1 - \frac12e^{-1} < 1$, and the renewal sequence of $f$ is summable (`Parking.Gres_sum_le`).

Because $f$ does not depend on the column or on the row, its renewal sequence is a single sequence, $G$ of `Parking.Gres` (`Parking.Gres_isRenewal`), for which a closed form and explicit bounds are available. The kernel is positive (`Parking.fker_pos`) and log-convex (`Parking.fker_logconvex`), which are the hypotheses of the extreme-column bound `Parking.extreme_column_le`.

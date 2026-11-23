---
weight: unit
short: tilted free prime kernel
---
## Description

The tilted free prime kernel $\varepsilon_m x^m$ at a tilt $x$, where $\varepsilon_m = (m-1)^{m-1}/m!$ for $m \ge 1$ and $\varepsilon_0 = 0$.

## Statement

For a real number $x$ and a natural number $m$, the tilted free prime kernel is
$$\varepsilon_m\, x^m, \qquad \varepsilon_m = \frac{(m-1)^{m-1}}{m!}\ \ (m \ge 1), \quad \varepsilon_0 = 0$$
(`Parking.eps`; $\varepsilon_1 = 1$).

## Explanation

The sequence $\varepsilon$ is the prime kernel of the parking functions without a bound on the displacement: $\sum_{m=1}^{n} \varepsilon_m c_{n-m} = c_n$ for $n \ge 1$ (`Parking.eps_conv`), with $c_n = (n+1)^{n-1}/n!$. The prime kernel $\kappa^{(y)}$ of a threshold $y$ (`Parking.kq`) agrees with it for $1 \le m \le y$ (`Parking.kq_eq_eps`), and so the tilted prime kernel $\kappa^{(y)}_m x^m$ (`Parking.kqT`) agrees with $\varepsilon_m x^m$ there (`Parking.kqT_eq_epsT`). The tilted free prime kernel is thus the explicit beginning of the tilted prime kernel of every threshold. The decay of $\kappa^{(y)}_m x^m$ beyond the threshold is derived from the hypothesis that $\varepsilon_m x^m$ does not increase on $1 \le m \le y$ (`Parking.kqT_succ_le`, `Parking.kqT_harmonic`), and at the critical tilt $x_k = (k/(k+1))^{k-1}$ (`Parking.xcrit`) this hypothesis holds for $y = k$ (`Parking.epsT_succ_le`). The first two values are $\varepsilon_1 x = x$ and $\varepsilon_2 x^2 = x^2/2$ (`Parking.epsT_one`, `Parking.epsT_two`).

In Lean this is `epsT x m = eps m * x ^ m`. The crossing criterion and the chain column use the same sequence at another tilt, the diagonal tilt $1/\gamma_k$ with $\gamma_k = (1+1/k)^{k-2}$ (`Parking.gam`), under the name `Parking.kapx` and with the power written first.

---
weight: unit
short: renewal equation of the numbers c_n
---
## Description

The numbers $c_n = (n+1)^{n-1}/n!$ satisfy the renewal equation $c_n = \sum_{m=1}^{n} \varepsilon_m\, c_{n-m}$ for $n \ge 1$, with the kernel $\varepsilon_m = (m-1)^{m-1}/m!$.

## Statement

For every natural number $n \ge 1$,

$$\sum_{m=1}^{n} \varepsilon_m\, c_{n-m} = c_n,$$

where $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`) and $\varepsilon_m = (m-1)^{m-1}/m!$ for $m \ge 1$, with $\varepsilon_1 = 1$ (`Parking.eps`).

## Explanation

Together with $c_0 = 1$, the equation says that $c$ is the renewal sequence of the kernel $\varepsilon$. It is the coefficient form of $(1/P) \cdot P = 1$ for the series $P = \sum_n c_n X^n$, given that $1/P = 1 - \sum_{m \ge 1} \varepsilon_m X^m$ (`Parking.TreeSeries.coeff_Eser_mul`). Multiplied by $n!$ it reads $(n+1)^{n-1} = \sum_{m=1}^{n} \binom{n}{m} (m-1)^{m-1} (n-m+1)^{n-m-1}$, which classically expresses the decomposition of a parking function into a first prime block of $m$ cars and a parking function of the remaining $n - m$; the library does not use that reading.

The hypothesis $n \ge 1$ is needed: for $n = 0$ the sum is empty while $c_0 = 1$.

The equation is used in two places. In the free range of a threshold, where the normalised counts equal $c_n$, it identifies the prime kernel of the threshold with $\varepsilon$ (`Parking.kq_eq_eps`). And, multiplied by $e^{-n}$, it is the renewal equation from which the sum $\sum_m e^{-m}\varepsilon_m = 1 - e^{-1}$ is obtained (`Parking.hasSum_eps`).

## Proof

Let $E = 1/P$ (`Parking.TreeSeries.Eser`). By `Parking.TreeSeries.Eser_mul_Pser`, $EP = 1$, so for $n \ge 1$ the coefficient of $X^n$ in $EP$ is $0$. By `Parking.TreeSeries.coeff_Eser_mul` with $f = P$, whose coefficients are $c_n$ (`Parking.TreeSeries.coeff_Pser`), that coefficient is $c_n - \sum_{m=1}^{n} \varepsilon_m\, c_{n-m}$.

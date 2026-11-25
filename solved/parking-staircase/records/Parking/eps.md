---
weight: unit
short: free prime kernel ε_m
---
## Description

The numbers $\varepsilon_m = (m-1)^{m-1}/m!$ for $m \ge 1$ (so $\varepsilon_1 = 1$), with $\varepsilon_0 = 0$.

## Statement

For a natural number $m$, the real number $\varepsilon_m$ is defined by $\varepsilon_0 = 0$ and

$$\varepsilon_m = \frac{(m-1)^{m-1}}{m!} \qquad (m \ge 1),$$

where $0^0 = 1$, so that $\varepsilon_1 = 1$.

## Explanation

The numbers $\varepsilon_m$ are, up to sign, the coefficients of the inverse of the series $P = \sum_n c_n X^n$ of the normalised parking numbers $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`): $1/P = 1 - \sum_{m \ge 1} \varepsilon_m X^m$ (`Parking.TreeSeries.coeff_Eser_mul`). Equivalently, $\varepsilon$ is the kernel of the renewal equation that $c$ satisfies, $c_n = \sum_{m=1}^{n} \varepsilon_m c_{n-m}$ for $n \ge 1$ (`Parking.eps_conv`). This is the reason for the definition, and it is what the library uses.

Classically, $(m-1)^{m-1}$ is the number of prime parking functions of length $m$, and the renewal equation, multiplied by $n!$, expresses that a parking function of length $n$ consists of a prime parking function on some $m$ of the cars followed by a parking function on the remaining $n-m$. The library does not use this interpretation; it obtains the equation from power series.

The first values are $\varepsilon_1 = 1$, $\varepsilon_2 = 1/2$, $\varepsilon_3 = 2/3$, $\varepsilon_4 = 9/8$. The identity $m\,\varepsilon_m = (m-1)^{m-1}/(m-1)!$ (`Parking.mul_eps`) connects $\varepsilon$ with the sequence $n^n/n!$ (`Parking.ren`), and through it with Stirling's formula.

Further on, $\varepsilon$ is the feedback kernel of the column equations (`Parking.bq_L0`, `Parking.dq_col`), and the prime kernel of a threshold agrees with it in the free range (`Parking.kq_eq_eps`).

The value $\varepsilon_0 = 0$ is a convention; it lets sums over $1 \le m \le n$ be written as sums over $0 \le m \le n$. In Lean the base of the power is the real number `(m : ℝ) - 1` and the exponent is the natural number `m - 1`; at $m = 1$ Lean's convention $0^0 = 1$ gives $\varepsilon_1 = 1$.

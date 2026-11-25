---
weight: unit
short: the series P of the numbers c_n
---
## Description

The formal power series $P = \sum_{n \ge 0} c_n X^n$ with real coefficients, where $c_n = (n+1)^{n-1}/n!$.

## Statement

$P$ is the formal power series over the real numbers whose coefficient of $X^n$ is $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`), for every $n \ge 0$:

$$P = \sum_{n \ge 0} c_n X^n = 1 + X + \tfrac{3}{2} X^2 + \tfrac{8}{3} X^3 + \cdots .$$

## Explanation

Since $n!\,c_n$ is the number of parking functions of length $n$, $P$ is their exponential generating series. It is a formal series: the library uses the ring operations, the formal derivative and the inverse of power series, and no convergence.

The series serves to turn the recursion `Parking.cc_rec` into algebra. With the tree series $T = XP$ (`Parking.TreeSeries.Tser`) the recursion reads $P' = T'P$, which is the derivative form of the classical relation $P = e^{T}$. The constant coefficient of $P$ is $c_0 = 1$, so $P$ has an inverse $E = 1/P$ (`Parking.TreeSeries.Eser`), whose coefficients are $-\varepsilon_m$ with $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.TreeSeries.coeff_Eser_mul`). Dividing by $P$ is the basic operation of the single-chain formula (`Parking.IsWSol.ez`): the series of a count with a displacement bound is compared with $P$ by forming their quotient.

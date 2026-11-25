---
weight: step
short: constant coefficient of E
---
## Description

The constant coefficient of the series $E = 1/P$ is $1$, where $P = \sum_n c_n X^n$ and $c_n = (n+1)^{n-1}/n!$.

## Statement

$[X^0]\,E = 1$, where $E$ is the inverse of $P = \sum_{n \ge 0} c_n X^n$ (`Parking.TreeSeries.Eser`, `Parking.TreeSeries.Pser`).

## Explanation

Together with the coefficients of positive index, which are $-\varepsilon_m$ (see `Parking.TreeSeries.coeff_Eser_mul`), this describes $E$ completely.

## Proof

The constant coefficient of the inverse of a power series is the inverse of its constant coefficient, and the constant coefficient of $P$ is $c_0 = 1$ (`Parking.cc_zero`).

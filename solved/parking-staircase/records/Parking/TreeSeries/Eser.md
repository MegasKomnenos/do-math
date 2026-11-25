---
weight: unit
short: the inverse series E = 1/P
---
## Description

The formal power series $E = 1/P$, the inverse of $P = \sum_{n \ge 0} c_n X^n$ with $c_n = (n+1)^{n-1}/n!$.

## Statement

$E$ is the inverse, in the ring of formal power series over the real numbers, of the series $P = \sum_{n \ge 0} c_n X^n$ (`Parking.TreeSeries.Pser`), where $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`). The inverse exists because the constant coefficient of $P$ is $c_0 = 1$.

## Explanation

The coefficients of $E$ are known explicitly: $E = 1 - \sum_{m \ge 1} \varepsilon_m X^m$ with $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`). This is the content of `Parking.TreeSeries.coeff_Eser_zero` and `Parking.TreeSeries.coeff_Eser_mul`. Classically $P = e^{T}$ with the tree function $T$, so $E = e^{-T}$; the library uses the corresponding differential equation $E' = -E\,T'$ (`Parking.TreeSeries.deriv_Eser`).

Multiplication by $E$ is division by $P$. It is the operation by which the single-chain formula (`Parking.IsWSol.ez`) compares the series of a solution of a weighted last-car recursion with $P$, and it is the reason why the kernel $\varepsilon$ appears in the column equations.

In Lean, `Parking.TreeSeries.Eser` is `Pser⁻¹`, Mathlib's inverse of a power series over a field. That operation is defined for every series and returns the true inverse when the constant coefficient is not zero, which is the case here; `Parking.TreeSeries.Eser_mul_Pser` records $E P = 1$.

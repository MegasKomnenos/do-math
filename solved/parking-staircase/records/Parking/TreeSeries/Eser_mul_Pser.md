---
weight: step
short: E P = 1
---
## Description

The series $E = 1/P$ is the inverse of $P = \sum_n c_n X^n$: $E \cdot P = 1$.

## Statement

$E \cdot P = 1$ in the ring of formal power series over the real numbers, where $P = \sum_{n \ge 0} c_n X^n$ with $c_n = (n+1)^{n-1}/n!$ (`Parking.TreeSeries.Pser`) and $E$ is the series of `Parking.TreeSeries.Eser`.

## Explanation

In Lean $E$ is defined by Mathlib's inverse of a power series over a field, an operation that is defined for every series and is a true inverse exactly when the constant coefficient is not zero. The statement records that this is the case for $P$, so that $E$ may be used as $1/P$.

## Proof

The constant coefficient of $P$ is $c_0 = 1$ (`Parking.TreeSeries.coeff_Pser`, `Parking.cc_zero`), which is not zero. A power series over a field with nonzero constant coefficient, multiplied by its inverse, gives $1$.

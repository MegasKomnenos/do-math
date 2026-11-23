---
weight: step
short: quadratic upper bound for the exponential on [0, 0.6679]
---
## Description

$e^s\le1+s+0.633\,s^2$ for real $s$ with $0\le s\le0.6679$.

## Statement

For every real number $s$ with $0\le s\le\frac{6679}{10000}$, $\ e^s\le1+s+\frac{633}{1000}s^2$.

## Explanation

The coefficient $0.633$ replaces the factor $\frac12+\frac s6+\frac{s^2}{24}+\dots$ of $s^2$ in the exponential series by a constant that bounds it on the interval; at $s=0.6679$ the bound used in the proof gives about $0.6329$. The inequality is used in the closed-form bounds for the crossing criterion (module `Parking.Crossing.Bounds`), where factors $e^{as}$ with a small exponent have to be bounded above by polynomials; the condition $\bar a R\le0.6679$ in `Parking.cross_of_bounds`, with $\bar a=5/(2k)$ (`Parking.abar`), is the range of this bound.

## Proof

For $0\le s\le1$ the exponential series with the standard estimate of its remainder gives
$$e^s\le1+s+\frac{s^2}{2}+\frac{s^3}{6}+\frac{s^4}{24}+\frac{s^5}{100}$$
(Mathlib's `Real.exp_bound'` with five terms, whose remainder term is $s^5\cdot\frac{6}{5!\cdot5}$). For $0\le s\le c=0.6679$ one has $s^{2+j}\le c^{j}s^2$, $j=1,2,3$, so the right-hand side is at most $1+s+\bigl(\frac12+\frac c6+\frac{c^2}{24}+\frac{c^3}{100}\bigr)s^2$, and $\frac12+\frac c6+\frac{c^2}{24}+\frac{c^3}{100}<0.633$, a routine evaluation.

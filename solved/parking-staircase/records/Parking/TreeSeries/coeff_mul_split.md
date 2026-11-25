---
weight: step
short: coefficient of a product, first term split off
---
## Description

The $n$-th coefficient of a product of two formal power series over the real numbers, with the term of index $0$ separated: $[X^n](fg) = f_0\, g_n + \sum_{m=1}^{n} f_m\, g_{n-m}$.

## Statement

For formal power series $f = \sum_j f_j X^j$ and $g = \sum_j g_j X^j$ with real coefficients and every natural number $n$,

$$[X^n](f g) = f_0\, g_n + \sum_{m=1}^{n} f_m\, g_{n-m}.$$

## Explanation

When $f$ has constant coefficient $1$, this displays the coefficient of $fg$ as $g_n$ plus a correction, which is how a renewal equation is read off from a product of series. It is used in this way for $f = 1/P$ in `Parking.TreeSeries.coeff_Eser_mul`, and for the series of a threshold in later parts. It carries no mathematical content of its own.

## Proof

By `Parking.TreeSeries.coeff_mul_range`, $[X^n](fg) = \sum_{j=0}^{n} f_j\, g_{n-j}$; separate the term $j = 0$.

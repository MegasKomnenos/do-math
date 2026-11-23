---
weight: step
short: coefficient of a product of power series
---
## Description

The $n$-th coefficient of a product of two formal power series over the real numbers, as a sum over one index: $[X^n](fg) = \sum_{j=0}^{n} f_j\, g_{n-j}$.

## Statement

For formal power series $f = \sum_j f_j X^j$ and $g = \sum_j g_j X^j$ with real coefficients and every natural number $n$,

$$[X^n](f g) = \sum_{j=0}^{n} f_j\, g_{n-j}.$$

## Explanation

This is the definition of the product of power series. Mathlib states it as a sum over the pairs $(i,j)$ with $i + j = n$; the present form indexes the same sum by $i$ alone, which is the form the coefficient comparisons of the library are written in. It carries no mathematical content of its own.

## Proof

Mathlib's formula for the coefficient of a product is the sum of $f_i g_j$ over the pairs with $i + j = n$. These pairs are $(j, n-j)$ for $0 \le j \le n$.

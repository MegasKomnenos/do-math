---
weight: step
short: the sum of the powers i^(-3/2) is at most 3
---
## Description

$\sum_{i=1}^{n}i^{-3/2}\le3$ for every natural number $n$.

## Statement

For every natural number $n$, $\ \displaystyle\sum_{i=1}^{n}\frac1{i\sqrt i}\le3$.

## Explanation

The partial sums of the convergent series $\sum i^{-3/2}$ are bounded by $1+\int_1^\infty t^{-3/2}\,dt=3$. The library needs only some explicit bound that does not depend on $n$; in the closed-form bounds for the crossing criterion (module `Parking.Crossing.Bounds`) this $3$ stands where the exact constant would be the value $\zeta(3/2)$ of the full series.

In Lean the sum is written over `range n` with the summand $1/((i+1)\sqrt{i+1})$, $0\le i<n$.

## Proof

The stronger statement $\sum_{i=1}^{m}i^{-3/2}\le3-\frac2{\sqrt m}$ holds for every $m\ge1$, by induction: for $m=1$ both sides are $1$, and the step is the left inequality of `Parking.inv_sqrt_diff_bounds` at $y=m$, namely $\frac1{(m+1)\sqrt{m+1}}\le2\bigl(\frac1{\sqrt m}-\frac1{\sqrt{m+1}}\bigr)$. For $n\ge1$ the claim follows since $\frac2{\sqrt n}\ge0$; for $n=0$ the sum is $0$.

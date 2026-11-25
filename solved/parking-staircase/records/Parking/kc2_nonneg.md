---
weight: step
short: the twofold convolution of the Poisson mass is nonnegative
---
## Description

$\kappa_2(m) \ge 0$ for every natural number $m$, where $\kappa_2(m) = \sum_{0<g<m} P(g)\,P(m-g)$ and $P(n) = e^{-n} n^n/n!$.

## Statement

For every natural number $m$, $\kappa_2(m) \ge 0$, where $\kappa_2$ is the twofold convolution of the Poisson mass (`Parking.kc2`).

## Explanation

The statement is used wherever an inequality is multiplied by $\kappa_2$ or a sum with the weights $\kappa_2$ is bounded term by term: in the lower bound of the pair sum (`Parking.pairSum_ge`), in the upper bound of the boundary term (`Parking.impulse_le`), in `Parking.kc3_nonneg`, and in the bounds of the sums of $\kappa_2$ and $\kappa_3$ that the estimates of the curve increase need. For $m \ge 2$ the number $\kappa_2(m)$ is in fact positive; the nonnegative form holds for all $m$ and is all that is used.

## Proof

Each term $P(g)\,P(m-g)$ of the sum is a product of two positive numbers (`Parking.poissonMass_pos`).

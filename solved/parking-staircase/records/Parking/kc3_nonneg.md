---
weight: step
short: the threefold convolution of the Poisson mass is nonnegative
---
## Description

$\kappa_3(m) \ge 0$ for every natural number $m$, where $\kappa_3(m) = \sum_{0<g<m} \kappa_2(g)\,P(m-g)$ is the threefold convolution of the Poisson mass $P(n) = e^{-n} n^n/n!$.

## Statement

For every natural number $m$, $\kappa_3(m) \ge 0$, where $\kappa_3$ is the threefold convolution of the Poisson mass (`Parking.kc3`).

## Explanation

The statement is used where a sum with the weights $\kappa_3$ is bounded term by term, in the lower bound of the pair sum (`Parking.pairSum_ge`) and in the bounds of the sums of $\kappa_3$ that the estimates of the curve increase need.

## Proof

Each term $\kappa_2(g)\,P(m-g)$ of the sum is a product of a nonnegative number (`Parking.kc2_nonneg`) and a positive one (`Parking.poissonMass_pos`).

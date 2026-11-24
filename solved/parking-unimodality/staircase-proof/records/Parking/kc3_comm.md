---
weight: step
short: the threefold convolution of the Poisson mass with the factors exchanged
---
## Description

For every natural number $m$: $\sum_{0<a<m} P(a)\,\kappa_2(m-a) = \kappa_3(m)$, where $P$ is the Poisson mass and $\kappa_2$, $\kappa_3$ are its twofold and threefold convolutions.

## Statement

For every natural number $m$,

$$\sum_{0 < a < m} P(a)\;\kappa_2(m-a) \;=\; \kappa_3(m),$$

where $P(n) = e^{-n} n^n/n!$ (`Parking.poissonMass`), $\kappa_2$ is the twofold convolution of `Parking.kc2`, and $\kappa_3(m) = \sum_{0<g<m} \kappa_2(g)\,P(m-g)$ (`Parking.kc3`).

## Explanation

The definition of $\kappa_3$ puts the factor $\kappa_2$ first and the factor $P$ second. In the lower bound of the pair sum (`Parking.pairSum_ge`) the same convolution arises with the single factor first, and the statement identifies the two.

## Proof

The substitution $a \mapsto m - a$ maps the range $0 < a < m$ onto itself and turns the left side into $\sum_{0<a<m} P(m-a)\,\kappa_2(a)$, which is the definition of $\kappa_3(m)$.

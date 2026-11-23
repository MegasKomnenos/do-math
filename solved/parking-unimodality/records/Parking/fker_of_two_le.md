---
weight: step
short: the frozen kernel beyond its first index
---
## Description

For $i \ge 2$ the frozen kernel is the prime kernel in the Borel scale: $f_i = e^{-i}\varepsilon_i$.

## Statement

For every natural number $i \ge 2$, $f_i = (e^{-1})^i\,\varepsilon_i$, where $f$ is the frozen kernel of `Parking.fker` and $\varepsilon_i = (i-1)^{i-1}/i!$ is the sequence of `Parking.eps`.

## Explanation

The definition of $f$ adds $\frac12e^{-1}$ at the index $1$ only, so for $i \ge 2$ the correction term vanishes. The Lean statement writes the factor as a power of $e^{-1}$ and not as $e^{-i}$; this is the form in which products such as $f_m\,e^{-(\rho-m)}$ are combined in the proofs of `Parking.fker_logconvex` and `Parking.caseFar`.

## Proof

Unfold the definition of `Parking.fker`: the case distinction $i = 1$ fails for $i \ge 2$, and $e^{-i} = (e^{-1})^i$ by `Parking.exp_neg_nat`.

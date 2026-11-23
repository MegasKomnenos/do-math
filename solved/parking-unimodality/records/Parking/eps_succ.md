---
weight: step
short: ε_{m+1} in closed form
---
## Description

The kernel $\varepsilon$ at a positive index, written without a case distinction: $\varepsilon_{m+1} = m^m/(m+1)!$.

## Statement

For every natural number $m$,

$$\varepsilon_{m+1} = \frac{m^m}{(m+1)!},$$

where $\varepsilon$ is the sequence of `Parking.eps` and $0^0 = 1$.

## Explanation

The definition of $\varepsilon_m$ distinguishes $m = 0$ from $m \ge 1$ and has $m - 1$ in the base and in the exponent. Writing a positive index as $m + 1$ removes both, which is the form used in calculations.

## Proof

Unfold the definition at the index $m + 1 \ne 0$; the base is $(m + 1) - 1 = m$ and the exponent is $(m+1) - 1 = m$.

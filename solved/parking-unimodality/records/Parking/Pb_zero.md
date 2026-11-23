---
weight: step
short: birthday tail at index 0
---
## Description

The birthday tail at the index $0$ is $1$: $P_{m,0} = 1$.

## Statement

For every natural number $m$, $P_{m,0} = 1$, where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail of `Parking.Pb`.

## Explanation

The product defining $P_{m,0}$ has no factors. In the reading of `Parking.Pb`, no draws are always pairwise distinct. The value is used where a sum of tails is extended to the index $0$: the proof of `Parking.sbirth_le` writes $\sum_{j=0}^{m} P_{m,j} = s_m + 1$, with $s_m$ from `Parking.sbirth`. The statement includes $m = 0$.

## Proof

The product over the empty range is $1$.

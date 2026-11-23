---
weight: step
short: lower bound 1 for the mean of the birthday law
---
## Description

The mean of the birthday law of $m \ge 1$ is at least $1$: $s_m \ge 1$.

## Statement

For every natural number $m \ge 1$, $s_m \ge 1$, where $s_m = \sum_{j=1}^{m} P_{m,j}$ (`Parking.sbirth`) and $P_{m,j}$ is the birthday tail (`Parking.Pb`).

## Explanation

The number of draws before the first repetition is at least $1$, and so is its mean. The bound is used in the proof of `Parking.Gfun_pos`, where an upper bound for $D_r$ (`Parking.Dbirth`) that is linear in $\sqrt r$ is derived from an upper bound for $s_r$ of the same kind; the bound $s_r \ge 1$ supplies the signs that this derivation needs.

## Proof

The sum defining $s_m$ contains the term with $j = 1$, which is $P_{m,1} = 1$ by `Parking.Pb_one`, and all its terms are nonnegative by `Parking.Pb_nonneg`.

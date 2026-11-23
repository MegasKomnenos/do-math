---
weight: step
short: birthday tail beyond m
---
## Description

The birthday tail of $m \ge 1$ vanishes beyond $m$: $P_{m,j} = 0$ for $j \ge m + 1$.

## Statement

For natural numbers $m \ge 1$ and $j \ge m + 1$, $P_{m,j} = 0$, where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail of `Parking.Pb`.

## Explanation

More than $m$ draws from $m$ values cannot be pairwise distinct. For the birthday law of `Parking.Pb` the statement says that the number $Q$ of draws before the first repetition is at most $m$; for compositions it matches the fact that a composition of $m$ has at most $m$ parts (`Parking.Vc_eq_zero_of_lt`), in accordance with `Parking.Tq_eq`. It is used in `Parking.Pb_nonneg` and, in the proof of `Parking.mu0_le_muh`, to see that the sequence $h^{j} P_{r,j+1}$ vanishes for $j \ge r$. The hypothesis $m \ge 1$ is needed, since $P_{0,j} = 1$ for all $j$ under the convention of `Parking.Pb`.

## Proof

Since $j > m$, the product defining $P_{m,j}$ contains the factor with $i = m$, which is $1 - m/m = 0$ because $m \ne 0$.

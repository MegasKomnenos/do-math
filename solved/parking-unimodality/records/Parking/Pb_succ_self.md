---
weight: step
short: birthday tail at index m + 1
---
## Description

The birthday tail of $m \ge 1$ vanishes at the index $m + 1$: $P_{m,m+1} = 0$.

## Statement

For every natural number $m \ge 1$, $P_{m,m+1} = 0$, where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail of `Parking.Pb`.

## Explanation

Among $m + 1$ draws from $m$ values two must coincide. The statement is the case $j = m+1$ of `Parking.Pb_eq_zero`, kept separately because it is the form in which the vanishing is used: it removes the upper boundary term of the Abel summation in `Parking.Pb_moment`, and it allows the sums over $j \le m$ in the proof of `Parking.tau_succ_le` to be shifted by one index without a remainder. The hypothesis $m \ge 1$ is needed, since $P_{0,j} = 1$ for all $j$ under the convention of `Parking.Pb`.

## Proof

By `Parking.Pb_succ` with $j = m$, $P_{m,m+1} = P_{m,m}\,(1 - m/m)$, and $m/m = 1$ because $m \ne 0$.

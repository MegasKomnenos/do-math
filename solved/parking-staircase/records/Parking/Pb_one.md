---
weight: step
short: birthday tail at index 1
---
## Description

The birthday tail at the index $1$ is $1$: $P_{m,1} = 1$.

## Statement

For every natural number $m$, $P_{m,1} = 1$, where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail of `Parking.Pb`.

## Explanation

A single draw is always distinct from the draws before it, since there are none. In terms of the birthday law of `Parking.Pb` the statement says $\Pr(Q \ge 1) = 1$. It gives the boundary term of the Abel summation in `Parking.Pb_moment`, the first step of the induction in `Parking.Tq_eq`, and, with `Parking.Pb_succ`, the value $P_{m,2} = 1 - 1/m$ in the proof of `Parking.sbirth_lt`. The statement includes $m = 0$.

## Proof

By `Parking.Pb_succ` with $j = 0$, $P_{m,1} = P_{m,0}\,(1 - 0/m) = P_{m,0}$, and $P_{m,0} = 1$ by `Parking.Pb_zero`.

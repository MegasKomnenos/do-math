---
weight: step
short: recursion of the birthday tail
---
## Description

The recursion of the birthday tail: $P_{m,j+1} = P_{m,j}\,(1 - j/m)$.

## Statement

For all natural numbers $m \ge 1$ and $j \ge 0$,

$$P_{m,j+1} \;=\; P_{m,j}\,\Bigl(1 - \frac{j}{m}\Bigr),$$

where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail of `Parking.Pb`. The Lean statement also covers $m = 0$, where both sides are $1$ under the convention $j/0 = 0$ of `Parking.Pb`.

## Explanation

In the reading of `Parking.Pb`: once $j$ draws from $m$ values are pairwise distinct, the next draw avoids them with probability $1 - j/m$. Rearranged, the recursion says $P_{m,j} - P_{m,j+1} = \frac{j}{m} P_{m,j}$, which is the probability that the first repetition occurs exactly at the draw number $j+1$; in this form it is the starting point of `Parking.Pb_moment`. Every inductive argument about the tails uses this recursion: the induction that identifies the weights of compositions in `Parking.Tq_eq`, the log-concavity used in the proof of `Parking.mu0_le_muh`, and the identity $P_{r,j}\,(r-j)!\,r^{j} = r!$ in the proof of `Parking.sbirth_le`.

## Proof

The product over $i = 0, \dots, j$ is the product over $i = 0, \dots, j-1$ times the factor with $i = j$.

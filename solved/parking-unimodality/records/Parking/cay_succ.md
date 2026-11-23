---
weight: step
short: a_{j+1} in closed form
---
## Description

The Cayley coefficient at a positive index, written without a case distinction: $a_{j+1} = (j+1)^j/(j+1)!$.

## Statement

For every natural number $j$,

$$a_{j+1} = \frac{(j+1)^j}{(j+1)!},$$

where $a$ denotes the Cayley coefficients (`Parking.cay`).

## Explanation

The definition of $a_j$ distinguishes $j = 0$ from $j \ge 1$. Writing a positive index as $j + 1$ removes the distinction and the subtraction in the exponent, which is the form in which the formula is convenient for calculation.

## Proof

Unfold the definition at the index $j + 1 \ne 0$; the exponent is $(j+1) - 1 = j$.

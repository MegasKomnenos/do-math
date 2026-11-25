---
weight: step
short: a_j ≥ 0
---
## Description

The Cayley coefficients are nonnegative: $a_j \ge 0$ for every $j \ge 0$.

## Statement

For every natural number $j$, $a_j \ge 0$, where $a_0 = 0$ and $a_j = j^{j-1}/j!$ for $j \ge 1$ (`Parking.cay`).

## Explanation

The form of `Parking.cay_pos` that needs no hypothesis on the index.

## Proof

If $j = 0$, then $a_0 = 0$. If $j \ge 1$, then $a_j > 0$ by `Parking.cay_pos`.

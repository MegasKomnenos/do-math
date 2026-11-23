---
weight: step
short: a_j > 0 for j ≥ 1
---
## Description

The Cayley coefficient $a_j = j^{j-1}/j!$ is positive for every $j \ge 1$.

## Statement

For every natural number $j \ge 1$, $a_j > 0$, where $a$ denotes the Cayley coefficients (`Parking.cay`).

## Explanation

The hypothesis $j \ge 1$ is needed because $a_0 = 0$ by convention.

## Proof

Write $j = i + 1$. By `Parking.cay_succ`, $a_{i+1} = (i+1)^i/(i+1)!$, a quotient of two positive numbers.

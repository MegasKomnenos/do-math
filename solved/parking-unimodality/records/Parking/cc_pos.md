---
weight: step
short: c_n > 0
---
## Description

The normalised parking numbers $c_n = (n+1)^{n-1}/n!$ are positive for every $n \ge 0$.

## Statement

For every natural number $n$, $c_n > 0$, where $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`).

## Explanation

Positivity is used wherever a quantity is divided by $c_n$, for instance in ratios such as $z^{(y)}_n/c_n$, and wherever an inequality is multiplied by $c_n$.

## Proof

By definition $c_n = a_{n+1}$ with $a$ the Cayley coefficients (`Parking.cay`), and `Parking.cay_pos` gives $a_j > 0$ for $j \ge 1$.

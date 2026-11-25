---
weight: step
short: c_n unfolded
---
## Description

The normalised parking number in the form that its definition unfolds to: $c_n = (n+1)^n/(n+1)!$.

## Statement

For every natural number $n$,

$$c_n = \frac{(n+1)^n}{(n+1)!},$$

where $c_n = a_{n+1}$ (`Parking.cc`) and $a$ denotes the Cayley coefficients (`Parking.cay`).

## Explanation

The right-hand side equals the usual form $(n+1)^{n-1}/n!$ after cancelling a factor $n + 1$. The form stated here has a natural-number exponent for every $n$, including $n = 0$, and is the one calculations in the library start from.

## Proof

By definition $c_n = a_{n+1}$, and `Parking.cay_succ` gives $a_{n+1} = (n+1)^n/(n+1)!$.

---
weight: step
short: c_k = w_k(1)/k!
---
## Description

The normalised parking number $c_k = (k+1)^{k-1}/k!$ is the Abel weight at $x = 1$ divided by $k!$: $c_k = w_k(1)/k!$.

## Statement

For every natural number $k$,

$$c_k = \frac{w_k(1)}{k!},$$

where $c_k = (k+1)^{k-1}/k!$ (`Parking.cc`) and $w_0(x) = 1$, $w_k(x) = x\,(x+k)^{k-1}$ for $k \ge 1$ (`Parking.abelW`).

## Explanation

This is what makes Abel's identity (`Parking.abel_identity`) a statement about the numbers $c_k$: at $x = 1$ its weights are $k!\,c_k$. It is used in the proof of `Parking.cc_rec`, and in the module of the resolvent kernel as the case of exponent $1$ of the formula for the coefficients of the powers of $\sum_n c_n X^n$.

## Proof

For $k = 0$ both sides are $1$ (`Parking.cc_zero`). For $k = i + 1$, `Parking.cc_eq` gives $c_{i+1} = (i+2)^{i+1}/(i+2)!$, and $w_{i+1}(1) = (i+2)^i$. Since $(i+2)! = (i+2)\,(i+1)!$, the two sides agree.

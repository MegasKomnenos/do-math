---
weight: unit
short: Abel weights w_k(x)
---
## Description

The weights of Abel's binomial identity: $w_0(x) = 1$ and $w_k(x) = x\,(x+k)^{k-1}$ for $k \ge 1$, for a real number $x$.

## Statement

For a real number $x$ and a natural number $k$,

$$w_k(x) = \begin{cases} 1, & k = 0, \\ x\,(x+k)^{k-1}, & k \ge 1. \end{cases}$$

## Explanation

These are the polynomials in $x$ that take the place of the powers $x^k$ in Abel's generalisation of the binomial theorem, `Parking.abel_identity`: $\sum_k \binom{n}{k} w_k(x)\,(y-k)^{n-k} = (x+y)^n$. Classically they are known as Abel polynomials.

Their connection with parking functions is that $w_k(1)/k! = (k+1)^{k-1}/k! = c_k$, the normalised number of parking functions of length $k$ (`Parking.cc_eq_abelW`). More generally, for a natural number $a$ the coefficient of $X^n$ in the power $P^{a+1}$ of the series $P = \sum_n c_n X^n$ (`Parking.TreeSeries.Pser`) is $w_n(a+1)/n!$; this is derived from `Parking.abel_identity` in the module of the resolvent kernel (`Parking.Hres`), which is the second place where the weights are used. Having the weight as a definition of its own lets both places speak of the same object.

The case $k = 0$ is separate because the expression $x\,(x+0)^{-1}$ is not defined at $x = 0$; with the definition by cases, $w_0(x) = 1$ for every $x$. In Lean, `Parking.abelW x k` takes a real $x$ and a natural $k$, and the exponent `k - 1` is a subtraction of natural numbers that is exact for $k \ge 1$.

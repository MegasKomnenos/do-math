---
weight: step
short: nonnegativity of the environment
---
## Description

The normalised cumulative counts are nonnegative: $z^{(y)}_n=A(n,y-1)/n!\ge0$.

## Statement

For all natural numbers $y$ and $n$, $0\le z^{(y)}_n$, where $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`; for $y=0$ the Lean definition gives $z^{(0)}_n=z^{(1)}_n$).

## Explanation

A count divided by a factorial. It is used wherever an inequality is multiplied by a value of $z^{(y)}$ or a sum with such values as coefficients is estimated term by term.

## Proof

$z^{(y)}_n$ is the quotient of the natural number $A(n,y-1)$ by the positive number $n!$.

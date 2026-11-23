---
weight: step
short: monotonicity of A in the bound
---
## Description

$A(n,k)$, the number of parking functions of length $n$ with maximum displacement at most $k$, is nondecreasing in $k$.

## Statement

For all natural numbers $n$ and $k\le k'$, $A(n,k)\le A(n,k')$ (`Parking.A`).

## Explanation

A parking function whose maximum displacement is at most $k$ also has maximum displacement at most $k'$. After division by $n!$ this is the monotonicity of $z^{(y)}_n$ in the threshold $y$ (`Parking.zr_mono`); it is also used for the column $k=1$ (`Parking.column_one`) and in the table of two signs.

## Proof

The set of functions $\alpha$ counted by $A(n,k)$, those for which the maximum displacement exists and equals some $m\le k$, is contained in the set counted by $A(n,k')$, because $m\le k\le k'$. A subset of a finite set has at most as many elements.

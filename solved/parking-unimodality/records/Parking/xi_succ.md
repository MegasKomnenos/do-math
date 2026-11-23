---
weight: step
short: the tree curvature at a positive index
---
## Description

The defining formula of the tree curvature at the index $t+1$: $(t+1)\,\xi_{t+1}=\min(t+1,k+1)\,z^{(k+1)}_t-2\min(t+1,k)\,z^{(k)}_t+\min(t+1,k-1)\,z^{(k-1)}_t$.

## Statement

For all natural numbers $k$ and $t$,
$$\xi_{t+1}=\frac{\min(t+1,k+1)\,z^{(k+1)}_{t}-2\,\min(t+1,k)\,z^{(k)}_{t}+\min(t+1,k-1)\,z^{(k-1)}_{t}}{t+1},$$
where $\xi=\xi^{(k)}$ is the tree curvature of the column $k$ (`Parking.xi`) and $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`). The statement holds for every $k$ with the conventions of the Lean definitions ($k-1$ is the truncated difference); it is used for $k\ge2$.

## Explanation

This is the definition `Parking.xi` with the case $t=0$ removed and the index shifted, so that no subtraction $t-1$ of natural numbers appears. Proofs that work with $\xi$ at a positive index start from this form.

## Proof

Unfold the definition `Parking.xi` at $t+1$: the case $t+1=0$ does not occur, and $(t+1)-1=t$.

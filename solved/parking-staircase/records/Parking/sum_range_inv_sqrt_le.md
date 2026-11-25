---
weight: step
short: upper bound for the sum of inverse square roots
---
## Description

$\sum_{i=1}^{n}1/\sqrt i\le2\sqrt n-1$ for every integer $n\ge1$.

## Statement

For every natural number $n\ge1$, $\ \displaystyle\sum_{i=1}^{n}\frac1{\sqrt i}\le2\sqrt n-1$.

## Explanation

The comparison of the sum with $1+\int_1^n t^{-1/2}\,dt=2\sqrt n-1$; equality holds for $n=1$. Sums of this kind arise when the numbers $e^{-i}i^i/i!$ are replaced by their Stirling bounds $c_0/\sqrt i$, where $c_0=1/\sqrt{2\pi}$ (`Parking.c0`, `Parking.poissonMass_le_c0`): in the bound for the growth of the normalised kernel deficit on a diagonal step (`Parking.kap_diag_le`) and in the estimate of the sum of tilted Cayley numbers at the critical tilt (`Parking.cayleySum_le_one`).

In Lean the sum is written over `range n` with the summand $1/\sqrt{i+1}$, $0\le i<n$.

## Proof

By induction on $n\ge1$. For $n=1$ both sides are $1$. For the step it suffices that $\frac1{\sqrt{n+1}}\le2\bigl(\sqrt{n+1}-\sqrt n\bigr)$. With $p=\sqrt n$ and $q=\sqrt{n+1}>0$, so that $q^2=p^2+1$, this is $1\le2q(q-p)$, and $2q(q-p)=q^2+p^2+1-2pq=(q-p)^2+1\ge1$.

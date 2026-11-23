---
weight: step
short: lower bound for the sum of inverse square roots
---
## Description

$2\sqrt{n+1}-2\le\sum_{i=1}^{n}1/\sqrt i$ for every natural number $n$.

## Statement

For every natural number $n$ (including $n=0$, where the sum is empty), $\ \displaystyle2\sqrt{n+1}-2\le\sum_{i=1}^{n}\frac1{\sqrt i}$.

## Explanation

The comparison of the sum with $\int_1^{n+1}t^{-1/2}\,dt=2\sqrt{n+1}-2$, which lies below the sum because $t^{-1/2}$ decreases. It is the lower counterpart of `Parking.sum_range_inv_sqrt_le` and is used in the closed-form bounds for the crossing criterion (module `Parking.Crossing.Bounds`), where a sum of the Stirling lower bounds $c_0(1-\frac1{12i})/\sqrt i$ for the numbers $e^{-i}i^i/i!$, with $c_0=1/\sqrt{2\pi}$ (`Parking.c0`, `Parking.poissonMass_ge_c0`), has to be bounded from below.

In Lean the sum is written over `range n` with the summand $1/\sqrt{i+1}$, $0\le i<n$.

## Proof

By induction on $n$. For $n=0$ both sides are $0$. For the step it suffices that $2\bigl(\sqrt{n+2}-\sqrt{n+1}\bigr)\le\frac1{\sqrt{n+1}}$. With $p=\sqrt{n+1}>0$ and $q=\sqrt{n+2}$, so that $q^2=p^2+1$, this is $2p(q-p)\le1$, and $2p(q-p)=2pq-p^2-q^2+1=1-(q-p)^2\le1$.

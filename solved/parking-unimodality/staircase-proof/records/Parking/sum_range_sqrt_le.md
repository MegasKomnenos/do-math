---
weight: step
short: upper bound for the sum of square roots
---
## Description

$\sum_{i=0}^{R-1}\sqrt i\le\frac23R\sqrt R$ for every natural number $R$.

## Statement

For every natural number $R$, $\ \displaystyle\sum_{i=0}^{R-1}\sqrt i\le\frac23\,R\sqrt R$.

## Explanation

The comparison of the sum with $\int_0^R\sqrt t\,dt=\frac23R^{3/2}$, which lies above the sum because $\sqrt t$ increases. It is used, without its first terms, in the estimate of the sum of tilted Cayley numbers at the critical tilt (`Parking.cayleySum_le_one`).

## Proof

By induction on $R$. For $R=0$ both sides are $0$. For the step it suffices that $\sqrt n\le\frac23\bigl((n+1)\sqrt{n+1}-n\sqrt n\bigr)$. With $p=\sqrt n\ge0$ and $q=\sqrt{n+1}\ge p$, so that $q^2=p^2+1$, this is $3p\le2(q^3-p^3)$, and
$$2(q^3-p^3)-3p=(q-p)^2(2q+p)+3p\,(q^2-p^2-1)=(q-p)^2(2q+p)\ \ge0.$$

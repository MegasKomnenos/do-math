---
weight: step
short: upper bound for the sum of the powers i^(3/2)
---
## Description

$\sum_{i=0}^{R-1}i\sqrt i\le\frac25R^2\sqrt R$ for every natural number $R$.

## Statement

For every natural number $R$, $\ \displaystyle\sum_{i=0}^{R-1}i\sqrt i\le\frac25\,R^2\sqrt R$.

## Explanation

The comparison of the sum with $\int_0^Rt^{3/2}\,dt=\frac25R^{5/2}$, which lies above the sum because $t^{3/2}$ increases. It is used in the closed-form bounds for the crossing criterion (module `Parking.Crossing.Bounds`), in the bound for the sum $S_R=\sum_{i<R}(ix)^i/i!$ of the crossing criterion (`Parking.SR`), in which $x=1/\gamma_k$ is the diagonal tilt of the column $k$ (`Parking.xk`). Writing $x=e^{a-1}$, each term is $e^{-i}i^i/i!$ times $e^{ai}$; the first factor is at most $c_0/\sqrt i$ with $c_0=1/\sqrt{2\pi}$ (`Parking.poissonMass_le_c0`), the second is at most $1+ai+0.633(ai)^2$ (`Parking.exp_le_quad`), and the product leads to the sums of $i^{-1/2}$, $i^{1/2}$ and $i^{3/2}$.

## Proof

By induction on $R$. For $R=0$ both sides are $0$. For the step it suffices that $n\sqrt n\le\frac25\bigl((n+1)^2\sqrt{n+1}-n^2\sqrt n\bigr)$. With $p=\sqrt n\ge0$ and $q=\sqrt{n+1}\ge p$, so that $q^2=p^2+1$, this is $5p^3\le2(q^5-p^5)$, and
$$2(q^5-p^5)-5p^3=(q-p)^2\bigl(2q^3+4pq^2+6p^2q+3p^3\bigr)+5p^3\,(q^2-p^2-1)=(q-p)^2\bigl(2q^3+4pq^2+6p^2q+3p^3\bigr)\ \ge0,$$
an identity that is checked by expanding.

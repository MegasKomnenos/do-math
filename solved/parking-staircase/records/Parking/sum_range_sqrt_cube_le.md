---
weight: step
short: upper bound for the sum of the powers i^(3/2)
---
## Description

$\sum_{i=0}^{R-1}i\sqrt i\le\frac25R^2\sqrt R$ for every natural number $R$.

## Statement

For every natural number $R$, $\ \displaystyle\sum_{i=0}^{R-1}i\sqrt i\le\frac25\,R^2\sqrt R$.

## Explanation

The comparison of the sum with $\int_0^Rt^{3/2}\,dt=\frac25R^{5/2}$, which lies above the sum because $t^{3/2}$ increases. It is used through the bounds `Parking.sum_Ioo_sqrt_cube_le` and `Parking.sum_Ioo_sqrt_cube_mul_le` for the sums $\sum_{0<c<R}c\sqrt c$ and $\sum_{0<c<R}c\sqrt c\,(R-c)$, which estimate the correction terms of the sums $G$ and $\mathcal A$ in the lower bound of the pair sum (`Parking.Gsum`, `Parking.Asum`, `Parking.pairSum_ge`). In those terms the threefold convolution $\kappa_3$ of the Poisson mass (`Parking.kc3`) satisfies $\kappa_3(c)\le c_0\sqrt c$ with $c_0=1/\sqrt{2\pi}$ (`Parking.c0`), and it is multiplied by a correction $\varrho_c$ (`Parking.rhoC`), which on the curve $k^2\approx R^3$ is at most a constant times $c/R^{3/2}$; the product leads to the sums of $c^{3/2}$.

## Proof

By induction on $R$. For $R=0$ both sides are $0$. For the step it suffices that $n\sqrt n\le\frac25\bigl((n+1)^2\sqrt{n+1}-n^2\sqrt n\bigr)$. With $p=\sqrt n\ge0$ and $q=\sqrt{n+1}\ge p$, so that $q^2=p^2+1$, this is $5p^3\le2(q^5-p^5)$, and
$$2(q^5-p^5)-5p^3=(q-p)^2\bigl(2q^3+4pq^2+6p^2q+3p^3\bigr)+5p^3\,(q^2-p^2-1)=(q-p)^2\bigl(2q^3+4pq^2+6p^2q+3p^3\bigr)\ \ge0,$$
an identity that is checked by expanding.

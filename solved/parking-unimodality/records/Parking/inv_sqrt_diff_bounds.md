---
weight: step
short: increments of the inverse square root
---
## Description

For $y>0$: $(y+1)^{-3/2}\le2\bigl(y^{-1/2}-(y+1)^{-1/2}\bigr)\le y^{-3/2}$.

## Statement

For every real number $y>0$,
$$\frac{1}{(y+1)\sqrt{y+1}}\ \le\ 2\Bigl(\frac1{\sqrt y}-\frac1{\sqrt{y+1}}\Bigr)\ \le\ \frac1{y\sqrt y}.$$

## Explanation

The middle term is $\int_y^{y+1}t^{-3/2}\,dt$, and the two inequalities say that this integral lies between the values of the decreasing function $t^{-3/2}$ at the two ends of the interval. The library does not use integrals here. It proves this and the neighbouring comparisons of sums with integrals (`Parking.sum_range_inv_sqrt_le`, `Parking.sum_range_inv_sqrt_ge`, `Parking.sum_range_sqrt_le`, `Parking.sum_range_sqrt_cube_le`, `Parking.sum_range_inv_sqrt_cube_le`) by one device: with $p=\sqrt y$ and $q=\sqrt{y+1}$ one has $0\le p\le q$ and $q^2=p^2+1$, and each comparison becomes a polynomial inequality in $p$ and $q$ that follows from an identity with a square $(q-p)^2$.

The first inequality, summed, gives $\sum_{i=1}^{n}i^{-3/2}\le3$ (`Parking.sum_range_inv_sqrt_cube_le`). The second, summed, gives the lower bound for sums of $j^{-3/2}$ over a range that the far rows of the persistence argument use (`Parking.tail_sqrt`). The closed-form bounds of the crossing criterion (module `Parking.Crossing.Bounds`) use both.

## Proof

Let $p=\sqrt y>0$ and $q=\sqrt{y+1}$, so that $p\le q$, $p^2=y$, $q^2=y+1=p^2+1$. The claim is $\frac1{q^3}\le2\bigl(\frac1p-\frac1q\bigr)\le\frac1{p^3}$.

*Left inequality.* $2\bigl(\frac1p-\frac1q\bigr)-\frac1{q^3}=\dfrac{2(q-p)q^2-p}{pq^3}$, and
$$2(q-p)q^2-p=(q-p)^2(2q+p)+p\,(q^2-p^2-1)=(q-p)^2(2q+p)\ \ge0.$$

*Right inequality.* $\frac1{p^3}-2\bigl(\frac1p-\frac1q\bigr)=\dfrac{q-2(q-p)p^2}{p^3q}$, and
$$q-2(q-p)p^2=(q-p)^2(q+2p)-q\,(q^2-p^2-1)=(q-p)^2(q+2p)\ \ge0.$$

Both polynomial identities are checked by expanding.

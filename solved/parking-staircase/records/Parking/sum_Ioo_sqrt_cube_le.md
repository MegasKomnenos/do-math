---
weight: step
short: upper bound for the sum of c^(3/2) over 0 < c < R
---
## Description

$\sum_{0<c<R}c\sqrt c\le\frac25R^2\sqrt R$ for every natural number $R$.

## Statement

For every natural number $R$,
$$\sum_{0<c<R}c\sqrt c\ \le\ \frac25\,R^{2}\sqrt R ,$$
where the sum runs over the natural numbers $c$ with $0<c<R$.

## Explanation

The function $x^{3/2}$ increases, so its value at the left end of an interval is at most its mean over the interval, and $\sum_{c<R}c^{3/2}\le\int_0^Rx^{3/2}\,dx=\frac25R^{5/2}$. This is `Parking.sum_range_sqrt_cube_le`; the present statement is the same inequality for the sum without its term $c=0$, which is zero. It is stated separately because the sum occurs in this form.

It is used for the correction term of the sum $G$ of the lower bound of the pair sum (`Parking.Gsum`, `Parking.pairSum_ge`). That term is $\sum_{0<c<R}\kappa_3(c)\,\varrho_c$, with the threefold convolution $\kappa_3$ of the Poisson mass (`Parking.kc3`) and the correction $\varrho_c$ of `Parking.rhoC`. One has $\kappa_3(c)\le c_0\sqrt c$ for $c\ge1$, with $c_0=1/\sqrt{2\pi}$ (by the closed form `Parking.kc3_eq` and Stirling's bound of the Poisson mass), and on the curve $k^2\approx R^3$ one has $\varrho_c\le\mathrm{const}\cdot c/R^{3/2}$. So the term is at most a constant times $R^{-3/2}\sum_{0<c<R}c^{3/2}$, which the present bound turns into a multiple of $R$. Since the whole term is a correction, the bound by the integral without a second-order term suffices here.

In Lean the summand is `c * Real.sqrt c`, the sum runs over `Finset.Ioo 0 R`, and $R^{5/2}$ is written `R ^ 2 * Real.sqrt R`.

## Proof

The set of natural numbers $c$ with $0<c<R$ is contained in the set of those with $c<R$, and the terms $c\sqrt c$ are nonnegative, so the sum is at most $\sum_{c=0}^{R-1}c\sqrt c$. By `Parking.sum_range_sqrt_cube_le` this is at most $\frac25R^2\sqrt R$.

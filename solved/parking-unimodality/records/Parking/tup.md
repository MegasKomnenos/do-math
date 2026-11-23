---
weight: step
short: upper bound for the kernel deficit
---
## Description

The closed form $\bar t(k,R)=2e^{-1}c_0/\sqrt{R-1}-e^{-1}\underline a\,[2+c_0(2\sqrt R-\tfrac94)]$, an upper bound for the kernel deficit $\bar\kappa_R$ of the column $k$.

## Statement

For natural numbers $k$ and $R$,
$$\bar t=\bar t(k,R)=\frac{2e^{-1}c_0}{\sqrt{R-1}}-e^{-1}\,\underline a\,\Bigl[2+c_0\Bigl(2\sqrt R-2-\frac14\Bigr)\Bigr],$$
where $c_0=1/\sqrt{2\pi}$ (`Parking.c0`) and $\underline a=\frac{5}{2k}-\frac{4}{3k^2}$ (`Parking.alow`).

## Explanation

For $k\ge2$ and $R\ge2$ one has $\bar\kappa_R\le\bar t$, where $\bar\kappa_R$ is the kernel deficit `Parking.kbar` at the diagonal tilt of the column $k$; this is the upper half of part (v) of the proof of `Parking.cross_of_bounds`. The upper bound is needed because the deficit occurs in the factor $\bar\kappa_R+x(R+1)/N$ on the smaller side of the crossing criterion `Parking.cross_criterion`.

The two terms follow the decomposition of the deficit in the record of `Parking.kbar`. The first is an upper bound for the tail $\sum_{m>R}e^{-m}\varepsilon_m$, from the upper Stirling bound (`Parking.poissonMass_le_c0`). The second is a lower bound for the excess of mass at the diagonal tilt $x=e^{\alpha-1}$, to first order in $\alpha\ge\underline a$: the excess is at least $e^{-1}\alpha\,(1+\sum_{i<R}p_i)$ with $p_i=e^{-i}i^i/i!$, and $\sum_{i<R}p_i\ge1+c_0(2\sqrt R-2-\frac14)$. The summand $-\frac14$ is $-\frac1{12}\cdot3$: the lower Stirling bound has the correction $1-\frac1{12i}$, and $\sum_{i\ge1}i^{-3/2}$ is bounded by $3$ (`Parking.sum_range_inv_sqrt_cube_le`). The sharp value of that sum is $\zeta(3/2)\approx2.612$; the library uses the bound $3$, which is enough.

In the crossing criterion the deficit is small compared with the other summand of its factor (numerically, for $k=265$ and $R=70$: $\bar t\approx0.0084$ against $x(R+1)/N\approx0.079$, where $N=k+R$), so the upper bound needs less precision than the lower bound `Parking.tlow`.

In Lean, `tup k R` is written with `Real.exp (-1)`, `Real.sqrt ((R : ℝ) - 1)` and `Real.sqrt R`; for $R\le1$ the first term is $0$ by the convention for division by zero. The closed form is used for $R\ge2$.

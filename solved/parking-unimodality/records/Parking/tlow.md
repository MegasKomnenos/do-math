---
weight: step
short: lower bound for the kernel deficit
---
## Description

The closed form $\underline t(k,R)$, a lower bound for the kernel deficit $\bar\kappa_R$ of the column $k$: a tail term $2e^{-1}c_0(1-\frac{1}{12R})/\sqrt{R+1}$ minus two terms of first and second order in $\bar a=5/(2k)$.

## Statement

For natural numbers $k$ and $R$,
$$\underline t=\underline t(k,R)=\frac{2e^{-1}c_0\bigl(1-\frac{1}{12R}\bigr)}{\sqrt{R+1}}-e^{-1}\,\bar a\,\Bigl[e^{\bar a}+1+c_0\bigl(2\sqrt{R-1}-1\bigr)\Bigr]-e^{-1}\,q\,\bar a^{2}\,\Bigl[1+c_0\Bigl(\frac23R\sqrt R+2\sqrt{R-1}-1\Bigr)\Bigr],$$
where $c_0=1/\sqrt{2\pi}$ (`Parking.c0`), $\bar a=5/(2k)$ (`Parking.abar`) and $q=633/1000$.

## Explanation

For $k\ge2$, $R\ge2$ and $\bar aR\le0.6679$ one has $\underline t\le\bar\kappa_R$, where $\bar\kappa_R=1-x-\sum_{m\le R}\kappa_m$ is the kernel deficit `Parking.kbar` at the diagonal tilt $x$ of the column $k$; this is the lower half of part (v) of the proof of `Parking.cross_of_bounds`. In that theorem the hypothesis $\underline t\ge0$ replaces the hypothesis $\bar\kappa_R\ge0$ of the crossing criterion.

The three terms follow the decomposition of the deficit given in the record of `Parking.kbar`: with $x=e^{\alpha-1}$, the deficit is the tail $\sum_{m>R}e^{-m}\varepsilon_m$ of the kernel at the tilt $e^{-1}$, minus the excess of mass that the larger tilt produces. The first term of $\underline t$ is a lower bound for the tail; it rests on the lower Stirling bound with its correction factor $1-\frac1{12R}$ (`Parking.poissonMass_ge_c0`) and on the exact value of the total mass (`Parking.hasSum_eps`). The second and third terms are upper bounds for the excess, of first and second order in $\alpha\le\bar a$; the number $q$ and the threshold $0.6679$ are those of $e^s\le1+s+0.633\,s^2$ (`Parking.exp_le_quad`).

The lower bound is the delicate one among the closed forms. The tail term is of order $R^{-1/2}$ and the first-order excess of order $\sqrt R/k$, so for $R$ of order $k^{2/3}$ the tail term is of order $k^{-1/3}$ and the first-order excess of order $k^{-2/3}$; their ratio is of order $k^{-1/3}$ and tends to $0$ as $k$ grows. At the smallest columns, however, the two nearly cancel: for $k=265$, $R=70$ the three terms are about $0.03479$, $0.02859$ and $0.00338$, leaving $\underline t\approx0.0028$, while the deficit itself is $\bar\kappa_R\approx0.0043$ (floating-point evaluation of the definitions, not part of any proof). This is why, for the columns just above $265$, the constants of the two Stirling bounds have to be the sharp ones.

In Lean, `tlow k R` is written with `Real.exp (-1)`, `Real.sqrt ((R : ℝ) + 1)`, `Real.sqrt ((R : ℝ) - 1)` and `(R : ℝ) * Real.sqrt R`; division by zero and the square root of a negative number give $0$ in Lean, which only concerns $R=0$. The closed form is used for $R\ge2$.

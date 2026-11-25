---
weight: step
short: E' = -E T'
---
## Description

The series $E = 1/P$ satisfies the differential equation $E' = -E\,T'$, where $P = \sum_n c_n X^n$, $c_n = (n+1)^{n-1}/n!$, and $T = XP$ is the tree series.

## Statement

In the ring of formal power series over the real numbers, with the formal derivative,

$$E' = -E \cdot T',$$

where $E = 1/P$ (`Parking.TreeSeries.Eser`), $P = \sum_{n \ge 0} c_n X^n$ (`Parking.TreeSeries.Pser`) and $T = XP$ (`Parking.TreeSeries.Tser`).

## Explanation

The recursion `Parking.cc_rec` of the numbers $c_n$ is the differential equation $P' = T'P$, and the present statement is the same equation for the inverse series. Both are derivative forms of the classical relations $P = e^{T}$ and $E = e^{-T}$; this part of the library works with the differential equations and does not form the exponential of a series.

The statement is used in two ways. In the proof of `Parking.TreeSeries.coeff_Eser_mul` it yields the coefficients of $E$. In the single-chain formula (`Parking.IsWSol.ez`) it is combined with the equation $W' = G'W$ of a weighted last-car recursion (`Parking.SingleChain.deriv_mk`): the quotient $V = EW$ then satisfies $V' = -(T - G)'\,V$.

## Proof

First, $P' = T'P$. The coefficient of $X^n$ in $P'$ is $(n+1)\,c_{n+1}$. The coefficient of $X^j$ in $T'$ is $(j+1)\,a_{j+1} = (j+1)\,c_j$, where $a$ denotes the Cayley coefficients (`Parking.TreeSeries.coeff_Tser`, and $c_j = a_{j+1}$ by the definition `Parking.cc`), so by `Parking.TreeSeries.coeff_mul_range` the coefficient of $X^n$ in $T'P$ is $\sum_{j=0}^{n} (j+1)\,c_j\,c_{n-j}$. The two agree by `Parking.cc_rec`.

Second, the derivative of the inverse of a power series is $E' = -E^2 P'$. Substituting $P' = T'P$ and using $EP = 1$ (`Parking.TreeSeries.Eser_mul_Pser`),

$$E' = -E^2\, T' P = -E\,T'\,(E P) = -E\,T'.$$

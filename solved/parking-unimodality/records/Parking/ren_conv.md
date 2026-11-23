---
weight: step
short: renewal equation of n^n/n!
---
## Description

The numbers $\operatorname{ren}(n) = n^n/n!$ satisfy the renewal equation $\operatorname{ren}(n) = \sum_{j=1}^{n} a_j \operatorname{ren}(n-j)$ for $n \ge 1$, with the Cayley coefficients $a_j = j^{j-1}/j!$ as kernel.

## Statement

For every natural number $n \ge 1$,

$$\sum_{j=0}^{n} a_j \operatorname{ren}(n-j) = \operatorname{ren}(n),$$

where $a_0 = 0$ and $a_j = j^{j-1}/j!$ for $j \ge 1$ (`Parking.cay`), and $\operatorname{ren}(n) = n^n/n!$ with $\operatorname{ren}(0) = 1$ (`Parking.ren`). The term $j = 0$ is zero.

## Explanation

With $\operatorname{ren}(0) = 1$, the equation says that $\operatorname{ren}$ is the renewal sequence of the kernel $a$. In terms of the tree series $T = \sum_{j \ge 1} a_j X^j$ it is the coefficient form of $(1 - T)(1 + XT') = 1$, the series $1 + XT'$ having the coefficients $\operatorname{ren}(n)$; so $\sum_n \operatorname{ren}(n) X^n = 1/(1 - T)$. Multiplied by $n!$ it reads $n^n = \sum_{j=1}^{n} \binom{n}{j} j^{j-1} (n-j)^{n-j}$, a classical identity of the family of Abel's binomial identity; the library derives it from the series identity, as the proof below shows.

Its one use is in `Parking.hasSum_borel`: multiplied by $e^{-n}$, it is the renewal equation that connects the Borel weights $e^{-j} a_j$ with the Poisson masses $e^{-n} n^n/n!$ (`Parking.poissonMass`).

The hypothesis $n \ge 1$ is needed: for $n = 0$ the left-hand side is $a_0 \operatorname{ren}(0) = 0$ while $\operatorname{ren}(0) = 1$.

## Proof

Let $P = \sum_n c_n X^n$ with $c_n = a_{n+1}$ (`Parking.TreeSeries.Pser`) and $T = XP$ (`Parking.TreeSeries.Tser`), so that $[X^j]\,T = a_j$ (`Parking.TreeSeries.coeff_Tser`).

*The identity $(1 - T)(1 + XT') = 1$.* Two relations are available: $P' = T'P$, which is the recursion `Parking.cc_rec` read coefficient by coefficient (the argument is in the proof of `Parking.TreeSeries.deriv_Eser`), and $T' = P + XP'$, the product rule for $T = XP$. Expanding,

$$(1 - T)(1 + XT') = 1 + XT' - T - X\,T\,T'.$$

Here $T = XP$ and $X\,T\,T' = X^2\,P\,T' = X^2 P'$, so the right-hand side is $1 + X\,(T' - P - XP') = 1$.

*The coefficients of $1 + XT'$.* The coefficient of $X^0$ is $1 = \operatorname{ren}(0)$. For $n \ge 1$ the coefficient of $X^n$ is the coefficient of $X^{n-1}$ in $T'$, namely $n\,a_n = n^n/n! = \operatorname{ren}(n)$.

*Conclusion.* Let $n \ge 1$. The coefficient of $X^n$ in $(1 - T)(1 + XT') = (1 + XT') - T\,(1 + XT')$ is, by `Parking.TreeSeries.coeff_mul_range`, $\operatorname{ren}(n) - \sum_{j=0}^{n} a_j \operatorname{ren}(n-j)$, and it equals the coefficient of $X^n$ in $1$, which is $0$.

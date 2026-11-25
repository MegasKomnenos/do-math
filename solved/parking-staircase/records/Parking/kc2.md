---
weight: unit
short: twofold convolution of the Poisson mass
---
## Description

$\kappa_2(m) = \sum_{0<g<m} P(g)\,P(m-g)$, where $P(n) = e^{-n} n^n/n!$ is the Poisson mass: the convolution of the Poisson mass with itself over the splittings of $m$ into two positive parts.

## Statement

For a natural number $m$,

$$\kappa_2(m) \;=\; \sum_{0 < g < m} P(g)\; P(m-g),$$

where $P(n) = e^{-n} n^n/n!$ is the mass at $n$ of the Poisson law of mean $n$ (`Parking.poissonMass`). The sum is empty for $m \le 1$, so $\kappa_2(0) = \kappa_2(1) = 0$.

## Explanation

**What it is.** The sum runs over the proper splittings $m = g + (m-g)$ with both parts positive; the terms $g = 0$ and $g = m$ of the full convolution, each equal to $P(m)$ because $P(0) = 1$, are left out. Since $P(g)\,P(m-g) = e^{-m}\,\operatorname{ren}(g)\operatorname{ren}(m-g)$ with $\operatorname{ren}(n) = n^n/n!$ (`Parking.poissonMass_mul`), and since $\operatorname{ren}(n)$ is the total weight of the compositions of $n$ when every cut has the weight $1$ (`Parking.Lam_one`), the number $e^{m}\kappa_2(m)$ is the total weight of the compositions of $m$ with one marked cut point for the cut profile $1$ (`Parking.Lam1`). Counting by the number of parts gives the closed form $\kappa_2(m) = P(m)\,(s_m - 1)$ of `Parking.kc2_eq`, where $s_m$ is the mean of the birthday law. By that closed form, $\kappa_2(m)$ tends to $\tfrac12$ as $m$ grows.

**Why it appears.** In the curve increase both sides of the pair–impulse criterion `Parking.dq_pos_of_pair` are sums of chain sums whose cut factors are slightly below $1$. The estimates compare each chain sum of length $m$ with its value $\operatorname{ren}(m) = e^{m}P(m)$ for the cut factors $1$. A term of the pair sum has two such chain sums, of the lengths $a$ and $b - a$ for a pair of marked points $a < b$, and summing $P(a)\,P(b-a)$ over $a$ gives $\kappa_2(b)$. Thus $\sum_{b \le R} \kappa_2(b)$ is the main term of the lower bound `Parking.pairSum_ge`, and $\kappa_2$ and the threefold convolution $\kappa_3$ (`Parking.kc3`) are the quantities in which that bound and the upper bound `Parking.impulse_le` of the boundary term are expressed.

**Notation.** The index $2$ of $\kappa_2$ counts the factors of the convolution. The symbol denotes a function of one argument and has no relation to the numbers $\kappa_k(t)$ that occur in the frozen polynomial, whose index is a column.

In Lean the definition is `kc2 m`, a sum over `Finset.Ioo 0 m` of `poissonMass g * poissonMass (m - g)`.

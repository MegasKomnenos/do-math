---
weight: unit
short: the tree series T
---
## Description

The tree series $T = X P = \sum_{j \ge 1} a_j X^j$, a formal power series with real coefficients, where $a_j = j^{j-1}/j!$ are the Cayley coefficients and $P = \sum_n c_n X^n$ with $c_n = a_{n+1}$.

## Statement

$T = X \cdot P$, where $P = \sum_{n \ge 0} c_n X^n$ is the series of the numbers $c_n = (n+1)^{n-1}/n!$ (`Parking.TreeSeries.Pser`). Its coefficient of $X^j$ is the Cayley coefficient $a_j$ (`Parking.cay`) for every $j \ge 0$ (`Parking.TreeSeries.coeff_Tser`):

$$T = \sum_{j \ge 1} a_j X^j = X + X^2 + \tfrac{3}{2} X^3 + \tfrac{8}{3} X^4 + \cdots .$$

## Explanation

Classically $T$ is the tree function, the exponential generating series of rooted labelled trees, characterised by $T = X e^{T}$. In the library it is a formal power series, defined as $XP$, and what is used of the functional equation is its derivative form $P' = T'P$, which is the recursion `Parking.cc_rec` (see the proof of `Parking.TreeSeries.deriv_Eser`). No analytic property of the tree function is used; its value at the singularity $X = e^{-1}$, which is the statement that the series $\sum_j e^{-j} a_j$ has sum $1$, is obtained separately in `Parking.hasSum_borel`.

The definition as $XP$, and not as the series with the coefficients $a_j$, makes the relation between $T$ and $P$ hold by definition. In the single-chain formula (`Parking.IsWSol.ez`) $T$ is the series from which the series of a weighted recursion is subtracted.

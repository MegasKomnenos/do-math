---
weight: unit
short: threefold convolution of the Poisson mass
---
## Description

$\kappa_3(m) = \sum_{0<g<m} \kappa_2(g)\,P(m-g)$, where $P(n) = e^{-n} n^n/n!$ is the Poisson mass and $\kappa_2$ its twofold convolution: the sum of $P(g_1)P(g_2)P(g_3)$ over the splittings of $m$ into three positive parts.

## Statement

For a natural number $m$,

$$\kappa_3(m) \;=\; \sum_{0 < g < m} \kappa_2(g)\; P(m-g),$$

where $P(n) = e^{-n} n^n/n!$ (`Parking.poissonMass`) and $\kappa_2(g) = \sum_{0<h<g} P(h)\,P(g-h)$ (`Parking.kc2`). Since $\kappa_2(1) = 0$, the sum vanishes for $m \le 2$.

## Explanation

Inserting the definition of $\kappa_2$ gives $\kappa_3(m) = \sum P(g_1)\,P(g_2)\,P(g_3)$, the sum over all triples of positive integers with $g_1 + g_2 + g_3 = m$. As for $\kappa_2$, the number $e^{m}\kappa_3(m)$ is the total weight of the compositions of $m$ with two marked cut points for the cut profile $1$ (`Parking.Lam2`), and counting by the number of parts gives the closed form $\kappa_3(m) = (m-1)\,P(m) - 2\kappa_2(m)$ of `Parking.kc3_eq`.

In the curve increase $\kappa_3$ appears wherever a third point is marked besides the two marked points of a pair: in the sums of the exponents on the pair side, where the third point is a cut point whose factor is being estimated (`Parking.pairSum_ge`), and in the weights $P(R-s)\,(R-1-s)\,\kappa_2(s)$ of the impulse side (`Parking.impulse_weight_sum`, `Parking.impulse_le`). The identities `Parking.kc3_comm`, `Parking.kc3_mom_left` and `Parking.kc3_mom_right` evaluate the sums that arise.

The definition places the twofold convolution first and the single factor second; by `Parking.kc3_comm` the other order, $\sum_{0<a<m} P(a)\,\kappa_2(m-a)$, gives the same number. The index $3$ of $\kappa_3$ counts the factors of the convolution, and the symbol has no relation to the numbers $\kappa_k(t)$ that occur in the frozen polynomial, whose index is a column. In Lean the definition is `kc3 m`, a sum over `Finset.Ioo 0 m` of `kc2 g * poissonMass (m - g)`.

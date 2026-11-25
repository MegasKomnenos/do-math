---
weight: unit
short: mean position of the impulse weights
---
## Description

For every natural number $R$, the weights $w_s = P(R-s)\,(R-1-s)\,\kappa_2(s)$, $0 < s < R$, satisfy $\tfrac{2R}{5}\sum_s w_s \le \sum_s s\,w_s$, where $P$ is the Poisson mass and $\kappa_2$ its twofold convolution: the mean position of the weights is at least $2R/5$.

## Statement

For a natural number $R$ and $0 < s < R$ put $w_s = P(R-s)\,(R-1-s)\,\kappa_2(s)$, where $P(n) = e^{-n} n^n/n!$ (`Parking.poissonMass`) and $\kappa_2$ is the twofold convolution of the Poisson mass (`Parking.kc2`). Then for every natural number $R$,

$$\frac{2R}{5} \sum_{0 < s < R} w_s \;\le\; \sum_{0 < s < R} s\; w_s .$$

## Explanation

The weights $w_s$ are those of `Parking.impulse_weight_sum`, where their origin in the upper bound of the boundary term is described and their total is computed. The present statement says that their mean position $\sum_s s\,w_s / \sum_s w_s$ is at least $2R/5$, whenever the total is positive.

The value $2R/5$ comes from a count of factors. By the closed form `Parking.kc3_eq`, $P(R-s)\,(R-1-s) = \kappa_3(R-s) + 2\kappa_2(R-s)$, so $w_s = \kappa_2(s)\,\kappa_3(R-s) + 2\,\kappa_2(s)\,\kappa_2(R-s)$. The sum over $s$ of the first term is a fivefold convolution of the Poisson mass, in which $s$ is the sum of the first two of five parts; since the five parts play the same role, the mean of $s$ under these weights is $2R/5$. The sum of the second term is a fourfold convolution in which $s$ is the sum of the first two of four parts, with the mean $R/2$. The mean position of the $w_s$ is an average of $2R/5$ and $R/2$ and is therefore at least $2R/5$.

In `Parking.impulse_le` the statement is used as follows. The sum to be bounded from above is $\sum_s w_s\, h(s)$ with $h(x) = (R - 1 - x/2)/(K + R - x)$, where $K$ is the threshold at which the boundary term is bounded; this function is concave on $[0,R]$ for $K \ge R$. The tangent of $h$ at $x_0 = 2R/5$ lies above $h$ and has a negative slope, so the sum is at most $h(x_0)$ times the total weight as soon as the mean position is at least $x_0$.

In Lean the left side is `2 * (R : ℝ) / 5 * ∑ s ∈ Ioo 0 R, poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s` and the summand on the right is `(s : ℝ) * (poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s)`.

## Proof

For functions $u, v : \mathbb{N} \to \mathbb{R}$ write $(u \star v)(m) = \sum_{0<g<m} u(g)\, v(m-g)$ for the convolution over the proper splittings of $m$, and $g\,u$ for the function $g \mapsto g\cdot u(g)$. Let $\kappa_3$ be the threefold convolution of `Parking.kc3`, so that $\kappa_2 = P \star P$ and $\kappa_3 = \kappa_2 \star P$. Three properties of $\star$ are used: it is commutative (substitute $g \mapsto m - g$); it is associative (both $(u \star v) \star w$ and $u \star (v \star w)$ at $m$ are the sum of $u(a)\, v(b-a)\, w(m-b)$ over $0 < a < b < m$); and $(g\,u) \star v + u \star (g\,v) = m\,(u \star v)$ at $m$, because $g + (m-g) = m$ in every term.

**The weights.** For $0 < s < R$ we have $R - s \ge 1$, and `Parking.kc3_eq` at $R - s$ gives $\kappa_3(R-s) + 2\kappa_2(R-s) = (R - s - 1)\,P(R-s)$. Hence $w_s = \kappa_2(s)\bigl(\kappa_3(R-s) + 2\kappa_2(R-s)\bigr)$, and with $A = (\kappa_2 \star \kappa_3)(R)$ and $B = (\kappa_2 \star \kappa_2)(R)$,

$$\sum_{0<s<R} w_s = A + 2B, \qquad \sum_{0<s<R} s\,w_s = \bigl((g\,\kappa_2) \star \kappa_3\bigr)(R) + 2\,\bigl((g\,\kappa_2) \star \kappa_2\bigr)(R).$$

**The fourfold convolution.** By the derivation property and commutativity, $2\,\bigl((g\,\kappa_2) \star \kappa_2\bigr)(R) = R\,B$; so $\bigl((g\,\kappa_2) \star \kappa_2\bigr)(R) = \tfrac{R}{2}\,B$.

**The fivefold convolution.** Put $X = \bigl((g\,\kappa_2) \star \kappa_3\bigr)(R)$ and $Y = \bigl(\kappa_2 \star (g\,\kappa_3)\bigr)(R)$. The derivation property gives $X + Y = R\,A$. By associativity, $X = \bigl(((g\,\kappa_2) \star \kappa_2) \star P\bigr)(R)$. By `Parking.kc3_mom_left`, $(g\,\kappa_2) \star P = \tfrac{2g}{3}\,\kappa_3$ at every argument $g$, that is, $g\,\kappa_3 = \tfrac32\,(g\,\kappa_2) \star P$ as functions; hence, by associativity and commutativity,

$$Y = \tfrac32\,\bigl(\kappa_2 \star ((g\,\kappa_2) \star P)\bigr)(R) = \tfrac32\,\bigl((\kappa_2 \star (g\,\kappa_2)) \star P\bigr)(R) = \tfrac32\,\bigl(((g\,\kappa_2) \star \kappa_2) \star P\bigr)(R) = \tfrac32\,X .$$

From $X + \tfrac32 X = R\,A$ we get $X = \tfrac{2R}{5}\,A$.

**Conclusion.** The two evaluations give $\sum_s s\,w_s = \tfrac{2R}{5}\,A + R\,B$, while $\tfrac{2R}{5}\sum_s w_s = \tfrac{2R}{5}\,A + \tfrac{4R}{5}\,B$. The difference is $\tfrac{R}{5}\,B$, which is nonnegative because $B$ is a sum of products of the nonnegative numbers $\kappa_2$ (`Parking.kc2_nonneg`).

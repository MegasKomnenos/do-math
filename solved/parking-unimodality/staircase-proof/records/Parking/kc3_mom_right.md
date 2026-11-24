---
weight: unit
short: mean position of the first factor in the threefold convolution
---
## Description

For every natural number $m$: $\sum_{0<a<m} a\,P(a)\,\kappa_2(m-a) = \tfrac{m}{3}\,\kappa_3(m)$, where $P$ is the Poisson mass and $\kappa_2$, $\kappa_3$ are its twofold and threefold convolutions.

## Statement

For every natural number $m$,

$$\sum_{0 < a < m} a\;P(a)\;\kappa_2(m-a) \;=\; \frac{m}{3}\;\kappa_3(m),$$

where $P(n) = e^{-n} n^n/n!$ (`Parking.poissonMass`), $\kappa_2$ is the twofold convolution of `Parking.kc2`, and $\kappa_3(m) = \sum_{0<a<m} \kappa_2(a)\,P(m-a)$ (`Parking.kc3`).

## Explanation

The number $\kappa_3(m)$ is the sum of $P(g_1)\,P(g_2)\,P(g_3)$ over the splittings $m = g_1 + g_2 + g_3$ into three positive parts, and by the symmetry of the three parts each has the mean $m/3$ under these weights. In the sum of the statement, $a = g_1$ is the first part. The statement is the complement of `Parking.kc3_mom_left`, which treats the sum $g_1 + g_2$ of the first two parts.

It is used in the lower bound of the pair sum (`Parking.pairSum_ge`), for the exponents of the cut points that lie between the two marked points of a pair: there $a$ is the upper marked point and the convolution $\kappa_2(m-a)$ comes from the chain between the marked points.

In Lean the summand is `(a : ℝ) * (poissonMass a * kc2 (m - a))` and the right side is `(m : ℝ) / 3 * kc3 m`.

## Proof

For functions $u, v : \mathbb{N} \to \mathbb{R}$ write $(u \star v)(m) = \sum_{0<g<m} u(g)\, v(m-g)$ for the convolution over the proper splittings of $m$, and $g\,u$ for the function $g \mapsto g\cdot u(g)$. Then $\kappa_2 = P \star P$ and $\kappa_3 = \kappa_2 \star P$. The convolution is commutative (substitute $g \mapsto m - g$) and associative (both $(u \star v) \star w$ and $u \star (v \star w)$ at $m$ are the sum of $u(a)\, v(b-a)\, w(m-b)$ over $0 < a < b < m$), and multiplication by the argument acts on it as a derivation: $(g\,u) \star v + u \star (g\,v) = m\,(u \star v)$ at $m$, because $g + (m-g) = m$ in every term.

The left side of the statement is $\bigl((g\,P) \star \kappa_2\bigr)(m)$, which equals $Y = \bigl(\kappa_2 \star (g\,P)\bigr)(m)$ by commutativity. Let $X = \bigl((g\,\kappa_2) \star P\bigr)(m)$. The derivation property for $u = \kappa_2$, $v = P$ gives

$$X + Y = m\,\kappa_3(m).$$

Moreover $X = 2Y$. Indeed, `Parking.kc2_mom` says $g\,\kappa_2 = 2\,(g\,P) \star P$ as functions, so $X = 2\bigl(((g\,P) \star P) \star P\bigr)(m) = 2\bigl((g\,P) \star (P \star P)\bigr)(m) = 2\bigl(\kappa_2 \star (g\,P)\bigr)(m) = 2Y$, by associativity and commutativity. The two relations give $Y = \tfrac{m}{3}\,\kappa_3(m)$.

This is the computation of the proof of `Parking.kc3_mom_left`, solved for $Y$ in the place of $X$.

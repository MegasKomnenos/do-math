---
weight: unit
short: mean position of the first two factors in the threefold convolution
---
## Description

For every natural number $m$: $\sum_{0<a<m} a\,\kappa_2(a)\,P(m-a) = \tfrac{2m}{3}\,\kappa_3(m)$, where $P$ is the Poisson mass and $\kappa_2$, $\kappa_3$ are its twofold and threefold convolutions.

## Statement

For every natural number $m$,

$$\sum_{0 < a < m} a\;\kappa_2(a)\;P(m-a) \;=\; \frac{2m}{3}\;\kappa_3(m),$$

where $P(n) = e^{-n} n^n/n!$ (`Parking.poissonMass`), $\kappa_2(a) = \sum_{0<g<a} P(g)\,P(a-g)$ (`Parking.kc2`) and $\kappa_3(m) = \sum_{0<a<m} \kappa_2(a)\,P(m-a)$ (`Parking.kc3`).

## Explanation

The number $\kappa_3(m)$ is the sum of $P(g_1)\,P(g_2)\,P(g_3)$ over the splittings $m = g_1 + g_2 + g_3$ into three positive parts. The three parts play the same role, so each has the mean $m/3$ under these weights. In the sum of the statement, $a = g_1 + g_2$ is the sum of the first two parts, whose mean is $2m/3$. The companion statement `Parking.kc3_mom_right` is about the first part alone.

In the curve increase, $a$ is the position of the second of two points on a chain of length $m$. The statement is used in the lower bound of the pair sum (`Parking.pairSum_ge`), twice: for the exponents of the cut points above the upper marked point, and for the weights of the sizes below the lower marked point. Inside this module it gives `Parking.impulse_weight_sum` and enters `Parking.impulse_weight_mean`.

In Lean the summand is `(a : ℝ) * (kc2 a * poissonMass (m - a))` and the right side is `2 * (m : ℝ) / 3 * kc3 m`.

## Proof

For functions $u, v : \mathbb{N} \to \mathbb{R}$ write $(u \star v)(m) = \sum_{0<g<m} u(g)\, v(m-g)$ for the convolution over the proper splittings of $m$, and $g\,u$ for the function $g \mapsto g\cdot u(g)$. Then $\kappa_2 = P \star P$ and $\kappa_3 = \kappa_2 \star P$. Three properties of $\star$ are used.

- *Commutativity:* $u \star v = v \star u$, by the substitution $g \mapsto m - g$.
- *Associativity:* $(u \star v) \star w = u \star (v \star w)$. Both sides at $m$ are the sum of $u(a)\, v(b-a)\, w(m-b)$ over $0 < a < b < m$: on the left one sums over $b$ and then over $a < b$, on the right over $a$ and then over the second part $h = b - a$.
- *Derivation:* $(g\,u) \star v + u \star (g\,v) = m\,(u \star v)$ at $m$, because $g + (m - g) = m$ in every term.

Let $X = \bigl((g\,\kappa_2) \star P\bigr)(m)$, the left side of the statement, and $Y = \bigl(\kappa_2 \star (g\,P)\bigr)(m)$. The derivation property for $u = \kappa_2$ and $v = P$ gives

$$X + Y = m\,\kappa_3(m).$$

Next, `Parking.kc2_mom` says $(g\,P) \star P = \tfrac{g}{2}\,\kappa_2$ at every argument $g$, that is, $g\,\kappa_2 = 2\,(g\,P) \star P$ as functions. Therefore

$$X = 2\,\bigl(((g\,P) \star P) \star P\bigr)(m) = 2\,\bigl((g\,P) \star (P \star P)\bigr)(m) = 2\,\bigl(\kappa_2 \star (g\,P)\bigr)(m) = 2Y,$$

by associativity and then commutativity. From $X + Y = m\,\kappa_3(m)$ and $X = 2Y$ we get $X = \tfrac{2m}{3}\,\kappa_3(m)$.

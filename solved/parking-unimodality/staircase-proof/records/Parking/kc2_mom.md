---
weight: unit
short: mean position in the twofold convolution of the Poisson mass
---
## Description

For every natural number $m$: $\sum_{0<g<m} g\,P(g)\,P(m-g) = \tfrac{m}{2}\,\kappa_2(m)$, where $P(n) = e^{-n} n^n/n!$ and $\kappa_2(m) = \sum_{0<g<m} P(g)\,P(m-g)$.

## Statement

For every natural number $m$,

$$\sum_{0 < g < m} g\; P(g)\; P(m-g) \;=\; \frac{m}{2}\;\kappa_2(m),$$

where $P(n) = e^{-n} n^n/n!$ is the Poisson mass (`Parking.poissonMass`) and $\kappa_2$ is its twofold convolution (`Parking.kc2`).

## Explanation

The weights $P(g)\,P(m-g)$ of the splittings $m = g + (m-g)$ are symmetric under the exchange of the two parts, so the mean of the first part is $m/2$. In the curve increase the splitting point $g$ is a cut point of a chain of length $m$, and the weight $P(g)\,P(m-g)$ is, up to the factor $e^{-m}$, the weight of the compositions of $m$ that have a cut point at $g$ when all cut factors are $1$. The estimates bound the logarithm of a cut factor at $g$ by a function that is linear in $g$; the present statement then evaluates the sum of these bounds over $g$. It is used in this way in the lower bound of the pair sum (`Parking.pairSum_ge`) and in the upper bound of the boundary term (`Parking.impulse_le`), and it is the first step of the corresponding identities for the threefold convolution (`Parking.kc3_mom_left`, `Parking.kc3_mom_right`).

In Lean the summand is `(g : ℝ) * (poissonMass g * poissonMass (m - g))` and the right side is `(m : ℝ) / 2 * kc2 m`.

## Proof

Let $X$ denote the left side. The substitution $g \mapsto m - g$ maps the range $0 < g < m$ onto itself and gives $X = \sum_{0<g<m} (m - g)\, P(m-g)\, P(g)$. Adding the two expressions for $X$,

$$2X = \sum_{0<g<m} \bigl(g + (m-g)\bigr)\, P(g)\, P(m-g) = m\,\kappa_2(m).$$

In the Lean proof these two steps are two general properties of the convolution $(u \star v)(m) = \sum_{0<g<m} u(g)\, v(m-g)$ over the proper splittings of $m$: it is commutative, and multiplication by the argument acts on it as a derivation, $(g\,u) \star v + u \star (g\,v) = m\,(u \star v)$.

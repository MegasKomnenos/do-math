---
weight: unit
short: closed form of the threefold convolution of the Poisson mass
---
## Description

For $m \ge 1$: $\kappa_3(m) = (m-1)\,P(m) - 2\,\kappa_2(m)$, where $P(n) = e^{-n} n^n/n!$ is the Poisson mass and $\kappa_2$, $\kappa_3$ are its twofold and threefold convolutions over splittings into positive parts.

## Statement

For every natural number $m \ge 1$,

$$\kappa_3(m) \;=\; (m-1)\,P(m) \;-\; 2\,\kappa_2(m),$$

where $P(n) = e^{-n} n^n/n!$ (`Parking.poissonMass`), $\kappa_2(m) = \sum_{0<g<m} P(g)\,P(m-g)$ (`Parking.kc2`) and $\kappa_3(m) = \sum_{0<g<m} \kappa_2(g)\,P(m-g)$ (`Parking.kc3`).

## Explanation

**Why it holds.** The number $e^{m}\kappa_3(m)$ is the total weight of the compositions of $m$ with two marked cut points, when a composition is weighted by the product of the Cayley coefficients of its parts (`Parking.Lam2`). A composition with $q$ parts has $\binom{q-1}{2}$ pairs of cut points (`Parking.Lam2_eq_sum`), so $e^{m}\kappa_3(m)$ is the total weight $m^m/m!$ times the mean of $\binom{Q-1}{2}$, where the number of parts $Q$ follows the birthday law of $m$. With the mean $s_m$ of that law, the second factorial moment is $\mathbb{E}[Q(Q-1)] = 2(m - s_m)$, and $\binom{Q-1}{2} = \tfrac12 Q(Q-1) - (Q-1)$. Hence the mean of $\binom{Q-1}{2}$ is $(m - s_m) - (s_m - 1) = m + 1 - 2s_m$, and $\kappa_3(m) = P(m)\,(m + 1 - 2s_m)$. Replacing $P(m)(s_m - 1)$ by $\kappa_2(m)$ (`Parking.kc2_eq`) gives the statement.

**What it is for.** The statement expresses $\kappa_3$ by $\kappa_2$ and $P$. The estimates of the curve increase use it to eliminate $\kappa_3$ from the sums of the pair side and from the bound of the boundary term, after which only the Poisson mass and $\kappa_2$ remain to be bounded. Inside this module it gives the form $P(R-s)\,(R-1-s) = \kappa_3(R-s) + 2\kappa_2(R-s)$ of the impulse weights (`Parking.impulse_weight_mean`).

**The hypothesis.** For $m = 1$ and $m = 2$ both sides vanish. For $m = 0$ the statement fails: the left side is $0$ and the right side is $-P(0) = -1$.

In Lean the statement is `kc3 m = ((m : ℝ) - 1) * poissonMass m - 2 * kc2 m`.

## Proof

Let $\operatorname{ren}(n) = n^n/n!$ (`Parking.ren`), $a_p = p^{p-1}/p!$ (`Parking.cay`), and let $P_{m,q} = \prod_{i<q}(1 - i/m)$ be the birthday tail (`Parking.Pb`) and $s_m = \sum_{q=1}^{m} P_{m,q}$ its sum (`Parking.sbirth`). The Poisson mass is $P(n) = e^{-n}\operatorname{ren}(n)$.

*Step 1.* By `Parking.poissonMass_mul`, $\kappa_2(b) = e^{-b}\sum_{0<a<b} \operatorname{ren}(a)\operatorname{ren}(b-a)$. In the term $\kappa_2(b)\,P(m-b)$ of $\kappa_3(m)$ the exponential factors are $e^{-b}\, e^{-(m-b)} = e^{-m}$, so

$$\kappa_3(m) = e^{-m} \sum_{0<b<m} \Bigl(\sum_{0<a<b} \operatorname{ren}(a)\operatorname{ren}(b-a)\Bigr)\operatorname{ren}(m-b).$$

*Step 2.* Let $\mathbf{1}$ be the constant cut profile $1$. By `Parking.Lam_one` the inner sum is $\Lambda^{(1)}_b[\mathbf{1}]$ (as in the proof of `Parking.kc2_eq`) and $\operatorname{ren}(m-b) = \Lambda_{m-b}[\mathbf{1}]$, so the double sum is $\Lambda^{(2)}_m[\mathbf{1}]$ by the definition of `Parking.Lam2`.

*Step 3.* By `Parking.Lam2_eq_sum` and `Parking.Tq_eq`, with $T_{m,q} = V_q(m;\mathbf{1}) = a_m\, q\, P_{m,q}$,

$$\Lambda^{(2)}_m[\mathbf{1}] = \sum_{q=1}^{m} \frac{(q-1)(q-2)}{2}\; T_{m,q} = a_m \sum_{q=1}^{m} \frac{(q-1)(q-2)}{2}\; q\, P_{m,q}.$$

*Step 4.* Since $\tfrac12 (q-1)(q-2)\,q = \tfrac12\, q^2(q-1) - q(q-1)$, the last sum is

$$\frac12 \sum_{q=1}^{m} q^2 (q-1)\, P_{m,q} \;-\; \sum_{q=1}^{m} (q-1)\, q\, P_{m,q} \;=\; \frac12\cdot 2m\,(m - s_m) \;-\; m\,(s_m - 1) \;=\; m\,(m + 1 - 2 s_m).$$

The first sum is evaluated by `Parking.Pb_sum3`. The second is `Parking.Pb_moment` with $g(j) = j - 1$, as in the proof of `Parking.kc2_eq`: there $g(0) = -1$ and $g(q) - g(q-1) = 1$, which gives $m(-1 + s_m)$.

*Step 5.* Using $m\, a_m = \operatorname{ren}(m)$ for $m \ge 1$,

$$\kappa_3(m) = e^{-m}\operatorname{ren}(m)\,(m + 1 - 2 s_m) = P(m)\,(m + 1 - 2 s_m) = (m-1)\,P(m) - 2\,P(m)\,(s_m - 1),$$

and $P(m)(s_m - 1) = \kappa_2(m)$ by `Parking.kc2_eq`.

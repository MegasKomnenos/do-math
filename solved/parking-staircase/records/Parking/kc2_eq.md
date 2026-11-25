---
weight: unit
short: closed form of the twofold convolution of the Poisson mass
---
## Description

For $m \ge 1$: $\kappa_2(m) = P(m)\,(s_m - 1)$, where $\kappa_2(m) = \sum_{0<g<m} P(g)\,P(m-g)$, $P(n) = e^{-n} n^n/n!$ is the Poisson mass, and $s_m = \sum_{j=1}^{m} \prod_{i<j}(1 - i/m)$ is the mean of the birthday law of $m$.

## Statement

For every natural number $m \ge 1$,

$$\kappa_2(m) \;=\; P(m)\,\bigl(s_m - 1\bigr),$$

where $\kappa_2(m) = \sum_{0<g<m} P(g)\,P(m-g)$ (`Parking.kc2`), $P(n) = e^{-n} n^n/n!$ (`Parking.poissonMass`), and $s_m = \sum_{j=1}^{m} P_{m,j}$ with the birthday tail $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ (`Parking.sbirth`, `Parking.Pb`).

## Explanation

**Why it holds.** Draw a composition of $m$ with probability proportional to the product of the Cayley coefficients $a_p = p^{p-1}/p!$ of its parts. `Parking.Tq_eq` shows that its number of parts follows the birthday law of $m$, whose mean is $s_m$; so the mean number of cut points is $s_m - 1$. The total of the weights is $m^m/m! = e^{m}P(m)$ (`Parking.Lam_one`). On the other side, $e^{m}\kappa_2(m) = \sum_{0<g<m} \operatorname{ren}(g)\operatorname{ren}(m-g)$ with $\operatorname{ren}(n) = n^n/n!$ is the total weight of the compositions of $m$ with one marked cut point (`Parking.Lam1`), which is the total weight times the mean number of cut points (`Parking.Lam1_eq_sum`). Dividing by $e^{m}$ gives the statement.

**What it is for.** The closed form reduces the convolution $\kappa_2$ to the two quantities $P(m)$ and $s_m$ for which sharp bounds are available: Stirling's formula for $P(m)$ and Ramanujan's estimate for $s_m$. Since $P(m)$ is about $1/\sqrt{2\pi m}$ and $s_m$ about $\sqrt{\pi m/2}$, the convolution $\kappa_2(m)$ tends to $\tfrac12$. The estimates of the curve increase use the closed form to turn a lower bound of $s_m$ into a lower bound of $\kappa_2(m)$, and `Parking.kc3_eq` uses it for the threefold convolution.

**The hypothesis.** For $m = 1$ both sides vanish, since $s_1 = 1$. For $m = 0$ the statement fails: $\kappa_2(0) = 0$, while $P(0)(s_0 - 1) = -1$.

**The Lean form.** The statement is `kc2 m = poissonMass m * (sbirth m - 1)`. The symbol $P$ for the Poisson mass has one argument and the birthday tail $P_{m,j}$ has two indices; in the proof below the Poisson mass is written $e^{-m}\operatorname{ren}(m)$.

## Proof

Let $\operatorname{ren}(n) = n^n/n!$ (`Parking.ren`), so that $P(n) = e^{-n}\operatorname{ren}(n)$.

*Step 1.* By `Parking.poissonMass_mul`, $P(g)\,P(m-g) = e^{-m}\operatorname{ren}(g)\operatorname{ren}(m-g)$ for $0 < g < m$, so $\kappa_2(m) = e^{-m}\sum_{0<g<m} \operatorname{ren}(g)\operatorname{ren}(m-g)$.

*Step 2.* Let $\mathbf{1}$ be the constant cut profile $1$. By `Parking.Lam_one`, $\Lambda_g[\mathbf{1}] = \operatorname{ren}(g)$ and $\Lambda_{m-g}[\mathbf{1}] = \operatorname{ren}(m-g)$ for $0 < g < m$, and the shifted profile of a constant profile is the same constant profile. Hence, by the definition of `Parking.Lam1`,

$$\sum_{0<g<m} \operatorname{ren}(g)\operatorname{ren}(m-g) = \Lambda^{(1)}_m[\mathbf{1}].$$

*Step 3.* By `Parking.Lam1_eq_sum`, $\Lambda^{(1)}_m[\mathbf{1}] = \sum_{q=1}^{m} (q-1)\, T_{m,q}$, where $T_{m,q} = V_q(m;\mathbf{1})$ is the total weight of the compositions of $m$ with $q$ parts (`Parking.Tq`). By `Parking.Tq_eq`, $T_{m,q} = a_m\, q\, P_{m,q}$ for $q \ge 1$. Therefore

$$\Lambda^{(1)}_m[\mathbf{1}] = a_m \sum_{q=1}^{m} (q-1)\; q\, P_{m,q}.$$

(The passage from a sum of the $T_{m,q}$ with polynomial coefficients to the birthday tails is a private lemma of the module on the birthday law; it is `Parking.Tq_eq` applied term by term.)

*Step 4.* `Parking.Pb_moment` states, for $m \ge 1$ and any function $g$, that $\sum_{q=1}^{m} g(q)\, q\, P_{m,q} = m\bigl(g(0) + \sum_{q=1}^{m} (g(q) - g(q-1))\, P_{m,q}\bigr)$. With $g(j) = j - 1$ we have $g(0) = -1$ and $g(q) - g(q-1) = 1$, so

$$\sum_{q=1}^{m} (q-1)\; q\, P_{m,q} = m\Bigl(-1 + \sum_{q=1}^{m} P_{m,q}\Bigr) = m\,(s_m - 1).$$

*Step 5.* For $m \ge 1$, $m\, a_m = m^m/m! = \operatorname{ren}(m)$. Combining the steps,

$$\kappa_2(m) = e^{-m}\, a_m\, m\,(s_m - 1) = e^{-m}\operatorname{ren}(m)\,(s_m - 1) = P(m)\,(s_m - 1).$$

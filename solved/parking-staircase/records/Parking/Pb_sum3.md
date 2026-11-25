---
weight: step
short: second factorial moment of the birthday law
---
## Description

The second factorial moment of the birthday law in terms of its mean: $\sum_{q=1}^{m} q^2(q-1)\,P_{m,q} = 2m\,(m - s_m)$ for $m \ge 1$.

## Statement

For every natural number $m \ge 1$,

$$\sum_{q=1}^{m} q^{2}\,(q-1)\,P_{m,q} \;=\; 2m\,(m - s_m),$$

where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail (`Parking.Pb`) and $s_m = \sum_{j=1}^{m} P_{m,j}$ (`Parking.sbirth`).

## Explanation

Let $Q$ follow the birthday law of $m$ (see `Parking.Pb`), with $\Pr(Q = q) = \frac{q}{m} P_{m,q}$. Divided by $m$, the identity says $\mathbb{E}[Q(Q-1)] = 2(m - s_m)$, where $s_m = \mathbb{E}[Q]$. Together with `Parking.Tq_eq` it gives the sum $\sum_q q(q-1)\,T_{m,q} = 2m\,a_m\,(m - s_m)$ over the weights of compositions, which is the denominator in `Parking.Dbirth_spec` and the quantity whose positivity is `Parking.sum_qq_Tq_pos`. It is used in the same way in the proof of `Parking.kc3_eq`, the closed form of the threefold convolution of the Poisson mass, in which a composition of $m$ with $q$ parts is counted once for each of the $\binom{q-1}{2}$ pairs of its cut points.

In the Lean statement the sum runs over $i < m$ with $q = i + 1$, and the summand is $(i+1)^2\, i\, P_{m,i+1}$.

## Proof

Apply `Parking.Pb_moment` to $g(j) = j(j-1)$. Then $g(q)\,q = q^2(q-1)$, $g(0) = 0$, and $g(q) - g(q-1) = 2q - 2$, so

$$\sum_{q=1}^{m} q^{2}(q-1)\,P_{m,q} \;=\; m \sum_{q=1}^{m}(2q - 2)\,P_{m,q}.$$

Two sums remain. The first is $\sum_{q=1}^{m} q\,P_{m,q} = m$, which is `Parking.Pb_moment` for the constant function $g = 1$ (then $g(q) - g(q-1) = 0$ and $g(0) = 1$). The second is $\sum_{q=1}^{m} P_{m,q} = s_m$, the definition of $s_m$. Hence the right-hand side is $m\,(2m - 2s_m)$.

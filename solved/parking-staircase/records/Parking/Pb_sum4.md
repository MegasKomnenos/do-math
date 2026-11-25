---
weight: step
short: third factorial moment of the birthday law
---
## Description

The third factorial moment of the birthday law in terms of its mean: $\sum_{q=1}^{m} q^2(q-1)(q-2)\,P_{m,q} = 3m\,((m+2)\,s_m - 3m)$ for $m \ge 1$.

## Statement

For every natural number $m \ge 1$,

$$\sum_{q=1}^{m} q^{2}\,(q-1)(q-2)\,P_{m,q} \;=\; 3m\,\bigl((m+2)\,s_m - 3m\bigr),$$

where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail (`Parking.Pb`) and $s_m = \sum_{j=1}^{m} P_{m,j}$ (`Parking.sbirth`).

## Explanation

Let $Q$ follow the birthday law of $m$ (see `Parking.Pb`), with $\Pr(Q = q) = \frac{q}{m} P_{m,q}$. Divided by $m$, the identity says $\mathbb{E}[Q(Q-1)(Q-2)] = 3((m+2)\,s_m - 3m)$. Divided by the second factorial moment $2(m - s_m)$ of `Parking.Pb_sum3`, this is the number $D_m$ of `Parking.Dbirth`; the identity is used in exactly this way in the proof of `Parking.Dbirth_spec`.

In the Lean statement the sum runs over $i < m$ with $q = i + 1$, and the summand is $(i+1)^2\, i\,(i-1)\, P_{m,i+1}$.

## Proof

Apply `Parking.Pb_moment` to $g(j) = j(j-1)(j-2)$. Then $g(q)\,q = q^2(q-1)(q-2)$, $g(0) = 0$, and $g(q) - g(q-1) = 3(q-1)(q-2) = 3q^2 - 9q + 6$, so

$$\sum_{q=1}^{m} q^{2}(q-1)(q-2)\,P_{m,q} \;=\; m \sum_{q=1}^{m}\bigl(3q^{2} - 9q + 6\bigr)\,P_{m,q}.$$

Three sums remain, each of which is known: $\sum_{q=1}^{m} q^2 P_{m,q} = m\,s_m$ (`Parking.Pb_moment` for $g(j) = j$, where $g(q) - g(q-1) = 1$ and $g(0) = 0$), $\sum_{q=1}^{m} q\,P_{m,q} = m$ (`Parking.Pb_moment` for $g = 1$), and $\sum_{q=1}^{m} P_{m,q} = s_m$ (the definition). The right-hand side is therefore $m\,(3m\,s_m - 9m + 6\,s_m) = 3m\,((m+2)\,s_m - 3m)$.

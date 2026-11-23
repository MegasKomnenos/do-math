---
weight: step
short: the moment ratio as a ratio of factorial moments
---
## Description

For $m \ge 2$, $D_m$ is the ratio of the third to the second factorial moment of the number of parts of a composition of $m$: $\sum_{q} q(q-1)(q-2)\,T_{m,q} = D_m \sum_{q} q(q-1)\,T_{m,q}$.

## Statement

For every natural number $m \ge 2$,

$$\sum_{q=1}^{m} q(q-1)(q-2)\;T_{m,q} \;=\; D_m \sum_{q=1}^{m} q(q-1)\;T_{m,q}.$$

Here $T_{m,q}$ is the total weight of the compositions of $m$ with exactly $q$ parts, each part of size $p$ weighted by $a_p = p^{p-1}/p!$ (`Parking.Tq`), and $D_m = 3((m+2)s_m - 3m)/(2(m - s_m))$ with $s_m$ the mean of the birthday law (`Parking.Dbirth`, `Parking.sbirth`).

## Explanation

Let $Q$ be the number of parts of a composition of $m$ drawn with probability proportional to its weight; by `Parking.Tq_eq` it follows the birthday law of $m$. Divided by the total weight, the identity says $\mathbb{E}[Q(Q-1)(Q-2)] = D_m\,\mathbb{E}[Q(Q-1)]$. The sum on the right is positive (`Parking.sum_qq_Tq_pos`), so $D_m$ is the quotient of the two factorial moments. The identity is the link between the closed formula that defines $D_m$ and the sums over compositions in which $D_m$ is used.

It is used in the proof of `Parking.curv_ratio`: after `Parking.lr_factorial_moment_le` has compared the ratio of factorial moments under a threshold profile with the ratio for the weights $T_{m,q}$, the present identity replaces the latter by $D_m$. It is used in the same way in `Parking.Dbirth_mono`, and it gives the sign of $D_m$ in `Parking.Dbirth_nonneg`.

The two sums are, explicitly, $3m\,a_m\,((m+2)s_m - 3m)$ and $2m\,a_m\,(m - s_m)$. In the Lean statement the factors $q$, $q - 1$, $q - 2$ are real numbers.

## Proof

*The two sums.* For any real function $G$, `Parking.Tq_eq` gives $\sum_{q=1}^{m} G(q)\,T_{m,q} = a_m \sum_{q=1}^{m} G(q)\,q\,P_{m,q}$, with $P_{m,q}$ the birthday tail (`Parking.Pb`). With $G(q) = q(q-1)$ the sum on the right is the one evaluated in `Parking.Pb_sum3`, and with $G(q) = q(q-1)(q-2)$ it is the one evaluated in `Parking.Pb_sum4`. Hence

$$\sum_{q=1}^{m} q(q-1)\,T_{m,q} = a_m\cdot 2m\,(m - s_m), \qquad \sum_{q=1}^{m} q(q-1)(q-2)\,T_{m,q} = a_m\cdot 3m\,\bigl((m+2)s_m - 3m\bigr).$$

*The quotient.* Since $m \ge 2$, `Parking.sbirth_lt` gives $m - s_m > 0$, so the definition of $D_m$ is a genuine quotient and $D_m\cdot 2(m - s_m) = 3((m+2)s_m - 3m)$. Multiplying this by $m\,a_m$ gives the assertion.

---
weight: step
short: bound for the moment ratio by the mean
---
## Description

The moment ratio of the birthday law is bounded by its mean: $D_m \le \frac32\,(s_m - 1)$ for $m \ge 2$.

## Statement

For every natural number $m \ge 2$,

$$D_m \;\le\; \tfrac32\,(s_m - 1),$$

where $s_m = \sum_{j=1}^{m} P_{m,j}$ (`Parking.sbirth`, with $P_{m,j}$ from `Parking.Pb`) and $D_m = 3((m+2)s_m - 3m)/(2(m - s_m))$ (`Parking.Dbirth`).

## Explanation

After multiplication by the positive denominator $2(m - s_m)$, the inequality is equivalent to $s_m^2 + s_m \le 2m$. Let $Q$ follow the birthday law of $m$ (see `Parking.Pb`). Then $\mathbb{E}[Q] = s_m$ and $\mathbb{E}[Q^2] = \mathbb{E}[Q(Q-1)] + \mathbb{E}[Q] = 2m - s_m$ by `Parking.Pb_sum3`, so the variance of $Q$ is $2m - s_m - s_m^2$. The statement is thus exactly the fact that this variance is nonnegative.

The bound is used in the proof of `Parking.Gfun_pos` for $2 \le r \le 13$, in the chain $D_r \le D_{13} \le \frac32(s_{13} - 1)$, whose first step is `Parking.Dbirth_mono` and whose right-hand side is bounded by `Parking.sbirth_le`. For $r \ge 14$ that proof does not use the present bound; it derives a bound for $D_r$ that is linear in $\sqrt r$ from the definition of $D_r$ and the upper bound for $s_r$.

## Proof

Write $s = s_m$. The proof has two steps.

*Step 1: $s^2 + s \le 2m$.* The sum

$$\sum_{q=1}^{m}(q - s)^2\;q\,P_{m,q}$$

is nonnegative, because $P_{m,q} \ge 0$ (`Parking.Pb_nonneg`). Since $(q-s)^2\,q = q^2(q-1) + (1 - 2s)\,q^2 + s^2\,q$, the sum equals

$$\sum_{q=1}^{m} q^2(q-1)\,P_{m,q} \;+\; (1 - 2s)\sum_{q=1}^{m} q^2 P_{m,q} \;+\; s^2 \sum_{q=1}^{m} q\,P_{m,q}.$$

The first sum is $2m(m - s)$ by `Parking.Pb_sum3`. The second is $m\,s$ and the third is $m$; these are `Parking.Pb_moment` applied to $g(j) = j$ and to $g = 1$. The total is $m\,(2m - s - s^2)$, and dividing by $m > 0$ gives the claim.

*Step 2.* By `Parking.sbirth_lt`, $2(m - s) > 0$. Multiplying the asserted inequality by this number turns it into $3((m+2)s - 3m) \le 3(s-1)(m-s)$, and the difference of the two sides is $3(2m - s - s^2)$, which is nonnegative by Step 1.

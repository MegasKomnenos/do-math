---
weight: step
short: monotonicity of the moment ratio
---
## Description

The moment ratio of the birthday law does not decrease: $D_m \le D_r$ for $2 \le m \le r$.

## Statement

For natural numbers $m$ and $r$ with $2 \le m \le r$, $D_m \le D_r$, where $D_m = 3((m+2)s_m - 3m)/(2(m - s_m))$ and $s_m$ is the mean of the birthday law (`Parking.Dbirth`, `Parking.sbirth`).

## Explanation

By `Parking.Dbirth_spec`, $D_m$ is the ratio of the third to the second factorial moment of the number $Q$ of parts of a composition of $m$, which follows the birthday law of $m$ (`Parking.Tq_eq`). With one more box the first repetition comes later: the law for $m+1$ is larger than the law for $m$ in likelihood-ratio order (`Parking.Pb_lr`), and a law that is larger in this order has a larger ratio of these two moments (`Parking.lr_factorial_moment_le`). The closed formula for $D_m$ does not show the monotonicity; the proof uses the description by moments.

The statement is used in two places. In the proof of `Parking.curv_ratio` the frozen polynomial of a first-layer position $n = k + r$ is a sum of contributions of the compositions of the integers $m \le r$; the contribution of each $m \ge 2$ satisfies a moment inequality with the constant $D_m$, and the monotonicity replaces all these constants by the single constant $D_r$. In the proof of `Parking.Gfun_pos`, for $2 \le r \le 13$, it gives $D_r \le D_{13}$, which is then bounded numerically through `Parking.Dbirth_le`.

## Proof

By induction on $r$ it suffices to prove $D_m \le D_{m+1}$ for every $m \ge 2$. Write $T_{m,q}$ for the total weight of the compositions of $m$ with $q$ parts (`Parking.Tq`), $P_{m,q}$ for the birthday tail (`Parking.Pb`) and $a_m$ for `Parking.cay`.

*Likelihood-ratio order.* For $1 \le q \le q' \le m + 1$,

$$T_{m,q'}\;T_{m+1,q} \;\le\; T_{m,q}\;T_{m+1,q'}.$$

Indeed, by `Parking.Tq_eq` the two sides are $a_m a_{m+1}\,q\,q'$ times $P_{m,q'}\,P_{m+1,q}$ and $P_{m,q}\,P_{m+1,q'}$ respectively; the common factor is nonnegative (`Parking.cay_nonneg`), and the inequality between the products of tails is `Parking.Pb_lr`.

*Comparison of moments.* `Parking.lr_factorial_moment_le` with $n = m+1$, $u(q) = T_{m,q}$ and $v(q) = T_{m+1,q}$ gives

$$\Bigl(\sum_{q=1}^{m+1} q(q-1)(q-2)\,T_{m,q}\Bigr)\Bigl(\sum_{q=1}^{m+1} q(q-1)\,T_{m+1,q}\Bigr) \;\le\; \Bigl(\sum_{q=1}^{m+1} q(q-1)(q-2)\,T_{m+1,q}\Bigr)\Bigl(\sum_{q=1}^{m+1} q(q-1)\,T_{m,q}\Bigr).$$

Since $T_{m,m+1} = 0$ (`Parking.Vc_eq_zero_of_lt`: a composition of $m$ has at most $m$ parts), the two sums that involve $T_{m,q}$ stop at $q = m$.

*Conclusion.* Put $S_m = \sum_{q=1}^{m} q(q-1)\,T_{m,q}$. By `Parking.Dbirth_spec` for $m$ and for $m+1$, the sums with the factor $q(q-1)(q-2)$ are $D_m\,S_m$ and $D_{m+1}\,S_{m+1}$, so the inequality reads $D_m\,S_m\,S_{m+1} \le D_{m+1}\,S_{m+1}\,S_m$. Both $S_m$ and $S_{m+1}$ are positive by `Parking.sum_qq_Tq_pos`, and dividing by their product gives $D_m \le D_{m+1}$.

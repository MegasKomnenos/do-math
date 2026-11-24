---
weight: step
short: positivity of the composition weights
---
## Description

For a cut profile that is positive at the cut points $1, \dots, m-1$, the weight $V_q(m;f)$ of the compositions of $m$ with $q$ parts is positive whenever $1 \le q \le m$.

## Statement

Let $f : \mathbb{N} \to \mathbb{R}$ and let $q$, $m$ be natural numbers with $1 \le q \le m$. If $f(s) > 0$ for every $s$ with $0 < s < m$, then $V_q(m;f) > 0$, where $V_q(m;f)$ is defined in `Parking.Vc`.

## Explanation

For $1 \le q \le m$ there is at least one composition of $m$ with $q$ parts, and with a positive profile its weight is positive because the Cayley numbers $a_p$, $p \ge 1$, are positive. Positivity, and not only nonnegativity (`Parking.Vc_nonneg`), is needed where a sum of such weights has to be positive: in `Parking.Tq_pos` for the constant profile, which gives the positive term of `Parking.tau_pos`, and in the proof of `Parking.curvSum_pos` for the threshold profile, where the compositions with two parts give the positive term of the curvature sum.

## Proof

By induction on $q$, for all $m$ at once. For $q = 1$, $V_1(m;f) = a_m$ by `Parking.Vc_one`, which is positive for $m \ge 1$ by `Parking.cay_pos`. For $q + 2 \le m$, `Parking.Vc_succ_succ` writes $V_{q+2}(m;f)$ as the sum over $0 < s < m$ of $V_{q+1}(s;f)\, f(s)\, a_{m-s}$. Every term is nonnegative by `Parking.Vc_nonneg` and `Parking.cay_nonneg`. The term $s = q + 1$ is positive: $V_{q+1}(q+1;f) > 0$ by the induction hypothesis, $f(q+1) > 0$ by hypothesis, and $a_{m-q-1} > 0$ because $m - q - 1 \ge 1$.

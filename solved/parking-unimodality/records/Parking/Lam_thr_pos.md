---
weight: step
short: positivity of the chain sums
---
## Description

The chain sum $\Lambda_m(y;N)$, the total weight of the compositions of $m$ for the threshold profile $s \mapsto y/(N-s)$, is positive for $y \ge 0$ and $1 \le m \le N$.

## Statement

Let $m \ge 1$ be a natural number and let $y$, $N$ be real numbers with $0 \le y$ and $m \le N$. Then $\Lambda_m(y;N) > 0$, where $\Lambda_m(y;N) = \Lambda_m[\lambda^{y,N}]$ is the total weight of `Parking.Lam` for the threshold profile $\lambda^{y,N}(s) = y/(N-s)$ of `Parking.thr`.

## Explanation

The chain sums are the boundary terms of `Parking.dq_frozen` and the common reference $\Lambda_r(k;N)$ of the two boundary comparisons. Their positivity is what allows `Parking.Lam_shorten` and `Parking.step_neg_of_Gfun` to cancel a chain sum from both sides of an inequality.

## Proof

For every profile $f$ that is nonnegative at the cut points $0 < s < m$ and every $m \ge 1$, $\Lambda_m[f] > 0$: the terms $V_q(m;f)$ of the sum are nonnegative by `Parking.Vc_nonneg`, and the term $q = 1$ is $a_m > 0$ by `Parking.Vc_one` and `Parking.cay_pos`. The threshold profile satisfies the hypothesis by `Parking.thr_nonneg`, since a cut point $s < m$ satisfies $s \le N$.

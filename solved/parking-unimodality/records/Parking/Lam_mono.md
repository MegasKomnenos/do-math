---
weight: step
short: monotonicity of the total composition weight in the profile
---
## Description

The total weight of the compositions of $m$ is monotone in a nonnegative cut profile: if $0 \le f \le g$ at the cut points $1, \dots, m-1$, then $\Lambda_m[f] \le \Lambda_m[g]$.

## Statement

Let $f, g : \mathbb{N} \to \mathbb{R}$ and let $m$ be a natural number such that $0 \le f(s) \le g(s)$ for every $s$ with $0 < s < m$. Then $\Lambda_m[f] \le \Lambda_m[g]$, where $\Lambda_m[f]$ is defined in `Parking.Lam`.

## Explanation

Every composition has a weight that is a product of nonnegative Cayley numbers and of values of the profile at its cut points, so raising a nonnegative profile raises every weight. The statement is used in the proof of `Parking.Lam_first_cell` to pass from the profile $(k-1)/(N-1-s)$, which is what remains of the threshold profile for the threshold $k-1$ after the first unit cell has been removed, to the larger threshold profile $k/(N-s)$.

## Proof

It suffices to show $V_q(m;f) \le V_q(m;g)$ for every $q$, with the weights of `Parking.Vc`, and to sum over $1 \le q \le m$. This is proved by induction on $q$, for all $m$ at once. For $q = 0$ and $q = 1$ the two sides are equal (`Parking.Vc_one`). For $q + 2$ parts, `Parking.Vc_succ_succ` writes both sides as sums over $0 < s < m$, and the terms are compared one by one: $V_{q+1}(s;f) \le V_{q+1}(s;g)$ by the induction hypothesis, $f(s) \le g(s)$ by hypothesis, both left factors are nonnegative (`Parking.Vc_nonneg` and the hypothesis), and the common factor $a_{m-s}$ is nonnegative (`Parking.cay_nonneg`).

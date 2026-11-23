---
weight: step
short: last-cut recursion for the total composition weight
---
## Description

The total weight of the compositions of $m$ satisfies the recursion by the last cut: $\Lambda_m[f] = a_m + \sum_{0<s<m} \Lambda_s[f]\, f(s)\, a_{m-s}$.

## Statement

For every function $f : \mathbb{N} \to \mathbb{R}$ and every natural number $m$,

$$\Lambda_m[f] = a_m + \sum_{0 < s < m} \Lambda_s[f]\, f(s)\, a_{m-s},$$

where $\Lambda_m[f]$ is the total weight of the compositions of $m$ for the cut profile $f$ (`Parking.Lam`) and $a_p = p^{p-1}/p!$, $a_0 = 0$ (`Parking.cay`).

## Explanation

A composition of $m$ either has one part, of weight $a_m$, or it has a last cut $s$; in the second case it consists of an arbitrary composition of $s$, the cut at $s$, and a last part of size $m - s$. The recursion is the one of `Parking.Vc_succ_succ` summed over the number of parts. It is used in `Parking.dq_frozen` to prove the knot identity between the frozen polynomials of two consecutive columns.

## Proof

For $m = 0$ both sides are $0$. For $m \ge 1$, write $\Lambda_m[f] = \sum_{q=1}^{m} V_q(m;f)$ with the weights of `Parking.Vc` and separate the term $q = 1$, which is $a_m$ by `Parking.Vc_one`. Each remaining term $V_{q+2}(m;f)$, $0 \le q \le m - 2$, is $\sum_{0<s<m} V_{q+1}(s;f)\, f(s)\, a_{m-s}$ by `Parking.Vc_succ_succ`. Exchanging the two summations gives, for each $s$, the factor $\sum_{q=0}^{m-2} V_{q+1}(s;f)$. Since $s \le m - 1$ and $V_{q'}(s;f) = 0$ for $q' > s$ (`Parking.Vc_eq_zero_of_lt`), this sum is $\Lambda_s[f]$.

---
weight: unit
short: two marked cut points count the pairs of cut points
---
## Description

For every cut profile $f$ and every $m$: $\Lambda^{(2)}_m[f] = \sum_{q=1}^{m} \tfrac12 (q-1)(q-2)\, V_q(m;f)$. The total weight of the compositions of $m$ with two marked cut points is the sum of the weights of the compositions, each multiplied by the number of pairs of its cut points.

## Statement

Let $f : \mathbb{N} \to \mathbb{R}$ be a function and $m$ a natural number. Then

$$\Lambda^{(2)}_m[f] \;=\; \sum_{q=1}^{m} \frac{(q-1)(q-2)}{2}\; V_q(m;f),$$

where $\Lambda^{(2)}_m[f]$ is the total weight of the compositions of $m$ with two marked cut points (`Parking.Lam2`), and $V_q(m;f)$ is the total weight of the compositions of $m$ with exactly $q$ parts for the cut profile $f$ (`Parking.Vc`).

## Explanation

A composition with $q$ parts has $q - 1$ cut points and therefore $\binom{q-1}{2} = \tfrac12 (q-1)(q-2)$ pairs of cut points. The statement is the counterpart of `Parking.Lam1_eq_sum` for two marks, and the proof is the same argument with $\Lambda^{(1)}$ in the place of the unmarked total $\Lambda$.

The statement is used in the curve increase only: in `Parking.sum_qq_Vc`, and, for the constant profile $1$, in the closed form of the threefold convolution $\kappa_3$ of the Poisson mass (`Parking.kc3_eq`).

In Lean the right side is a sum over `Finset.Icc 1 m` of `((q : ℝ) - 1) * ((q : ℝ) - 2) / 2 * Vc f q m`.

## Proof

In Lean the statement is the instance $c(q) = q$, $d(q) = \tfrac12 q(q-1)$ of the marking lemma that is proved in the record of `Parking.Lam1_eq_sum`; these functions satisfy $d(0) = 0$ and $d(q+1) = d(q) + c(q)$. Written out for this instance, the argument is the following induction, which uses only public statements.

Fix $f$ and write $V_q(m) = V_q(m;f)$, $\Lambda^{(1)}_m = \Lambda^{(1)}_m[f]$, $\Lambda^{(2)}_m = \Lambda^{(2)}_m[f]$. We prove the statement by strong induction on $m$.

By `Parking.Lam2_last`,

$$\Lambda^{(2)}_m = \sum_{0<s<m} \bigl(\Lambda^{(1)}_s + \Lambda^{(2)}_s\bigr)\; f(s)\; a_{m-s}, \qquad a_p = p^{p-1}/p! .$$

For $s < m$, `Parking.Lam1_eq_sum` gives $\Lambda^{(1)}_s = \sum_{p=1}^{s} (p-1)\, V_p(s)$ and the induction hypothesis gives $\Lambda^{(2)}_s = \sum_{p=1}^{s} \tfrac12 (p-1)(p-2)\, V_p(s)$. Since $(p-1) + \tfrac12 (p-1)(p-2) = \tfrac12 p(p-1)$,

$$\Lambda^{(2)}_m = \sum_{0<s<m} \Bigl(\sum_{p=1}^{s} \frac{p(p-1)}{2}\, V_p(s)\Bigr) f(s)\; a_{m-s}.$$

Now consider the right side of the statement. Its term $q = 1$ vanishes. For $q = p + 1$ with $p \ge 1$, `Parking.Vc_succ_succ` gives $V_{p+1}(m) = \sum_{0<s<m} V_p(s)\, f(s)\, a_{m-s}$, and the coefficient of this term is $\tfrac12 p(p-1)$. Hence

$$\sum_{q=1}^{m} \frac{(q-1)(q-2)}{2}\, V_q(m) = \sum_{0<s<m} \Bigl(\sum_{p=1}^{m-1} \frac{p(p-1)}{2}\, V_p(s)\Bigr) f(s)\; a_{m-s}.$$

In the inner sum the terms with $p > s$ vanish, because a composition of $s$ has at most $s$ parts (`Parking.Vc_eq_zero_of_lt`), so the inner sum equals the inner sum of the previous display. The two sides agree.

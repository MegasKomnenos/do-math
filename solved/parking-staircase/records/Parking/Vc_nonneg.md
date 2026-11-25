---
weight: step
short: nonnegativity of the composition weights
---
## Description

For a cut profile that is nonnegative at the cut points $1, \dots, m-1$, the weight $V_q(m;f)$ of the compositions of $m$ with $q$ parts is nonnegative.

## Statement

Let $f : \mathbb{N} \to \mathbb{R}$ and let $m$ be a natural number such that $f(s) \ge 0$ for every $s$ with $0 < s < m$. Then $V_q(m;f) \ge 0$ for every natural number $q$, where $V_q(m;f)$ is defined in `Parking.Vc`.

## Explanation

Each composition has a weight that is a product of Cayley numbers, which are nonnegative, and of values of $f$ at its cut points. The statement is the sign information that the inequalities between the weights rest on: it is used for the terms of the curvature sum in `Parking.curvSum_pos` and for the signs of $T_{m,q}$ in `Parking.Tq_nonneg`.

## Proof

By induction on $q$, for all $m$ at once. For $q = 0$ the value is $0$. For $q = 1$ it is $a_m \ge 0$ by `Parking.Vc_one` and `Parking.cay_nonneg`. For $q + 2$ parts, `Parking.Vc_succ_succ` gives $V_{q+2}(m;f) = \sum_{0<s<m} V_{q+1}(s;f)\, f(s)\, a_{m-s}$. For each $s$ the profile is nonnegative on the cut points $0 < u < s$, which are among those below $m$, so $V_{q+1}(s;f) \ge 0$ by the induction hypothesis. The other two factors are nonnegative by the hypothesis on $f$ and by `Parking.cay_nonneg`.

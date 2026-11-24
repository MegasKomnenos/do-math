---
weight: unit
short: second factorial moment of the number of parts
---
## Description

For every cut profile $f$ and every $m$: $\sum_{q=1}^{m} q(q-1)\, V_q(m;f) = 2\Lambda^{(1)}_m[f] + 2\Lambda^{(2)}_m[f]$. The compositions of $m$, each counted with its weight times $q(q-1)$ for its number $q$ of parts, have twice the total weight of the compositions with one or two marked cut points.

## Statement

Let $f : \mathbb{N} \to \mathbb{R}$ be a function and $m$ a natural number. Then

$$\sum_{q=1}^{m} q\,(q-1)\; V_q(m;f) \;=\; 2\,\Lambda^{(1)}_m[f] + 2\,\Lambda^{(2)}_m[f],$$

where $V_q(m;f)$ is the total weight of the compositions of $m$ with exactly $q$ parts for the cut profile $f$ (`Parking.Vc`), and $\Lambda^{(1)}_m[f]$, $\Lambda^{(2)}_m[f]$ are the total weights of the compositions of $m$ with one and with two marked cut points (`Parking.Lam1`, `Parking.Lam2`).

## Explanation

The identity behind the statement is $\tfrac12 q(q-1) = (q-1) + \tfrac12 (q-1)(q-2)$. It has a direct meaning. A composition of $m$ with $q$ parts has $q - 1$ cut points, and together with the end point $m$ of the segment these are $q$ points. A pair of these $q$ points either consists of the end point and one cut point, in $q - 1$ ways, or of two cut points, in $\binom{q-1}{2}$ ways. So $\Lambda^{(1)} + \Lambda^{(2)}$ counts each composition with its weight times the number $\binom q2$ of pairs among its $q$ points.

This is the form in which marked cut points enter the curve increase. Let $\Lambda_m(y;N)$ denote the total weight of the compositions of $m$ for the threshold profile $s \mapsto y/(N-s)$ (`Parking.thr`). Every cut point contributes one factor $y$, so $y\,\Lambda_m(y;N) = \sum_q y^q\, V_q$, where $V_q$ is the weight of the compositions with $q$ parts for the profile $s \mapsto 1/(N-s)$. For $m \le N$ this is a polynomial in $y$ with nonnegative coefficients, in which a composition with $q$ parts contributes to the coefficient of $y^q$; the exponent $q$ counts the $q$ points just described. The second difference of $y^q$ at a real point $y = k > 0$, multiplied by $k^2$, is at least $q(q-1)\,k^q$, and the present statement turns the resulting sum $\sum_q q(q-1)\, k^q\, V_q$ into marked compositions. This is carried out in the proof of `Parking.curv_ge_pair`, the one place where the statement is used.

When $f$ is nonnegative and the total weight $\Lambda_m[f]$ is positive, the left side divided by $\Lambda_m[f]$ is the second factorial moment $\mathbb{E}[Q(Q-1)]$ of the number of parts $Q$ of a composition drawn with probability proportional to its weight.

In Lean the left side is a sum over `Finset.Icc 1 m` of `(q : ℝ) * ((q : ℝ) - 1) * Vc f q m`.

## Proof

By `Parking.Lam1_eq_sum`, $\Lambda^{(1)}_m[f] = \sum_{q=1}^{m} (q-1)\, V_q(m;f)$, and by `Parking.Lam2_eq_sum`, $\Lambda^{(2)}_m[f] = \sum_{q=1}^{m} \tfrac12 (q-1)(q-2)\, V_q(m;f)$. Multiplying both by $2$ and adding term by term gives the statement, since $2(q-1) + (q-1)(q-2) = q(q-1)$.

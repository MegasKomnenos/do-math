---
weight: step
short: no composition of m has more than m parts
---
## Description

The weight of the compositions of $m$ with $q$ parts vanishes when $q > m$: $V_q(m;f) = 0$.

## Statement

For every function $f : \mathbb{N} \to \mathbb{R}$ and all natural numbers $q$ and $m$ with $m < q$, $V_q(m;f) = 0$, where $V_q(m;f)$ is the total weight of the compositions of $m$ with $q$ parts for the cut profile $f$ (`Parking.Vc`).

## Explanation

A composition of $m$ into positive parts has at most $m$ parts, so the sum that defines $V_q(m;f)$ is empty for $q > m$. In the recursive definition this has to be proved, and it also covers the conventional values: $V_0(m;f) = 0$ and $V_1(0;f) = a_0 = 0$. The statement is what allows the sums over the number of parts to be written over any range that contains $1, \dots, m$, for instance when the summations over the last cut and over the number of parts are exchanged in the proof of `Parking.Lam_last`.

## Proof

By induction on $q$, for all $m$ at once. For $q = 0$ the value is $0$ by definition. For $q = 1$ the hypothesis gives $m = 0$, and $V_1(0;f) = a_0 = 0$ by `Parking.Vc_one` and `Parking.cay_zero`. For $q + 2$ parts, `Parking.Vc_succ_succ` writes $V_{q+2}(m;f)$ as a sum over $0 < s < m$ of terms with the factor $V_{q+1}(s;f)$. Since $s < m < q + 2$, we have $s < q + 1$, so this factor vanishes by the induction hypothesis.

---
weight: step
short: last-part recursion for the composition weights
---
## Description

The weight of the compositions of $m$ with $q+2$ parts is obtained from the weights with $q+1$ parts by removing the last part: $V_{q+2}(m;f) = \sum_{0<s<m} V_{q+1}(s;f)\,f(s)\,a_{m-s}$.

## Statement

For every function $f : \mathbb{N} \to \mathbb{R}$ and all natural numbers $q$ and $m$,

$$V_{q+2}(m;f) = \sum_{0 < s < m} V_{q+1}(s;f)\, f(s)\, a_{m-s},$$

where $V_q(m;f)$ is the total weight of the compositions of $m$ with $q$ parts for the cut profile $f$ (`Parking.Vc`) and $a_p = p^{p-1}/p!$ (`Parking.cay`).

## Explanation

A composition of $m$ with at least two parts has a last cut $s$. Before it stands a composition of $s$ with one part fewer, the cut contributes $f(s)$, and the last part contributes $a_{m-s}$. The statement is the third clause of the recursive definition of `Parking.Vc`, and it is the form in which the definition is used in the proofs of `Parking.Tq_ratio`, `Parking.Vc_ratio_le` and `Parking.Vc_thr_ratio_ge`.

## Proof

This is the clause for $q + 2$ parts of the definition of $V_q(m;f)$.

---
weight: unit
short: total weight of the compositions of m
---
## Description

$\Lambda_m[f]$ is the total weight of all compositions of $m$ for the cut profile $f$: the sum over $q$ of the weights $V_q(m;f)$ of the compositions with exactly $q$ parts.

## Statement

For a function $f : \mathbb{N} \to \mathbb{R}$ and a natural number $m$,

$$\Lambda_m[f] = \sum_{q=1}^{m} V_q(m;f),$$

where $V_q(m;f)$ is the total weight of the compositions of $m$ with $q$ parts defined in `Parking.Vc`. Equivalently, $\Lambda_m[f]$ is the sum, over all sets $S \subseteq \{1, \dots, m-1\}$ of cut points, of the product of the Cayley numbers $a_p = p^{p-1}/p!$ of the parts that $S$ cuts out of a segment of length $m$ times $\prod_{s \in S} f(s)$. In particular $\Lambda_0[f] = 0$.

## Explanation

For a nonnegative profile, $\Lambda_m[f]$ is the normalising constant of the law of the number of parts described in `Parking.Vc`. For the threshold profile $\lambda^{y,N}(s) = y/(N-s)$ (`Parking.thr`) we write $\Lambda_m(y;N) = \Lambda_m[\lambda^{y,N}]$ and call it a chain sum. Chain sums are what the parking problem produces: the frozen polynomial `Parking.Kpoly` is a combination of the chain sums $\Lambda_m(y;N)$, $1 \le m \le n-k$, and the two boundary terms of `Parking.dq_frozen` are chain sums of the lengths $r+1$ and $r$. For the constant profile the total is $\tau_m(h)$ (`Parking.tau`).

The sum stops at $q = m$ because a composition of $m$ has at most $m$ parts (`Parking.Vc_eq_zero_of_lt`). The total satisfies two recursions, by the last cut (`Parking.Lam_last`) and by the first part (`Parking.Lam_first`); the first-part recursion is the one that matches the iteration of the Volterra equation in `Parking.dq_frozen`. In Lean the definition is `Lam f m`.

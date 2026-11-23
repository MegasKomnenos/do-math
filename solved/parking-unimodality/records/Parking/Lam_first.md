---
weight: step
short: first-part recursion for the total composition weight
---
## Description

The total weight of the compositions of $m$ satisfies the recursion by the first part: $\Lambda_m[f] = a_m + \sum_{0<g<m} a_g\, f(g)\, \Lambda_{m-g}[f(g+\cdot)]$, where the remaining composition sees the profile shifted by $g$.

## Statement

For every function $f : \mathbb{N} \to \mathbb{R}$ and every natural number $m$,

$$\Lambda_m[f] = a_m + \sum_{0 < g < m} a_g\, f(g)\, \Lambda_{m-g}[f(g+\cdot)],$$

where $\Lambda_m[f]$ is the total weight of the compositions of $m$ for the cut profile $f$ (`Parking.Lam`), $f(g+\cdot)$ is the profile $s \mapsto f(g+s)$, and $a_p = p^{p-1}/p!$, $a_0 = 0$ (`Parking.cay`).

## Explanation

A composition of $m$ either has one part or begins with a part of size $g < m$, followed by a cut at $g$ and a composition of the remaining segment of length $m - g$. The cuts of the remaining composition lie at the positions $g + s$ of the original segment, which is why its profile is shifted. Unlike the recursion by the last cut (`Parking.Lam_last`), this one changes the profile, and for the threshold profile the change is transparent: $\lambda^{y,N}(g + s) = y/(N - g - s) = \lambda^{y,N-g}(s)$, so removing a first part of size $g$ lowers the top size from $N$ to $N - g$. In this form the recursion is the iteration step of the Volterra equation in `Parking.dq_frozen`. It is also the starting point of the removal of the first unit cell in `Parking.Lam_first_cell`, where the law of the first part is what the correlation inequality compares.

## Proof

The statement follows from the corresponding recursion for a fixed number of parts: for all $q$ and $m$,

$$V_{q+2}(m;f) = \sum_{0<g<m} a_g\, f(g)\, V_{q+1}(m-g; f(g+\cdot)),$$

with the weights of `Parking.Vc`. This is proved by induction on $q$. For $q = 0$ it is `Parking.Vc_succ_succ` with $V_1(s;f) = a_s$ and $V_1(m-s; f(s+\cdot)) = a_{m-s}$ (`Parking.Vc_one`). For the step, `Parking.Vc_succ_succ` writes $V_{q+3}(m;f)$ as $\sum_{0<s<m} V_{q+2}(s;f)\, f(s)\, a_{m-s}$, and the induction hypothesis expands $V_{q+2}(s;f)$ as $\sum_{0<g<s} a_g\, f(g)\, V_{q+1}(s-g; f(g+\cdot))$. Exchanging the summations over $s$ and $g$ and substituting $s = g + s'$ with $0 < s' < m - g$ turns the inner sum into

$$\sum_{0<s'<m-g} V_{q+1}(s'; f(g+\cdot))\, f(g+s')\, a_{m-g-s'} = V_{q+2}(m-g; f(g+\cdot)),$$

again by `Parking.Vc_succ_succ`, which is the claim for $q + 1$.

For the totals, the case $m = 0$ is trivial. For $m \ge 1$ separate the term $q = 1$ of $\Lambda_m[f] = \sum_{q=1}^{m} V_q(m;f)$, which is $a_m$, apply the recursion above to each remaining term and exchange the summations over $q$ and $g$. For each $g$ the sum over the number of parts is $\Lambda_{m-g}[f(g+\cdot)]$, because $m - g \le m - 1$ and the weights vanish beyond $m - g$ parts (`Parking.Vc_eq_zero_of_lt`).

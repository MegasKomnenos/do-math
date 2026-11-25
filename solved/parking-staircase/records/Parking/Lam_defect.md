---
weight: unit
short: first violating point identity
---
## Description

For every cut profile $f$ and every $m \ge 1$: $\operatorname{ren}(m) - \Lambda_m[f] = \sum_{0<s<m} \operatorname{ren}(m-s)\,(1 - f(s))\,\Lambda_s[f]$, where $\operatorname{ren}(m) = m^m/m!$ and $\Lambda_m[f]$ is the total weight of the compositions of $m$ for the profile $f$.

## Statement

Let $f : \mathbb{N} \to \mathbb{R}$ be a function and $m \ge 1$ a natural number. Then

$$\operatorname{ren}(m) - \Lambda_m[f] \;=\; \sum_{0 < s < m} \operatorname{ren}(m-s)\;\bigl(1 - f(s)\bigr)\;\Lambda_s[f],$$

where $\operatorname{ren}(n) = n^n/n!$ (`Parking.ren`) and $\Lambda_m[f]$ is the total weight of the compositions of $m$ for the cut profile $f$ (`Parking.Lam`).

## Explanation

**What it says.** The number $\operatorname{ren}(m)$ is the total weight of the compositions of $m$ when every cut has the weight $1$; this is the case $f = 1$ of the statement, recorded as `Parking.Lam_one`. The statement expresses the amount by which the total weight for a general profile $f$ falls short of $\operatorname{ren}(m)$, as a sum over one cut point $s$ in which the factor $1 - f(s)$ occurs once.

**Where it comes from.** For a set $S = \{s_1 < \dots < s_j\}$ of cut points,

$$1 - \prod_{i=1}^{j} f(s_i) \;=\; \sum_{i=1}^{j} \bigl(1 - f(s_i)\bigr) \prod_{l < i} f(s_l),$$

a telescoping sum. In the term of index $i$ the cut points before $s_i$ carry the factors of $f$, the point $s_i$ carries $1 - f(s_i)$, and the cut points after $s_i$ carry the factor $1$. Multiply by the product of the Cayley coefficients of the parts and sum over all $S$, grouping the terms by $s = s_i$: the part of the composition before $s$ is a composition of $s$ weighted with the profile $f$, of total weight $\Lambda_s[f]$, and the part after $s$ is a composition of $m - s$ weighted with the profile $1$, of total weight $\operatorname{ren}(m-s)$. This is the right side. When $0 \le f \le 1$, one may read $f(s)$ as the probability that the cut point $s$ passes a test, independently of the other cut points; then $\Lambda_m[f]/\operatorname{ren}(m)$ is the probability that all cut points of a random composition pass, and the identity sorts the compositions with a failing cut point by the first such point. This reading gives the identity its name. The statement itself needs no assumption on the sign or the size of $f$.

**What it is for.** The inequalities of Jensen type of this module (`Parking.Lam_tangent`, `Parking.Lam_jensen`) bound a total weight $\Lambda$ from below. The curve increase also needs an upper bound, for the boundary term of the pair–impulse criterion `Parking.dq_pos_of_pair`, which is the total weight $\Lambda_R(k+1;k+R)$ of the compositions of $R$ for the cut factors $(k+1)/(k+R-s)$. The present identity makes this possible. For a profile with values in $[0,1]$ it writes $\operatorname{ren}(m) - \Lambda_m[f]$ as a combination of the shorter totals $\Lambda_s[f]$ with nonnegative coefficients, so lower bounds for the $\Lambda_s[f]$ give an upper bound for $\Lambda_m[f]$. This is how `Parking.impulse_le` is proved.

**How the proof goes.** The Lean proof does not expand into sets of cut points. Both $\operatorname{ren}$ and $\Lambda[f]$ satisfy a recursion on the last part with the kernel $a_p = p^{p-1}/p!$, and the difference of the two recursions is an equation for $w = \operatorname{ren} - \Lambda[f]$ of the same kind, which is solved by the fact that $\operatorname{ren}$ is the resolvent of the kernel.

In Lean the right side is the sum over `Finset.Ioo 0 m` of `ren (m - s) * ((1 - f s) * Lam f s)`. The hypothesis $m \ge 1$ is needed: for $m = 0$ the left side is $\operatorname{ren}(0) - \Lambda_0[f] = 1$ and the right side is an empty sum.

## Proof

Write $a_p = p^{p-1}/p!$ with $a_0 = 0$ (`Parking.cay`). Two facts about the sequence $\operatorname{ren}$ are used.

*The renewal recursion in last-part form.* For every $m \ge 1$,

$$\operatorname{ren}(m) = a_m + \sum_{0<s<m} a_{m-s}\, \operatorname{ren}(s). \tag{1}$$

This is `Parking.ren_conv`, which states $\sum_{j=0}^{m} a_j \operatorname{ren}(m-j) = \operatorname{ren}(m)$ for $m \ge 1$: the term $j = 0$ vanishes because $a_0 = 0$, the term $j = m$ is $a_m \operatorname{ren}(0) = a_m$, and the remaining terms become the sum in (1) under the substitution $s = m - j$.

*The resolvent identity.* For every function $g : \mathbb{N} \to \mathbb{R}$ and all natural numbers $t_0$ and $M$,

$$\sum_{t_0<t<M} a_{M-t}\,\Bigl(g(t) + \sum_{t_0<c<t} \operatorname{ren}(t-c)\, g(c)\Bigr) = \sum_{t_0<c<M} \operatorname{ren}(M-c)\; g(c). \tag{2}$$

To see this, expand the left side and exchange the two summations in the double sum over $t_0 < c < t < M$. For a fixed $c$ the coefficient of $g(c)$ is

$$a_{M-c} + \sum_{c<t<M} a_{M-t}\, \operatorname{ren}(t-c) = a_{M-c} + \sum_{0<s<M-c} a_{M-c-s}\, \operatorname{ren}(s) = \operatorname{ren}(M-c),$$

where the first equality is the substitution $t = c + s$ and the second is (1) at $M - c \ge 1$.

*The induction.* Put $g(s) = (1 - f(s))\,\Lambda_s[f]$ and $w(m) = \operatorname{ren}(m) - \Lambda_m[f]$. The claim is $w(m) = \sum_{0<s<m} \operatorname{ren}(m-s)\, g(s)$ for $m \ge 1$, and we prove it by strong induction on $m$. The last-cut recursion `Parking.Lam_last` gives $\Lambda_m[f] = a_m + \sum_{0<s<m} \Lambda_s[f]\, f(s)\, a_{m-s}$. Subtracting it from (1),

$$w(m) = \sum_{0<s<m} a_{m-s}\,\bigl(\operatorname{ren}(s) - f(s)\,\Lambda_s[f]\bigr) = \sum_{0<s<m} a_{m-s}\,\bigl(g(s) + w(s)\bigr),$$

because $\operatorname{ren}(s) - f(s)\Lambda_s[f] = (1 - f(s))\Lambda_s[f] + (\operatorname{ren}(s) - \Lambda_s[f])$. For $0 < s < m$ the induction hypothesis gives $w(s) = \sum_{0<c<s} \operatorname{ren}(s-c)\, g(c)$. Inserting this, the right side is the left side of (2) with $t_0 = 0$ and $M = m$, and (2) gives $w(m) = \sum_{0<c<m} \operatorname{ren}(m-c)\, g(c)$.

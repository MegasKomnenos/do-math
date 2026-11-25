---
weight: unit
short: reflection invariance of the composition sums
---
## Description

Reading a composition backwards does not change the weight of its parts, so the cut profile may be reflected: $V_q(m;\,s \mapsto f(m-s)) = V_q(m;f)$ for all $q$, $m$ and every profile $f$.

## Statement

For a function $f : \mathbb{N} \to \mathbb{R}$ and natural numbers $q$, $m$ let $V_q(m;f)$ be the total weight of the compositions of $m$ with exactly $q$ parts, in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and a cut at the position $s$ weighs $f(s)$ (`Parking.Vc`, `Parking.cay`). Then for all natural numbers $q$, $m$ and every $f$,

$$V_q\bigl(m;\,s \mapsto f(m-s)\bigr) = V_q(m;f).$$

## Explanation

A composition of $m$ with the cut points $s_1 < \dots < s_{q-1}$, read from the right end, is the composition with the cut points $m - s_{q-1} < \dots < m - s_1$. It has the same parts in the reverse order, so the same product of the weights $a_p$, and its cut factors for the profile $f$ are those of the original composition for the reflected profile $s \mapsto f(m-s)$. The reversal is a bijection of the compositions of $m$ with $q$ parts, which gives the identity.

The identity is what makes symmetric information about a profile usable. In `Parking.Vc_sum_pow_le` it is combined with the log-convexity `Parking.Vc_rpow_mul_rpow_le` at the exponents $\frac12, \frac12$: a profile $g$ can be replaced from below by the geometric mean of $g$ and its reflection, and for the profiles of the chain sums that geometric mean is bounded from below by a constant, because the sum of the two denominators $N - s$ and $N - (m - s)$ does not depend on $s$.

In Lean $m - s$ is the truncated subtraction of natural numbers; on the cut points $0 < s < m$, which are the only points where the profile is read, it is the ordinary one. The statement holds for all $q$ and $m$, including $q = 0$ and $q > m$, where both sides are $0$.

## Proof

The Lean proof does not construct the bijection. It is an induction on $q$, for all $m$ and $f$ at once, that removes the last part on one side and the first part on the other.

**The first-part recursion.** The definition of $V_q$ removes the last part (`Parking.Vc_succ_succ`): $V_{q+2}(m;f) = \sum_{0<s<m} V_{q+1}(s;f)\,f(s)\,a_{m-s}$. The proof needs the same with the first part removed: for all $q$, $m$, $f$,

$$V_{q+2}(m;f) = \sum_{0<g<m} a_g\,f(g)\,V_{q+1}\bigl(m-g;\,f(g+\cdot)\bigr), \tag{F}$$

where $f(g+\cdot)$ is the shifted profile $u \mapsto f(g+u)$. This is proved by induction on $q$ for all $m$. For $q = 0$ it is the last-part recursion, since $V_1(s;f) = a_s$ and $V_1(m-s;\cdot) = a_{m-s}$ (`Parking.Vc_one`). For the step, remove the last part of $V_{q+3}(m;f)$ and apply (F) to each $V_{q+2}(s;f)$:

$$V_{q+3}(m;f) = \sum_{0<s<m}\;\sum_{0<g<s} a_g\,f(g)\,V_{q+1}\bigl(s-g;\,f(g+\cdot)\bigr)\,f(s)\,a_{m-s}.$$

Exchange the two sums, so that $g$ runs over $0 < g < m$ and $s$ over $g < s < m$, and substitute $s = g + u$ with $0 < u < m - g$. The inner sum becomes $\sum_{0<u<m-g} V_{q+1}(u;f(g+\cdot))\,f(g+u)\,a_{(m-g)-u}$, which is $V_{q+2}(m-g;f(g+\cdot))$ by the last-part recursion for the shifted profile.

**The induction.** For $q = 0$ both sides are $0$, and for $q = 1$ both are $a_m$. For $q + 2$, write $\tilde f(s) = f(m-s)$. Removing the last part on the left,

$$V_{q+2}(m;\tilde f) = \sum_{0<s<m} V_{q+1}(s;\tilde f)\,f(m-s)\,a_{m-s}.$$

On the right, apply (F) and reflect the summation index, $g = m - s$ (a sum over $0 < g < m$ is unchanged by this substitution):

$$V_{q+2}(m;f) = \sum_{0<s<m} a_{m-s}\,f(m-s)\,V_{q+1}\bigl(s;\,f(m-s+\cdot)\bigr).$$

It remains to see $V_{q+1}(s;\tilde f) = V_{q+1}(s;f(m-s+\cdot))$ for $0 < s < m$. The induction hypothesis at $(q+1, s)$ for the profile $h = f(m-s+\cdot)$ gives $V_{q+1}(s;\,u \mapsto h(s-u)) = V_{q+1}(s;h)$. At a cut point $0 < u < s$ we have $h(s-u) = f(m-s+s-u) = f(m-u) = \tilde f(u)$, and $V_{q+1}(s;\cdot)$ depends on the profile at these points only (`Parking.Vc_congr`). So the left side is $V_{q+1}(s;\tilde f)$, and the two sums agree term by term.

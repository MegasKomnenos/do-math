---
weight: unit
short: weight of the compositions with a given number of parts
---
## Description

For a real function $f$ on the natural numbers (a cut profile), $V_q(m;f)$ is the total weight of the compositions of $m$ with exactly $q$ parts, where a part of size $p$ weighs $a_p = p^{p-1}/p!$ and a cut at the position $s$ weighs $f(s)$.

## Statement

Let $a_p = p^{p-1}/p!$ for $p \ge 1$ and $a_0 = 0$ (the Cayley numbers, `Parking.cay`). For a function $f : \mathbb{N} \to \mathbb{R}$ and natural numbers $q$ and $m$, the real number $V_q(m;f)$ is defined by recursion on $q$:

$$V_0(m;f) = 0, \qquad V_1(m;f) = a_m, \qquad V_{q+2}(m;f) = \sum_{0 < s < m} V_{q+1}(s;f)\, f(s)\, a_{m-s}.$$

Unfolding the recursion gives, for $q \ge 1$,

$$V_q(m;f) = \sum_{0 = s_0 < s_1 < \dots < s_{q-1} < s_q = m} \ \prod_{i=1}^{q} a_{s_i - s_{i-1}} \ \prod_{i=1}^{q-1} f(s_i).$$

## Explanation

A composition of $m$ with $q$ parts is a way of cutting a segment of length $m$ at $q-1$ of its interior integer points $1, \dots, m-1$. The chosen points $s_1 < \dots < s_{q-1}$ are the cut points, and the parts are the lengths $s_i - s_{i-1}$ of the pieces, with $s_0 = 0$ and $s_q = m$. The weight of a composition for the cut profile $f$ is the product of $a_p$ over its parts $p$ times the product of $f(s)$ over its cut points $s$. The recursion of the definition removes the last part: a composition with $q+2$ parts is a composition of some $s < m$ with $q+1$ parts, followed by a cut at $s$ and a last part of size $m - s$.

Compositions enter the library at this point, and the reason is the following. In the range of rows that this part of the argument works in, the normalised number of parking functions with all displacements below a threshold $y$ satisfies a linear equation of Volterra type whose kernel is $a_{M-t} \cdot y/t$ (see `Parking.Kpoly`). Solving that equation by iteration produces sums over decreasing chains of sizes $N > t_1 > t_2 > \dots$. Each jump from a size $t'$ down to a size $t$ contributes the Cayley number $a_{t'-t}$, and each size $t$ that the chain visits contributes the factor $y/t$. A chain is therefore a composition of the distance it covers, in which the jumps are the parts and the visited sizes are the cuts. The parts carry Cayley weights and the cuts carry a factor that depends on their position. The profile that arises in this way is the threshold profile `Parking.thr`. The constant profile gives the model with which the threshold profile is compared (`Parking.Tq`, `Parking.tau`), and the comparison results are proved for classes of profiles, which is why the definition takes an arbitrary $f$.

When $f$ is nonnegative, dividing $V_q(m;f)$ by the total $\Lambda_m[f] = \sum_q V_q(m;f)$ (`Parking.Lam`) gives a probability law for the number of parts $Q$ of a random composition of $m$. The later results of this part are comparisons between such laws for different profiles.

In Lean the definition is `Vc f q m`, with the arguments in the order profile, number of parts, size. The profile is a function on all natural numbers, but only its values at the cut points $0 < s < m$ matter (`Parking.Vc_congr`). The value for $q = 0$ is a convention, $V_1(0;f) = a_0 = 0$, and $V_q(m;f) = 0$ for $q > m$ (`Parking.Vc_eq_zero_of_lt`).

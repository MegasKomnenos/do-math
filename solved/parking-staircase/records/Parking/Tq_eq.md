---
weight: unit
short: the birthday law of the number of parts
---
## Description

The compositions of $m$ with exactly $q \ge 1$ parts, each part of size $p$ weighted by $a_p = p^{p-1}/p!$, have the total weight $T_{m,q} = a_m\, q\, P_{m,q}$, where $P_{m,q} = \prod_{i<q}(1 - i/m)$ is the birthday tail.

## Statement

For all natural numbers $m$ and $q$ with $q \ge 1$,

$$T_{m,q} \;=\; a_m\; q\; P_{m,q}.$$

Here $T_{m,q}$ is the total weight of the compositions of $m$ with exactly $q$ parts, where a composition is weighted by the product of the numbers $a_p$ over its parts (`Parking.Tq`; it is $V_q(m;f)$ of `Parking.Vc` for the constant cut profile $f = 1$); $a_p = p^{p-1}/p!$ for $p \ge 1$ and $a_0 = 0$ (`Parking.cay`); and $P_{m,q} = \prod_{i=0}^{q-1}(1 - i/m)$ is the birthday tail (`Parking.Pb`).

## Explanation

**What the identity says.** A composition of $m$ with $q$ parts is a sequence of positive integers $p_1, \dots, p_q$ with sum $m$, and $T_{m,q}$ is the sum of the products $a_{p_1}\cdots a_{p_q}$ over all of them. The identity evaluates this sum in closed form. For $1 \le q \le m$, inserting $a_m = m^{m-1}/m!$ and $P_{m,q} = m!/((m-q)!\,m^{q})$ gives

$$T_{m,q} \;=\; \frac{q\; m^{\,m-q-1}}{(m-q)!}.$$

For instance $T_{m,1} = a_m$, the single composition with one part, and $T_{m,m} = 1$, the single composition into $m$ parts of size $1$, each of weight $a_1 = 1$. For $q > m \ge 1$ both sides vanish: there is no composition (`Parking.Vc_eq_zero_of_lt`) and $P_{m,q} = 0$ (`Parking.Pb_eq_zero`). For $m = 0$ both sides vanish because $a_0 = 0$.

**The birthday law.** This identity is the reason why the birthday problem enters the library. Let $m \ge 1$. Summing over $q$ and using $\sum_{q=1}^{m} q\,P_{m,q} = m$ (`Parking.Pb_moment` with $g = 1$), the total weight of all compositions of $m$ is $m\,a_m$. Draw a composition of $m$ with probability proportional to its weight and let $Q$ be its number of parts. Then

$$\Pr(Q = q) \;=\; \frac{T_{m,q}}{m\,a_m} \;=\; \frac{q}{m}\,P_{m,q} \;=\; P_{m,q} - P_{m,q+1}, \qquad\text{so}\qquad \Pr(Q \ge j) = P_{m,j},$$

where the last equality of the first formula is `Parking.Pb_succ`. This is the law of the number of balls that can be thrown uniformly into $m$ boxes before one falls into an occupied box, as the record of `Parking.Pb` explains. Its mean is $s_m$ (`Parking.sbirth`), and the ratio of its third to its second factorial moment is $D_m$ (`Parking.Dbirth`, `Parking.Dbirth_spec`).

**What rests on it.** The later modules compare sums over compositions whose cuts carry weights that depend on the position of the cut (the threshold profile `Parking.thr`) with sums in which every cut carries the same weight $h$. In the second case the compositions with $q$ parts have the total weight $T_{m,q}\,h^{q-1} = a_m\,q\,P_{m,q}\,h^{q-1}$, so the total $\tau_m(h)$ (`Parking.tau`) and the mean number of cuts $\mu_m(h)$ (`Parking.muh`) are explicit sums of birthday tails. This is how `Parking.Dbirth_spec` and the inequality `Parking.mu0_le_muh` are proved: each is reduced by the present identity to a statement about the numbers $P_{m,j}$.

**Why it holds.** The identity is equivalent to the ratio $q\,m\,T_{m,q+1} = (q+1)(m-q)\,T_{m,q}$, which is `Parking.Tq_ratio` and carries the combinatorial content. The sequence $q\,P_{m,q}$ has the same ratio, since $P_{m,q+1} = P_{m,q}\,(m-q)/m$, and the two sequences agree at $q = 1$.

## Proof

If $m = 0$, then $T_{0,q} = 0$ because $q > 0$ (`Parking.Vc_eq_zero_of_lt`: there is no composition of $m$ with more than $m$ parts), and the right-hand side is $0$ because $a_0 = 0$.

Let $m \ge 1$. We argue by induction on $q \ge 1$.

For $q = 1$: $T_{m,1} = a_m$ by `Parking.Vc_one`, and $P_{m,1} = 1$ by `Parking.Pb_one`.

For the step from $q = k$ to $q = k+1$, with $k \ge 1$: `Parking.Tq_ratio` gives

$$k\,m\,T_{m,k+1} \;=\; (k+1)(m-k)\,T_{m,k} \;=\; (k+1)(m-k)\;a_m\,k\,P_{m,k},$$

the second equality being the induction hypothesis. On the other side, `Parking.Pb_succ` gives $P_{m,k+1} = P_{m,k}(1 - k/m)$, hence $m\,P_{m,k+1} = (m-k)\,P_{m,k}$ and

$$k\,m\cdot a_m\,(k+1)\,P_{m,k+1} \;=\; (k+1)(m-k)\;a_m\,k\,P_{m,k}.$$

The two right-hand sides agree, and $k\,m \ne 0$, so $T_{m,k+1} = a_m\,(k+1)\,P_{m,k+1}$. The step does not assume $k < m$: for $k \ge m$ the factor $m - k$ or the tail $P_{m,k}$ vanishes and the same calculation applies.

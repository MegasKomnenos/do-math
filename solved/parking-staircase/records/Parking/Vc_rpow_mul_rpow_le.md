---
weight: unit
short: log-convexity of the composition sums in the cut profile
---
## Description

The weight $V_q(m;f)$ of the compositions of $m$ with $q$ parts is log-convex in the cut profile $f$: for profiles $a, b \ge 0$ on the cut points and $\alpha, \beta > 0$ with $\alpha + \beta = 1$, $V_q(m;a^\alpha b^\beta) \le V_q(m;a)^\alpha\,V_q(m;b)^\beta$.

## Statement

For a function $f : \mathbb{N} \to \mathbb{R}$ (a cut profile) and natural numbers $q$, $m$ let $V_q(m;f)$ be the total weight of the compositions of $m$ with exactly $q$ parts, in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and a cut at the position $s$ weighs $f(s)$ (`Parking.Vc`, `Parking.cay`).

Let $\alpha, \beta > 0$ be real numbers with $\alpha + \beta = 1$, let $q$ and $m$ be natural numbers, and let $a, b : \mathbb{N} \to \mathbb{R}$ satisfy $a(s) \ge 0$ and $b(s) \ge 0$ for all $0 < s < m$. Then

$$V_q\bigl(m;\,s \mapsto a(s)^\alpha\,b(s)^\beta\bigr) \;\le\; V_q(m;a)^\alpha\;V_q(m;b)^\beta .$$

## Explanation

**What it says.** Unfolding the definition, $V_q(m;f) = \sum \prod_i a_{s_i - s_{i-1}} \prod_i f(s_i)$, the sum running over the sequences $0 = s_0 < s_1 < \dots < s_q = m$ of cut points. As a function of the values $f(1), \dots, f(m-1)$ this is a polynomial with nonnegative coefficients, a sum of monomials. For such a function Hölder's inequality gives log-convexity along geometric interpolation: the monomial of the profile $a^\alpha b^\beta$ is the product of the $\alpha$-th power of the monomial of $a$ and the $\beta$-th power of the monomial of $b$, and a sum of products $x_i^\alpha y_i^\beta$ is at most $(\sum x_i)^\alpha (\sum y_i)^\beta$.

**What it is used for.** It carries two steps in the proof of `Parking.Vc_sum_pow_le`, the comparison of two profiles on which the diagonal step of the curvature sum (`Parking.curvSum_step`) rests.

- With $a = \mathbf 1$, the constant profile $1$: a profile $g \le w^\beta$ has $V_q(m;g) \le T_{m,q}^{1-\beta}\,V_q(m;w)^\beta$, where $T_{m,q} = V_q(m;\mathbf 1)$ (`Parking.Tq`). The profile of a position on the diagonal is at most a power of the profile of the position before it, and this turns the pointwise comparison into a comparison of the sums.
- With $\alpha = \beta = \frac12$ and $b$ the reflection $s \mapsto a(m-s)$ of $a$: together with `Parking.Vc_reverse` it gives $V_q(m;\sqrt{a \cdot a(m - \cdot)}) \le V_q(m;a)$, so a profile may be replaced from below by the geometric mean of itself and its reflection.

**The Lean form.** The statement is proved for all natural numbers $q$ and $m$, including $q = 0$ (where $V_0 = 0$ and the right side is $0^\alpha \cdot 0^\beta = 0$) and $q > m$ (where both sides vanish). The hypotheses on $a$ and $b$ are asked on the cut points $0 < s < m$ only, which are the only points at which $V_q(m;\cdot)$ reads a profile (`Parking.Vc_congr`); the powers are real powers of nonnegative numbers.

## Proof

The proof is an induction on $q$ along the recursion that defines $V_q$, the removal of the last part, for all $m$ at once. It uses Hölder's inequality for finite sums in the following form: for nonnegative real numbers $x_i$, $y_i$ and $\alpha, \beta > 0$ with $\alpha + \beta = 1$,

$$\sum_i x_i^\alpha\,y_i^\beta \;\le\; \Bigl(\sum_i x_i\Bigr)^{\alpha}\Bigl(\sum_i y_i\Bigr)^{\beta}. \tag{H}$$

This is the usual inequality $\sum u_i v_i \le (\sum u_i^{p})^{1/p}(\sum v_i^{p'})^{1/p'}$ with the conjugate exponents $p = 1/\alpha$, $p' = 1/\beta$ applied to $u_i = x_i^\alpha$, $v_i = y_i^\beta$ (Mathlib's `Real.inner_le_Lp_mul_Lq_of_nonneg`).

*$q = 0$.* The left side is $V_0 = 0$ and the right side is a product of two nonnegative numbers.

*$q = 1$.* By `Parking.Vc_one` all three sums equal $a_m \ge 0$, and $a_m = a_m^\alpha\,a_m^\beta$ because $\alpha + \beta = 1$.

*From $q + 1$ to $q + 2$.* Write $c = a^\alpha b^\beta$ for the interpolated profile. By `Parking.Vc_succ_succ`, for every profile $f$,

$$V_{q+2}(m;f) = \sum_{0<s<m} V_{q+1}(s;f)\,f(s)\,a_{m-s}.$$

Fix $0 < s < m$. The cut points of $s$ are cut points of $m$, so $a$ and $b$ are nonnegative there, the induction hypothesis applies at $(q+1, s)$, and $V_{q+1}(s;a)$, $V_{q+1}(s;b)$ are nonnegative (`Parking.Vc_nonneg`). Hence

$$V_{q+1}(s;c)\,c(s)\,a_{m-s} \;\le\; V_{q+1}(s;a)^\alpha\,V_{q+1}(s;b)^\beta \cdot a(s)^\alpha\,b(s)^\beta \cdot a_{m-s}^\alpha\,a_{m-s}^\beta = x_s^\alpha\,y_s^\beta,$$

with $x_s = V_{q+1}(s;a)\,a(s)\,a_{m-s}$ and $y_s = V_{q+1}(s;b)\,b(s)\,a_{m-s}$, both nonnegative. Summing over $s$ and applying (H),

$$V_{q+2}(m;c) \;\le\; \sum_{0<s<m} x_s^\alpha\,y_s^\beta \;\le\; \Bigl(\sum_s x_s\Bigr)^\alpha\Bigl(\sum_s y_s\Bigr)^\beta = V_{q+2}(m;a)^\alpha\;V_{q+2}(m;b)^\beta .$$

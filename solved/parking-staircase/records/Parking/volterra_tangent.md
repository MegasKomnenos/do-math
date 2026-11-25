---
weight: unit
short: tangent inequality for a Volterra equation with the Cayley kernel
---
## Description

If $r(M) = \kappa(M) + \sum_{t_0<t<M} a_{M-t}\, r(t)$ and $u(M) = \kappa(M) + \sum_{t_0<t<M} a_{M-t}\, e^{-x(t)}\, u(t)$ for $1 \le M \le B$, with $\kappa \ge 0$ and $a_p = p^{p-1}/p!$, then $e^{-\mu}\bigl((1+\mu)\, r(M) - \sum_{t_0<t<M} \operatorname{ren}(M-t)\, r(t)\, x(t)\bigr) \le u(M)$ for every real $\mu$ and $1 \le M \le B$, where $\operatorname{ren}(n) = n^n/n!$.

## Statement

Let $a_p = p^{p-1}/p!$ for $p \ge 1$ and $a_0 = 0$ (`Parking.cay`), and $\operatorname{ren}(n) = n^n/n!$ (`Parking.ren`). Let $t_0$ and $B$ be natural numbers and let $\kappa, r, u, x : \mathbb{N} \to \mathbb{R}$ be functions such that for every natural number $M$ with $1 \le M \le B$:

- $\kappa(M) \ge 0$;
- $r(M) = \kappa(M) + \sum_{t_0 < t < M} a_{M-t}\; r(t)$;
- $u(M) = \kappa(M) + \sum_{t_0 < t < M} a_{M-t}\; e^{-x(t)}\; u(t)$.

Then for every real number $\mu$ and every natural number $M$ with $1 \le M \le B$,

$$e^{-\mu}\,\Bigl((1+\mu)\; r(M) \;-\; \sum_{t_0 < t < M} \operatorname{ren}(M-t)\; r(t)\; x(t)\Bigr) \;\le\; u(M).$$

## Explanation

**The equations.** Several sequences of the curve increase satisfy an equation of the form $u(M) = \kappa(M) + \sum_{t_0<t<M} a_{M-t}\, w(t)\, u(t)$, in which the value at $M$ is expressed by the values at smaller arguments through the kernel $a_{M-t}$. This is a Volterra equation of the second kind in discrete form; we say that it has the Cayley kernel. The total weight $\Lambda_M[f]$ of the compositions of $M$ satisfies it with $\kappa = a$, $w = f$ and $t_0 = 0$ (remove the last part). The sequence $\operatorname{ren}$ satisfies it with $\kappa = a$ and $w = 1$. The environment $z^{(k)}_{M-1}$ of the threshold $k$ (`Parking.zr`), the normalised number of parking functions of length $M - 1$ with all displacements less than $k$, satisfies it for $M \le 2k+1$ with $w(t) = k/t$ and $t_0 = k$. The statement collects what follows from the form of the equation alone, when the weights are written as $w(t) = e^{-x(t)}$ and $r$ denotes the solution of the equation without weights.

**What the inequality says.** Iterating the equation expresses $u(M)$ as a sum over decreasing chains $M > t_1 > \dots > t_j > t_0$, $j \ge 0$: the chain contributes $a_{M-t_1}\, a_{t_1-t_2} \cdots a_{t_{j-1}-t_j}\, \kappa(t_j)$ times $e^{-X}$, where $X = x(t_1) + \dots + x(t_j)$ is the sum of the exponents at the points that the chain visits; the empty chain contributes $\kappa(M)$. The sequence $r$ is the same sum without the factor $e^{-X}$. Since $\kappa \ge 0$, the chains carry nonnegative weights, and if $r(M) > 0$ then $u(M)/r(M)$ is the average of $e^{-X}$ over the chains, each chain being taken with the probability proportional to its weight. For every real $\mu$ the tangent to the convex function $X \mapsto e^{-X}$ at the point $\mu$ lies below it:

$$e^{-X} \;\ge\; e^{-\mu}\,(1 + \mu - X).$$

Averaging gives $u(M) \ge e^{-\mu}\bigl((1+\mu)\, r(M) - r(M)\,\mathbb{E}[X]\bigr)$. The product $r(M)\,\mathbb{E}[X]$ is the sum over the points $t$ of $x(t)$ times the total weight of the chains that visit $t$. A chain that visits $t$ consists of a chain from $M$ down to $t$ and a chain that starts at $t$. The second has the total weight $r(t)$. The first is a composition of $M - t$ with free cut points, and the total weight of these is $\operatorname{ren}(M-t)$ (`Parking.Lam_one`). So $r(M)\,\mathbb{E}[X] = \sum_{t_0<t<M} \operatorname{ren}(M-t)\, r(t)\, x(t)$, which is the sum in the statement. With $\mu = \mathbb{E}[X]$ the inequality becomes Jensen's inequality $u(M) \ge r(M)\, e^{-\mathbb{E}[X]}$; this choice is made in `Parking.Lam_jensen` and `Parking.zr_jensen`.

**Why the tangent form is the one that is stated.** There are three reasons. First, the proof is an induction on $M$ that uses the hypothesis at a point $t$ with the parameter $\mu - x(t)$, so the statement has to be available for all $\mu$ at once. Second, for a fixed $\mu$ the left side is linear in the exponents $x(t)$; a user can therefore replace the sum of the exponents by an upper bound, or add up several instances with a common $\mu$, which is not possible once the exponents sit inside an exponential. `Parking.impulse_le` uses `Parking.Lam_tangent` in this way. Third, the tangent form needs no positivity of $r$: the statement holds as written, without the assumption $r(M) > 0$ that the average requires and without any assumption on the sign of $x$.

**The proof does not expand into chains.** It is an induction on $M$ on the two equations, and the one identity it needs about the kernel is that $\operatorname{ren}$ is its resolvent: applying the kernel to a function and to its convolution with $\operatorname{ren}$ gives the convolution with $\operatorname{ren}$ (identity (2) below). The same identity carries the proof of `Parking.Lam_defect`. The statement is used through its two instances, `Parking.Lam_tangent` for the composition sums and `Parking.zr_jensen` for the environment of a threshold.

**The Lean form.** The lower limit $t_0$ is the implicit argument `a` of the Lean statement, and the sums run over `Finset.Ioo a M`. The three hypotheses are functions `hκ`, `hr`, `hu` of $M$ with the conditions $1 \le M$ and $M \le B$; in the equation of $u$ the summand is `cay (M - t) * (Real.exp (-(x t)) * u t)`, and in the conclusion the summand is `ren (M - t) * (r t * x t)`.

## Proof

Write $S(M) = \sum_{t_0<t<M} \operatorname{ren}(M-t)\, r(t)\, x(t)$. We prove, by strong induction on $M$, the following claim for every $M$ with $1 \le M \le B$:

$$\text{for every real } \nu: \qquad e^{-\nu}\bigl((1+\nu)\, r(M) - S(M)\bigr) \;\le\; u(M).$$

**Two facts about the kernel.** For every $m \ge 1$,

$$\operatorname{ren}(m) = a_m + \sum_{0<s<m} a_{m-s}\, \operatorname{ren}(s). \tag{1}$$

This is `Parking.ren_conv`, $\sum_{j=0}^{m} a_j \operatorname{ren}(m-j) = \operatorname{ren}(m)$, in which the term $j = 0$ vanishes, the term $j = m$ is $a_m$, and the others are reindexed by $s = m - j$. Consequently, for every function $g : \mathbb{N} \to \mathbb{R}$ and every $M$,

$$\sum_{t_0<t<M} a_{M-t}\,\Bigl(g(t) + \sum_{t_0<c<t} \operatorname{ren}(t-c)\, g(c)\Bigr) = \sum_{t_0<c<M} \operatorname{ren}(M-c)\; g(c). \tag{2}$$

Indeed, after the exchange of the two summations in the double sum over $t_0 < c < t < M$, the coefficient of $g(c)$ on the left is $a_{M-c} + \sum_{c<t<M} a_{M-t} \operatorname{ren}(t-c)$, which equals $\operatorname{ren}(M-c)$ by (1) at $M - c \ge 1$, with $s = t - c$. For $g(t) = r(t)\, x(t)$, identity (2) reads

$$\sum_{t_0<t<M} a_{M-t}\,\bigl(r(t)\, x(t) + S(t)\bigr) = S(M). \tag{3}$$

**The induction step.** Let $1 \le M \le B$, let $\nu$ be real, and assume the claim for all smaller arguments. Take $t$ with $t_0 < t < M$. Then $1 \le t \le B$, and the claim at $t$ with the parameter $\nu - x(t)$ says

$$e^{-(\nu - x(t))}\,\bigl((1 + \nu - x(t))\, r(t) - S(t)\bigr) \;\le\; u(t).$$

Multiply by $e^{-x(t)} > 0$ and by $a_{M-t} \ge 0$ (`Parking.cay_nonneg`). Since $e^{-x(t)}\, e^{-(\nu - x(t))} = e^{-\nu}$, this gives

$$e^{-\nu}\; a_{M-t}\,\Bigl((1+\nu)\, r(t) - \bigl(r(t)\, x(t) + S(t)\bigr)\Bigr) \;\le\; a_{M-t}\; e^{-x(t)}\; u(t). \tag{4}$$

The shift of the parameter by $x(t)$ is what makes the weight $e^{-x(t)}$ of the equation of $u$ disappear into the common factor $e^{-\nu}$. Next, $1 + \nu \le e^{\nu}$ gives $e^{-\nu}(1+\nu) \le 1$, and $\kappa(M) \ge 0$, so

$$e^{-\nu}\,(1+\nu)\,\kappa(M) \;\le\; \kappa(M). \tag{5}$$

Add (5) and the inequalities (4) for all $t_0 < t < M$. On the right we obtain $\kappa(M) + \sum_{t_0<t<M} a_{M-t}\, e^{-x(t)}\, u(t) = u(M)$, by the equation of $u$. On the left we obtain

$$e^{-\nu}\,\Bigl((1+\nu)\Bigl(\kappa(M) + \sum_{t_0<t<M} a_{M-t}\, r(t)\Bigr) - \sum_{t_0<t<M} a_{M-t}\bigl(r(t)\, x(t) + S(t)\bigr)\Bigr) = e^{-\nu}\bigl((1+\nu)\, r(M) - S(M)\bigr),$$

by the equation of $r$ and by (3). This is the claim at $M$. The statement is the claim with $\nu = \mu$.

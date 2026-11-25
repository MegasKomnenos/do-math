---
weight: unit
short: tangent inequality for composition sums
---
## Description

For a cut profile of the form $e^{-x(s)}$, every real $\mu$ and every $m \ge 1$: $e^{-\mu}\bigl((1+\mu)\operatorname{ren}(m) - \sum_{0<c<m} \operatorname{ren}(m-c)\operatorname{ren}(c)\, x(c)\bigr) \le \Lambda_m[e^{-x}]$, where $\operatorname{ren}(n) = n^n/n!$ and $\Lambda_m$ is the total weight of the compositions of $m$.

## Statement

Let $x : \mathbb{N} \to \mathbb{R}$ be a function, $\mu$ a real number and $m \ge 1$ a natural number. Then

$$e^{-\mu}\,\Bigl((1+\mu)\,\operatorname{ren}(m) \;-\; \sum_{0 < c < m} \operatorname{ren}(m-c)\,\operatorname{ren}(c)\; x(c)\Bigr) \;\le\; \Lambda_m\bigl[e^{-x}\bigr],$$

where $\operatorname{ren}(n) = n^n/n!$ (`Parking.ren`) and $\Lambda_m[e^{-x}]$ is the total weight of the compositions of $m$ for the cut profile $s \mapsto e^{-x(s)}$ (`Parking.Lam`).

## Explanation

The statement is `Parking.volterra_tangent` for the compositions. The weight of a composition of $m$ with the set $S$ of cut points, for the profile $e^{-x}$, is the product of the Cayley coefficients of its parts times $e^{-X(S)}$ with $X(S) = \sum_{c \in S} x(c)$. Without the factor $e^{-X(S)}$ the weights add up to $\operatorname{ren}(m)$ (`Parking.Lam_one`), and the compositions that have a cut point at $c$ have the total weight $\operatorname{ren}(c)\operatorname{ren}(m-c)$, because such a composition is a composition of $c$ followed by a composition of $m - c$. So the sum in the statement is $\operatorname{ren}(m)$ times the mean of $X(S)$ over a composition drawn with probability proportional to the product of the Cayley coefficients of its parts, and the statement is the average of the tangent inequality $e^{-X} \ge e^{-\mu}(1 + \mu - X)$. The record of `Parking.volterra_tangent` explains why the parameter $\mu$ is left free.

Every positive cut profile has the form $e^{-x}$. The profiles of the curve increase are threshold profiles $s \mapsto y/(N-s)$ with values in $(0,1]$, for which $x(s) = \log\bigl((N-s)/y\bigr) \ge 0$ is the logarithm of the excess of the size $N - s$ over the threshold. The statement is used with a fixed parameter $\mu$ in the upper bound of the boundary term, `Parking.impulse_le`, where it bounds from below the composition sums that the first violating point identity `Parking.Lam_defect` produces. With $\mu$ equal to the mean exponent it becomes `Parking.Lam_jensen`.

In Lean the profile is `fun s => Real.exp (-(x s))`, and the sum runs over `Finset.Ioo 0 m` with the summand `ren (m - c) * (ren c * x c)`.

## Proof

Apply `Parking.volterra_tangent` with $t_0 = 0$, $B = m$, $\kappa(M) = a_M$ where $a_p = p^{p-1}/p!$ (`Parking.cay`), $r = \operatorname{ren}$ and $u(M) = \Lambda_M[e^{-x}]$. Its three hypotheses hold for every $M \ge 1$:

- $a_M \ge 0$ by `Parking.cay_nonneg`;
- $\operatorname{ren}(M) = a_M + \sum_{0<t<M} a_{M-t} \operatorname{ren}(t)$; this is `Parking.ren_conv`, $\sum_{j=0}^{M} a_j \operatorname{ren}(M-j) = \operatorname{ren}(M)$, in which the term $j = 0$ vanishes, the term $j = M$ is $a_M$, and the others are reindexed by $t = M - j$;
- $\Lambda_M[e^{-x}] = a_M + \sum_{0<t<M} a_{M-t}\, e^{-x(t)}\, \Lambda_t[e^{-x}]$; this is the last-cut recursion `Parking.Lam_last` for the profile $e^{-x}$.

The conclusion of `Parking.volterra_tangent` at $M = m$ is the statement.

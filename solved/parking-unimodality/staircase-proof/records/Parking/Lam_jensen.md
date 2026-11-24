---
weight: unit
short: Jensen's inequality for composition sums
---
## Description

For a cut profile of the form $e^{-x(s)}$ and every $m \ge 1$: $\operatorname{ren}(m)\,\exp\bigl(-\sum_{0<c<m} \operatorname{ren}(m-c)\operatorname{ren}(c)\, x(c)/\operatorname{ren}(m)\bigr) \le \Lambda_m[e^{-x}]$, where $\operatorname{ren}(n) = n^n/n!$ and $\Lambda_m$ is the total weight of the compositions of $m$.

## Statement

Let $x : \mathbb{N} \to \mathbb{R}$ be a function and $m \ge 1$ a natural number. Then

$$\operatorname{ren}(m)\;\exp\Bigl(-\,\frac{1}{\operatorname{ren}(m)} \sum_{0 < c < m} \operatorname{ren}(m-c)\,\operatorname{ren}(c)\; x(c)\Bigr) \;\le\; \Lambda_m\bigl[e^{-x}\bigr],$$

where $\operatorname{ren}(n) = n^n/n!$ (`Parking.ren`) and $\Lambda_m[e^{-x}]$ is the total weight of the compositions of $m$ for the cut profile $s \mapsto e^{-x(s)}$ (`Parking.Lam`).

## Explanation

Draw a composition of $m$ with probability proportional to the product of the Cayley coefficients $a_p = p^{p-1}/p!$ of its parts. The total of these products is $\operatorname{ren}(m)$ (`Parking.Lam_one`), and the point $c$ is a cut point with probability $\operatorname{ren}(c)\operatorname{ren}(m-c)/\operatorname{ren}(m)$. For the set $S$ of cut points put $X(S) = \sum_{c \in S} x(c)$. Then $\Lambda_m[e^{-x}]/\operatorname{ren}(m)$ is the mean of $e^{-X(S)}$, and the exponent in the statement is minus the mean of $X(S)$. The statement is thus Jensen's inequality $\mathbb{E}[e^{-X}] \ge e^{-\mathbb{E}[X]}$ for the convex function $e^{-X}$: the total weight for the profile $e^{-x}$ is at least the total weight for the profile $1$ times the exponential of minus the mean total exponent.

In the curve increase the cut profiles are threshold profiles with values in $(0,1]$, and the statement bounds the composition sums from below by an explicit exponential. The lower bound of the pair sum, `Parking.pairSum_ge`, applies it to the two composition sums that occur in the term of each pair of marked cut points.

In Lean the exponent is written `-((∑ c ∈ Ioo 0 m, ren (m - c) * (ren c * x c)) / ren m)`.

## Proof

Put $S = \sum_{0<c<m} \operatorname{ren}(m-c)\operatorname{ren}(c)\, x(c)$ and $r = \operatorname{ren}(m)$, which is positive (`Parking.ren_pos`). `Parking.Lam_tangent` gives $e^{-\mu}\bigl((1+\mu)\, r - S\bigr) \le \Lambda_m[e^{-x}]$ for every real $\mu$. Take $\mu = S/r$. Then $(1 + S/r)\, r - S = r$, and the inequality reads $e^{-S/r}\, r \le \Lambda_m[e^{-x}]$.

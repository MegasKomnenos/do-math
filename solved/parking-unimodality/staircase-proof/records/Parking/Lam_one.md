---
weight: unit
short: total composition weight for the profile 1
---
## Description

For $m \ge 1$, the total weight of the compositions of $m$ in which every cut has the weight $1$ is $\Lambda_m[1] = m^m/m!$.

## Statement

For every natural number $m \ge 1$,

$$\Lambda_m[\mathbf{1}] \;=\; \operatorname{ren}(m) \;=\; \frac{m^m}{m!},$$

where $\Lambda_m[\mathbf{1}]$ is the total weight of the compositions of $m$ for the constant cut profile $\mathbf{1}(s) = 1$ (`Parking.Lam`), that is, the sum over all compositions of $m$ of the product of the Cayley coefficients $a_p = p^{p-1}/p!$ of their parts, and $\operatorname{ren}$ is the sequence of `Parking.ren`.

## Explanation

The statement evaluates the sum $\sum_{p_1 + \dots + p_q = m} a_{p_1} \cdots a_{p_q}$ over all compositions of $m$ into any number $q$ of positive parts. It is the combinatorial meaning of the renewal equation of the sequence $n^n/n!$ with the kernel $a$: a composition of $m$ is either the single part $m$ or a composition of some $s < m$ followed by a last part of size $m - s$, so the total weight satisfies the recursion $u(m) = a_m + \sum_{0<s<m} a_{m-s}\, u(s)$, and $\operatorname{ren}$ satisfies the same recursion. In the library the statement is obtained as the case of `Parking.Lam_defect` in which the defect vanishes.

It is used in the closed forms of the convolutions $\kappa_2$ and $\kappa_3$ of the Poisson mass (`Parking.kc2_eq`, `Parking.kc3_eq`), where it identifies the convolutions of the sequence $\operatorname{ren}$ with the weights of the compositions with one and with two marked cut points for the profile $1$. It also explains, although their proofs do not use it, the form of the inequalities of Jensen type of this module: in `Parking.Lam_jensen` the number $\operatorname{ren}(m)$ is the total weight of the measure over which the average is taken, and $\operatorname{ren}(c)\operatorname{ren}(m-c)$ is the weight of the compositions that have a cut point at $c$.

The hypothesis $m \ge 1$ is needed, since $\Lambda_0[\mathbf{1}] = 0$ and $\operatorname{ren}(0) = 1$. In Lean the statement is `Lam (fun _ => (1 : ℝ)) m = ren m`.

## Proof

`Parking.Lam_defect` for the profile $f = \mathbf{1}$ gives $\operatorname{ren}(m) - \Lambda_m[\mathbf{1}] = \sum_{0<s<m} \operatorname{ren}(m-s)\,(1 - 1)\,\Lambda_s[\mathbf{1}] = 0$.

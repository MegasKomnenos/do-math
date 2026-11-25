---
weight: unit
short: compositions with two marked cut points
---
## Description

$\Lambda^{(2)}_m[f] = \sum_{0<b<m} \Lambda^{(1)}_b[f]\, f(b)\, \Lambda_{m-b}[f(b+\cdot)]$: the total weight, for the cut profile $f$, of the compositions of $m$ in which two cut points are marked.

## Statement

Let $f : \mathbb{N} \to \mathbb{R}$ be a function (a cut profile) and $m$ a natural number. For a natural number $b$ write $f^{+b}$ for the shifted profile $s \mapsto f(b+s)$. Then

$$\Lambda^{(2)}_m[f] \;=\; \sum_{0 < b < m} \Lambda^{(1)}_b[f]\; f(b)\; \Lambda_{m-b}\bigl[f^{+b}\bigr],$$

where $\Lambda^{(1)}_b[f]$ is the total weight of the compositions of $b$ with one marked cut point (`Parking.Lam1`) and $\Lambda_m[f]$ is the total weight of the compositions of $m$ (`Parking.Lam`). Since $\Lambda^{(1)}_1[f] = 0$, the sum vanishes for $m \le 2$.

## Explanation

The definition repeats that of `Parking.Lam1` one level higher. Let a composition of $m$ have two marked cut points $a < b$. Cut it at the larger marked point $b$: what lies before $b$ is a composition of $b$ in which the cut point $a$ is marked, and what lies after $b$ is a composition of $m - b$, whose cut points sit at the positions $b + s'$ and therefore carry the shifted profile $f^{+b}$. The term of index $b$ is the total weight of the compositions of $m$ with two marked cut points of which the larger is $b$. So $\Lambda^{(2)}_m[f]$ counts each composition of $m$ with its weight times the number of pairs of its cut points, which `Parking.Lam2_eq_sum` proves in the form $\Lambda^{(2)}_m[f] = \sum_q \tfrac12 (q-1)(q-2)\, V_q(m;f)$, where $V_q(m;f)$ is the total weight of the compositions of $m$ with exactly $q$ parts (`Parking.Vc`).

Only the curve increase uses $\Lambda^{(2)}$, in two places. First, together with $\Lambda^{(1)}$ it expresses the second factorial moment of the number of parts, $\sum_q q(q-1)\, V_q(m;f) = 2\Lambda^{(1)}_m[f] + 2\Lambda^{(2)}_m[f]$ (`Parking.sum_qq_Vc`), which is the quantity that the second difference of the frozen polynomial dominates (`Parking.curv_ge_pair`); in that proof the sum $\Lambda^{(1)} + \Lambda^{(2)}$ enters through its recursion on the last part (`Parking.Lam2_last`). Second, for the constant profile $1$ the number $\Lambda^{(2)}_m[1]$ is a threefold convolution of the sequence $m^m/m!$, and `Parking.Lam2_eq_sum` gives its closed form (`Parking.kc3_eq`).

In Lean the definition is `Lam2 f m`, a sum over `Finset.Ioo 0 m` of `Lam1 f b * f b * Lam (fun s => f (b + s)) (m - b)`.

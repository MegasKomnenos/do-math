---
weight: unit
short: compositions with one marked cut point
---
## Description

$\Lambda^{(1)}_m[f] = \sum_{0<a<m} \Lambda_a[f]\, f(a)\, \Lambda_{m-a}[f(a+\cdot)]$: the total weight, for the cut profile $f$, of the compositions of $m$ in which one cut point is marked.

## Statement

Let $f : \mathbb{N} \to \mathbb{R}$ be a function (a cut profile) and $m$ a natural number. For a natural number $a$ write $f^{+a}$ for the shifted profile $s \mapsto f(a+s)$. Then

$$\Lambda^{(1)}_m[f] \;=\; \sum_{0 < a < m} \Lambda_a[f]\; f(a)\; \Lambda_{m-a}\bigl[f^{+a}\bigr],$$

where $\Lambda_m[f]$ is the total weight of the compositions of $m$ for the cut profile $f$ (`Parking.Lam`). The sum is empty for $m \le 1$, so $\Lambda^{(1)}_0[f] = \Lambda^{(1)}_1[f] = 0$.

## Explanation

**What the sum is.** A composition of $m$ is a way of cutting a segment of length $m$ at some of its interior integer points $1, \dots, m-1$, the cut points; its weight for the profile $f$ is the product of the Cayley coefficients $a_p = p^{p-1}/p!$ of its parts times the product of $f(s)$ over its cut points $s$ (see `Parking.Vc`). A composition of $m$ that has a cut point at $a$ consists of a composition of $a$, the cut at $a$, and a composition of $m - a$ placed after it. Its weight is the product of three factors: the weight of the first composition for the profile $f$, the factor $f(a)$, and the weight of the second composition for the profile $f^{+a}$, because a cut point $s'$ of the second composition sits at the position $a + s'$ of the segment. Summing over the two compositions, the term of index $a$ in the definition is the total weight of the compositions of $m$ that have a cut point at $a$. Summing over $a$, $\Lambda^{(1)}_m[f]$ is the total weight of the pairs formed by a composition of $m$ and one of its cut points; that is, each composition is counted with its weight times its number of cut points. `Parking.Lam1_eq_sum` proves this in the form $\Lambda^{(1)}_m[f] = \sum_q (q-1)\, V_q(m;f)$, where $V_q(m;f)$ is the total weight of the compositions of $m$ with exactly $q$ parts.

**Why it is defined by the splitting.** The splitting at the marked point is the form in which the quantity arises in the arguments, and the form with the number of cut points is the form in which it can be evaluated. In the curve increase a marked cut point separates a chain into the part above it and the part below it, and the two parts are estimated separately. In the diagonal step a constant profile $\rho$ occurs, and the sum $\sum_{0<t<q} \Lambda_t[\rho]\,\rho\,\Lambda_{q-t}[\rho]$ of the weights of the compositions of $q$ that have a cut point at $t$ is recognised as $\Lambda^{(1)}_q[\rho]$ by unfolding this definition, so the definition has to have exactly this shape.

**Where it is used.** The module that contains $\Lambda^{(1)}$, $\Lambda^{(2)}$ (`Parking.Lam2`) and the statements about them serves two separate arguments of the proof.

- *The curve increase* takes everything in the module. The pair sum `Parking.pairSum` is defined with $\Lambda^{(1)}$ for the threshold profile $s \mapsto k/(N-s)$. `Parking.sum_qq_Vc` and `Parking.Lam2_last` are the two facts about marked cut points behind `Parking.curv_ge_pair`. And for the constant profile $1$, where $\Lambda_m[1] = m^m/m!$ (`Parking.Lam_one`), the sums $\Lambda^{(1)}_m[1]$ and $\Lambda^{(2)}_m[1]$ are convolutions of the sequence $m^m/m!$, which `Parking.Lam1_eq_sum` and `Parking.Lam2_eq_sum` evaluate (`Parking.kc2_eq`, `Parking.kc3_eq`).
- *The diagonal step behind the curve* takes $\Lambda^{(1)}$ and `Parking.Lam1_eq_sum`, for a constant profile $\rho$: in the proof of `Parking.Lam_gain` they show that the weights of the compositions of $q$ with a cut point at $t$, summed over $t = 1, \dots, q-1$, add up to the mean number of cut points times the total weight of the compositions of $q$.

**The Lean form.** The definition is `Lam1 f m`, a sum over `Finset.Ioo 0 m` of `Lam f a * f a * Lam (fun s => f (a + s)) (m - a)`. The subtraction $m - a$ is exact on the range of summation. As for `Parking.Lam`, only the values of $f$ at the points $1, \dots, m-1$ matter.

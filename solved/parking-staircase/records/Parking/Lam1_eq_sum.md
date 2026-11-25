---
weight: unit
short: one marked cut point counts the cut points
---
## Description

For every cut profile $f$ and every $m$: $\Lambda^{(1)}_m[f] = \sum_{q=1}^{m} (q-1)\, V_q(m;f)$. The total weight of the compositions of $m$ with one marked cut point is the sum of the weights of the compositions, each multiplied by its number of cut points.

## Statement

Let $f : \mathbb{N} \to \mathbb{R}$ be a function and $m$ a natural number. Then

$$\Lambda^{(1)}_m[f] \;=\; \sum_{q=1}^{m} (q-1)\; V_q(m;f),$$

where $\Lambda^{(1)}_m[f] = \sum_{0<a<m} \Lambda_a[f]\, f(a)\, \Lambda_{m-a}[f(a+\cdot)]$ is the total weight of the compositions of $m$ with one marked cut point (`Parking.Lam1`), and $V_q(m;f)$ is the total weight of the compositions of $m$ with exactly $q$ parts for the cut profile $f$ (`Parking.Vc`).

## Explanation

A composition with $q$ parts has $q - 1$ cut points, so there are $q - 1$ ways to mark one of them. The left side counts the pairs of a composition and a marked cut point by the position of the mark, the right side counts them by the number of parts of the composition. If $f$ is nonnegative and the total weight $\Lambda_m[f] = \sum_q V_q(m;f)$ is positive, the statement says that $\Lambda^{(1)}_m[f] / \Lambda_m[f]$ is the mean number of cut points of a composition of $m$ drawn with probability proportional to its weight.

If the weights were defined as sums over sets of cut points, the statement would be an exchange of two summations. The library defines $V_q(m;f)$ by the recursion that removes the last part, and $\Lambda^{(1)}$ by the splitting at the marked point, so the proof shows that both sides satisfy the same recursion on the last part. It is organised around one lemma about marking, which also gives `Parking.Lam2_eq_sum`. Let $c$ be a function of a natural number, and consider the compositions of $m$ with one marked cut point, each multiplied in addition by $c(i)$, where $i$ is the number of cut points that lie before the mark. A composition with $q$ cut points arises once for each of its cut points, and the mark at its $(i+1)$-st cut point leaves $i$ cut points before it; so the composition is counted with its weight times $d(q) = c(0) + \dots + c(q-1)$. The lemma states this as an identity between two sums. With $c = 1$ it is the present statement, and with $c(i) = i$ it is the statement about two marked cut points.

Both arguments that use the module rest on this statement. In the curve increase it enters `Parking.sum_qq_Vc`, and for the constant profile $1$ it gives the closed form of the convolution $\kappa_2$ of the Poisson mass (`Parking.kc2_eq`). In the diagonal step behind the curve it is applied to a constant profile $\rho$ in the proof of `Parking.Lam_gain`.

In Lean the right side is a sum over `Finset.Icc 1 m` of `((q : ℝ) - 1) * Vc f q m`.

## Proof

Fix $f$ and write $V_q(m) = V_q(m;f)$, $\Lambda_m = \Lambda_m[f]$ and $f^{+b}(s) = f(b+s)$.

**Sums weighted by the number of cut points.** For a function $c : \mathbb{N} \to \mathbb{R}$ put

$$S_c(m) = \sum_{q=0}^{m-1} c(q)\; V_{q+1}(m).$$

Here $q$ is the number of cut points of a composition with $q + 1$ parts. Since $V_{q+1}(m) = 0$ for $q \ge m$ (`Parking.Vc_eq_zero_of_lt`), the upper limit $m - 1$ may be replaced by any larger number. For the constant function $c = 1$ the sum is $S_1(m) = \sum_{q=1}^{m} V_q(m) = \Lambda_m$, by the definition of `Parking.Lam`.

**Step 1: removing the last part in $S_c$.** For every $c$ and every $m$,

$$S_c(m) = c(0)\, a_m + \sum_{0<s<m} S_{c^+}(s)\; f(s)\; a_{m-s}, \qquad c^+(q) = c(q+1).$$

For $m = 0$ both sides are $0$. For $m \ge 1$, the term $q = 0$ of $S_c(m)$ is $c(0)\, V_1(m) = c(0)\, a_m$ by `Parking.Vc_one`. For the other terms, `Parking.Vc_succ_succ` gives $V_{q+2}(m) = \sum_{0<s<m} V_{q+1}(s)\, f(s)\, a_{m-s}$, so that

$$\sum_{q=0}^{m-2} c(q+1)\, V_{q+2}(m) = \sum_{0<s<m} \Bigl(\sum_{q=0}^{m-2} c(q+1)\, V_{q+1}(s)\Bigr) f(s)\, a_{m-s},$$

and the inner sum is $S_{c^+}(s)$ because $s \le m - 1$.

**Step 2: removing the last part in a sum with a marked cut point.** For every function $g : \mathbb{N} \to \mathbb{R}$ and every $m$,

$$\sum_{0<b<m} g(b)\, f(b)\, \Lambda_{m-b}\bigl[f^{+b}\bigr] = \sum_{0<s<m} \Bigl(g(s) + \sum_{0<b<s} g(b)\, f(b)\, \Lambda_{s-b}\bigl[f^{+b}\bigr]\Bigr) f(s)\, a_{m-s}.$$

Indeed, `Parking.Lam_last` for the profile $f^{+b}$ and the length $m - b$ gives, after the substitution $s = b + u$ in its sum over $0 < u < m - b$,

$$\Lambda_{m-b}\bigl[f^{+b}\bigr] = a_{m-b} + \sum_{b<s<m} \Lambda_{s-b}\bigl[f^{+b}\bigr]\, f(s)\, a_{m-s}.$$

Multiply by $g(b)\, f(b)$ and sum over $0 < b < m$. The first terms are the terms $g(s)\, f(s)\, a_{m-s}$ of the right side, and the remaining double sum over $0 < b < s < m$, summed first over $b$, gives the inner sum of the right side. In words: the marked point is the last cut point $s$, or the last cut point $s$ lies after it, and then the marked point is a marked cut point of the composition of $s$ that remains when the last part is removed.

**Step 3: the marking lemma.** Let $c, d : \mathbb{N} \to \mathbb{R}$ satisfy $d(0) = 0$ and $d(q+1) = d(q) + c(q)$ for all $q$. Then for every $m$,

$$\sum_{0<b<m} S_c(b)\; f(b)\; \Lambda_{m-b}\bigl[f^{+b}\bigr] = S_d(m).$$

We prove this by strong induction on $m$. Denote the left side by $M(m)$. Step 2 with $g = S_c$ gives $M(m) = \sum_{0<s<m} \bigl(S_c(s) + M(s)\bigr) f(s)\, a_{m-s}$, and the induction hypothesis replaces $M(s)$ by $S_d(s)$, since $s < m$. On the other side, Step 1 for $d$ gives $S_d(m) = \sum_{0<s<m} S_{d^+}(s)\, f(s)\, a_{m-s}$, because $d(0) = 0$. Finally $d^+(q) = d(q+1) = d(q) + c(q)$, and $S$ is linear in its weight, so $S_{d^+}(s) = S_d(s) + S_c(s)$. The two expressions agree.

**Conclusion.** Take $c = 1$ and $d(q) = q$, which satisfy the two relations. Since $S_1(b) = \Lambda_b$, the left side of the marking lemma is $\sum_{0<b<m} \Lambda_b\, f(b)\, \Lambda_{m-b}[f^{+b}] = \Lambda^{(1)}_m[f]$. Hence

$$\Lambda^{(1)}_m[f] = \sum_{q=0}^{m-1} q\; V_{q+1}(m) = \sum_{q=1}^{m} (q-1)\; V_q(m),$$

the last equality being the change of index of `Parking.sum_Icc_one_eq_range`.

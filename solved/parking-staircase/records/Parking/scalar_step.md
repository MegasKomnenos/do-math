---
weight: unit
short: the scalar inequality of the diagonal step
---
## Description

Behind the curve in a column $k \ge 265$, the factors that the coefficient and the curvature sum of one term gain on a diagonal step are together smaller than the factors that the boundary term gains: $\gamma_{k+a}\bigl(1+\frac{\mathsf T(k,a)}{k}\bigr)\frac{k}{k+1}\,e^{E_m} < \gamma_k\,(1+x)^{E_0}$ for $(q-1)^3 \le k^2$, $1 \le a \le q-2$, $m = q-a$.

## Statement

Let $\gamma_j = (1+1/j)^{j-2}$ (`Parking.gam`); let $\mathsf T(k,a)$ be the closed form of `Parking.kapStepBound`, that is, with $\xi = a/k$,

$$\mathsf T(k,a) = \frac{\frac32\,\xi\,\bigl(1+\frac{2}{3(k+2)}\bigr)\bigl(1+\frac32\xi+\frac38\xi^2\bigr)}{\frac{23}{24}-\frac32\,\xi\,\bigl(1+\frac\xi4\bigr)};$$

let $D_m$ be the moment ratio of the birthday law (`Parking.Dbirth`) and $\mu^0_r(X) = \bigl(\sqrt{(4+X)^2+12(r-1)}-(4+X)\bigr)/3$ (`Parking.mu0`).

Let $k$, $q$, $a$ be natural numbers with $k \ge 265$, $(q-1)^3 \le k^2$, $1 \le a$ and $a+2 \le q$, and put $m = q - a$,

$$E_m = \frac{\bigl(1+\frac1{400}\bigr)(D_m+1)\bigl(q-\frac m2\bigr)}{k\,(k+1)}, \qquad x = \frac{q}{(k-1)(k+q)}, \qquad E_0 = \frac{q+2}{2q}\;\mu^0_q\Bigl(\frac{q^2}{k-1}\Bigr).$$

Then

$$\gamma_{k+a}\;\Bigl(1+\frac{\mathsf T(k,a)}{k}\Bigr)\cdot\frac{k}{k+1}\cdot e^{E_m} \;<\; \gamma_k\;(1+x)^{E_0}.$$

## Explanation

**What the two sides collect.** For a position $(k+r,k)$ with $q = r+1$ and a term $m = q - a$ of its curvature term, three comparisons relate the quantities of the position to those of the position one row down and one column to the right:

- the coefficient grows by at most $\gamma_{k+a}\bigl(1 + \mathsf T(k,a)/k\bigr)$ (`Parking.kap_diag_le`, with $a_{M+1}/(M+1) = \gamma_M\,a_M/M$);
- the curvature sum grows by at most $\frac{k}{k+1}\,e^{E_m}$ (`Parking.curvSum_step`);
- the boundary term grows by at least $\gamma_k\,(1+x)^{E_0}$ (`Parking.Lam_gain`, with $a_{k+1}/(k+1) = \gamma_k\,a_k/k$).

The statement says that the product of the first two is strictly smaller than the third. `Parking.term_step` multiplies the three comparisons, and this is the inequality that remains; it is the source of the strict sign in the diagonal step.

**How close the two sides are.** All four factors on the left and both on the right differ from the corresponding power of $e$ by terms of order $1/k$: $\gamma_{k+a}/\gamma_k = 1 + O(a/k^2)$, $\mathsf T/k = O(a/k^2)$, $\frac{k}{k+1} = 1 - \frac1k + \dots$, $E_m = O(q\sqrt m/k^2)$, and $E_0\log(1+x) = O(q^{3/2}/k^2)$. The inequality holds because $-\log\frac{k}{k+1} \approx \frac1k$ outweighs the growth terms as long as $q^{3/2}$ is at most about $k$, with the help of the gain of the boundary term for the larger $q$. This balance is the content of `Parking.ledger`, and the hypothesis $(q-1)^3 \le k^2$ is the range in which it is proved.

**The Lean form.** The exponent is written with `Dbirth (q - a)` and `((q - a : ℕ) : ℝ) / 2`, the subtraction $q - a$ being that of natural numbers, ordinary because $a + 2 \le q$; `(q - 1) ^ 3 ≤ k ^ 2` is an inequality of natural numbers, with $q \ge 3$. The power $(1+x)^{E_0}$ is a real power.

## Proof

Both sides are positive: $\gamma_j > 0$ (`Parking.gam_pos`), $1 + x > 0$, and $\mathsf T(k,a) \ge 0$. For the last, $(q-1)^3 \le k^2$ and $k \ge 8$ give $2(q-1) \le k$ (otherwise $k^3 < 8(q-1)^3 \le 8k^2 \le k^3$), so $2a \le k$ and `Parking.kapStepBound_nonneg` applies. It therefore suffices to compare logarithms:

$$\log\gamma_{k+a} + \log\Bigl(1+\frac{\mathsf T(k,a)}{k}\Bigr) + \log\frac{k}{k+1} + E_m \;<\; \log\gamma_k + E_0\,\log(1+x).$$

Four bounds are used.

1. $\log\gamma_{k+a} - \log\gamma_k \le \frac52\bigl(\frac1k - \frac1{k+a}\bigr)$, by `Parking.log_gam_sub_le` for $2 \le k \le k+a$.
2. $\log\bigl(1 + \mathsf T(k,a)/k\bigr) \le \mathsf T(k,a)/k$, by $\log u \le u - 1$ for $u > 0$.
3. $\log\frac{k}{k+1} = -\log\bigl(1+\frac1k\bigr)$.
4. $E_m \le \frac{401}{400}\bigl(\frac32\sqrt{\pi m/2} - \frac85\bigr)\cdot\frac{(q+a)/2}{k(k+1)}$: by `Parking.Dbirth_add_one_le` for $m = q - a \ge 2$, $D_m + 1 \le \frac32\sqrt{\pi m/2} - \frac85$; and $q - \frac m2 = \frac{q+a}2 \ge 0$, $1 + \frac1{400} = \frac{401}{400}$.

With these, the difference of the two sides of the logarithmic inequality is bounded by the difference of the two sides of `Parking.ledger` for the same $k$, $q$, $a$:

$$\frac52\Bigl(\frac1k-\frac1{k+a}\Bigr)+\frac{\mathsf T(k,a)}{k}+\frac{401}{400}\Bigl(\frac32\sqrt{\frac{\pi(q-a)}{2}}-\frac85\Bigr)\frac{(q+a)/2}{k(k+1)} \;<\; \log\Bigl(1+\frac1k\Bigr)+E_0\,\log(1+x),$$

which holds under exactly the hypotheses of the present statement.

---
weight: unit
short: slow increase of the logarithm of the diagonal factor
---
## Description

The factor $\gamma_n = (1+1/n)^{n-2}$ increases slowly: $\log\gamma_i - \log\gamma_k \le \frac52\bigl(\frac1k - \frac1i\bigr)$ for $2 \le k \le i$.

## Statement

Let $\gamma_n = (1 + 1/n)^{n-2}$ for a natural number $n \ge 2$ (`Parking.gam`). For all natural numbers $k$, $i$ with $2 \le k \le i$,

$$\log\gamma_i - \log\gamma_k \;\le\; \frac52\Bigl(\frac1k - \frac1i\Bigr).$$

## Explanation

**The factor.** The Cayley coefficients $a_j = j^{j-1}/j!$ (`Parking.cay`) satisfy $a_{n+1}/a_n = (1+1/n)^{n-1} = \gamma_n\,(1+1/n)$ (`Parking.cay_ratio`, `Parking.psi_eq_gam`), that is $a_{n+1}/(n+1) = \gamma_n\,a_n/n$. Whenever an index of a Cayley coefficient is raised by one, a factor $\gamma$ appears, and a comparison of two positions that differ by a diagonal step produces quotients $\gamma_i/\gamma_k$ with $i \ge k$.

**The bound.** Since $\log\gamma_n = (n-2)\log(1+1/n) = 1 - \frac{5}{2n} + O(n^{-2})$, the sequence $\log\gamma_n$ increases to $1$, and the difference $\log\gamma_i - \log\gamma_k$ is $\frac52(\frac1k - \frac1i)$ to first order. The statement says that this first-order value is an upper bound for all $2 \le k \le i$, with the exact constant $\frac52$.

**What it is used for.** In `Parking.scalar_step` it bounds the factor $\gamma_{k+a}/\gamma_k$ by which the coefficient of a term of the curvature term outgrows the boundary term along the diagonal; this is the first term on the left of `Parking.ledger`. In the proof of `Parking.kap_diag_le` it bounds how much a ratio $a_i/a_{i+j}$ of Cayley coefficients decreases when both indices are raised by one.

**The Lean form.** The statement is `Real.log (gam i) - Real.log (gam k) ≤ 5 / 2 * (1 / (k : ℝ) - 1 / (i : ℝ))`. The Lean definition of $\gamma_n$ has the truncated exponent $n - 2$ of natural numbers, which is the ordinary one for $n \ge 2$.

## Proof

**One step.** For a natural number $m \ge 2$,

$$\log\gamma_{m+1} - \log\gamma_m \;\le\; \frac{5}{2\,m\,(m+1)} = \frac52\Bigl(\frac1m - \frac1{m+1}\Bigr).$$

Here $\log\gamma_{m+1} = (m-1)\log\bigl(1 + \frac1{m+1}\bigr)$ and $\log\gamma_m = (m-2)\log\bigl(1+\frac1m\bigr)$, with nonnegative factors $m - 1$ and $m - 2$. The first logarithm is bounded from above by the Taylor polynomial of degree three, $\log(1+u) \le u - \frac{u^2}2 + \frac{u^3}3$ at $u = \frac1{m+1}$ (`Parking.log_one_add_le3`), and the second from below by the Taylor polynomial of degree four, $\log(1+u) \ge u - \frac{u^2}2 + \frac{u^3}3 - \frac{u^4}4$ at $u = \frac1m$ (`Parking.log_one_add_ge4`). What remains is an inequality between rational functions of $m$: the difference of $\frac{5}{2m(m+1)}$ and the resulting bound equals

$$\frac{29\,(m-2)^4 + 253\,(m-2)^3 + 823\,(m-2)^2 + 1191\,(m-2) + 656}{12\,m^4\,(m+1)^3},$$

which is nonnegative for $m \ge 2$.

**Telescoping.** By induction on $i \ge k$: for $i = k$ both sides are $0$, and adding the step from $i$ to $i+1$ to the bound for $i$ gives $\frac52(\frac1k - \frac1i) + \frac52(\frac1i - \frac1{i+1}) = \frac52(\frac1k - \frac1{i+1})$.

In the Lean source the two paragraphs above are a private lemma of the Lean source, stated for $\log(\gamma_k^{-1}\gamma_i) \le \frac{5(i-k)}{2ki}$; the present theorem rewrites it into the form of the statement.

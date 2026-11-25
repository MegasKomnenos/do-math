---
weight: unit
short: the ledger inequality of the diagonal step
---
## Description

The inequality between closed forms to which the diagonal step reduces behind the curve: for $k \ge 265$, $(q-1)^3 \le k^2$ and $1 \le a \le q-2$, the bounds for the growth of the coefficient and of the curvature sum of one term, in logarithms, add up to less than $\log(1+\frac1k)$ plus the logarithm of the gain of the boundary term.

## Statement

For natural numbers $k \ge 1$ and $a$, with $\xi = a/k$, let

$$\mathsf T(k,a) = \frac{\frac32\,\xi\,\bigl(1+\frac{2}{3(k+2)}\bigr)\bigl(1+\frac32\xi+\frac38\xi^2\bigr)}{\frac{23}{24}-\frac32\,\xi\,\bigl(1+\frac\xi4\bigr)}$$

(`Parking.kapStepBound`), and for a natural number $r$ and a real number $X$ let $\mu^0_r(X) = \bigl(\sqrt{(4+X)^2+12(r-1)}-(4+X)\bigr)/3$ (`Parking.mu0`).

Let $k$, $q$, $a$ be natural numbers with $k \ge 265$, $(q-1)^3 \le k^2$, $1 \le a$ and $a + 2 \le q$. Then

$$\frac52\Bigl(\frac1k-\frac1{k+a}\Bigr) \;+\; \frac{\mathsf T(k,a)}{k} \;+\; \frac{401}{400}\Bigl(\frac32\sqrt{\frac{\pi\,(q-a)}{2}}-\frac85\Bigr)\cdot\frac{(q+a)/2}{k\,(k+1)} \;<\; \log\Bigl(1+\frac1k\Bigr) \;+\; \frac{q+2}{2q}\;\mu^0_q\Bigl(\frac{q^2}{k-1}\Bigr)\,\log\Bigl(1+\frac{q}{(k-1)(k+q)}\Bigr).$$

## Explanation

**What the five terms are.** The diagonal step is proved term by term in the index $m$ of the curvature term; here $q = r + 1$ for a position of deficit $r$, $m = q - a$, and $a$ runs over $1 \le a \le q - 2$ as $m$ runs over $2 \le m \le r$. `Parking.scalar_step` is the inequality between the scalar factors that the three comparisons along the diagonal leave, and the present statement is its logarithm with each factor replaced by its closed bound:

- $\frac52(\frac1k - \frac1{k+a})$ bounds $\log\gamma_{k+a} - \log\gamma_k$, with $\gamma_j = (1+1/j)^{j-2}$ (`Parking.log_gam_sub_le`);
- $\mathsf T(k,a)/k$ bounds the logarithm of the growth $1 + \mathsf T(k,a)/k$ of the normalised kernel deficit (`Parking.kap_diag_le`);
- the third term is the exponent of the growth of the curvature sum (`Parking.curvSum_step`), $(1+\frac1{400})(D_m+1)(q-\frac m2)/(k(k+1))$, with $D_m + 1$ replaced by $\frac32\sqrt{\pi m/2} - \frac85$ (`Parking.Dbirth_add_one_le`) and $q - \frac m2 = \frac{q+a}2$;
- $\log(1+\frac1k)$ is minus the logarithm of the factor $\frac{k}{k+1}$ of `Parking.curvSum_step`;
- the last term is the logarithm of the gain $(1+x)^{E_0}$ of the boundary term (`Parking.Lam_gain`), $x = q/((k-1)(k+q))$, $E_0 = \frac{q+2}{2q}\mu^0_q(q^2/(k-1))$.

**The sizes.** Multiplied by $k^2$, the right side is about $k$ plus a gain of the order $q^{3/2}$, and the left side is of the order $a + q\sqrt{q-a}$, at most of the order $q^{3/2}$. Behind the curve $q^{3/2}$ is about $k$ at most. So the inequality compares quantities of the same order with explicit constants; it is not an asymptotic statement, and it is the one place of the diagonal step where the range of $q$ against $k$ matters. For $q \le 36$ the term $\log(1+\frac1k)$ alone suffices. For larger $q$ the gain is needed.

**Where the hypothesis on the curve is used.** The proof draws two facts from $k \ge 265$ and $(q-1)^3 \le k^2$ and uses the hypothesis $(q-1)^3 \le k^2$ in no other way; $k \ge 265$ is also used directly in several steps below:

$$q^{3/2} \le 1.036\,k, \qquad q - 2 \le 0.151\,k .$$

For $q \le 42$ both follow from $k \ge 265$ alone; the hypothesis $(q-1)^3 \le k^2$ is used for $q \ge 43$. The second fact gives $a/k \le 0.151$, the range on which the rational function of $\xi$ in $\mathsf T$ is bounded by a chord. The first is used for $q > 36$: it bounds $a^2/k$, it gives $k \ge q^{3/2}/1.036$ on the right side, and it enters the lower bound for the gain.

**The constants are fitted to the smallest column.** At $k = 265$ the positions behind the curve have $q \le 42$, and $42^3/265^2 = 1.055$, $40/265 = 0.1509$; the constant $0.151$ is the second of these values rounded up, and $1.036 = \sqrt{1.073296}$ is $(43/42)^{3/2} \approx 1.03593$ rounded up, since for $q \ge 43$ the bound $q^3 \le (43/42)^3 (q-1)^3$ is what Step 0 uses. The following figures on the room come from floating-point evaluations, which are not part of the proof. The chord of the kernel deficit term holds on $0 \le \xi \le 0.151$ with a smallest margin of $0.0009$ and fails at $\xi = 0.16$. In the case $q \le 36$ the bound for the left side reaches $260.33$ where $264.5$ is allowed. In the case $q > 36$ the polynomial inequality reaches $1.2458$ where $1.2703$ is allowed, and the gain is bounded below by $0.305\,q^{3/2}$ where the bounded expression is at least $0.324\,q^{3/2}$. The inequality as stated, evaluated directly, has at $k = 265$, $q = 42$ a smallest margin of about a tenth of its right side; with the hypothesis weakened to $(q-1)^3 \le c\,k^2$ it holds for all $k \ge 265$ only up to about $c = 1.3$ (the first failure is at $k = 272$, $q = 47$, $a = 29$). Of what is lost between the true quantities and their closed bounds, the largest part is in `Parking.curvSum_step`, then in `Parking.kap_diag_le` and `Parking.Lam_gain`; the bounds `Parking.log_gam_sub_le` and `Parking.Dbirth_add_one_le` are nearly sharp.

**The Lean form.** All quantities are real numbers; $k$, $q$, $a$ are cast from natural numbers. The hypothesis is `(q - 1) ^ 3 ≤ k ^ 2` with the subtraction of natural numbers, which is the ordinary one because $q \ge 3$ follows from $1 \le a$ and $a + 2 \le q$. The term $q - a$ under the square root is `(q : ℝ) - a`. The constants appear in Lean exactly as written here: `5 / 2`, `401 / 400`, `3 / 2`, `8 / 5`, and inside the proof the decimals quoted below.

## Proof

Write $m = q - a \ge 2$, $t = \sqrt m$, $\xi = a/k$, $x = q/((k-1)(k+q))$, $E_0 = \frac{q+2}{2q}\mu^0_q\bigl(\frac{q^2}{k-1}\bigr)$, and

$$\Phi = \Bigl(\frac52 + \frac32\cdot1.047\Bigr)a + \frac32\cdot4.45\cdot\frac{a^2}{k} + (q+a)\,(0.94235\,t - 0.8), \qquad G = k^2\,E_0\,\Bigl(x - \frac{x^2}2\Bigr).$$

The proof shows: the left side is at most $\Phi/k^2$ (Step 1), the right side is at least $(k - \frac12 + G)/k^2$ (Step 2), and $\Phi < k - \frac12 + G$ (Steps 3 and 4). Note $q \ge 3$, $t \ge 1.4$ (as $m \ge 2 > 1.96$), $0 \le x \le 1$, and $E_0 \ge 0$ because $\mu^0_q(X) \ge 0$ for $X \ge 0$ (`Parking.mu0_nonneg`); so $G \ge 0$.

**Step 0: the range.** (R1) $q^3 \le (1.036\,k)^2 = 1.073296\,k^2$, that is $(\sqrt q)^3 \le 1.036\,k$; (R2) $q - 2 \le 0.151\,k$. If $q \le 42$: $q^3 \le 74088 \le 1.073296\cdot265^2$ and $q - 2 \le 40 \le 0.151\cdot265$. If $q \ge 43$: $42\,q \le 43\,(q-1)$, so $q^3 \le (43/42)^3 (q-1)^3 \le 1.0732\,k^2$; and $(q-2)^2 \le 0.022801\,(q-1)^3 \le (0.151\,k)^2$, the first inequality being a polynomial inequality in $q - 43 \ge 0$ (at $q = 43$: $1681 \le 1689.3$). From (R2) and $a \le q - 2$: $\xi \le 0.151$.

**Step 1: the left side is at most $\Phi/k^2$.**

(a) $\frac1k - \frac1{k+a} = \frac{a}{k(k+a)} \le \frac{a}{k^2}$.

(b) $\mathsf T(k,a) \le \frac32\,\xi\,(1.047 + 4.45\,\xi)$. Put $\lambda = 1 + \frac{2}{3(k+2)}$; $\lambda \le 1.0025$ because $k \ge 265$. For $0 \le \xi \le 0.151$ the denominator $D = \frac{23}{24} - \frac32\xi(1+\frac\xi4)$ is positive and

$$\lambda\,\bigl(1 + \tfrac32\xi + \tfrac38\xi^2\bigr) \;\le\; (1.047 + 4.45\,\xi)\,D ,$$

a cubic inequality in $\xi$ on the interval, verified from $\xi\,(0.151-\xi) \ge 0$ and $\xi^2(0.151-\xi) \ge 0$. Dividing by $D$ and multiplying by $\frac32\xi$ gives the claim; divided by $k$ it is $\frac{\mathsf T}{k} \le \bigl(\frac32\cdot1.047\,a + \frac32\cdot4.45\,\frac{a^2}k\bigr)/k^2$.

(c) $\frac{401}{400}\bigl(\frac32\sqrt{\pi m/2} - \frac85\bigr) \le 2\,(0.94235\,t - 0.8)$. From $\pi < 3.1416$, $\sqrt{\pi m/2} \le 1.25332\,t$ (as $1.25332^2 \ge 1.5708$), and $\frac{401}{400}\cdot\frac32\cdot1.25332 \le 2\cdot0.94235$, $\frac{401}{400}\cdot\frac85 \ge 1.6$. Since $0.94235\,t - 0.8 \ge 0$ and $k(k+1) \ge k^2$, the third term of the left side is at most $(q+a)(0.94235\,t - 0.8)/k^2$.

Adding (a) times $\frac52$, (b) and (c) gives $\Phi/k^2$.

**Step 2: the right side is at least $(k - \frac12 + G)/k^2$.** By $\log(1+u) \ge u - \frac{u^2}2$ for $u \ge 0$ (`Parking.log_one_add_ge2`) at $u = \frac1k$ and at $u = x$, and $E_0 \ge 0$, the right side is at least $\frac1k - \frac1{2k^2} + E_0\bigl(x - \frac{x^2}2\bigr)$, which is $(k - \frac12 + G)/k^2$.

**Step 3: $\Phi < k - \frac12$ for $q \le 36$.** Here the gain is not needed. The tangent of the parabola at $t = \frac72$, that is $(t - \frac72)^2 \ge 0$, gives $t \le (m + 12.25)/7$, and $a^2/k \le a^2/265$. With $\alpha = 0.94235/7$ and $\beta = 12.25\,\alpha - 0.8$,

$$\Phi \;\le\; \alpha\,q^2 + \beta\,q \;+\; (4.0705 + \beta)\,a - \Bigl(\alpha - \frac{6.675}{265}\Bigr)a^2 .$$

The first two terms are at most their value at $q = 36$, which is less than $205.1$; the quadratic in $a$ has its maximum at $a = 22.478$, where it is less than $55.3$. So $\Phi < 264.5 \le k - \frac12$.

**Step 4: $\Phi < k - \frac12 + G$ for $q > 36$.** Let $s = \sqrt q \ge 6$; by (R1) $s^3 \le 1.036\,k$.

*The gain: $G \ge 0.305\,s^3$.* Let $S = 4.657\,s + 5.25$. Three lower bounds are multiplied.

- $E_0 \ge 2q/S$. First, $\mu^0_q(X) \ge \mu := 4(q-1)/S$ whenever $s \ge 6$ and $X \le 1.04\,s$: one checks $3\mu \le 2.577\,s - 2.75$ (that is $12(s^2-1) \le (2.577s - 2.75)\,S$), hence $\mu\,(2(4+X) + 3\mu) \le \mu\,(4.657\,s + 5.25) = 4(q-1)$, which is $(4 + X + 3\mu)^2 \le (4+X)^2 + 12(q-1)$ and so $\mu \le \mu^0_q(X)$. Here $X = q^2/(k-1) \le 1.04\,s$ because $s^3 \le 1.036\,k \le 1.04\,(k-1)$ for $k \ge 265$. Then $E_0 \ge \frac{q+2}{2q}\cdot\frac{4(q-1)}{S} \ge \frac{2q}{S}$, since $(q+2)(q-1) \ge q^2$.
- $x - \frac{x^2}2 \ge 0.998\,x$, because $0 \le x \le \frac{1}{k-1} \le \frac1{264}$.
- $k^2 x \ge \frac{q\,s}{s + 1.036}$: this is $k^2(s + 1.036) \ge s\,(k-1)(k+q)$, which follows from $1.036\,k \ge s^3 = s\,q$.

The product is $G \ge 0.998\cdot\frac{q\,s}{s+1.036}\cdot\frac{2q}{S} = \frac{1.996\,s^5}{(s+1.036)\,S} \ge 0.305\,s^3$, the last step being $0.305\,(s+1.036)(4.657\,s+5.25) \le 1.996\,s^2$ for $s \ge 6$.

*The polynomial inequality.* For $0 \le e \le \frac16$ and every real $w$,

$$L(e,w) := 4.0705\,(1-w)\,e + 6.9153\,(1-w)^2 e^2 + (2-w)\Bigl(\frac{18847}{24000}(w + 0.36) - 0.8\,e\Bigr) + \frac{e^3}{2} + 0.02 \;\le\; \frac{250}{259} + 0.305 .$$

Indeed $e^2 \le e/6$ and $e^3 \le e/36$ make $L - 0.02$ at most $(1 - 6e)\,A(w) + 6e\,B(w)$, where $A(w) = (2-w)\frac{18847}{24000}(w+0.36) \le 1.1$ (a quadratic in $w$ with its maximum at $w = 0.82$) and $B(w) = A(w) + \frac16\bigl(4.0705(1-w) + \frac{6.9153}{6}(1-w)^2 - 0.8(2-w) + \frac1{72}\bigr) \le 1.23$ (a quadratic with its maximum near $w = 0.3023$). So $L \le 1.25 \le \frac{250}{259} + 0.305$.

*Conclusion of the case.* The tangent of the parabola at $t = \frac35 s$ gives $t \le (m + 0.36\,s^2)/(1.2\,s)$, and $a^2/k \le 1.036\,a^2/s^3$ by (R1). Inserting both into $\Phi$ and writing $e = 1/s$, $w = m/q$, so that $a = s^2(1-w)$, $q + a = s^2(2-w)$, $\frac32\cdot4.45\cdot1.036 = 6.9153$ and $0.94235/1.2 = \frac{18847}{24000}$, one finds

$$\Phi + \frac12 + 0.02\,s^3 \;\le\; s^3\,L(e,w) \;\le\; s^3\Bigl(\frac{250}{259} + 0.305\Bigr) \;\le\; k + G,$$

because $\frac{250}{259}\,s^3 = s^3/1.036 \le k$ and $0.305\,s^3 \le G$. As $0.02\,s^3 > 0$, $\Phi < k - \frac12 + G$.

**Step 5: conclusion.** In both cases $\Phi < k - \frac12 + G$, since $G \ge 0$. Dividing by $k^2$ and using Steps 1 and 2, the left side of the statement is at most $\Phi/k^2 < (k - \frac12 + G)/k^2$, which is at most the right side.

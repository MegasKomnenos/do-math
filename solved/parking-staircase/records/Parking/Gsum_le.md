---
weight: unit
short: upper bound of the sum G of the pair side
---
## Description

For natural numbers $R\ge42$ and $k$ with $R^{3/2}\le1.07593\,k$, and $s=\sqrt R$: $G(k,R)\le2\,(0.478731\,s^3-0.974453\,s^2+0.642741\,s)$, where $G(k,R)$ is the sum of the convolutions $\kappa_2$, $\kappa_3$ of the Poisson mass that multiplies the logarithmic coefficient in the lower bound of the pair sum.

## Statement

Let $P(m)=e^{-m}m^m/m!$ be the Poisson mass (`Parking.poissonMass`), and let
$$\kappa_2(m)=\sum_{g=1}^{m-1}P(g)\,P(m-g),\qquad\kappa_3(m)=\sum_{g=1}^{m-1}\kappa_2(g)\,P(m-g)$$
(`Parking.kc2`, `Parking.kc3`). For natural numbers $k$ and $R$ let
$$G(k,R)=\sum_{b=1}^{R}\Bigl(\frac72\,\kappa_2(b)+2\,\kappa_3(b)\Bigr)+\sum_{c=1}^{R-1}\kappa_3(c)\,(1+\varrho_c),\qquad\varrho_c=\frac{c}{2\,(k+R-c)}+\frac{c^2}{8\,(k+R-c)^2}$$
(`Parking.Gsum`, `Parking.rhoC`). Let $R\ge42$ and $k$ be natural numbers with $(\sqrt R)^3\le1.07593\,k$, and put $s=\sqrt R$. Then
$$G(k,R)\ \le\ 2\,\bigl(0.478731\,s^3-0.974453\,s^2+0.642741\,s\bigr).$$

## Explanation

**What the statement is for.** The lower bound `Parking.pairSum_ge` of the pair sum contains, with a negative sign, the term $\bigl(\log(1+\theta)-\frac{\theta}{1+\theta}\bigr)\,G(k,R)+\frac{1}{k(1+\theta)}\,\mathcal A(k,R)$, in which $\theta\ge0$ is a free parameter and $\mathcal A$ is the sum `Parking.Asum`. The coefficient of $G$ is nonnegative, so an upper bound of $G$ is what makes the lower bound of the pair sum usable. The present statement gives it as a polynomial in $s=\sqrt R$; `Parking.Asum_le` does the same for $\mathcal A$ and `Parking.Wsum_ge` bounds the third sum $W_\Sigma$ from below. The three are hypotheses of `Parking.pair_numeric` in the proof of `Parking.curve_step_pos`.

**The hypothesis on $k$.** The sum depends on $k$ only through the corrections $\varrho_c$, which decrease as $k$ grows. The hypothesis $s^3\le1.07593\,k$ is used for one thing: it gives $\varrho_c\le0.560302\,c/s^3$ for $c\le R$. It is the form in which `Parking.k_window` states that the position lies on the curve $k^2=(n-k)^3$.

**Why the bound has this form.** Write $q_0(s)=0.478731\,s^2-0.974453\,s+0.642741$. The right side is $G_0=2s\,q_0(s)$, and the bound of `Parking.Asum_le` is $A_0=s^3\,q_0(s)$, so $G_0=2A_0/s^2$. This relation is intended. `Parking.pair_numeric` chooses $\theta=R/(2k)$, and for this value $\frac{\theta}{1+\theta}\,G_0=\frac{1}{k(1+\theta)}\,A_0$, so that after the two sums are replaced by their bounds the terms without a logarithm cancel. The polynomial $q_0$ is fitted to $\mathcal A$: its three coefficients are the leading coefficients of the bound that the proof of `Parking.Asum_le` assembles, as the record of that statement shows. The bound of $G$ is therefore the one that has room. With the power sums replaced by their bounds, $c_0=1/\sqrt{2\pi}$ by its upper bound $0.39894229$ and $\frac{1}{2s}$ by its value at $s=6.48$, the left side of the inequality in Step 7 of the proof below becomes the polynomial $0.79788\,s^3-1.16059\,s^2+0.86437\,s-0.36737$ (coefficients rounded to five decimals). Its leading coefficient is $2\cdot0.39894229$, against the leading coefficient $0.957462$ of $G_0$. In floating point, which is not part of any proof, at $R=42$ and $k=253$ the value of $G$ is $169.06$, this polynomial is $173.67$ and $G_0$ is $187.09$.

**How the proof is organised.** The sum $G$ contains $\kappa_2$ and $\kappa_3$ with positive coefficients, and an upper bound of $G$ is wanted, while the bound of $\kappa_2$ that the library has is a lower bound. The closed form $\kappa_3(b)=(b-1)P(b)-2\kappa_2(b)$ (`Parking.kc3_eq`) removes $\kappa_3$, and what remains of a term is $3(b-1)P(b)-\frac52\kappa_2(b)$: the Poisson mass with a nonnegative coefficient, for which Stirling's upper bound serves, and $\kappa_2$ with a negative coefficient, for which the lower bound `Parking.kc2_lower` serves. The terms are then sums of half-integer powers of $b$. Only the part of $G$ that carries the correction $\varrho_c$ is bounded more roughly, by $\kappa_3(c)\le c_0\sqrt c$.

**The Lean form.** The hypothesis is `Real.sqrt (R : ℝ) ^ 3 ≤ 1.07593 * (k : ℝ)` and the conclusion is `Gsum k R ≤ 2 * (0.478731 * Real.sqrt (R : ℝ) ^ 3 - 0.974453 * Real.sqrt (R : ℝ) ^ 2 + 0.642741 * Real.sqrt (R : ℝ))`; $k$ and $R$ are natural numbers cast to real numbers, and the decimal numbers are exact rational numbers. In `Gsum` the second sum runs over the natural numbers $c$ with $0<c<R$.

## Proof

Let $s=\sqrt R$, so that $R=s^2$ and $s\ge6.48$ (`Parking.sqrt_ge_648`), and let $c_0=1/\sqrt{2\pi}$ (`Parking.c0`), so that $0<c_0\le0.39894229$ (`Parking.c0_pos`, `Parking.c0_le`). The proof splits $G$ into a main part and a correction, reduces the main part to sums of powers of $b$, bounds the correction, and ends with an inequality between real numbers.

**Three bounds at one point.** They are used below.

(a) For $b\ge1$: $P(b)\le c_0/\sqrt b$. This is Stirling's bound `Parking.poissonMass_le_c0`.

(b) For $b\ge2$: $\kappa_2(b)\ge\frac12-\frac43\,c_0\,b^{-1/2}-\frac{c_0}{15}\,b^{-3/2}$. This is `Parking.kc2_lower`, $\kappa_2(b)\ge\frac12-\bigl(\frac43+\frac{1}{15b}\bigr)P(b)$, with (a) applied to $P(b)$, whose coefficient is negative.

(c) For $c\ge1$: $\kappa_3(c)\le c_0\sqrt c$. By `Parking.kc3_eq`, $\kappa_3(c)=(c-1)P(c)-2\kappa_2(c)$; since $\kappa_2(c)\ge0$ (`Parking.kc2_nonneg`) and $P(c)>0$ (`Parking.poissonMass_pos`), this is at most $c\,P(c)$, and $c\,P(c)\le c\cdot c_0/\sqrt c=c_0\sqrt c$ by (a).

**Step 1: main part and correction.** Since $\kappa_3(c)(1+\varrho_c)=\kappa_3(c)+\kappa_3(c)\varrho_c$,
$$G(k,R)=\sum_{b=1}^{R}\Bigl(\frac72\kappa_2(b)+2\kappa_3(b)\Bigr)+\sum_{c=1}^{R-1}\kappa_3(c)+\sum_{c=1}^{R-1}\kappa_3(c)\,\varrho_c .$$
The middle sum is at most $\sum_{b=1}^{R}\kappa_3(b)$, because the added term is nonnegative (`Parking.kc3_nonneg`). So $G(k,R)\le M+C$ with
$$M=\sum_{b=1}^{R}\Bigl(\frac72\kappa_2(b)+3\kappa_3(b)\Bigr),\qquad C=\sum_{c=1}^{R-1}\kappa_3(c)\,\varrho_c .$$

**Step 2: the main part without $\kappa_3$.** By `Parking.kc3_eq`, for $b\ge1$,
$$\frac72\kappa_2(b)+3\kappa_3(b)=3\,(b-1)\,P(b)-\frac52\,\kappa_2(b).$$
For $b=1$ the right side is zero, because $\kappa_2(1)=0$ (`Parking.kc2_one`). Hence $M=\sum_{b=2}^{R}\bigl(3(b-1)P(b)-\frac52\kappa_2(b)\bigr)$.

**Step 3: one term of the main part.** For $2\le b\le R$,
$$3\,(b-1)\,P(b)-\frac52\,\kappa_2(b)\ \le\ c_0\Bigl(3\sqrt b+\frac13\,\frac{1}{\sqrt b}+\frac16\,\frac{1}{b\sqrt b}\Bigr)-\frac54 .$$
This is `Parking.term_G`, an inequality between real numbers, applied with $p=\sqrt b$, $B=b$, and with $1\le b$, (a) and (b) as its hypotheses. It holds because the coefficient $3(b-1)$ of $P(b)$ is nonnegative and the coefficient of $\kappa_2(b)$ is negative, so that the upper bound (a) and the lower bound (b) may be inserted; the right side is what results.

**Step 4: the sum of the terms.** With
$$S_1=\sum_{b=2}^{R}\frac{1}{\sqrt b},\qquad S_2=\sum_{b=2}^{R}\frac{1}{b\sqrt b},\qquad S_3=\sum_{b=2}^{R}\sqrt b,$$
and since the interval $2\le b\le R$ has $R-1$ elements, Steps 2 and 3 give
$$M\ \le\ c_0\Bigl(3\,S_3+\frac13\,S_1+\frac16\,S_2\Bigr)-\frac54\,(R-1).$$

**Step 5: the correction.** Let $1\le c\le R-1$. The number $\varrho_c$ is nonnegative (`Parking.rhoC_nonneg`), and
$$\varrho_c\ \le\ 0.560302\,\frac{c}{s^3}.$$
This is `Parking.rho_bound`, which states: if $s\ge6.48$, $s^3\le1.07593\,k$, $0\le c\le s^2$ and $d\ge k$, then $\frac{c}{2d}+\frac{c^2}{8d^2}\le0.560302\,c/s^3$. It is applied with $d=k+R-c$, which is at least $k$ because $c\le R$; this is where the hypothesis on $k$ is used. With (c), $\kappa_3(c)\,\varrho_c\le c_0\sqrt c\cdot0.560302\,c/s^3$, and therefore
$$C\ \le\ \frac{0.560302\,c_0}{s^3}\,S_G,\qquad S_G=\sum_{c=1}^{R-1}c\sqrt c .$$

**Step 6: the power sums.** The statements of `PowerSums` give
$$S_1\le2s+\frac{1}{2s}-2.44948,\qquad S_2\le1.63300,\qquad S_3\le\frac23\,R\,s+\frac12\,s-1.17851,\qquad S_G\le\frac25\,R^2s$$
(`Parking.sum_Icc_two_inv_sqrt_le`, `Parking.sum_Icc_two_inv_sqrt_cube_le`, `Parking.sum_Icc_two_sqrt_le`, `Parking.sum_Ioo_sqrt_cube_le`).

**Step 7: the inequality between real numbers.** Under the hypotheses $s\ge6.48$, $R=s^2$, $0\le c_0\le0.39894229$ and the four bounds of Step 6, the statement `Parking.Gsum_numeric` concludes
$$c_0\Bigl(3\,S_3+\frac13\,S_1+\frac16\,S_2\Bigr)-\frac54\,(R-1)+\frac{0.560302\,c_0}{s^3}\,S_G\ \le\ 2\,\bigl(0.478731\,s^3-0.974453\,s^2+0.642741\,s\bigr).$$
The left side is the sum of the bounds of $M$ and $C$ from Steps 4 and 5, and $G(k,R)\le M+C$ by Step 1.

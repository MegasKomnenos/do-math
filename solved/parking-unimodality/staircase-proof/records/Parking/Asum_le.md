---
weight: unit
short: upper bound of the sum A of the pair side
---
## Description

For natural numbers $R\ge42$ and $k$ with $R^{3/2}\le1.07593\,k$, and $s=\sqrt R$: $\mathcal A(k,R)\le0.478731\,s^5-0.974453\,s^4+0.642741\,s^3$, where $\mathcal A(k,R)$ is the sum of the convolutions $\kappa_2$, $\kappa_3$ of the Poisson mass, weighted by distances to $R$, that multiplies the coefficient $1/(k(1+\theta))$ in the lower bound of the pair sum.

## Statement

Let $P(m)=e^{-m}m^m/m!$ be the Poisson mass (`Parking.poissonMass`), and let
$$\kappa_2(m)=\sum_{g=1}^{m-1}P(g)\,P(m-g),\qquad\kappa_3(m)=\sum_{g=1}^{m-1}\kappa_2(g)\,P(m-g)$$
(`Parking.kc2`, `Parking.kc3`). For natural numbers $k$ and $R$ let
$$\mathcal A(k,R)=\sum_{b=1}^{R}\Bigl(\bigl(R-\tfrac b2\bigr)\bigl(\kappa_2(b)+2\,\kappa_3(b)\bigr)+\tfrac52\,(R-b)\,\kappa_2(b)\Bigr)+\sum_{c=1}^{R-1}(R-c)\,\kappa_3(c)\,(1+\varrho_c),$$
$$\varrho_c=\frac{c}{2\,(k+R-c)}+\frac{c^2}{8\,(k+R-c)^2}$$
(`Parking.Asum`, `Parking.rhoC`). Let $R\ge42$ and $k$ be natural numbers with $(\sqrt R)^3\le1.07593\,k$, and put $s=\sqrt R$. Then
$$\mathcal A(k,R)\ \le\ 0.478731\,s^5-0.974453\,s^4+0.642741\,s^3 .$$

## Explanation

**What the statement is for.** The lower bound `Parking.pairSum_ge` of the pair sum contains, with a negative sign, the term $\frac{1}{k(1+\theta)}\,\mathcal A(k,R)$, in which $\theta\ge0$ is a free parameter. The present statement bounds $\mathcal A$ from above by a polynomial in $s=\sqrt R$. It is one of three statements of this kind, with `Parking.Wsum_ge` and `Parking.Gsum_le`, and the three are hypotheses of `Parking.pair_numeric` in the proof of `Parking.curve_step_pos`. Of the two sums that `Parking.pairSum_ge` subtracts, $\mathcal A$ gives the larger term. Measured by the bounds of the three statements and with $\theta=R/(2k)$, the choice of `Parking.pair_numeric`, the term $\frac{1}{k(1+\theta)}\mathcal A$ is about $0.4787\,s^5/k$. At a position on the curve, where $k$ is about $s^3$, this is about $0.96$ times the weight $W_\Sigma\approx s^2/2$ from which it is subtracted, while the term with $G$ is of the order $s$.

**Where the three coefficients come from.** The proof assembles an upper bound of $\mathcal A$ from bounds of sums of half-integer powers. With those sums replaced by their bounds and $c_0=1/\sqrt{2\pi}$ by its upper bound $0.39894229$, the assembled bound is a polynomial of degree five in $s$ whose three leading coefficients are
$$\tfrac65\cdot0.39894229=0.4787307\ldots,\qquad-\bigl(1-\tfrac{4}{35}\cdot0.560302\cdot0.39894229\bigr)=-0.9744539\ldots,\qquad\tfrac{29}{18}\cdot0.39894229=0.6427403\ldots$$
The three coefficients of the statement are these numbers rounded upwards in the sixth decimal. The remaining terms of the assembled bound, $-0.03541\,s^2+0.14628\,s-0.07126$ to five decimals, are negative for $s\ge6.48$ and are dropped. So the bound of the statement gives away almost nothing of the assembled bound. In floating point, which is not part of any proof, at $R=42$ the assembled bound is $3928.26$ and the bound of the statement is $3928.88$, while the value of $\mathcal A$ itself is $3863.76$ for $k=253$.

The leading coefficient $\frac65c_0$ arises as follows. After $\kappa_3$ is removed, the term of index $b$ has the main part $(3R-2b)(b-1)P(b)\approx c_0\,(3R-2b)\sqrt b$, and $\sum_{b\le R}(3R-2b)\sqrt b\approx3R\cdot\frac23R^{3/2}-2\cdot\frac25R^{5/2}=\frac65R^{5/2}$. The coefficient of $s^4$ comes from the constant $\frac12$ in the lower bound of $\kappa_2$: taken with the weights $\frac52R-b$ it sums to $R^2-\frac32R+\frac12$, and $R^2=s^4$. The part of $\mathcal A$ that carries the corrections $\varrho_c$ adds a term whose leading part is $\frac{4}{35}\cdot0.560302\,c_0\,s^4$, where $0.560302$ is the constant of the bound $\varrho_c\le0.560302\,c/s^3$.

**The common polynomial.** Write $q_0(s)=0.478731\,s^2-0.974453\,s+0.642741$. The bound of the statement is $s^3\,q_0(s)$ and the bound of `Parking.Gsum_le` is $2s\,q_0(s)$. The record of `Parking.Gsum_le` says why the two bounds are given with a common factor.

**The hypothesis on $k$.** As in `Parking.Gsum_le`, the sum depends on $k$ only through the corrections $\varrho_c$, and the hypothesis $s^3\le1.07593\,k$ is used only to bound them.

**The Lean form.** The hypothesis is `Real.sqrt (R : ℝ) ^ 3 ≤ 1.07593 * (k : ℝ)` and the conclusion is `Asum k R ≤ 0.478731 * Real.sqrt (R : ℝ) ^ 5 - 0.974453 * Real.sqrt (R : ℝ) ^ 4 + 0.642741 * Real.sqrt (R : ℝ) ^ 3`; $k$ and $R$ are natural numbers cast to real numbers, the differences $R-\frac b2$, $R-b$, $R-c$ in `Asum` are differences of real numbers, and the decimal numbers are exact rational numbers. In `Asum` the second sum runs over the natural numbers $c$ with $0<c<R$.

## Proof

The proof has the plan of the proof of `Parking.Gsum_le`, with the weights $R-\frac b2$, $R-b$ and $R-c$ in the sums. Let $s=\sqrt R$, so that $R=s^2$ and $s\ge6.48$ (`Parking.sqrt_ge_648`), and let $c_0=1/\sqrt{2\pi}$ (`Parking.c0`), so that $0<c_0\le0.39894229$ (`Parking.c0_pos`, `Parking.c0_le`).

**Three bounds at one point.** They are used below.

(a) For $b\ge1$: $P(b)\le c_0/\sqrt b$. This is Stirling's bound `Parking.poissonMass_le_c0`.

(b) For $b\ge2$: $\kappa_2(b)\ge\frac12-\frac43\,c_0\,b^{-1/2}-\frac{c_0}{15}\,b^{-3/2}$. This is `Parking.kc2_lower`, $\kappa_2(b)\ge\frac12-\bigl(\frac43+\frac{1}{15b}\bigr)P(b)$, with (a) applied to $P(b)$, whose coefficient is negative.

(c) For $c\ge1$: $\kappa_3(c)\le c_0\sqrt c$. By `Parking.kc3_eq`, $\kappa_3(c)=(c-1)P(c)-2\kappa_2(c)$; since $\kappa_2(c)\ge0$ (`Parking.kc2_nonneg`) and $P(c)>0$ (`Parking.poissonMass_pos`), this is at most $c\,P(c)$, and $c\,P(c)\le c_0\sqrt c$ by (a).

**Step 1: main part and correction.** Since $\kappa_3(c)(1+\varrho_c)=\kappa_3(c)+\kappa_3(c)\varrho_c$, and since the sum $\sum_{c=1}^{R-1}(R-c)\kappa_3(c)$ does not change when the term $c=R$, which is zero, is added to it, $\mathcal A(k,R)=M+C$ with
$$M=\sum_{b=1}^{R}\Bigl(\bigl(R-\tfrac b2\bigr)\bigl(\kappa_2(b)+2\kappa_3(b)\bigr)+\tfrac52(R-b)\kappa_2(b)+(R-b)\kappa_3(b)\Bigr),\qquad C=\sum_{c=1}^{R-1}(R-c)\,\kappa_3(c)\,\varrho_c .$$

**Step 2: the main part without $\kappa_3$.** In the term of index $b$ of $M$ the coefficient of $\kappa_3(b)$ is $2(R-\frac b2)+(R-b)=3R-2b$ and the coefficient of $\kappa_2(b)$ is $(R-\frac b2)+\frac52(R-b)=\frac72R-3b$. Inserting $\kappa_3(b)=(b-1)P(b)-2\kappa_2(b)$ (`Parking.kc3_eq`, for $b\ge1$) gives the term
$$(3R-2b)\,(b-1)\,P(b)-\bigl(\tfrac52R-b\bigr)\,\kappa_2(b).$$
For $b=1$ it is zero, because $\kappa_2(1)=0$ (`Parking.kc2_one`). Hence $M$ is the sum of these terms over $2\le b\le R$.

**Step 3: one term of the main part.** For $2\le b\le R$,
$$(3R-2b)(b-1)P(b)-\bigl(\tfrac52R-b\bigr)\kappa_2(b)\ \le\ c_0\Bigl(-2\,b\sqrt b+\bigl(3R+\tfrac23\bigr)\sqrt b+\bigl(\tfrac R3-\tfrac1{15}\bigr)\frac{1}{\sqrt b}+\frac R6\,\frac{1}{b\sqrt b}\Bigr)-\frac12\bigl(\tfrac52R-b\bigr).$$
This is `Parking.term_A`, an inequality between real numbers, applied with $p=\sqrt b$, $B=b$, and with $1\le b\le R$, (a) and (b) as its hypotheses. The range of $b$ matters here: for $1\le b\le R$ the coefficient $(3R-2b)(b-1)$ of $P(b)$ is nonnegative and the coefficient $\frac52R-b$ of $\kappa_2(b)$ is positive, so the upper bound (a) and the lower bound (b) may be inserted, and the right side is what results.

**Step 4: the sum of the terms.** Let
$$S_1=\sum_{b=2}^{R}\frac{1}{\sqrt b},\qquad S_2=\sum_{b=2}^{R}\frac{1}{b\sqrt b},\qquad S_3=\sum_{b=2}^{R}\sqrt b,\qquad S_4=\sum_{b=2}^{R}b\sqrt b .$$
The last terms of Step 3 sum to $\sum_{b=2}^{R}\frac12\bigl(\frac52R-b\bigr)=\frac12\bigl((R-1)\cdot\frac52R-\bigl(\frac{R(R+1)}{2}-1\bigr)\bigr)=R^2-\frac32R+\frac12$, by the formula for $2+3+\dots+R$. Steps 2 and 3 therefore give
$$M\ \le\ c_0\Bigl(-2\,S_4+\bigl(3R+\tfrac23\bigr)S_3+\bigl(\tfrac R3-\tfrac1{15}\bigr)S_1+\frac R6\,S_2\Bigr)-\Bigl(R^2-\frac32R+\frac12\Bigr).$$

**Step 5: the correction.** Let $1\le c\le R-1$. The number $\varrho_c$ is nonnegative (`Parking.rhoC_nonneg`), and
$$\varrho_c\ \le\ 0.560302\,\frac{c}{s^3}.$$
This is `Parking.rho_bound`, which states: if $s\ge6.48$, $s^3\le1.07593\,k$, $0\le c\le s^2$ and $d\ge k$, then $\frac{c}{2d}+\frac{c^2}{8d^2}\le0.560302\,c/s^3$. It is applied with $d=k+R-c$, which is at least $k$ because $c\le R$; this is where the hypothesis on $k$ is used. With (c) and $R-c\ge0$, $(R-c)\,\kappa_3(c)\,\varrho_c\le(R-c)\cdot c_0\sqrt c\cdot0.560302\,c/s^3$, and therefore
$$C\ \le\ \frac{0.560302\,c_0}{s^3}\,S_T,\qquad S_T=\sum_{c=1}^{R-1}c\sqrt c\,(R-c).$$

**Step 6: the power sums.** The statements of `PowerSums` give
$$S_1\le2s+\frac{1}{2s}-2.44948,\qquad S_2\le1.63300,\qquad S_3\le\frac23\,R\,s+\frac12\,s-1.17851,$$
$$S_4\ge\frac25\,R^2s+\frac12\,R\,s-0.84853,\qquad S_T\le\frac{4}{35}\,(R+1)^3\sqrt{R+1}$$
(`Parking.sum_Icc_two_inv_sqrt_le`, `Parking.sum_Icc_two_inv_sqrt_cube_le`, `Parking.sum_Icc_two_sqrt_le`, `Parking.sum_Icc_two_sqrt_cube_ge`, `Parking.sum_Ioo_sqrt_cube_mul_le`). The sum $S_4$ has the negative coefficient $-2c_0$ in Step 4, which is why a lower bound of it is used.

**Step 7: the inequality between real numbers.** Under the hypotheses $s\ge6.48$, $R=s^2$, $0\le c_0\le0.39894229$ and the five bounds of Step 6, the statement `Parking.Asum_numeric` concludes
$$c_0\Bigl(-2\,S_4+\bigl(3R+\tfrac23\bigr)S_3+\bigl(\tfrac R3-\tfrac1{15}\bigr)S_1+\frac R6\,S_2\Bigr)-\Bigl(R^2-\frac32R+\frac12\Bigr)+\frac{0.560302\,c_0}{s^3}\,S_T\ \le\ 0.478731\,s^5-0.974453\,s^4+0.642741\,s^3 .$$
The left side is the sum of the bounds of $M$ and $C$ from Steps 4 and 5, and $\mathcal A(k,R)=M+C$ by Step 1.

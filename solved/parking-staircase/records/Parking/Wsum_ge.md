---
weight: unit
short: lower bound of the total weight of the pairs
---
## Description

For every natural number $R\ge42$: $W_\Sigma(R)\ge\frac R2-1.06385\,\sqrt R+0.7184$, where $W_\Sigma(R)=\sum_{b=1}^{R}\kappa_2(b)$ and $\kappa_2$ is the convolution of the Poisson mass $e^{-m}m^m/m!$ with itself.

## Statement

Let $P(m)=e^{-m}m^m/m!$ be the Poisson mass (`Parking.poissonMass`), let $\kappa_2(b)=\sum_{g=1}^{b-1}P(g)\,P(b-g)$ (`Parking.kc2`), and let $W_\Sigma(R)=\sum_{b=1}^{R}\kappa_2(b)$ (`Parking.Wsum`). Then for every natural number $R\ge42$,
$$\frac R2-1.06385\,\sqrt R+0.7184\ \le\ W_\Sigma(R).$$

## Explanation

**What the statement is for.** $W_\Sigma(R)$ is the total weight of the pairs of marked cut points in the lower bound `Parking.pairSum_ge` of the pair sum; its record `Parking.Wsum` says where it comes from. That lower bound is stated with three sums of the convolutions $\kappa_2$ and $\kappa_3$, namely $W_\Sigma$, $G$ and $\mathcal A$. The present statement, `Parking.Gsum_le` and `Parking.Asum_le` replace the three sums by polynomials in the one variable $s=\sqrt R$, so that the comparison which proves `Parking.curve_step_pos` becomes an inequality in $s$. There the statement is a hypothesis of `Parking.pair_numeric`, and the polynomial $W_0(s)=\frac{s^2}{2}-1.06385\,s+0.7184$ on the left is the factor that the final lower bound of the pair sum carries.

**Where the three constants come from.** Each term satisfies $\kappa_2(b)\ge\frac12-\frac43\,c_0\,b^{-1/2}-\frac{c_0}{15}\,b^{-3/2}$ with $c_0=1/\sqrt{2\pi}$, by `Parking.kc2_lower` and Stirling's bound. Summed over $2\le b\le R$, the constant $\frac12$ gives $\frac{R-1}{2}$. The sum of $b^{-1/2}$ is about $2\sqrt R$, which gives the term $-\frac83c_0\,s$; the number $\frac83c_0$ is $1.0638461\ldots$, and $1.06385$ is this number rounded up. The constant $0.7184$ collects what is left: $-\frac12$, the constant $2.44948$ in the bound of $\sum b^{-1/2}$, the term $\frac{1}{2s}$ of that bound, taken at $s=6.48$ where it is largest, and the bound $1.63300$ of $\sum b^{-3/2}$. With $c_0$ replaced by its upper bound $0.39894229$ these add up to $0.71845\ldots$, so the constant has room only in the fifth decimal. The polynomial is thus the beginning of the expansion of the sum in powers of $s$, rounded in the direction that keeps the inequality.

**How sharp it is.** In floating point, which is not part of any proof, $W_\Sigma(42)=14.9157$ and the bound is $14.8239$, a difference of $0.6$ per cent.

**The range.** The hypothesis $R\ge42$ is the range of `Parking.curve_step_pos`. In the proof it is used as $\sqrt R\ge6.48$, which the constant $0.7184$ needs.

**The Lean form.** The statement is `(R : ℝ) / 2 - 1.06385 * Real.sqrt (R : ℝ) + 0.7184 ≤ Wsum R`, with $R$ a natural number cast to a real number. The decimal numbers are exact rational numbers.

## Proof

Let $R\ge42$, $s=\sqrt R$, so that $R=s^2$, and $c_0=1/\sqrt{2\pi}$ (`Parking.c0`).

*The sum from $b=2$.* All terms of $W_\Sigma(R)$ are nonnegative (`Parking.kc2_nonneg`), so $\sum_{b=2}^{R}\kappa_2(b)\le W_\Sigma(R)$.

*One term.* For $b\ge2$,
$$\kappa_2(b)\ \ge\ \frac12-\frac43\,c_0\,\frac{1}{\sqrt b}-\frac{c_0}{15}\,\frac{1}{b\sqrt b}.$$
Indeed `Parking.kc2_lower` gives $\kappa_2(b)\ge\frac12-\bigl(\frac43+\frac1{15b}\bigr)P(b)$, the coefficient $\frac43+\frac{1}{15b}$ is positive, and $P(b)\le c_0/\sqrt b$ by Stirling's bound `Parking.poissonMass_le_c0`.

*The sum of the terms.* The interval $2\le b\le R$ has $R-1$ elements. Summing the last inequality over it gives
$$\sum_{b=2}^{R}\kappa_2(b)\ \ge\ \frac{R-1}{2}-\frac43\,c_0\,S_1-\frac{c_0}{15}\,S_2,\qquad S_1=\sum_{b=2}^{R}\frac{1}{\sqrt b},\quad S_2=\sum_{b=2}^{R}\frac{1}{b\sqrt b}.$$

*The two power sums.* `Parking.sum_Icc_two_inv_sqrt_le` gives $S_1\le2s+\frac{1}{2s}-2.44948$, and `Parking.sum_Icc_two_inv_sqrt_cube_le` gives $S_2\le1.63300$.

*The inequality between real numbers.* By `Parking.sqrt_ge_648`, $s\ge6.48$; by `Parking.c0_pos` and `Parking.c0_le`, $0\le c_0\le0.39894229$. Under exactly these hypotheses on $s$, $R=s^2$, $c_0$, $S_1$ and $S_2$, the statement `Parking.Wsum_numeric` concludes
$$\frac R2-1.06385\,s+0.7184\ \le\ \frac{R-1}{2}-\frac43\,c_0\,S_1-\frac{c_0}{15}\,S_2 .$$
The three displayed inequalities and the first step together give the claim.

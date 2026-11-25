---
weight: step
short: lower bound for the sum of b^(3/2) over 2 ≤ b ≤ R
---
## Description

$\frac25R^2\sqrt R+\frac12R\sqrt R-0.84853\le\sum_{b=2}^{R}b\sqrt b$ for every natural number $R\ge2$.

## Statement

For every natural number $R\ge2$,
$$\frac25\,R^{2}\sqrt R+\frac12\,R\sqrt R-0.84853\ \le\ \sum_{b=2}^{R}b\sqrt b .$$

## Explanation

**The comparison behind the bound.** The function $x^{3/2}$ is convex, so the mean of its two end values on an interval is at least its mean over the interval (the trapezoid rule): $\frac12\bigl(b^{3/2}+(b+1)^{3/2}\bigr)\ge\int_b^{b+1}x^{3/2}\,dx$. Adding this for $2\le b\le R-1$ gives $\sum_{b=2}^{R}b^{3/2}-\frac12\bigl(2^{3/2}+R^{3/2}\bigr)\ge\frac25\bigl(R^{5/2}-2^{5/2}\bigr)$, that is,
$$\sum_{b=2}^{R}b^{3/2}\ \ge\ \frac25R^{5/2}+\frac12R^{3/2}-\frac35\sqrt2 .$$
The statement is this bound with $\frac35\sqrt2=0.848528\ldots$ rounded up. The proof does not use integrals; the trapezoid inequality becomes a polynomial identity in $\sqrt b$ and $\sqrt{b+1}$.

**Where it is used.** This is the one lower bound among the bounds for sums of half-integer powers. It is needed for the sum $\mathcal A$ of the lower bound of the pair sum (`Parking.Asum`, `Parking.pairSum_ge`), which is bounded from above by a polynomial in $\sqrt R$. After the closed form of $\kappa_3$ (`Parking.kc3_eq`) is inserted, the main part of $\mathcal A$ contains the terms $(3R-2b)(b-1)P(b)$ with the Poisson mass $P(b)=e^{-b}b^b/b!$, and it is bounded termwise with Stirling's bound $P(b)\le c_0/\sqrt b$, $c_0=1/\sqrt{2\pi}$. The part $-2b^2P(b)$ of these terms leads to the sum of $b^{3/2}$ with the negative coefficient $-2c_0$, and an upper bound of $\mathcal A$ then requires a lower bound of that sum. The part $3Rb\,P(b)$ leads to $3R$ times the sum of $b^{1/2}$, which is bounded from above by `Parking.sum_Icc_two_sqrt_le`. The leading terms of the two bounds combine to $c_0\bigl(-2\cdot\frac25+3\cdot\frac23\bigr)R^{5/2}=\frac65c_0R^{5/2}$, the leading term of the bound of $\mathcal A$; since this is a difference of two larger terms, the second-order terms $\frac12R^{3/2}$ and $\frac12R^{1/2}$ of the two bounds are needed as well.

**The Lean form.** The summand is `b * Real.sqrt b`, the sum runs over `Finset.Icc 2 R`, and $R^{5/2}$, $R^{3/2}$ are written `R ^ 2 * Real.sqrt R`, `R * Real.sqrt R`.

## Proof

**Telescoping.** If $g,\Gamma:\mathbb R\to\mathbb R$ satisfy $g(b+1)\le\Gamma(b+1)-\Gamma(b)$ for every natural number $b$, then $\sum_{b=m+1}^{n}g(b)\le\Gamma(n)-\Gamma(m)$ for all natural numbers $m\le n$; this is an induction on $n$. It is applied below to $-g$ and $-\Gamma$, that is, in the form: if $\Gamma(b+1)-\Gamma(b)\le g(b+1)$ for every $b$, then $\Gamma(n)-\Gamma(m)\le\sum_{b=m+1}^{n}g(b)$.

**The trapezoid inequality.** For real $y\ge0$,
$$\frac25\Bigl((y+1)^{2}\sqrt{y+1}-y^{2}\sqrt y\Bigr)\ \le\ \frac{y\sqrt y+(y+1)\sqrt{y+1}}{2}.$$
Put $p=\sqrt y$ and $q=\sqrt{y+1}$, so $0\le p\le q$ and $q^2-p^2=1$. The claim is $\frac25(q^5-p^5)\le\frac{p^3+q^3}{2}\,(q^2-p^2)$, and
$$\frac{p^3+q^3}{2}\,(q^2-p^2)-\frac25\,(q^5-p^5)=\frac{(q-p)^3\,(q^2+3qp+p^2)}{10}\ \ge\ 0 ,$$
an identity that is checked by expanding.

**The sum.** Let $\Gamma(x)=\frac25x^2\sqrt x+\frac12x\sqrt x$. By the trapezoid inequality at $y=b$,
$$\Gamma(b+1)-\Gamma(b)\ \le\ \frac{b\sqrt b+(b+1)\sqrt{b+1}}{2}+\frac{(b+1)\sqrt{b+1}-b\sqrt b}{2}=(b+1)\sqrt{b+1}.$$
The telescoping statement with $g(x)=x\sqrt x$, $m=2$ and $n=R$ gives $\Gamma(R)-\Gamma(2)\le\sum_{b=3}^{R}b\sqrt b$. Adding the term $b=2$, which is $2\sqrt2$,
$$\Gamma(R)-\bigl(\Gamma(2)-2\sqrt2\bigr)\ \le\ \sum_{b=2}^{R}b\sqrt b,\qquad\Gamma(2)-2\sqrt2=\Bigl(\frac85+1-2\Bigr)\sqrt2=\frac35\sqrt2 .$$
Finally $\frac35\sqrt2\le0.84853$, because $2\le1.414216^2$ gives $\sqrt2\le1.414216$ and $\frac35\cdot1.414216=0.8485296$.

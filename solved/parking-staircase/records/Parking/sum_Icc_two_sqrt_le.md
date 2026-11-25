---
weight: step
short: upper bound for the sum of b^(1/2) over 2 ≤ b ≤ R
---
## Description

$\sum_{b=2}^{R}\sqrt b\le\frac23R\sqrt R+\frac12\sqrt R-1.17851$ for every natural number $R\ge2$.

## Statement

For every natural number $R\ge2$,
$$\sum_{b=2}^{R}\sqrt b\ \le\ \frac23\,R\sqrt R+\frac12\,\sqrt R-1.17851 .$$

## Explanation

**The comparison behind the bound.** The function $\sqrt x$ is concave, so the mean of its two end values on an interval is at most its mean over the interval (the trapezoid rule): $\frac12\bigl(\sqrt b+\sqrt{b+1}\bigr)\le\int_b^{b+1}\sqrt x\,dx$. Adding this for $2\le b\le R-1$ gives $\sum_{b=2}^{R}\sqrt b-\frac12\bigl(\sqrt2+\sqrt R\bigr)\le\frac23\bigl(R^{3/2}-2^{3/2}\bigr)$, that is,
$$\sum_{b=2}^{R}\sqrt b\ \le\ \frac23R^{3/2}+\frac12\sqrt R-\frac56\sqrt2 .$$
The statement is this bound with $\frac56\sqrt2=1.178511\ldots$ rounded down. The proof does not use integrals; the trapezoid inequality becomes a polynomial identity in $\sqrt b$ and $\sqrt{b+1}$.

**Where it is used.** The sums $G$ and $\mathcal A$ of the lower bound of the pair sum (`Parking.Gsum`, `Parking.Asum`, `Parking.pairSum_ge`) are bounded from above by polynomials in $\sqrt R$. Their main parts contain the Poisson mass $P(b)=e^{-b}b^b/b!$ with coefficients of the order $b$, and with Stirling's bound $P(b)\le c_0/\sqrt b$, $c_0=1/\sqrt{2\pi}$, this produces the sum of $\sqrt b$ over $2\le b\le R$ with a positive coefficient, so that an upper bound is required. The sum starts at $b=2$ because the terms of $G$ and $\mathcal A$ at $b=1$ vanish. The second term $\frac12\sqrt R$ and the constant matter: the comparison in which these bounds end has little room at its smallest case $R=42$.

**The Lean form.** The summand is `Real.sqrt b`, the sum runs over `Finset.Icc 2 R`, and $R^{3/2}$ is written `R * Real.sqrt R`.

## Proof

**Telescoping.** If $g,\Gamma:\mathbb R\to\mathbb R$ satisfy $g(b+1)\le\Gamma(b+1)-\Gamma(b)$ for every natural number $b$, then $\sum_{b=m+1}^{n}g(b)\le\Gamma(n)-\Gamma(m)$ for all natural numbers $m\le n$; this is an induction on $n$.

**The trapezoid inequality.** For real $y\ge0$,
$$\frac{\sqrt y+\sqrt{y+1}}{2}\ \le\ \frac23\Bigl((y+1)\sqrt{y+1}-y\sqrt y\Bigr).$$
Put $p=\sqrt y$ and $q=\sqrt{y+1}$, so $0\le p\le q$ and $q^2-p^2=1$. The claim is $\frac{p+q}{2}\,(q^2-p^2)\le\frac23(q^3-p^3)$, and
$$\frac23\,(q^3-p^3)-\frac{p+q}{2}\,(q^2-p^2)=\frac{(q-p)^3}{6}\ \ge\ 0 .$$

**The sum.** Let $\Gamma(x)=\frac23x\sqrt x+\frac12\sqrt x$. By the trapezoid inequality at $y=b$,
$$\Gamma(b+1)-\Gamma(b)=\frac23\Bigl((b+1)\sqrt{b+1}-b\sqrt b\Bigr)+\frac12\bigl(\sqrt{b+1}-\sqrt b\bigr)\ \ge\ \frac{\sqrt b+\sqrt{b+1}}{2}+\frac{\sqrt{b+1}-\sqrt b}{2}=\sqrt{b+1}.$$
The telescoping statement with $g(x)=\sqrt x$, $m=2$ and $n=R$ gives $\sum_{b=3}^{R}\sqrt b\le\Gamma(R)-\Gamma(2)$. Adding the term $b=2$,
$$\sum_{b=2}^{R}\sqrt b\ \le\ \Gamma(R)-\bigl(\Gamma(2)-\sqrt2\bigr),\qquad\Gamma(2)-\sqrt2=\Bigl(\frac43+\frac12-1\Bigr)\sqrt2=\frac56\sqrt2 .$$
Finally $\frac56\sqrt2\ge1.17851$, because $1.414212^2\le2$ gives $\sqrt2\ge1.414212$ and $\frac56\cdot1.414212=1.17851$.

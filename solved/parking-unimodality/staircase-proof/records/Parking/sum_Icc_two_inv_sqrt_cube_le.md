---
weight: step
short: upper bound for the sum of b^(-3/2) over 2 ≤ b ≤ R
---
## Description

$\sum_{b=2}^{R}\frac{1}{b\sqrt b}\le1.63300$ for every natural number $R$.

## Statement

For every natural number $R$,
$$\sum_{b=2}^{R}\frac{1}{b\sqrt b}\ \le\ 1.63300 .$$
For $R\le1$ the sum is empty.

## Explanation

**The comparison behind the bound.** The function $x^{-3/2}$ is convex, so $b^{-3/2}\le\int_{b-1/2}^{b+1/2}x^{-3/2}\,dx$, and adding this for $2\le b\le R$ gives $\sum_{b=2}^{R}b^{-3/2}\le\int_{3/2}^{R+1/2}x^{-3/2}\,dx=\frac{2}{\sqrt{3/2}}-\frac{2}{\sqrt{R+1/2}}$. The second term is dropped, which makes the bound uniform in $R$, and $2/\sqrt{3/2}=1.632993\ldots$ is rounded up. The proof does not use integrals; the midpoint inequality is proved directly.

**Where it is used.** The three sums $W_\Sigma$, $G$, $\mathcal A$ of the lower bound of the pair sum (`Parking.Wsum`, `Parking.Gsum`, `Parking.Asum`, `Parking.pairSum_ge`) are bounded by polynomials in $\sqrt R$. On the way the convolution $\kappa_2(b)$ of the Poisson mass (`Parking.kc2`) is bounded from below, for $b\ge2$, by $\frac12$ minus a multiple of $b^{-1/2}$ minus a multiple of $b^{-3/2}$; the last term comes from the correction $\frac{1}{15b}$ in `Parking.sbirth_ge`. The sum of $b^{-3/2}$ over $2\le b\le R$ occurs in all three bounds with a small coefficient, each time in a place where an upper bound is required.

**The Lean form.** The summand is `1 / (b * Real.sqrt b)`, the sum runs over `Finset.Icc 2 R`, and the bound is the rational number `1.63300`.

## Proof

**Telescoping.** If $g,\Gamma:\mathbb R\to\mathbb R$ satisfy $g(b+1)\le\Gamma(b+1)-\Gamma(b)$ for every natural number $b$, then $\sum_{b=m+1}^{n}g(b)\le\Gamma(n)-\Gamma(m)$ for all natural numbers $m\le n$; this is an induction on $n$.

**The midpoint inequality.** For real $y\ge0$,
$$\frac{1}{(y+1)\sqrt{y+1}}\ \le\ \frac{2}{\sqrt{y+\frac12}}-\frac{2}{\sqrt{y+\frac32}}.$$
Write $u=\sqrt{y+\frac32}$ and $w=\sqrt{y+\frac12}$, so $u\ge w>0$ and $u^2-w^2=1$. The right side is $\frac{2(u-w)}{uw}$. Two facts are used. First, $uw\le\frac{u^2+w^2}{2}=y+1$. Second, $\frac{1}{\sqrt{y+1}}\le2(u-w)$: from the first fact, $(u+w)^2=2(y+1)+2uw\le4(y+1)$, so $u+w\le2\sqrt{y+1}$ and $1=(u-w)(u+w)\le(u-w)\cdot2\sqrt{y+1}$. Hence
$$\frac{1}{(y+1)\sqrt{y+1}}\ \le\ \frac{2(u-w)}{y+1}\ \le\ \frac{2(u-w)}{uw}.$$

**The sum.** For $R=0$ the sum is empty and the claim is $0\le1.633$. For $R\ge1$ apply the telescoping statement with $g(x)=\frac{1}{x\sqrt x}$, $\Gamma(x)=-\frac{2}{\sqrt{x+1/2}}$, $m=1$ and $n=R$; the hypothesis is the midpoint inequality at $y=b$. This gives
$$\sum_{b=2}^{R}\frac{1}{b\sqrt b}\ \le\ \frac{2}{\sqrt{3/2}}-\frac{2}{\sqrt{R+\frac12}}\ \le\ \frac{2}{\sqrt{3/2}}.$$
Finally $\frac{2}{\sqrt{3/2}}\le1.633$, because $1.224744^2\le\frac32$ gives $\sqrt{\frac32}\ge1.224744$, and $1.633\cdot1.224744\ge2$.

---
weight: step
short: upper bound for the sum of b^(-1/2) over 2 ≤ b ≤ R
---
## Description

$\sum_{b=2}^{R}\frac{1}{\sqrt b}\le2\sqrt R+\frac{1}{2\sqrt R}-2.44948$ for every natural number $R\ge2$.

## Statement

For every natural number $R\ge2$,
$$\sum_{b=2}^{R}\frac{1}{\sqrt b}\ \le\ 2\sqrt R+\frac{1}{2\sqrt R}-2.44948 .$$

## Explanation

**The comparison behind the bound.** The function $x^{-1/2}$ is convex, so its value at the midpoint of an interval is at most its mean over the interval: $b^{-1/2}\le\int_{b-1/2}^{b+1/2}x^{-1/2}\,dx$. Adding this for $2\le b\le R$ gives $\sum_{b=2}^{R}b^{-1/2}\le\int_{3/2}^{R+1/2}x^{-1/2}\,dx=2\sqrt{R+\frac12}-2\sqrt{\frac32}$. The statement is this bound in a form without nested roots: $\sqrt{R+\frac12}$ is replaced by the larger $\sqrt R+\frac{1}{4\sqrt R}$, and the constant $2\sqrt{3/2}=2.449489\ldots$ is rounded down to five decimals. The proof does not use integrals; the midpoint inequality is proved directly.

**Where it is used, and why with this precision.** The three sums $W_\Sigma$, $G$, $\mathcal A$ of the lower bound of the pair sum (`Parking.Wsum`, `Parking.Gsum`, `Parking.Asum`, `Parking.pairSum_ge`) are bounded by polynomials in $\sqrt R$. On the way the convolution $\kappa_2(b)$ of the Poisson mass (`Parking.kc2`) is bounded from below, for $b\ge2$, by $\frac12$ minus multiples of $b^{-1/2}$ and $b^{-3/2}$, and the Poisson mass itself from above by a multiple of $b^{-1/2}$. The sums of these powers over $2\le b\le R$ are then needed, and they start at $b=2$ because $\kappa_2(1)=0$. The sum of $b^{-1/2}$ occurs in all three bounds, each time in a place where an upper bound is required. The term $-2.44948$ is kept to five decimals because the comparison in which these bounds end has little room at its smallest case $R=42$; the cruder estimate $\sum_{b=2}^{R}b^{-1/2}\le2\sqrt R-2$, which follows from the monotonicity of $x^{-1/2}$ alone, is weaker by $0.449-\frac{1}{2\sqrt R}$, which is $0.37$ at $R=42$.

**The Lean form.** The summand is `1 / Real.sqrt b` and the sum runs over `Finset.Icc 2 R`. The decimal `2.44948` is a rational number.

## Proof

**Telescoping.** If $g,\Gamma:\mathbb R\to\mathbb R$ satisfy $g(b+1)\le\Gamma(b+1)-\Gamma(b)$ for every natural number $b$, then $\sum_{b=m+1}^{n}g(b)\le\Gamma(n)-\Gamma(m)$ for all natural numbers $m\le n$; this is an induction on $n$.

**The midpoint inequality.** For real $y\ge0$,
$$\frac{1}{\sqrt{y+1}}\ \le\ 2\sqrt{y+\tfrac32}-2\sqrt{y+\tfrac12}.$$
Write $u=\sqrt{y+\frac32}$ and $w=\sqrt{y+\frac12}$, so $u\ge w>0$ and $u^2-w^2=1$. By the inequality between the geometric and the arithmetic mean, $uw\le\frac{u^2+w^2}{2}=y+1$. Hence $(u+w)^2=2(y+1)+2uw\le4(y+1)$, that is, $u+w\le2\sqrt{y+1}$. Then $1=(u-w)(u+w)\le(u-w)\cdot2\sqrt{y+1}$, and dividing by $\sqrt{y+1}$ gives the claim.

**The sum.** Apply the telescoping statement with $g(x)=1/\sqrt x$, $\Gamma(x)=2\sqrt{x+\frac12}$, $m=1$ and $n=R$; the hypothesis is the midpoint inequality at $y=b$. This gives
$$\sum_{b=2}^{R}\frac{1}{\sqrt b}\ \le\ 2\sqrt{R+\tfrac12}-2\sqrt{\tfrac32}.$$
Two elementary estimates finish the proof. First, $\sqrt{R+\frac12}\le\sqrt R+\frac{1}{4\sqrt R}$, because the square of the right side is $R+\frac12+\frac{1}{16R}\ge R+\frac12$. Second, $2\sqrt{\frac32}\ge2.44948$, because $1.22474^2\le\frac32$. Together, $2\sqrt{R+\frac12}-2\sqrt{\frac32}\le2\sqrt R+\frac{1}{2\sqrt R}-2.44948$.

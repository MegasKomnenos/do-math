---
weight: unit
short: property K under the factor (z+a)(z+b)/z
---
## Description

Property K at $k>1$ is preserved when the three values are multiplied by the values at $k-1$, $k$, $k+1$ of $z\mapsto(z+a)(z+b)/z$, where $a,b\ge 0$ and $ab\le k^2-1$, provided the middle value is nonnegative.

## Statement

Let $k>1$ be real, let $(a',b',c')$ have property K at $k$ (`Parking.FirstLayer.TK`) with $b'\ge 0$, and let $a,b\ge 0$ be real with $ab\le k^2-1$. Then the triple
$$\Big(\frac{(k-1+a)(k-1+b)}{k-1}\,a',\ \ \frac{(k+a)(k+b)}{k}\,b',\ \ \frac{(k+1+a)(k+1+b)}{k+1}\,c'\Big)$$
has property K at $k$.

## Explanation

With $b=0$ the factor is $z\mapsto z+a$: the three values are multiplied by $k-1+a$, $k+a$, $k+1+a$. This is the only case the library uses. In `Parking.FirstLayer.zrT_weak_requirement` it turns property K of the diagonal triple of tilted masses (`Parking.FirstLayer.kernel_TK`) into a convexity in which the three masses carry the weights $c-1$, $c$, $c+1$, for every real $c\ge k$; this is the form in which the first layer enters the induction over all sizes (`Parking.DeltaId_nonneg`).

The factor $F(z)=(z+a)(z+b)/z=z+a+b+ab/z$ is of a different kind from the factor $(z+\alpha)/(z+\beta)$ of `Parking.FirstLayer.TK.mul_ratio`: it contains the division by $z$, which decreases. The condition $ab\le k^2-1$ is what keeps $F(k-1)\le F(k+1)$, since $F(k+1)-F(k-1)=2\,(1-ab/(k^2-1))$. As in `Parking.FirstLayer.TK.mul_ratio`, the second requirement is the convexity of $z\mapsto z\log F(z)$ at $k-1,k,k+1$.

## Proof

The proof uses two facts established in the proof of `Parking.FirstLayer.TK.mul_ratio`. (i) If $k>0$, $(a',b',c')$ has property K at $k$ with $b'\ge 0$, and $f_-,f_0,f_+>0$ satisfy $f_-\le f_+$ and $(k+1)\log(f_+/f_0)+(k-1)\log(f_-/f_0)\ge 0$, then $(f_-a',f_0b',f_+c')$ has property K at $k$. (ii) For $k>1$, the logarithmic condition holds as soon as $f_+/f_0=1+u$ with $u\ge 0$ and $w:=f_0/f_--1$ satisfy $(k-1)w\le(k+1)\frac{2u}{u+2}$.

Take $f_-=F(k-1)$, $f_0=F(k)$, $f_+=F(k+1)$; they are positive since $k-1>0$ and $a,b\ge 0$.

*Monotonicity.* $F(k-1)\le F(k+1)$ is, after clearing the denominators $k-1$ and $k+1$, the inequality $ab\le k^2-1$.

*The logarithmic condition.* A direct computation gives
$$u=\frac{F(k+1)}{F(k)}-1=\frac{k(k+1)-ab}{(k+a)(k+b)(k+1)},\qquad w=\frac{F(k)}{F(k-1)}-1=\frac{k(k-1)-ab}{(k-1+a)(k-1+b)\,k},$$
and $u\ge 0$ because $ab\le k^2-1\le k(k+1)$. The number $w$ may be negative. With denominators cleared, the inequality $(k-1)w\le(k+1)\frac{2u}{u+2}$ reads
$$(k-1)\big(k(k-1)-ab\big)\big[2(k+a)(k+b)(k+1)+k(k+1)-ab\big]\le 2(k+1)\big(k(k+1)-ab\big)(k-1+a)(k-1+b)\,k,$$
and the right side minus the left side is
$$k^2(k-1)^2(k+1)+4k^2(k^2-1)(a+b)+ab\big(10k^3+2k^2-4k-(3k+1)\,ab\big).$$
The first two terms are nonnegative. In the third, $ab\le k^2-1$ gives $10k^3+2k^2-4k-(3k+1)ab\ge 7k^3+k^2-k+1>0$, and $ab\ge 0$. The expansion is a routine polynomial identity, verified in the Lean proof by the arithmetic tactic from these three nonnegative terms.

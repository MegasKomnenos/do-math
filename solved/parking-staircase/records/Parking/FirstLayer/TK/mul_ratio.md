---
weight: unit
short: property K under the factor (z+α)/(z+β)
---
## Description

Property K at $k>1$ is preserved when the three values are multiplied by the values at $k-1$, $k$, $k+1$ of $z\mapsto(z+\alpha)/(z+\beta)$, $0\le\alpha\le\beta$, provided the middle value is nonnegative.

## Statement

Let $k>1$ be real, let $(a,b,c)$ have property K at $k$ (`Parking.FirstLayer.TK`) with $b\ge 0$, and let $0\le\alpha\le\beta$ be real. Then the triple
$$\Big(\frac{k-1+\alpha}{k-1+\beta}\,a,\ \ \frac{k+\alpha}{k+\beta}\,b,\ \ \frac{k+1+\alpha}{k+1+\beta}\,c\Big)$$
has property K at $k$.

## Explanation

The factor $f(z)=(z+\alpha)/(z+\beta)$ increases with the threshold $z$. In the last-car recursion at size $c+\rho$ and threshold $c$, the term in which one piece has size $i\le\rho-2$ carries the factor $(c+i+1)/(c+\rho)$, which is $f(c)$ with $\alpha=i+1$, $\beta=\rho$. The statement is what lets the induction of `Parking.FirstLayer.kernel_TK` pass through these terms. Convexity alone ($\mu=0$) is not preserved by such a factor; the record of `Parking.FirstLayer.TK` gives an example and explains how property K is designed so that it is.

Two properties of $f$ are used: $f(k-1)\le f(k+1)$, and
$$(k+1)\log\frac{f(k+1)}{f(k)}+(k-1)\log\frac{f(k-1)}{f(k)}\ge 0,$$
which is the convexity of $z\mapsto z\log f(z)$ at the three points $k-1,k,k+1$. The proof shows that any three positive numbers $f_-,f_0,f_+$ with these two properties may be used as factors; the library keeps this general form private and states it for the two families of factors it needs, the present one and that of `Parking.FirstLayer.TK.mul_prod`.

The hypothesis $b\ge 0$ is needed because a multiplier at least $1$ on the middle value is discarded in the proof.

## Proof

**A general factor.** Let $k>0$, let $(a,b,c)$ have property K at $k$ with $b\ge 0$, and let $f_-,f_0,f_+$ be positive reals with $f_-\le f_+$ and $\Xi:=(k+1)\log(f_+/f_0)+(k-1)\log(f_-/f_0)\ge 0$. Then $(f_-a,f_0b,f_+c)$ has property K at $k$. Indeed, put $L=\log(f_+/f_0)$ and $M=\log(f_-/f_0)$. Since $L\ge M$, every $\mu\ge 0$ satisfies $\mu+(L-M)/2\ge 0$, and `Parking.FirstLayer.TK.shift` gives
$$2e^{\mu/k}e^{\Xi/(2k)}\,b\le e^{\mu}\frac{f_+}{f_0}c+e^{-\mu}\frac{f_-}{f_0}a .$$
Because $e^{\Xi/(2k)}\ge 1$ and $2e^{\mu/k}b\ge 0$, the left side is at least $2e^{\mu/k}b$. Multiplying by $f_0>0$ gives the defining inequality for $(f_-a,f_0b,f_+c)$.

**A criterion for $\Xi\ge 0$.** Let $k>1$. Suppose $f_+/f_0=1+u$ with $u\ge 0$, and put $w=f_0/f_--1$. If $(k-1)\,w\le(k+1)\cdot\frac{2u}{u+2}$, then $\Xi\ge 0$. This follows from the two elementary inequalities $\log(1+u)\ge\frac{2u}{u+2}$ for $u\ge 0$ and $\log r\ge 1-\frac1r$ for $r>0$, the second applied to $r=f_-/f_0$, where $1-\frac1r=-w$.

**The factor $(z+\alpha)/(z+\beta)$.** The three values are positive because $k-1>0$ and $\alpha,\beta\ge 0$. First, $f(k-1)\le f(k+1)$: after clearing denominators the difference of the two sides is $2(\beta-\alpha)\ge 0$. Second, a direct computation gives
$$u=\frac{f(k+1)}{f(k)}-1=\frac{\beta-\alpha}{(k+\alpha)(k+1+\beta)}\ge 0,\qquad w=\frac{f(k)}{f(k-1)}-1=\frac{\beta-\alpha}{(k+\beta)(k-1+\alpha)} ,$$
and $\frac{2u}{u+2}=\frac{2(\beta-\alpha)}{2(k+\alpha)(k+1+\beta)+(\beta-\alpha)}$. The inequality of the criterion, with denominators cleared, is
$$(k-1)(\beta-\alpha)\big[2(k+\alpha)(k+1+\beta)+(\beta-\alpha)\big]\le 2(k+1)(\beta-\alpha)(k+\beta)(k-1+\alpha),$$
and the right side minus the left side equals $(\beta-\alpha)\big[\alpha(4\beta+3k+1)+\beta(k-1)\big]$, which is nonnegative. This expansion is a routine polynomial identity. The general factor statement now applies.

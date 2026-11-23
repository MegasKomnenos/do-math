---
weight: unit
short: property K of the self-convolutions of a tilted-convex sequence
---
## Description

If a positive sequence $f$ satisfies the tilted convexity $2e^{\mu/k}f(j+1)\le e^{\mu}f(j+2)+e^{-\mu}f(j)$ for $j\le n$ and all $\mu\ge 0$, has $f(n+2)=f(n+1)\le f(a)$ for $a\le n$, and $n+2\le k$, then its self-convolutions at the lengths $n$, $n+1$, $n+2$ have property K at $k$.

## Statement

Let $k$ and $n$ be natural numbers with $n+2\le k$, and let $f:\mathbb{N}\to\mathbb{R}$ satisfy

1. $f(a)>0$ for $a\le n+2$;
2. $f(n+1)\le f(a)$ for $a\le n$;
3. $f(n+2)=f(n+1)$;
4. for every real $\mu\ge 0$ and every $j\le n$: $\;2e^{\mu/k}f(j+1)\le e^{\mu}f(j+2)+e^{-\mu}f(j)$.

Write $T(j)=\sum_{a=0}^{j}f(a)f(j-a)$ (`Parking.FirstLayer.conv`). Then the triple $\big(T(n),T(n+1),T(n+2)\big)$ has property K at $k$ (`Parking.FirstLayer.TK`): for every $\lambda\ge 0$,
$$2e^{\lambda/k}\,T(n+1)\le e^{\lambda}\,T(n+2)+e^{-\lambda}\,T(n).$$

## Explanation

Hypothesis 4 says that every three consecutive values of $f$ up to the index $n+2$ satisfy the inequality of property K at $k$; the statement says that this passes to the self-convolution at the three top lengths. It is applied once, in `Parking.FirstLayer.pairT_TK`, to $f(a)=\omega_{\rho+a}$ with $\rho+n+2=k$, where $\omega$ is the sequence of tilted Cayley masses at the critical tilt: it decreases up to the index $k-1$, has $\omega_{k-1}=\omega_k$, and is tilted-convex below the top (`Parking.FirstLayer.ccT_tilt_mid`). Hypotheses 2 and 3 describe exactly that shape.

A self-convolution of a convex sequence need not be convex in this sense because of its ends. When the combination $e^{\lambda}T(n+2)+e^{-\lambda}T(n)-2e^{\lambda/k}T(n+1)$ is sorted by the second index, each inner term is a value of $f$ times a tilted second difference of $f$, which is nonnegative, but a boundary term $f(n+1)\big(e^{\lambda}f(1)-2e^{\lambda/k}f(0)\big)$ remains, and it is negative when $f$ decreases at the start and $\lambda$ is small. The inner terms have to pay for it, and the proof needs two different ways of bounding them from below. For tilts with $\cosh\lambda\ge e^{\lambda/k}$ it is enough to replace each value of $f$ by the minimum $f(n+1)$. For the remaining tilts, which are small positive ones, that bound is too weak, and the tilted sequence is compared instead with the solution of the three-term recurrence $g(y+1)+g(y-1)=2e^{\lambda/k}g(y)$ that agrees with it at the two top indices; the comparison solution cancels the boundary term exactly, and what remains is an explicit expression in the two top values whose sign is decided by the hypothesis $n+2\le k$.

The hypothesis $n+2\le k$ is used in that last decision and nowhere else: it bounds the length of the convolution by the number $k$ that appears in the margin $e^{\lambda/k}$.

Of hypothesis 1 the proof uses only that $f(n+1)\ge 0$ and $\sum_{a\le n+1}f(a)\ge 0$.

## Proof

Fix $\lambda\ge 0$. The tilt is called $\lambda$ here because $\mu$ will denote a hyperbolic angle.

**Decomposition.** For real numbers $A$, $B$, $D$,
$$A\,T(n+2)+B\,T(n)-D\,T(n+1)=\sum_{j=0}^{n}f(n-j)\big(A f(j+2)+B f(j)-D f(j+1)\big)+f(n+1)\big(A f(1)-D f(0)\big)+A f(n+2)f(0).\tag{1}$$
This follows by writing $T(n)=\sum_{j\le n}f(n-j)f(j)$, $T(n+1)=\sum_{j\le n}f(n-j)f(j+1)+f(n+1)f(0)$ and $T(n+2)=\sum_{j\le n}f(n-j)f(j+2)+f(n+1)f(1)+f(n+2)f(0)$.

**Case 1: $\cosh\lambda\ge e^{\lambda/k}$.** Use (1) with $A=e^{\lambda}$, $B=e^{-\lambda}$, $D=2e^{\lambda/k}$. By hypothesis 4 every bracket in the sum is nonnegative, so by hypothesis 2 each $f(n-j)$ may be replaced by the smaller number $f(n+1)$. With $S=\sum_{a=0}^{n+1}f(a)$ one has $\sum_{j\le n}f(j)=S-f(n+1)$, $\sum_{j\le n}f(j+1)=S-f(0)$ and $\sum_{j\le n}f(j+2)=S-f(0)-f(1)+f(n+2)$. Substituting, and using hypothesis 3, the terms with $f(0)$ and $f(1)$ cancel against the boundary terms of (1), and
$$e^{\lambda}T(n+2)+e^{-\lambda}T(n)-2e^{\lambda/k}T(n+1)\;\ge\;2f(n+1)\Big(\big(\cosh\lambda-e^{\lambda/k}\big)S+\sinh\lambda\cdot f(n+1)\Big).$$
The right side is nonnegative: $f(n+1)\ge 0$, $S\ge 0$, $\sinh\lambda\ge 0$, and $\cosh\lambda-e^{\lambda/k}\ge 0$ in this case.

**Case 2: $\cosh\lambda<e^{\lambda/k}$.** Then $\lambda>0$, since both sides equal $1$ at $\lambda=0$. Let $\mu>0$ be the number with $\cosh\mu=e^{\lambda/k}$. Since $\cosh\lambda<\cosh\mu$ and both are nonnegative, $\lambda\le\mu$.

*The tilted sequence.* Put $F(a)=e^{\lambda a}f(a)$. Then $\sum_{a\le j}F(a)F(j-a)=e^{\lambda j}T(j)$, and hypothesis 4 at the tilt $\lambda$, multiplied by $e^{\lambda(j+1)}$, reads
$$2\cosh\mu\cdot F(j+1)\le F(j+2)+F(j)\qquad(j\le n).\tag{2}$$
Write $T_F(j)=e^{\lambda j}T(j)$. The claim, multiplied by $e^{\lambda(n+1)}$, is $T_F(n+2)+T_F(n)-2\cosh\mu\cdot T_F(n+1)\ge 0$.

*The comparison solution.* For real $y$ put
$$g(y)=\sinh\big((n+2-y)\mu\big)\,F(n+1)-\sinh\big((n+1-y)\mu\big)\,F(n+2).$$
By the addition formula for $\sinh$, $g(y+1)+g(y-1)=2\cosh\mu\cdot g(y)$, and $g(n+1)=\sinh\mu\cdot F(n+1)$, $g(n+2)=\sinh\mu\cdot F(n+2)$. Let $e(j)=\sinh\mu\cdot F(j)-g(j)$ for integers $0\le j\le n+2$. Then $e(n+1)=e(n+2)=0$, and by (2) and the recurrence of $g$, $e(j+2)+e(j)-2\cosh\mu\cdot e(j+1)\ge 0$ for $j\le n$. From this, $0\le e(j+1)\le e(j)$ for all $j\le n+1$, by downward induction on $j$: if $0\le e(j+2)\le e(j+1)$, then $e(j)\ge 2\cosh\mu\cdot e(j+1)-e(j+2)\ge 2e(j+1)-e(j+2)\ge e(j+1)$, using $\cosh\mu\ge 1$ and $e(j+1)\ge 0$. In particular $e(j)\ge 0$ for $0\le j\le n$. This is a discrete maximum principle: the tilted sequence lies above the solution of the recurrence that it touches at the two top indices.

*The boundary term is cancelled.* Apply (1) to $F$ with $A=B=1$, $D=2\cosh\mu$ and multiply by $\sinh\mu>0$. Let $c_j=F(j+2)+F(j)-2\cosh\mu\cdot F(j+1)\ge 0$. In the $j$-th term write $\sinh\mu\cdot F(n-j)=e(n-j)+g(n-j)$. The part $e(n-j)c_j$ is nonnegative. For the other part, the recurrence of $g$ at $y=n-j$ gives $g(n-j)\,c_j=V_{j+1}-V_j$ with $V_j=g(n+1-j)F(j+1)-g(n-j)F(j)$, so $\sum_{j=0}^{n}g(n-j)c_j=V_{n+1}-V_0$. Now $g(n)=2\cosh\mu\cdot g(n+1)-g(n+2)=\sinh\mu\,(2\cosh\mu\cdot F(n+1)-F(n+2))$, hence
$$V_0=\sinh\mu\,\Big(F(n+1)\big(F(1)-2\cosh\mu\cdot F(0)\big)+F(n+2)F(0)\Big),$$
which is $\sinh\mu$ times the two boundary terms of (1). They cancel, and with $g(0)$ and $g(-1)$ read from the definition of $g$,
$$\sinh\mu\,\big(T_F(n+2)+T_F(n)-2\cosh\mu\,T_F(n+1)\big)\ \ge\ V_{n+1}=2F(n+1)F(n+2)\sinh((n+2)\mu)-F(n+2)^2\sinh((n+1)\mu)-F(n+1)^2\sinh((n+3)\mu).$$

*The sign of the remainder.* By hypothesis 3, $F(n+2)=e^{\lambda}F(n+1)$. With $R=e^{\lambda}$ and $m=n+1$, $V_{n+1}=F(n+1)^2\,P$, where
$$P=2R\sinh((m+1)\mu)-R^2\sinh(m\mu)-\sinh((m+2)\mu).$$
Put $a=m\mu/2\ge 0$. The double-angle and addition formulas give the factorisation
$$P=2\,\big(\sinh(a+\mu)-R\sinh a\big)\,\big(R\cosh a-\cosh(a+\mu)\big).$$
The first factor is nonnegative: $R\le e^{\mu}=\cosh\mu+\sinh\mu$ because $\lambda\le\mu$, and $\sinh a\le\cosh a$, so $R\sinh a\le\sinh a\cosh\mu+\cosh a\sinh\mu=\sinh(a+\mu)$. The second factor is nonnegative by the chain
$$\cosh(a+\mu)=\cosh a\cosh\mu+\sinh a\sinh\mu\le\cosh a\cosh\mu\,\Big(1+m\frac{\mu^2}{2}\Big)\le\cosh a\cosh\mu\,\Big(1+\frac{\mu^2}{2}\Big)^{m}\le\cosh a\,(\cosh\mu)^{m+1}\le\cosh a\,(\cosh\mu)^{k}=R\cosh a .$$
Its steps are: $\sinh y\le y\cosh y$ for $y\ge 0$, used for $y=a$ and $y=\mu$ (the derivative of $y\cosh y-\sinh y$ is $y\sinh y\ge 0$); Bernoulli's inequality; $1+\mu^2/2\le\cosh\mu$ (from $\cosh\mu=1+2\sinh^2(\mu/2)$ and $\sinh t\ge t$ for $t\ge 0$); $m+1=n+2\le k$ and $\cosh\mu\ge 1$; and $(\cosh\mu)^k=e^{\lambda}$ by the choice of $\mu$. This last chain is the place where $n+2\le k$ is used.

Hence $P\ge 0$, so $T_F(n+2)+T_F(n)-2\cosh\mu\,T_F(n+1)\ge 0$, and dividing by $e^{\lambda(n+1)}$ gives the defining inequality of property K at the tilt $\lambda$.

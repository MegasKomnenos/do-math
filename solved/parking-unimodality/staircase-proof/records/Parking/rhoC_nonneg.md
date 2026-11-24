---
weight: step
short: nonnegativity of the correction ϱ
---
## Description

$\varrho(k+R,c)=\frac{c}{2(k+R-c)}+\frac{c^2}{8(k+R-c)^2}\ge0$ for natural numbers $k$, $R$ and $c\le R$.

## Statement

Let $k$, $R$, $c$ be natural numbers with $c\le R$. Then
$$\varrho(k+R,c)=\frac{c}{2\,(k+R-c)}+\frac{c^{2}}{8\,(k+R-c)^{2}}\ \ge\ 0,$$
where $\varrho$ is the function of `Parking.rhoC`. In the one case in which the denominators vanish, $k=0$ and $c=R$, the expression is read with the convention that a quotient with denominator zero is $0$; the statement holds there as well.

## Explanation

The correction $\varrho_c=\varrho(k+R,c)$ occurs in the sums $G(k,R)$ and $\mathcal A(k,R)$ (`Parking.Gsum`, `Parking.Asum`) in the factor $\kappa_3(c)\,(1+\varrho_c)$, where $\kappa_3\ge0$ is the threefold convolution of the Poisson mass (`Parking.kc3`). Its sign is needed in two places. In the proof of `Parking.pairSum_ge` an inequality is multiplied by $\kappa_3(c)\,(1+\varrho_c)$, which must be nonnegative. And where the two sums are bounded from above by polynomials in $\sqrt R$, the product $\kappa_3(c)\,\varrho_c$ is bounded by the product of an upper bound of $\kappa_3(c)$ and an upper bound of $\varrho_c$, which is legitimate because both factors are nonnegative.

In those uses $k\ge1$ and $0<c<R$, so the denominators are positive and the convention at zero plays no role.

## Proof

Since $c\le R$ and $k\ge0$, the real number $k+R-c$ is nonnegative. Both terms of $\varrho(k+R,c)$ are then quotients of nonnegative numbers, $c$ by $2(k+R-c)$ and $c^{2}$ by $8(k+R-c)^{2}$, and such a quotient is nonnegative, also under the convention for a zero denominator.

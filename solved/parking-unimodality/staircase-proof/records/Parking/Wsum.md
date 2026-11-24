---
weight: unit
short: total weight of the pairs
---
## Description

$W_\Sigma(R)=\sum_{b=1}^{R}\kappa_2(b)=\sum_{0<a<b\le R}P(a)\,P(b-a)$, where $P(m)=e^{-m}m^m/m!$ is the Poisson mass: the total weight of the pairs of marked cut points in the lower bound of the pair sum.

## Statement

For a natural number $R$,
$$W_\Sigma(R)=\sum_{b=1}^{R}\kappa_2(b),$$
where $\kappa_2(b)=\sum_{0<a<b}P(a)\,P(b-a)$ (`Parking.kc2`) and $P(m)=e^{-m}m^m/m!$ is the Poisson mass (`Parking.poissonMass`). Written out, $W_\Sigma(R)$ is the sum of $P(a)\,P(b-a)$ over all pairs of natural numbers $a$, $b$ with $0<a<b\le R$. In particular $W_\Sigma(0)=W_\Sigma(1)=0$.

## Explanation

**Where the sum comes from.** The pair sum `Parking.pairSum` of a first-layer position $(k+R-1,k)$ is a sum over the pairs of marked cut points $0<a<b\le R$. Its lower bound `Parking.pairSum_ge` bounds the term of the pair $(a,b)$ from below by
$$a_k\,e^{R}\cdot P(a)\,P(b-a)\cdot e^{-X_{ab}},$$
where $a_k=k^{k-1}/k!$ and $X_{ab}$ is an exponent that collects the logarithms of all the cut factors of the term. The product $P(a)P(b-a)$ is the weight that the pair carries in this bound, and $W_\Sigma(R)$ is the total of these weights. The weight is what the two chain sums of the pair term become when every cut factor is replaced by $1$: for the cut profile $1$ the total weight of the compositions of $m$ is $m^m/m!=e^{m}P(m)$ (`Parking.Lam_one`).

In `Parking.pairSum_ge` the sum $W_\Sigma$ stands beside two other sums, $G$ (`Parking.Gsum`) and $\mathcal A$ (`Parking.Asum`), which bound the total of the exponents $X_{ab}$ taken with the same weights. With the best choice of the two parameters of that theorem the bound is $a_k e^{R}\,W_\Sigma(R)$ times the exponential of minus a bound for the mean exponent; so $W_\Sigma$ is the size of the pair sum before the cut factors are taken into account, in the unit $a_ke^{R}$.

**Its size.** For $b\ge2$ one has $\kappa_2(b)\ge\frac12-\bigl(\frac43+\frac{1}{15b}\bigr)P(b)$. This follows from the closed form $\kappa_2(b)=P(b)\,(s_b-1)$ (`Parking.kc2_eq`), in which $s_b$ is the mean of the birthday law (`Parking.sbirth`), and from the lower bound `Parking.sbirth_ge` for $s_b$. Since $P(b)$ is of the order $b^{-1/2}$, the sum $W_\Sigma(R)$ is at least $R/2$ minus a multiple of $\sqrt R$, and the library proves a lower bound of this form with explicit constants for $R\ge42$. The term of order $\sqrt R$ is not small in the range where the bound is used. A floating-point evaluation, which is not part of any proof, gives $W_\Sigma(42)=14.916$, against $R/2=21$.

Only a lower bound of $W_\Sigma$ is needed. In `Parking.pairSum_ge` it is multiplied by $1+\mu$, and where that theorem is applied the parameter $\mu$ is nonnegative, so replacing $W_\Sigma$ by a smaller number gives a smaller, still valid, lower bound of the pair sum.

**The Lean form.** `Wsum R` is the sum of `kc2 b` over `Finset.Icc 1 R`, a real number. The term $b=1$ is zero (`Parking.kc2_one`), so the sum could equally start at $b=2$.

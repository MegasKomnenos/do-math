---
weight: unit
short: total excess in the exponents of the pairs
---
## Description

$\mathcal A(k,R)=\sum_{b=1}^{R}\bigl((R-\frac b2)(\kappa_2(b)+2\kappa_3(b))+\frac52(R-b)\kappa_2(b)\bigr)+\sum_{0<c<R}(R-c)\,\kappa_3(c)\,(1+\varrho_c)$ with $\varrho_c=\frac{c}{2(k+R-c)}+\frac{c^2}{8(k+R-c)^2}$: in the lower bound of the pair sum, the total of the excesses at which logarithms of cut factors enter the exponents of the pairs.

## Statement

For natural numbers $k$ and $R$,
$$\mathcal A(k,R)=\sum_{b=1}^{R}\Bigl(\bigl(R-\tfrac b2\bigr)\bigl(\kappa_2(b)+2\,\kappa_3(b)\bigr)+\tfrac52\,(R-b)\,\kappa_2(b)\Bigr)+\sum_{0<c<R}(R-c)\,\kappa_3(c)\,\bigl(1+\varrho(k+R,c)\bigr),$$
where $\kappa_2(m)=\sum_{0<g<m}P(g)P(m-g)$ and $\kappa_3(m)=\sum_{0<g<m}\kappa_2(g)P(m-g)$ are the convolutions of the Poisson mass $P(m)=e^{-m}m^m/m!$ (`Parking.kc2`, `Parking.kc3`, `Parking.poissonMass`), and $\varrho(N,c)=\frac{c}{2(N-c)}+\frac{c^{2}}{8(N-c)^{2}}$ (`Parking.rhoC`). The second sum runs over the natural numbers $c$ with $0<c<R$.

## Explanation

**What the sum is.** Fix $k\ge1$, $R\le k$, put $N=k+R$ and $L(y)=\log(1+y/k)$. A cut point $s\le R$ of a composition counted in the pair sum (`Parking.pairSum`) stands for the size $N-s=k+(R-s)$, and it carries the cut factor $k/(N-s)=e^{-L(R-s)}$; the number $R-s$ is its *excess* over $k$. In the proof of `Parking.pairSum_ge` the term of a pair of marked cut points $0<a<b\le R$ is bounded from below by $a_ke^{R}P(a)P(b-a)e^{-X_{ab}}$, where the exponent $X_{ab}$ is at most a weighted sum of values $L(y)$ at excesses $0\le y\le R$. When $L$ is replaced by a line above it, $L(y)\le\alpha+\beta y$, the total $\sum_{a<b}P(a)P(b-a)X_{ab}$ of the exponents is at most $\alpha\,G(k,R)+\beta\,\mathcal A(k,R)$: $G$ (`Parking.Gsum`) is the total weight of the values of $L$, and $\mathcal A$ is the total of the excesses $y$ at which they are taken, with the same weights.

**Why it has this form.** The summand of $\mathcal A$ is obtained from the summand of $G$ by multiplying each weight with the mean excess of the points it belongs to, and the mean positions are given by the moment identities of the convolutions. The words above and below refer to sizes, so that the cut points above $a$ are those with $s<a$. For a fixed larger point $b$, summed over $a$:

- the marked point $a$ has the weight $\kappa_2(b)$ and the mean position $\frac b2$ (`Parking.kc2_mom`), hence the mean excess $R-\frac b2$;
- a cut point of the chain above $a$ has the weight $\kappa_3(b)$ and the mean position $\frac b3$, hence the mean excess $R-\frac b3$ (`Parking.kc2_mom` and `Parking.kc3_mom_left`);
- a cut point of the chain between $a$ and $b$ has the weight $\kappa_3(b)$ and the mean position $\frac{2b}3$, hence the mean excess $R-\frac{2b}3$ (`Parking.kc2_mom` and `Parking.kc3_mom_right`);
- the marked point $b$ and the end term have together the weight $\frac52\kappa_2(b)$ and the excess $R-b$.

The two contributions of weight $\kappa_3(b)$ add up to $(2R-b)\,\kappa_3(b)=(R-\frac b2)\cdot2\kappa_3(b)$, which gives the summand of the first sum. The second sum is the contribution of the environments below the points $b$: the cut point $c$ carries the weight $\kappa_3(c)\,(1+\varrho_c)$, as in $G$, and has the excess $R-c$.

**The mean excess.** The quotient $\mathcal A/G$ is the mean excess of a factor. It determines the best line in `Parking.pairSum_ge`: the tangent of $L$ at the excess $y=k\theta$ gives the bound $\alpha G+\beta\mathcal A$ with $\alpha=\log(1+\theta)-\frac{\theta}{1+\theta}$ and $\beta=\frac{1}{k(1+\theta)}$, and for $k\theta=\mathcal A/G$ the terms $-\frac{\theta}{1+\theta}G$ and $\beta\mathcal A$ cancel, so that the bound is $G\,\log\bigl(1+\frac{\mathcal A}{kG}\bigr)$. This is Jensen's inequality for the concave function $L$: the weighted mean of $L$ is at most $L$ at the weighted mean. The mean excess is close to $R/2$. For $R=42$ and $k=262$ a floating-point evaluation, which is not part of any proof, gives $G=169.0$, $\mathcal A=3863.0$ and $\mathcal A/G=22.9$.

**Dependence on $k$ and size.** The column $k$ enters only through $\varrho_c=\varrho(k+R,c)$. The sum is of the order $R^{5/2}$, and the library proves an upper bound by a polynomial of degree five in $\sqrt R$ for $R\ge42$ and columns near the curve $k^2=R^3$. An upper bound is what is needed, because $\mathcal A$ enters `Parking.pairSum_ge` with the coefficient $-\beta<0$.

**The Lean form.** `Asum k R` is the sum over `Finset.Icc 1 R` of `(R - b / 2) * (kc2 b + 2 * kc3 b) + 5 / 2 * (R - b) * kc2 b` plus the sum over `Finset.Ioo 0 R` of `(R - c) * kc3 c * (1 + rhoC (k + R) c)`, with $k$, $R$, $b$, $c$ cast to real numbers, so that the differences $R-\frac b2$, $R-b$, $R-c$ are differences of real numbers.

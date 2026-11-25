---
weight: unit
short: total weight of the logarithms in the exponents of the pairs
---
## Description

$G(k,R)=\sum_{b=1}^{R}\bigl(\frac72\kappa_2(b)+2\kappa_3(b)\bigr)+\sum_{0<c<R}\kappa_3(c)\,(1+\varrho_c)$ with $\varrho_c=\frac{c}{2(k+R-c)}+\frac{c^2}{8(k+R-c)^2}$: in the lower bound of the pair sum, the total weight with which logarithms of cut factors enter the exponents of the pairs.

## Statement

For natural numbers $k$ and $R$,
$$G(k,R)=\sum_{b=1}^{R}\Bigl(\frac72\,\kappa_2(b)+2\,\kappa_3(b)\Bigr)+\sum_{0<c<R}\kappa_3(c)\,\bigl(1+\varrho(k+R,c)\bigr),$$
where $\kappa_2(m)=\sum_{0<g<m}P(g)P(m-g)$ and $\kappa_3(m)=\sum_{0<g<m}\kappa_2(g)P(m-g)$ are the convolutions of the Poisson mass $P(m)=e^{-m}m^m/m!$ (`Parking.kc2`, `Parking.kc3`, `Parking.poissonMass`), and $\varrho(N,c)=\frac{c}{2(N-c)}+\frac{c^{2}}{8(N-c)^{2}}$ (`Parking.rhoC`). The second sum runs over the natural numbers $c$ with $0<c<R$.

## Explanation

**What the sum is.** Fix $k\ge1$, $R\le k$, put $N=k+R$ and $L(y)=\log(1+y/k)$. In the proof of `Parking.pairSum_ge` the term of the pair sum for a pair of marked cut points $0<a<b\le R$ is bounded from below by $a_ke^{R}\,P(a)P(b-a)\,e^{-X_{ab}}$, and the exponent $X_{ab}$ is a sum of six parts. Five of them are weighted sums of values $L(y)$ at excesses $0\le y\le R$, because a cut factor $k/(k+y)$ of the term is $e^{-L(y)}$; the remaining one, an end term, is at most $\frac32L(R-b)$. The logarithm is then replaced by a line that lies above it, $L(y)\le\alpha+\beta y$. After this replacement the total of the exponents, $\sum_{a<b}P(a)P(b-a)X_{ab}$, is at most $\alpha$ times the total weight of the values of $L$ plus $\beta$ times the total of the excesses $y$ taken with the same weights. The first total is $G(k,R)$, and the second is $\mathcal A(k,R)$ (`Parking.Asum`). So $G$ counts, with the weights $P(a)P(b-a)$ of the pairs, how many factors $k/(k+y)$ a pair carries in the mean; the sum $W_\Sigma(R)$ of the weights themselves is `Parking.Wsum`.

**Why it has this form.** The six parts of the exponent contribute as follows; the proof of `Parking.pairSum_ge` gives the computations. A cut point $s$ stands for the size $N-s$, and the words above and below refer to sizes, so that the cut points above $a$ are those with $s<a$. For a fixed larger point $b$, summed over $a$:

- the cut points of the chain above $a$ contribute $\kappa_3(b)$;
- the marked point $a$ contributes $\kappa_2(b)$;
- the cut points of the chain between $a$ and $b$ contribute $\kappa_3(b)$;
- the marked point $b$ contributes $\kappa_2(b)$;
- the end term, which compares the Cayley coefficients $a_k$ and $a_{N-b}$ and is at most $\frac32L(R-b)$, contributes $\frac32\kappa_2(b)$.

These add up to $\frac72\kappa_2(b)+2\kappa_3(b)$, the summand of the first sum. The sixth part comes from the environment below $b$. It is a sum over the cut points $c$ with $b<c<R$, and after the order of summation over $b$ and $c$ is exchanged, the cut point $c$ carries the weight $\kappa_3(c)\,(1+\varrho_c)$; the record of `Parking.rhoC` explains the factor $1+\varrho_c$. This is the second sum.

**Dependence on $k$ and size.** The column $k$ enters only through $\varrho_c=\varrho(k+R,c)$, which decreases when $k$ grows. For $k\ge1$ and $c<R$ the denominators $k+R-c$ are positive. Since $\kappa_2(b)$ is close to $\frac12$ and $\kappa_3(b)$ is of the order $\sqrt b$ (by the closed forms `Parking.kc2_eq` and `Parking.kc3_eq`), $G(k,R)$ is of the order $R^{3/2}$; the library proves an upper bound by a polynomial of degree three in $\sqrt R$ for $R\ge42$ and columns near the curve $k^2=R^3$. An upper bound is what is needed, because $G$ enters `Parking.pairSum_ge` with the coefficient $-\alpha\le0$.

**The Lean form.** `Gsum k R` is the sum over `Finset.Icc 1 R` of `7 / 2 * kc2 b + 2 * kc3 b` plus the sum over `Finset.Ioo 0 R` of `kc3 c * (1 + rhoC (k + R) c)`, with $k$ and $R$ cast to real numbers. The terms $b=1$ of the first sum and $c=1,2$ of the second vanish, since $\kappa_2(1)=0$, $\kappa_3(1)=0$ as an empty sum, and therefore $\kappa_3(2)=\kappa_2(1)P(1)=0$.

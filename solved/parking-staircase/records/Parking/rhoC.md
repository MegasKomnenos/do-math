---
weight: unit
short: correction of the weight of a cut point below the marked points
---
## Description

$\varrho(N,c)=\dfrac{c}{2(N-c)}+\dfrac{c^{2}}{8(N-c)^{2}}$ for a real number $N$ and a natural number $c$: the relative correction that the sums $G$ and $\mathcal A$ of the lower bound of the pair sum apply to the weight $\kappa_3(c)$ of a cut point $c$ below the larger marked point.

## Statement

For a real number $N$ and a natural number $c$ with $N\ne c$,
$$\varrho(N,c)=\frac{c}{2\,(N-c)}+\frac{c^{2}}{8\,(N-c)^{2}} .$$
With $z=c/(N-c)$ this is $\varrho(N,c)=\frac z2+\frac{z^{2}}{8}$.

## Explanation

**Where it is used.** The quantity occurs in the definitions of the two sums $G(k,R)$ (`Parking.Gsum`) and $\mathcal A(k,R)$ (`Parking.Asum`), always with $N=k+R$ and a cut point $0<c<R$; there one writes $\varrho_c$ for $\varrho(k+R,c)$. In both sums it appears in the factor $\kappa_3(c)\,(1+\varrho_c)$, where $\kappa_3$ is the threefold convolution of the Poisson mass (`Parking.kc3`).

**Where it comes from.** In the proof of `Parking.pairSum_ge` the term of a pair of marked cut points $a<b$ contains the environment below $b$, and Jensen's inequality for the environment produces, for every cut point $c$ with $b<c<R$ (a cut point $c$ stands for the size $N-c$, so these are the sizes between $k$ and $N-b$, below the size of $b$), the weight $\operatorname{ren}(c-b)\,a_{N-c}/a_{N-b}$, where $\operatorname{ren}(m)=m^m/m!$ and $a_j=j^{j-1}/j!$. If the Cayley coefficients $a_j$ were exactly proportional to $e^{j}$, this weight would be the Poisson mass $P(c-b)=e^{-(c-b)}\operatorname{ren}(c-b)$. They are not: $e^{-j}a_j$ decreases, roughly like $j^{-3/2}$. What is proved is that the sequence $e^{-j}a_j\,j^{3/2}$ does not decrease (`Parking.borel_log_mono`), and the resulting bound for the ratio is
$$\frac{e^{c-b}\,a_{N-c}}{a_{N-b}}\ \le\ 1+\frac32\,z'+\frac38\,z'^{2},\qquad z'=\frac{c-b}{N-c}$$
(`Parking.borel_ratio_le`). When this is summed over the marked point $b<c$ against the weights $\kappa_2(b)\,P(c-b)$, the constant $1$ gives $\kappa_3(c)$, and the two further terms are evaluated with the mean position of $b$: by `Parking.kc3_mom_left` the mean of $b$ is $\frac{2c}{3}$, so the mean of $c-b$ is $\frac c3$, and the square is bounded through $(c-b)^2\le c\,(c-b)$. The result is $\frac32\cdot\frac{c}{3(N-c)}+\frac38\cdot\frac{c^{2}}{3(N-c)^{2}}=\varrho(N,c)$. So $\kappa_3(c)\,(1+\varrho_c)$ bounds the total weight with which the cut point $c$ enters the exponents of the pairs through their environments, and $\varrho_c$ measures by how much this exceeds the weight $\kappa_3(c)$ that Cayley coefficients exactly proportional to $e^{j}$ would give.

**Its size.** In the uses $N-c>k$, so $\varrho_c\le\frac{c}{2k}+\frac{c^{2}}{8k^{2}}$ with $c<R$. On the curve $k^2\approx R^3$ this is of the order $R^{-1/2}$: a correction, but one that the numerical part of the argument has to carry, because the comparison in which the bounds end has little room at the smallest value $R=42$.

**The Lean form.** `rhoC N c` takes a real number `N` and a natural number `c`, which is cast to a real number. At $N=c$ both denominators vanish, and Lean's convention that a quotient with denominator zero is zero gives the value $0$ there; this value is not used, except that `Parking.rhoC_nonneg` covers it.

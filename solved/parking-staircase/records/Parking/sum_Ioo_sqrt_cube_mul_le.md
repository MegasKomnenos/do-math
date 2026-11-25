---
weight: step
short: upper bound for the sum of c^(3/2)(R - c) over 0 < c < R
---
## Description

$\sum_{0<c<R}c\sqrt c\,(R-c)\le\frac{4}{35}(R+1)^3\sqrt{R+1}$ for every natural number $R$.

## Statement

For every natural number $R$,
$$\sum_{0<c<R}c\sqrt c\,(R-c)\ \le\ \frac{4}{35}\,(R+1)^{3}\sqrt{R+1},$$
where the sum runs over the natural numbers $c$ with $0<c<R$.

## Explanation

**The comparison behind the bound.** The integral of $x^{3/2}(R-x)$ over $[0,R]$ is $\bigl(\frac25-\frac27\bigr)R^{7/2}=\frac{4}{35}R^{7/2}$. The summand is not monotone on $[0,R]$ (it increases up to $x=\frac35R$ and decreases after it), so the sum cannot be compared with this integral term by term. The proof goes another way. Writing $R-c$ as the number of integers $n$ with $c\le n<R$ turns the sum into a double sum,
$$\sum_{c<R}c^{3/2}(R-c)=\sum_{n<R}\ \sum_{c\le n}c^{3/2},$$
and now both sums are sums of increasing functions: the inner one is at most $\frac25(n+1)^{5/2}$, and $\sum_{n<R}(n+1)^{5/2}\le\int_1^{R+1}x^{5/2}\,dx\le\frac27(R+1)^{7/2}$. This gives the constant $\frac25\cdot\frac27=\frac{4}{35}$ of the integral, with $R+1$ in the place of $R$. In the Lean proof the double sum appears as an induction on $R$.

**Where it is used.** For the correction term of the sum $\mathcal A$ of the lower bound of the pair sum (`Parking.Asum`, `Parking.pairSum_ge`). That term is $\sum_{0<c<R}(R-c)\,\kappa_3(c)\,\varrho_c$, with the threefold convolution $\kappa_3$ of the Poisson mass (`Parking.kc3`) and the correction $\varrho_c$ of `Parking.rhoC`. One has $\kappa_3(c)\le c_0\sqrt c$ for $c\ge1$, with $c_0=1/\sqrt{2\pi}$ (by the closed form `Parking.kc3_eq` and Stirling's bound of the Poisson mass), and on the curve $k^2\approx R^3$ one has $\varrho_c\le\mathrm{const}\cdot c/R^{3/2}$. So the term is at most a constant times $R^{-3/2}\sum_{0<c<R}c^{3/2}(R-c)$, which the present bound turns into a multiple of $(R+1)^{7/2}/R^{3/2}$, of the order $R^2$. The corresponding term of $G$ is treated with `Parking.sum_Ioo_sqrt_cube_le`.

**The Lean form.** The summand is `c * Real.sqrt c * (R - c)` with $R$ and $c$ cast to real numbers, the sum runs over `Finset.Ioo 0 R`, and $(R+1)^{7/2}$ is written `(R + 1) ^ 3 * Real.sqrt (R + 1)`.

## Proof

**Reduction.** The terms $c\sqrt c\,(R-c)$ with $c<R$ are nonnegative, so the sum over $0<c<R$ is at most the sum over $0\le c<R$. (The added term $c=0$ is zero.) Put $S(R)=\sum_{c=0}^{R-1}c\sqrt c\,(R-c)$. It suffices to show $S(R)\le\frac{4}{35}(R+1)^3\sqrt{R+1}$.

**The increment.** For every function $\phi$ on the natural numbers and every $n$,
$$\sum_{c=0}^{n}\phi(c)\,(n+1-c)=\sum_{c=0}^{n-1}\phi(c)\,(n-c)+\sum_{c=0}^{n}\phi(c),$$
because each term with $c<n$ on the left exceeds the corresponding term on the right by $\phi(c)$, and the term $c=n$ on the left is $\phi(n)$. With $\phi(c)=c\sqrt c$ this is $S(n+1)=S(n)+\sum_{c=0}^{n}c\sqrt c$.

**The left endpoint inequality for $x^{5/2}$.** For real $y\ge0$,
$$y^{2}\sqrt y\ \le\ \frac27\Bigl((y+1)^{3}\sqrt{y+1}-y^{3}\sqrt y\Bigr).$$
Put $p=\sqrt y$ and $q=\sqrt{y+1}$, so $0\le p\le q$ and $q^2-p^2=1$. The claim is $p^5(q^2-p^2)\le\frac27(q^7-p^7)$, and
$$\frac27\,(q^7-p^7)-p^5\,(q^2-p^2)=\frac{(q-p)^{2}\bigl(2q^5+4q^4p+6q^3p^2+8q^2p^3+10qp^4+5p^5\bigr)}{7}\ \ge\ 0 ,$$
an identity that is checked by expanding.

**Induction on $R$.** For $R=0$, $S(0)=0\le\frac{4}{35}$. Suppose $S(n)\le\frac{4}{35}(n+1)^3\sqrt{n+1}$. By the increment formula and `Parking.sum_range_sqrt_cube_le` at $n+1$, which states $\sum_{c=0}^{n}c\sqrt c\le\frac25(n+1)^2\sqrt{n+1}$,
$$S(n+1)\ \le\ \frac{4}{35}\,(n+1)^3\sqrt{n+1}+\frac25\,(n+1)^2\sqrt{n+1}.$$
By the left endpoint inequality at $y=n+1$, $\frac25(n+1)^2\sqrt{n+1}\le\frac{4}{35}\bigl((n+2)^3\sqrt{n+2}-(n+1)^3\sqrt{n+1}\bigr)$. Hence $S(n+1)\le\frac{4}{35}(n+2)^3\sqrt{n+2}$.

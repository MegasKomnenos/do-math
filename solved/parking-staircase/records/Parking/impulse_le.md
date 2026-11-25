---
weight: unit
short: upper bound of the boundary chain sum
---
## Description

For $R\ge1$, real $0\le y\le K$ with $R\le K$, and real $c'\ge-1$: $e^{-R}\Lambda_R(y+1;y+R)\le P(R)-e^{-c'}\Bigl((1+c')\frac{R-2}{2(K+R-1)}\kappa_2(R)-\frac{1}{K+1}\cdot\frac{R-3}{3}\kappa_3(R)\cdot\frac{\frac45R-1}{K+\frac35R}\Bigr)$, an upper bound of the chain sum with the cut factors $(y+1)/(y+R-s)$ by the Poisson mass $P$ and its convolutions $\kappa_2$, $\kappa_3$ at $R$.

## Statement

Let $R\ge1$ be a natural number, let $y$ and $K$ be real numbers with $0\le y\le K$ and $R\le K$, and let $c'$ be a real number with $1+c'\ge0$. Then
$$e^{-R}\,\Lambda_R(y+1;\,y+R)\ \le\ P(R)-e^{-c'}\Bigl((1+c')\,\frac{R-2}{2\,(K+R-1)}\,\kappa_2(R)-\frac{1}{K+1}\cdot\frac{R-3}{3}\,\kappa_3(R)\cdot\frac{\frac45R-1}{K+\frac35R}\Bigr).$$

Here $\Lambda_R(y+1;y+R)$ is the total weight of the compositions of $R$ (`Parking.Lam`) for the threshold profile $s\mapsto\frac{y+1}{y+R-s}$ (`Parking.thr`): the sum, over all sets $S\subseteq\{1,\dots,R-1\}$ of cut points, of the product of the Cayley coefficients $a_p=p^{p-1}/p!$ of the parts that $S$ cuts out of a segment of length $R$, times $\prod_{s\in S}\frac{y+1}{y+R-s}$. Further $P(m)=e^{-m}m^m/m!$ is the Poisson mass (`Parking.poissonMass`), $\kappa_2(m)=\sum_{0<g<m}P(g)P(m-g)$ (`Parking.kc2`) and $\kappa_3(m)=\sum_{0<g<m}\kappa_2(g)P(m-g)$ (`Parking.kc3`).

## Explanation

**The quantity.** At a position $(n,k)$ with $n=k+R-1$ and $1\le R\le k-2$, the normalised step $\bigl(b(n,k)-b(n,k-1)\bigr)/n!$ is a curvature term minus a boundary term, and the boundary term is $(a_k/k)\,\Lambda_R(k+1;k+R)$. This chain sum is called the impulse, which is where the name of the declaration comes from. The pair–impulse criterion `Parking.dq_pos_of_pair` gives a positive step as soon as $k\,a_k\,\Lambda_R(k+1;k+R)<2\mathcal P(k,R)$, with the pair sum of `Parking.pairSum`. The pair sum has the lower bound `Parking.pairSum_ge`, which carries the factor $a_ke^{R}$; the present theorem is the matching upper bound of $e^{-R}\Lambda_R(k+1;k+R)$. The two are compared on the curve $k^2\approx R^3$, and the result is the curve increase `Parking.curve_crossing`.

**What the bound says.** Every cut factor $\frac{y+1}{y+R-s}$, $0<s<R$, is at most $1$, and for the cut profile $1$ the total weight of the compositions of $R$ is $R^R/R!$ (the case $f=1$ of `Parking.Lam_defect`). So $e^{-R}\Lambda_R(y+1;y+R)\le P(R)$ trivially. The theorem says by how much the chain sum falls short of $P(R)$. The bracket has a main term, with $\kappa_2(R)$, and a correction of the opposite sign, with $\kappa_3(R)$. The main term is the first-order effect of the factors: a cut at $s$ loses the fraction $\delta(s)=\frac{R-1-s}{K+R-s}$, and summing this over the position of one cut gives a multiple of $\kappa_2(R)$. The correction accounts for the cut factors at the cut points before the one considered, which have already reduced the weight. For $R=1$ and $R=2$ the statement is the equality $e^{-R}\Lambda_R(y+1;y+R)=P(R)$: a composition of $1$ has no cut point, the only cut point $s=1$ of a composition of $2$ has the factor $\frac{y+1}{y+1}=1$, and the bracket is $0$, because $\kappa_2(1)=\kappa_3(1)=\kappa_3(2)=0$ and the factor $R-2$ vanishes at $R=2$.

On the curve the two terms of the bracket are of the same order as $P(R)$ itself. There $K$ is of the order $R^{3/2}$, $\kappa_2(R)$ is close to $\frac12$ and $\kappa_3(R)$ is of the order $\sqrt R$ (by the closed forms `Parking.kc2_eq`, `Parking.kc3_eq`), so that $\frac{R-2}{2(K+R-1)}\kappa_2(R)$ and $\frac{1}{K+1}\cdot\frac{R-3}{3}\kappa_3(R)\cdot\frac{4R/5-1}{K+3R/5}$ are both of the order $R^{-1/2}$, like $P(R)$. The bound is therefore not a small improvement of the trivial one. In the floating-point evaluation reported below, which is not part of the proof, at $R=42$ and $y=262$ it is about two thirds of $P(R)$. The pair side behaves in the same way: in `Parking.pairSum_ge` the cut factors enter the lower bound through an exponent that is of order $1$ exactly when $k$ is of the order $R^{3/2}$. On the curve neither side can be replaced by its value without cut factors.

**The two parameters.** The threshold $K$ is there because the chain sum does not decrease when $y$ grows, so the bound for any larger threshold serves. In the proof of the curve increase the theorem is applied with $y=k$ and with a threshold $K$ that depends on $R$ alone and is at least every column $k$ with $k^2\le(R-1)^3$; the bound then no longer contains $k$, and the comparison with the pair side becomes an inequality in the single variable $\sqrt R$. Raising the threshold costs little, because the chain sum grows slowly with it. In the floating-point evaluation reported below, the left side at $R=42$ grows by about $1.3\%$ between $y=253$ and $y=262$, the two ends of the range of columns $k$ with $40^3\le k^2\le41^3$.

The number $c'$ is the point at which a tangent of the exponential is taken: the chain sum of the part before a cut is bounded from below through $e^{-x}\ge e^{-c'}(1+c'-x)$ (`Parking.Lam_tangent`). Every $c'\ge-1$ gives a valid bound; the best value is the mean exponent, which depends on $R$ and $K$, and in the application one fixed numerical value is used. The hypothesis $1+c'\ge0$ is needed because the first sum of the proof is bounded from below and is multiplied by $1+c'$.

**Where the bound gives something away.** A floating-point evaluation at $R=42$, $y=262$, $c'=0.35$ and $K=41\cdot83/(2\sqrt{42})=262.547\ldots$, which is not part of the proof, gives: $P(R)=0.06144$; the left side $0.03947$ (and $0.03894$ at $y=253$); the same chain sum at the threshold $K$, $0.03950$; the bound with the two sums of step 2 of the proof, $0.04067$; and the right side of the theorem, $0.04186$. So the tangent inequality costs about $3\%$ and the two closed forms together another $3\%$, most of it in the first sum, where the denominator $K+R-s$ is replaced by $K+R-1$ and the closed form is $0.963$ of the sum.

**The Lean form.** The left side is `Real.exp (-R) * Lam (thr (y + 1) (y + R)) R` and the right side is as displayed, with $R$ cast to a real number, $\frac45R-1$ written `4 / 5 * R - 1` and $K+\frac35R$ written `K + 3 / 5 * R`. Under the hypotheses all denominators are positive: $y+R-s\ge1$ at the cut points, and $K\ge R\ge1$. So no convention of the proof assistant intervenes.

## Proof

Throughout, $\operatorname{ren}(m)=m^m/m!$ (`Parking.ren`), so that $P(m)=e^{-m}\operatorname{ren}(m)$, and for $0<s<R$
$$\delta(s)=1-\frac{K+1}{K+R-s}=\frac{R-1-s}{K+R-s}.$$
Since $R\ge1$ and $K\ge R$, we have $K>0$, and $0\le\delta(s)<1$. The proof has four steps: the chain sum is raised to the threshold $K$; at that threshold it is bounded through the first cut at which the factor $1$ is not chosen, which gives a bound with two sums; and each of the two sums is replaced by a closed form.

**Step 1: raising the threshold.** For $0\le y\le K$,
$$\Lambda_R(y+1;y+R)\le\Lambda_R(K+1;K+R).$$
At a cut point $0<s<R$ the factor $\frac{y+1}{y+R-s}$ is nonnegative, and it does not decrease with $y$: for $y\le y'$, cross-multiplying, $\frac{y+1}{y+R-s}\le\frac{y'+1}{y'+R-s}$ is equivalent to $(y'-y)(R-s-1)\ge0$, which holds because $R-s\ge1$. The total weight of the compositions is monotone in a nonnegative profile (`Parking.Lam_mono`).

**Step 2: the bound with two sums.** For $K>0$ and every real $c'$,
$$e^{-R}\Lambda_R(K+1;K+R)\ \le\ P(R)-e^{-c'}\Bigl((1+c')\,\Sigma_1-\frac{1}{K+1}\,\Sigma_2\Bigr),\tag{1}$$
$$\Sigma_1=\sum_{0<s<R}\delta(s)\,P(s)\,P(R-s),\qquad\Sigma_2=\sum_{0<s<R}\delta(s)\,\bigl(R-1-\tfrac s2\bigr)\,P(R-s)\,\kappa_2(s).$$

*The first violating point.* `Parking.Lam_defect` states, for every cut profile $f$ and $m\ge1$, that $\operatorname{ren}(m)-\Lambda_m[f]=\sum_{0<s<m}\operatorname{ren}(m-s)\,(1-f(s))\,\Lambda_s[f]$. (Expand the weight for the profile $1=f+(1-f)$ and sort the compositions by the first cut point $s$ at which the factor $1-f(s)$ is chosen: before $s$ the profile is $f$, after it the profile is $1$.) Apply it with $m=R$ and $f(s)=\frac{K+1}{K+R-s}$, for which $1-f(s)=\delta(s)$ and $\Lambda_s[f]=\Lambda_s(K+1;K+R)$, and multiply by $e^{-R}=e^{-s}e^{-(R-s)}$:
$$P(R)-e^{-R}\Lambda_R(K+1;K+R)=\sum_{0<s<R}\delta(s)\cdot e^{-s}\Lambda_s(K+1;K+R)\cdot P(R-s).\tag{2}$$

*The chain sum before a cut.* For $0<s<R$ and every real $c'$,
$$e^{-c'}\Bigl((1+c')\,P(s)-\frac{1}{K+1}\bigl(R-1-\tfrac s2\bigr)\kappa_2(s)\Bigr)\ \le\ e^{-s}\Lambda_s(K+1;K+R).\tag{3}$$
At a cut point $0<c<s$ the factor is $\frac{K+1}{K+R-c}=e^{-x(c)}$ with $x(c)=\log\frac{K+R-c}{K+1}$, and the chain sum depends on the profile at these points only (`Parking.Lam_congr`). `Parking.Lam_tangent` states, for exponents $x$, a real $\mu$ and $m\ge1$, that $e^{-\mu}\bigl((1+\mu)\operatorname{ren}(m)-\sum_{0<c<m}\operatorname{ren}(m-c)\operatorname{ren}(c)\,x(c)\bigr)\le\Lambda_m[e^{-x}]$. With $m=s$ and $\mu=c'$, multiplied by $e^{-s}$, and with $e^{-s}\operatorname{ren}(c)\operatorname{ren}(s-c)=P(c)P(s-c)$ (`Parking.poissonMass_mul`), it gives
$$e^{-c'}\Bigl((1+c')\,P(s)-\sum_{0<c<s}P(c)\,P(s-c)\,x(c)\Bigr)\ \le\ e^{-s}\Lambda_s(K+1;K+R).$$
Now $\log t\le t-1$ gives $x(c)\le\frac{K+R-c}{K+1}-1=\frac{R-1-c}{K+1}$, and the weights $P(c)P(s-c)$ are positive (`Parking.poissonMass_pos`). Their sum over $0<c<s$ is $\kappa_2(s)$ by definition, and $\sum_{0<c<s}c\,P(c)P(s-c)=\frac s2\kappa_2(s)$ by `Parking.kc2_mom`. Hence $\sum_{0<c<s}P(c)P(s-c)\,x(c)\le\frac{1}{K+1}\bigl(R-1-\frac s2\bigr)\kappa_2(s)$, which proves (3).

*Conclusion of step 2.* In (2) every term has the nonnegative factors $\delta(s)$ and $P(R-s)$, so (3) may be inserted. The sum of the resulting lower bounds is $e^{-c'}\bigl((1+c')\Sigma_1-\frac{1}{K+1}\Sigma_2\bigr)$, and (1) follows.

**Step 3: the first sum.** For $K>0$ and $R\ge1$,
$$\frac{R-2}{2\,(K+R-1)}\,\kappa_2(R)\ \le\ \Sigma_1 .$$
For $0<s<R$ the numerator $R-1-s$ is nonnegative and $K+R-s\le K+R-1$, so $\delta(s)\ge\frac{R-1-s}{K+R-1}$. The weights $P(s)P(R-s)$ sum to $\kappa_2(R)$ and have the first moment $\frac R2\kappa_2(R)$ (`Parking.kc2_mom`), so $\sum_{0<s<R}(R-1-s)\,P(s)P(R-s)=\bigl(R-1-\frac R2\bigr)\kappa_2(R)=\frac{R-2}{2}\kappa_2(R)$.

**Step 4: the second sum.** For $R\ge1$ and $K\ge R$,
$$\Sigma_2\ \le\ \frac{R-3}{3}\,\kappa_3(R)\cdot\frac{\frac45R-1}{K+\frac35R}.$$
Write $\Sigma_2=\sum_{0<s<R}w_s\,h(s)$ with the weights and the function
$$w_s=P(R-s)\,(R-1-s)\,\kappa_2(s)\ \ge0,\qquad h(x)=\frac{R-1-\frac x2}{K+R-x}=\frac12-\frac{K-R+2}{2\,(K+R-x)} .$$
(The weights are nonnegative by `Parking.kc2_nonneg`.) Since $K-R+2>0$, the function $h$ is concave and decreasing on $x<K+R$. Two facts about the weights are used: their sum is $\sum_sw_s=\frac{R-3}{3}\kappa_3(R)$ (`Parking.impulse_weight_sum`), and their mean position is at least $x_0=\frac{2R}{5}$, that is, $\frac{2R}{5}\sum_sw_s\le\sum_ss\,w_s$ (`Parking.impulse_weight_mean`). The concavity is used in the form of an explicit tangent at $x_0$. With $D=K+R-x_0=K+\frac35R>0$, $M=K+R-s>0$ and $\gamma=K-R+2>0$, a direct computation gives the identity
$$\frac{\frac D2-\frac\gamma2}{D}-\frac{\gamma}{2D^{2}}\,(D-M)-\frac{\frac M2-\frac\gamma2}{M}=\frac{\gamma\,(D-M)^{2}}{2\,D^{2}\,M}\ \ge\ 0 .$$
Here $\frac D2-\frac\gamma2=\frac45R-1$, $\frac M2-\frac\gamma2=R-1-\frac s2$ and $D-M=s-x_0$, so the identity says
$$h(s)\ \le\ h(x_0)-\frac{\gamma}{2D^{2}}\,(s-x_0),\qquad h(x_0)=\frac{\frac45R-1}{K+\frac35R}.$$
Multiply by $w_s\ge0$ and sum over $0<s<R$:
$$\Sigma_2\ \le\ h(x_0)\sum_sw_s-\frac{\gamma}{2D^{2}}\Bigl(\sum_ss\,w_s-\frac{2R}{5}\sum_sw_s\Bigr)\ \le\ h(x_0)\sum_sw_s,$$
because $\gamma>0$ and the bracket is nonnegative. Inserting the value of $\sum_sw_s$ gives the claim.

**Conclusion.** Let $R\ge1$, $0\le y\le K$, $R\le K$ and $1+c'\ge0$. Step 1, multiplied by $e^{-R}>0$, and step 2 give $e^{-R}\Lambda_R(y+1;y+R)\le P(R)-e^{-c'}\bigl((1+c')\Sigma_1-\frac{1}{K+1}\Sigma_2\bigr)$. By step 3 and $1+c'\ge0$, $(1+c')\Sigma_1\ge(1+c')\frac{R-2}{2(K+R-1)}\kappa_2(R)$; by step 4 and $\frac{1}{K+1}>0$, $\frac{1}{K+1}\Sigma_2\le\frac{1}{K+1}\cdot\frac{R-3}{3}\kappa_3(R)\cdot\frac{\frac45R-1}{K+\frac35R}$. Since $e^{-c'}>0$, the bracket of step 2 is at least the bracket of the statement, and the statement follows.

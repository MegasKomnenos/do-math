---
weight: unit
short: lower bound of the pair sum
---
## Description

For $k\ge1$, $R\le k$ and all real $\theta\ge0$ and $\mu$: $a_k e^{R}e^{-\mu}\bigl((1+\mu)W_\Sigma-(\alpha G+\beta\mathcal A)\bigr)\le\mathcal P(k,R)$ with $\alpha=\log(1+\theta)-\frac{\theta}{1+\theta}$ and $\beta=\frac{1}{k(1+\theta)}$. The pair sum of the pair–impulse criterion is bounded from below by three sums $W_\Sigma$, $G$, $\mathcal A$ of convolutions of the Poisson mass.

## Statement

Let $k\ge1$ and $R\le k$ be natural numbers, and let $\theta\ge0$ and $\mu$ be real numbers. Put
$$\alpha=\log(1+\theta)-\frac{\theta}{1+\theta},\qquad\beta=\frac{1}{k\,(1+\theta)} .$$
Then
$$a_k\,e^{R}\,e^{-\mu}\Bigl((1+\mu)\,W_\Sigma(R)-\bigl(\alpha\,G(k,R)+\beta\,\mathcal A(k,R)\bigr)\Bigr)\ \le\ \mathcal P(k,R).$$

Here $a_k=k^{k-1}/k!$ is the Cayley coefficient (`Parking.cay`), and $W_\Sigma(R)$, $G(k,R)$, $\mathcal A(k,R)$ are the sums of `Parking.Wsum`, `Parking.Gsum`, `Parking.Asum`. The right side is the pair sum of `Parking.pairSum`. By its definition and that of `Parking.Lam1`, with $N=k+R$ and the cut profile $f(s)=k/(N-s)$ (`Parking.thr`),
$$\mathcal P(k,R)=\sum_{b=1}^{R}\ \sum_{0<a<b}\Lambda_a[f]\;f(a)\;\Lambda_{b-a}[f(a+\cdot)]\;f(b)\;z^{(k)}_{N-b-1},$$
where $\Lambda_m[g]$ is the total weight of the compositions of $m$ for a cut profile $g$ (`Parking.Lam`), $f(a+\cdot)$ is the profile $s\mapsto f(a+s)=k/(N-a-s)$, and $z^{(k)}_n=A(n,k-1)/n!$ is the environment of the threshold $k$ (`Parking.zr`), $A(n,k-1)$ being the number of parking functions of length $n$ with maximum displacement at most $k-1$. In the notation $\Lambda_m(y;N)$ for the total weight of the compositions of $m$ with the cut factors $y/(N-s)$, the two composition sums of a term are the chain sums $\Lambda_a(k;N)$ and $\Lambda_{b-a}(k;N-a)$, and $f(a)=k/(N-a)$, $f(b)=k/(N-b)$; this is the form in which the record of `Parking.pairSum` displays the sum.

## Explanation

**What the theorem is for.** At a position $(k+R-1,k)$ with $1\le R\le k-2$, the pair–impulse criterion `Parking.dq_pos_of_pair` says that the step $b(k+R-1,k)-b(k+R-1,k-1)$ is positive as soon as $k\,a_k\,\Lambda_R(k+1;k+R)<2\mathcal P(k,R)$. The chain sum $\Lambda_R(k+1;k+R)$ on the left, the total weight of the compositions of $R$ with the cut factors $(k+1)/(k+R-s)$, is the boundary term. The pair sum is a sum over pairs of marked cut points of products of chain sums and of the environment, and none of these has a closed form. The theorem replaces it by an expression in which the column $k$ occurs only through $a_k$, $\beta$ and a small correction inside $G$ and $\mathcal A$, and in which everything else is a sum of the two convolutions $\kappa_2$, $\kappa_3$ of the Poisson mass $P(m)=e^{-m}m^m/m!$ (`Parking.kc2`, `Parking.kc3`). The boundary term has the upper bound `Parking.impulse_le` of the same kind. The two bounds are compared on the curve $k^2\approx R^3$, where the three sums are bounded by polynomials in $\sqrt R$, and the outcome is the curve increase `Parking.curve_crossing`.

**The idea.** Every factor of a pair term is a sum, over compositions or over chains, of products of cut factors $k/(k+y)$, where $y\ge0$ is the excess of a size over $k$. Write such a factor as $e^{-L(y)}$ with the *log-excess* $L(y)=\log(1+y/k)$. Then each factor of the pair term is an average of exponentials, and Jensen's inequality bounds it from below by the exponential of minus the average exponent. For the chain sums this is `Parking.Lam_jensen`, for the environment `Parking.zr_jensen`. The result for one pair $a<b$ is a lower bound $a_ke^{R}\,P(a)P(b-a)\,e^{-X_{ab}}$, in which $P(a)P(b-a)$ is the value that the two chain sums would have with all cut factors equal to $1$, up to the factor $e^{b}$, and $X_{ab}$ is the mean total log-excess of the pair. The pair sum is thus at least $a_ke^{R}$ times a sum of exponentials $e^{-X_{ab}}$ with the weights $P(a)P(b-a)$, whose total is $W_\Sigma$.

**The two parameters.** Two tangent lines turn this into a statement about three sums. The exponential lies above each of its tangents, $e^{-X}\ge e^{-\mu}(1+\mu-X)$, so the sum of the exponentials is at least $e^{-\mu}\bigl((1+\mu)W_\Sigma-\sum P(a)P(b-a)X_{ab}\bigr)$. And the logarithm lies below each of its tangents: for $\theta\ge0$ the tangent of $L$ at the excess $y=k\theta$ is the line $\alpha+\beta y$, and $L(y)\le\alpha+\beta y$ for $y\ge0$. With a line in the place of $L$ the sum of the exponents can be evaluated, because the moment identities of the convolutions (`Parking.kc2_mom`, `Parking.kc3_mom_left`, `Parking.kc3_mom_right`) give the mean positions of the marked points and of the cut points; the result is $\alpha G+\beta\mathcal A$. The sum of the logarithms themselves has no such evaluation, and this is the reason for the tangent of $L$.

The parameters are left free because the theorem is used together with numerical bounds of the three sums: a lower bound of $W_\Sigma$ and upper bounds of $G$ and $\mathcal A$. For $\mu\ge-1$ the left side of the theorem increases with $W_\Sigma$ and decreases with $G$ and $\mathcal A$ (note $\alpha\ge0$ and $\beta>0$), so such bounds can be inserted, and $\theta$ and $\mu$ are then chosen in terms of the inserted bounds. The best choice for given values of the sums is $k\theta=\mathcal A/G$, the mean excess, and $\mu=\frac{G}{W_\Sigma}\log(1+\theta)$, the bound of the mean exponent. With it the terms $-\frac{\theta}{1+\theta}G$ and $\beta\mathcal A$ cancel and the theorem reads
$$\mathcal P(k,R)\ \ge\ a_k\,e^{R}\;W_\Sigma\,\Bigl(1+\frac{\mathcal A}{k\,G}\Bigr)^{-G/W_\Sigma}.$$
This is the form in which the bound is best understood: $W_\Sigma$ pairs, each carrying in the mean $G/W_\Sigma$ factors $k/(k+y)$ at the mean excess $y=\mathcal A/G$.

**Why the curve $k^2=R^3$.** The sums are of the orders $W_\Sigma\sim R$, $G\sim R^{3/2}$, $\mathcal A\sim R^{5/2}$, and the mean excess $\mathcal A/G$ is about $R/2$. The exponent of the displayed bound is therefore about $\frac{G}{W_\Sigma}\cdot\frac{R}{2k}$, of the order $R^{3/2}/k$. For $k$ much larger than $R^{3/2}$ the exponent is small and the bound is close to $a_ke^{R}W_\Sigma$; for $k$ of the order $R^{3/2}$ the exponent is of order $1$, and the bound keeps a fixed fraction of $a_ke^{R}W_\Sigma$, neither close to all of it nor negligible. This is the range of the curve increase, and it is why the constants of the three sums have to be exact there.

**How much the bound gives away.** A floating-point evaluation, which is not part of the proof, gives at $R=42$, $k=262$ the values $W_\Sigma=14.916$, $G=169.0$, $\mathcal A=3863.0$, and the bound with the best parameters is $0.934$ of the pair sum. In the same evaluation most of the loss comes from Jensen's inequality for the chain sums and the environment of each pair; the loss grows when $k$ decreases at fixed $R$, that is, away from the curve into the range where the cut factors are far from $1$.

**The hypotheses.** $R\le k$ places the sizes $N-b$, $1\le b\le R$, in the range $k\le N-b\le 2k-1$ in which the environment satisfies a Volterra equation with the Cayley kernel, which is what `Parking.zr_jensen` needs. This is the only use of the hypothesis, and it is more than that use requires: `Parking.zr_jensen` is stated for sizes up to $2k+1$, which $R\le k+2$ would already give. $k\ge1$ makes the log-excess meaningful. For $R\le1$ both sides are zero.

**The Lean form.** The left side is `cay k * Real.exp R * (Real.exp (-μ) * ((1 + μ) * Wsum R - ((Real.log (1 + θ) - θ / (1 + θ)) * Gsum k R + 1 / (k * (1 + θ)) * Asum k R)))`, with $k$ and $R$ cast to real numbers. No convention of the proof assistant intervenes: all denominators are positive under the hypotheses, and the index $N-b-1$ of the environment is a difference of natural numbers with $N-b\ge k\ge1$.

## Proof

Throughout, $N=k+R$, $f(s)=k/(N-s)$, $\operatorname{ren}(m)=m^m/m!$ (`Parking.ren`), $P(m)=e^{-m}\operatorname{ren}(m)$, and $L(y)=\log(1+y/k)$ for real $y\ge0$. All sums over $0<c<m$ and the like run over natural numbers. The proof has four parts: the properties of $L$; the lower bound for one pair; the bound for the sum of the exponents, which is the longest part; and the assembly.

**1. The log-excess.** Four facts are used.

(a) $L(y)\ge0$ for $y\ge0$.

(b) For natural numbers $j\ge k$: $L(j-k)=\log j-\log k=\log(j/k)$.

(c) For $y\ge0$: $L(y)\le\alpha+\beta y$. Indeed $\log t\le t-1$ at $t=\frac{1+y/k}{1+\theta}>0$ gives $L(y)-\log(1+\theta)\le\frac{1+y/k}{1+\theta}-1=-\frac{\theta}{1+\theta}+\frac{y}{k(1+\theta)}$.

(d) For a natural number $s\le R$: $f(s)=\frac{k}{k+(R-s)}=e^{-L(R-s)}$.

**2. One pair.** For $0<a<b\le R$ define the exponent $X_{ab}=X^{(1)}+\dots+X^{(6)}$ by
$$X^{(1)}=\frac{1}{\operatorname{ren}(a)}\sum_{0<c<a}\operatorname{ren}(a-c)\operatorname{ren}(c)\,L(R-c),\qquad X^{(2)}=L(R-a),$$
$$X^{(3)}=\frac{1}{\operatorname{ren}(b-a)}\sum_{0<c<b-a}\operatorname{ren}(b-a-c)\operatorname{ren}(c)\,L(R-a-c),\qquad X^{(4)}=L(R-b),$$
$$X^{(5)}=\log\frac{a_k\,e^{R-b}}{a_{N-b}},\qquad X^{(6)}=\frac{1}{a_{N-b}}\sum_{k<t<N-b}\operatorname{ren}(N-b-t)\,a_t\,\log\frac tk .$$
A cut point $s$ stands for the size $N-s$, and the words above and below refer to sizes. So $X^{(1)}$ is the mean total log-excess of the cut points $c<a$ of the first chain, which lie above $a$; $X^{(2)}$ is the log-excess of $a$; $X^{(3)}$ is the mean total log-excess of the cut points $a+c$ between $a$ and $b$; $X^{(4)}$ is the log-excess of $b$; $X^{(5)}$ is an end term that compares the Cayley coefficients at the sizes $k$ and $N-b$; and $X^{(6)}$ is the mean total of $\log(t/k)$ over the sizes $k<t<N-b$ below $b$ that the environment visits. The claim is
$$a_k\,e^{R}\,P(a)\,P(b-a)\,e^{-X_{ab}}\ \le\ \Lambda_a[f]\;f(a)\;\Lambda_{b-a}[f(a+\cdot)]\;f(b)\;z^{(k)}_{N-b-1}.\tag{1}$$
The five factors on the right are bounded from below one by one.

- By (d) the profile $f$ agrees at the cut points $0<s<a$ with $s\mapsto e^{-L(R-s)}$, and $\Lambda_a$ depends on the profile at these points only (`Parking.Lam_congr`). `Parking.Lam_jensen`, applied to the exponents $x(s)=L(R-s)$, states $\operatorname{ren}(a)\,\exp\bigl(-\frac{1}{\operatorname{ren}(a)}\sum_{0<c<a}\operatorname{ren}(a-c)\operatorname{ren}(c)\,x(c)\bigr)\le\Lambda_a[e^{-x}]$. Hence $\operatorname{ren}(a)\,e^{-X^{(1)}}\le\Lambda_a[f]$.
- By (d), $f(a)=e^{-X^{(2)}}$ and $f(b)=e^{-X^{(4)}}$.
- In the same way the profile $f(a+\cdot)$ agrees at the cut points $0<s<b-a$ with $s\mapsto e^{-L(R-a-s)}$, and `Parking.Lam_jensen` gives $\operatorname{ren}(b-a)\,e^{-X^{(3)}}\le\Lambda_{b-a}[f(a+\cdot)]$.
- `Parking.zr_jensen` states, for $k\ge1$ and $1\le M\le2k+1$, that $a_M\exp\bigl(-\frac{1}{a_M}\sum_{k<t<M}\operatorname{ren}(M-t)\,a_t\log\frac tk\bigr)\le z^{(k)}_{M-1}$. With $M=N-b$, which satisfies $k\le M\le2k-1$ because $1\le b\le R\le k$, this is $a_{N-b}\,e^{-X^{(6)}}\le z^{(k)}_{N-b-1}$.
- By the definition of $X^{(5)}$, $a_{N-b}=a_k\,e^{R-b}\,e^{-X^{(5)}}$; here $a_k>0$ and $a_{N-b}>0$ (`Parking.cay_pos`).

All five lower bounds are positive, since $\operatorname{ren}(m)>0$ (`Parking.ren_pos`), $a_{N-b}>0$ and exponentials are positive; so they may be multiplied. Their product is $\operatorname{ren}(a)\operatorname{ren}(b-a)\,a_k\,e^{R-b}\,e^{-X_{ab}}$, and since $\operatorname{ren}(a)=e^{a}P(a)$, $\operatorname{ren}(b-a)=e^{b-a}P(b-a)$ and $e^{a}e^{b-a}e^{R-b}=e^{R}$, this is the left side of (1).

**3. The sum of the exponents.** The claim of this part is
$$\sum_{b=1}^{R}\ \sum_{0<a<b}P(a)\,P(b-a)\,X_{ab}\ \le\ \alpha\,G(k,R)+\beta\,\mathcal A(k,R).\tag{2}$$
Only (a), (b), (c) and identities for the convolutions enter; from $\theta$ nothing is used except the inequality (c). Fix $b$ with $1\le b\le R$. The sums over $a$ of the six parts are treated in five rows. The weights $P(a)P(b-a)$ are positive (`Parking.poissonMass_pos`), $\kappa_2\ge0$ and $\kappa_3\ge0$ (`Parking.kc2_nonneg`, `Parking.kc3_nonneg`), and for $g\le m$ one has $P(g)P(m-g)=e^{-m}\operatorname{ren}(g)\operatorname{ren}(m-g)$ (`Parking.poissonMass_mul`).

*Row for a marked point.* For a natural number $m$ and a real number $\rho\ge m$,
$$\sum_{0<g<m}P(g)\,P(m-g)\,L(\rho-g)\ \le\ \Bigl(\alpha+\beta\bigl(\rho-\tfrac m2\bigr)\Bigr)\kappa_2(m).\tag{3}$$
By (c), $L(\rho-g)\le\alpha+\beta\rho-\beta g$. The sum of the weights is $\kappa_2(m)$ by definition, and $\sum_{0<g<m}g\,P(g)P(m-g)=\frac m2\kappa_2(m)$ by `Parking.kc2_mom`. With $m=b$ and $\rho=R$, (3) bounds the sum of the parts $X^{(2)}$:
$$\sum_{0<a<b}P(a)P(b-a)\,X^{(2)}\le\Bigl(\alpha+\beta\bigl(R-\tfrac b2\bigr)\Bigr)\kappa_2(b).$$

*Row for the cut points above $a$.* Since $P(a)/\operatorname{ren}(a)=e^{-a}$, `Parking.poissonMass_mul` gives $P(a)\,X^{(1)}=\sum_{0<c<a}P(c)P(a-c)\,L(R-c)$, and by (3) with $m=a$, $\rho=R$ this is at most $\bigl(\alpha+\beta(R-\frac a2)\bigr)\kappa_2(a)$. Multiply by $P(b-a)$ and sum over $a$: $\sum_{0<a<b}\kappa_2(a)P(b-a)=\kappa_3(b)$ by definition and $\sum_{0<a<b}a\,\kappa_2(a)P(b-a)=\frac{2b}{3}\kappa_3(b)$ by `Parking.kc3_mom_left`. Hence
$$\sum_{0<a<b}P(a)P(b-a)\,X^{(1)}\le\Bigl(\alpha+\beta\bigl(R-\tfrac b3\bigr)\Bigr)\kappa_3(b).$$

*Row for the cut points between $a$ and $b$.* In the same way $P(b-a)\,X^{(3)}=\sum_{0<c<b-a}P(c)P(b-a-c)\,L(R-a-c)$, and (3) with $m=b-a$ and $\rho=R-a\ge b-a$ bounds this by $\bigl(\alpha+\beta(R-\frac b2-\frac a2)\bigr)\kappa_2(b-a)$. Multiply by $P(a)$ and sum over $a$: $\sum_{0<a<b}P(a)\kappa_2(b-a)=\kappa_3(b)$ by `Parking.kc3_comm` and $\sum_{0<a<b}a\,P(a)\kappa_2(b-a)=\frac b3\kappa_3(b)$ by `Parking.kc3_mom_right`. Hence
$$\sum_{0<a<b}P(a)P(b-a)\,X^{(3)}\le\Bigl(\alpha+\beta\bigl(R-\tfrac{2b}3\bigr)\Bigr)\kappa_3(b).$$

*Row for the point $b$ and the end term.* The end term satisfies $X^{(5)}\le\frac32L(R-b)$. Indeed `Parking.borel_log_mono` states $\log a_i-i+\frac32\log i\le\log a_j-j+\frac32\log j$ for $1\le i\le j$; with $i=k$ and $j=N-b$ this is $\log a_k+(R-b)-\log a_{N-b}\le\frac32\bigl(\log(N-b)-\log k\bigr)$, and the right side is $\frac32L(R-b)$ by (b). So $X^{(4)}+X^{(5)}\le\frac52L(R-b)\le\frac52\bigl(\alpha+\beta(R-b)\bigr)$ by (c). These parts do not depend on $a$, and the weights sum to $\kappa_2(b)$:
$$\sum_{0<a<b}P(a)P(b-a)\bigl(X^{(4)}+X^{(5)}\bigr)\le\tfrac52\bigl(\alpha+\beta(R-b)\bigr)\kappa_2(b).$$

Adding the four rows, the parts $X^{(1)},\dots,X^{(5)}$ contribute for the fixed $b$ at most
$$\alpha\Bigl(\tfrac72\kappa_2(b)+2\kappa_3(b)\Bigr)+\beta\Bigl(\bigl(R-\tfrac b2\bigr)\bigl(\kappa_2(b)+2\kappa_3(b)\bigr)+\tfrac52(R-b)\kappa_2(b)\Bigr),$$
and the sum of this over $1\le b\le R$ is $\alpha$ times the first sum of $G$ plus $\beta$ times the first sum of $\mathcal A$.

*Row for the environment below $b$.* The part $X^{(6)}$ does not depend on $a$ either, so its contribution is $\sum_{b=1}^{R}\kappa_2(b)\,X^{(6)}$, where $X^{(6)}$ depends on $b$. The claim is
$$\sum_{b=1}^{R}\kappa_2(b)\,X^{(6)}\ \le\ \sum_{0<c<R}\kappa_3(c)\,(1+\varrho_c)\,\bigl(\alpha+\beta(R-c)\bigr),\qquad\varrho_c=\varrho(N,c)\tag{4}$$
with $\varrho$ as in `Parking.rhoC`; the right side is $\alpha$ times the second sum of $G$ plus $\beta$ times the second sum of $\mathcal A$, so (4) completes (2). The proof of (4) has three steps.

First, the sum in $X^{(6)}$ is rewritten in the coordinate of a cut point. The substitution $t=N-c$ turns the range $k<t<N-b$ into $b<c<R$, and $\log\frac tk=L(t-k)=L(R-c)$ by (b), so
$$\sum_{k<t<N-b}\operatorname{ren}(N-b-t)\,a_t\,\log\frac tk=\sum_{b<c<R}\operatorname{ren}(c-b)\,a_{N-c}\,L(R-c).$$

Second, the weight of the cut point $c$ is bounded. `Parking.borel_ratio_le` states $e^{j-i}a_i/a_j\le1+\frac32z+\frac38z^{2}$ with $z=(j-i)/i$ for $1\le i\le j$. With $i=N-c$ and $j=N-b$, so that $j-i=c-b$, and with $\operatorname{ren}(c-b)=e^{c-b}P(c-b)$,
$$\frac{\operatorname{ren}(c-b)\,a_{N-c}}{a_{N-b}}\ \le\ P(c-b)\Bigl(1+\frac32\cdot\frac{c-b}{N-c}+\frac38\Bigl(\frac{c-b}{N-c}\Bigr)^{2}\Bigr).$$
Since $L(R-c)\ge0$ by (a), the left side of (4) is at most
$$\sum_{b=1}^{R}\ \sum_{b<c<R}\kappa_2(b)\,P(c-b)\Bigl(1+\frac32\cdot\frac{c-b}{N-c}+\frac38\Bigl(\frac{c-b}{N-c}\Bigr)^{2}\Bigr)L(R-c).$$

Third, the two sums are exchanged, so that $c$ runs over $0<c<R$ and $b$ over $0<b<c$, and the inner sum is evaluated for fixed $c$. Put $D=N-c>0$. Since $0\le c-b\le c$, one has $(c-b)^2\le c\,(c-b)$, and therefore
$$1+\frac32\cdot\frac{c-b}{D}+\frac38\Bigl(\frac{c-b}{D}\Bigr)^{2}\ \le\ \Bigl(1+\frac{3c}{2D}+\frac{3c^{2}}{8D^{2}}\Bigr)-b\,\Bigl(\frac{3}{2D}+\frac{3c}{8D^{2}}\Bigr).$$
Multiply by $\kappa_2(b)P(c-b)\ge0$ and sum over $0<b<c$, using $\sum_b\kappa_2(b)P(c-b)=\kappa_3(c)$ and $\sum_b b\,\kappa_2(b)P(c-b)=\frac{2c}{3}\kappa_3(c)$ (`Parking.kc3_mom_left`):
$$\sum_{0<b<c}\kappa_2(b)\,P(c-b)\Bigl(1+\frac32\cdot\frac{c-b}{D}+\frac38\Bigl(\frac{c-b}{D}\Bigr)^{2}\Bigr)\ \le\ \kappa_3(c)\Bigl(1+\frac{c}{2D}+\frac{c^{2}}{8D^{2}}\Bigr)=\kappa_3(c)\,(1+\varrho_c).$$
Finally $L(R-c)\le\alpha+\beta(R-c)$ by (c), and the factor $\kappa_3(c)(1+\varrho_c)$ is nonnegative by `Parking.rhoC_nonneg`. This proves (4), and with it (2).

**4. Assembly.** For every real $X$, $e^{\mu-X}\ge1+\mu-X$, hence $e^{-X}\ge e^{-\mu}(1+\mu-X)$. Applied to $X=X_{ab}$ in (1), and since $a_ke^{R}P(a)P(b-a)\ge0$, every term of the pair sum satisfies
$$a_k\,e^{R}\,e^{-\mu}\Bigl((1+\mu)\,P(a)P(b-a)-P(a)P(b-a)\,X_{ab}\Bigr)\ \le\ \Lambda_a[f]\;f(a)\;\Lambda_{b-a}[f(a+\cdot)]\;f(b)\;z^{(k)}_{N-b-1}.$$
Sum over $1\le b\le R$ and $0<a<b$. The right sides add up to $\mathcal P(k,R)$. On the left, $\sum_{b}\sum_{a}P(a)P(b-a)=\sum_b\kappa_2(b)=W_\Sigma(R)$, so the left sides add up to
$$a_k\,e^{R}\,e^{-\mu}\Bigl((1+\mu)\,W_\Sigma(R)-\sum_{b=1}^{R}\sum_{0<a<b}P(a)P(b-a)\,X_{ab}\Bigr).$$
By (2) the double sum is at most $\alpha G(k,R)+\beta\mathcal A(k,R)$, and it enters with the nonpositive factor $-a_ke^{R}e^{-\mu}$. This gives the statement.

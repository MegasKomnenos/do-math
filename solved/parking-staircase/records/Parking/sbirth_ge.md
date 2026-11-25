---
weight: unit
short: lower bound for the mean of the birthday law
---
## Description

The mean $s_m=\sum_{j=1}^{m}\prod_{i<j}(1-\frac im)$ of the birthday law (Ramanujan's function $Q(m)$) satisfies $\frac{1}{2P(m)}-\frac13-\frac{1}{15m}\le s_m$ for every $m\ge2$, where $P(m)=e^{-m}m^m/m!$. This is the lower half of Ramanujan's estimate for the Poisson law: $e^{-m}\sum_{i\le m}m^i/i!\ge\frac12+\bigl(\frac23-\frac{1}{15m}\bigr)P(m)$.

## Statement

For a natural number $m$ let $s_m=\sum_{j=1}^{m}\prod_{i=0}^{j-1}\bigl(1-\frac im\bigr)$ (`Parking.sbirth`) and let $P(m)=e^{-m}m^m/m!$ be the Poisson mass (`Parking.poissonMass`). Then for every natural number $m\ge2$,
$$\frac{1}{2\,P(m)}-\frac13-\frac{1}{15\,m}\ \le\ s_m .$$

## Explanation

**The quantity and two other forms of the statement.** The number $s_m$ is the mean of the number of uniform draws from $m$ values before the first repetition; the record of `Parking.sbirth` describes it. Let $\mathfrak p(m)=e^{-m}\sum_{i=0}^{m}m^i/i!$ be the probability that a Poisson variable of mean $m$ is at most $m$; $P(m)$ is the probability that it equals $m$. Multiplying out the products gives $1+s_m=\mathfrak p(m)/P(m)$ for $m\ge1$ (step 1 of the proof), so the statement is equivalent to
$$\mathfrak p(m)\ \ge\ \frac12+\Bigl(\frac23-\frac{1}{15\,m}\Bigr)P(m)\qquad(m\ge2).$$
In the classical notation, in which $\theta_m$ is defined by $\frac12e^{m}=\sum_{i<m}\frac{m^i}{i!}+\theta_m\frac{m^m}{m!}$, one has $\mathfrak p(m)=\frac12+(1-\theta_m)P(m)$, and the statement is $\theta_m\le\frac13+\frac{1}{15m}$. With Stirling's bound $P(m)\le1/\sqrt{2\pi m}$ (`Parking.poissonMass_le_c0`) the theorem gives $s_m\ge\sqrt{\pi m/2}-\frac13-\frac{1}{15m}$.

**The two halves.** The library proves the other half, $\mathfrak p(m)\le\frac12+\frac23P(m)$ for $m\ge1$, on the way to its upper bound for $s_m$, and the present module is built on the same objects. Both halves compare $\mathfrak p(m+1)-\mathfrak p(m)$ with $\frac23\bigl(P(m+1)-P(m)\bigr)$. With $g_m(x)=e^{-x}x^m/m!$, the difference $\mathfrak p(m+1)-\mathfrak p(m)$ is $P(m+1)$ minus the integral of $g_m$ over $[m,m+1]$, and the claim is about the two-point rule $\frac23g_m(m)+\frac13g_m(m+1)$ for this integral: the upper half says that the rule is not below the integral, the lower half that it exceeds the integral by at most $\frac{2}{45}P(m)/m^2$. Both follow from a pointwise estimate of $g_m$ to the right of its maximum,
$$g_m(m)\Bigl(1-\frac{s^3/6+s^4/8}{m^2}\Bigr)\ \le\ g_m(m+s)\Bigl(1+\frac{s^2}{2(m+s)}\Bigr)\ \le\ g_m(m),$$
of which the right inequality is the upper half and the left one, for $0\le s\le m$, is proved here. To first order $g_m(m+s)$ is $g_m(m)e^{-s^2/(2m)}$, and the factor $1+\frac{s^2}{2(m+s)}$ compensates this decay; what remains is of the order $s^3/m^2$.

Together the two halves confine $s_m$ to an interval of length $\frac{1}{15m}$: $\frac{1}{2P(m)}-\frac13-\frac{1}{15m}\le s_m\le\frac{1}{2P(m)}-\frac13$ for $m\ge2$. The sequence $\mathfrak p(m)-\frac23P(m)$ increases to its limit $\frac12$, and the lower half bounds how far below the limit it is.

**Where the constants come from.** The number $\frac{2}{45}=\frac{1}{36}+\frac{1}{60}$ is the value at $s=1$ of the integral of $\frac23\bigl(\frac{s^3}{6}+\frac{s^4}{8}\bigr)$. The correction $\frac{P(m)}{15m}$ is chosen so that the sequence $S(m)=\mathfrak p(m)-\frac23P(m)+\frac{P(m)}{15m}$ does not increase: its increment is at most $P(m)\bigl(\frac{2}{45m^2}+\frac{1}{15(m+1)}-\frac{1}{15m}\bigr)=-P(m)\frac{m-2}{45m^2(m+1)}$. So $\frac{1}{15}$ is the smallest constant for which this argument works from $m=2$ on, with equality in the increment bound at $m=2$, and the hypothesis $m\ge2$ is where the monotonicity starts. The inequality itself also holds at $m=1$, where $s_1=1$ and the left side is $\frac e2-\frac25=0.959\ldots$; this is a direct evaluation and is not covered by the theorem.

**What it is used for.** The convolution $\kappa_2(m)=\sum_{0<g<m}P(g)P(m-g)$ of the Poisson mass has the closed form $\kappa_2(m)=P(m)\,(s_m-1)$ (`Parking.kc2_eq`). The theorem therefore gives $\kappa_2(m)\ge\frac12-\bigl(\frac43+\frac{1}{15m}\bigr)P(m)$ for $m\ge2$, and this is the only lower bound of $\kappa_2$ that the curve increase needs. It enters in three places: the lower bound of the total weight $W_\Sigma$ of the pairs (`Parking.Wsum`); the upper bounds of the sums $G$ and $\mathcal A$ (`Parking.Gsum`, `Parking.Asum`), where $\kappa_3(m)=(m-1)P(m)-2\kappa_2(m)$ (`Parking.kc3_eq`) brings $\kappa_2$ in with a negative sign; and the numerical evaluation of the upper bound of the boundary term, whose right side (`Parking.impulse_le`) contains $\kappa_2(R)$ and $\kappa_3(R)$; the proof of `Parking.impulse_le` itself does not use it. The term $-\frac43P(m)$ is of the order $m^{-1/2}$, and summed over $m\le R$ it produces a deficit of order $\sqrt R$ against the leading value $R/2$ of $W_\Sigma$, which is large at the smallest values of $R$ that the argument treats. The lower bound of $\kappa_2$ therefore has to carry the term of order $m^{-1/2}$ with its true constant, and $\frac43$ is the true constant: by the other half of the estimate, $\kappa_2(m)\le\frac12-\frac43P(m)$.

**Relation to the literature.** The sum $s_m$ is Ramanujan's $Q$-function, and the statement about $\theta_m$ is a weak form of a classical estimate. Flajolet, Grabner, Kirschenhofer and Prodinger prove Ramanujan's form $\theta_m=\frac13+\frac{4}{135(m+k_m)}$ with $\frac{2}{21}\le k_m\le\frac{8}{45}$ for all integers $m\ge0$ [flajolet1995, Theorem 7]. This is sharper than the present bound: since $k_m>0$ it gives $\theta_m<\frac13+\frac{4}{135\,m}$, and the constant of the term $1/m$ is $\frac{4}{135}$ against $\frac{1}{15}=\frac{9}{135}$ here. The theorem is Theorem 7 on p. 113 of the printed article; in the authors' manuscript of 25 August 1993 it is Theorem 2. The library takes nothing from the literature: the proof below is complete and elementary.

**The Lean form.** The statement is `1 / (2 * poissonMass m) - 1 / 3 - 1 / (15 * m) ≤ sbirth m` with $m$ cast to a real number. $P(m)>0$ and $m\ge2$, so the divisions are ordinary ones.

## Proof

**Notation and organisation.** For a natural number $m$ and a real number $x$ put
$$\Psi_m(x)=e^{-x}\sum_{i=0}^{m}\frac{x^i}{i!},\qquad g_m(x)=e^{-x}\frac{x^m}{m!},$$
the probabilities that a Poisson variable of mean $x$ is at most $m$, and equal to $m$. Then $\mathfrak p(m)=\Psi_m(m)$ and $P(m)=g_m(m)$. Step 1 is the identity $1+s_m=\mathfrak p(m)/P(m)$. Step 2 collects the calculus of $\Psi_m$ and $g_m$. Steps 3 and 4 are two auxiliary facts: the Poisson mass does not increase, and $\mathfrak p(m)\ge\frac12$. Step 5 is the estimate of one step of the sequence $\mathfrak p(m)-\frac23P(m)$; this is where the argument could fail. Step 6 derives the monotone sequence, step 7 passes to the limit, and step 8 concludes.

**Step 1: $1+s_m=\mathfrak p(m)/P(m)$ for $m\ge1$.** For $0\le j\le m$ the product $\prod_{i<j}(1-\frac im)$ equals $\frac{m!}{(m-j)!\,m^{j}}$ (by induction on $j$). With $j=m-i$ this reads $\frac{m^i}{i!}=\prod_{l<m-i}\bigl(1-\frac lm\bigr)\cdot\frac{m^m}{m!}$ for $0\le i\le m$. Summing over $i$ and reversing the order of summation gives $\sum_{i=0}^{m}\frac{m^i}{i!}=\frac{m^m}{m!}\sum_{j=0}^{m}\prod_{l<j}\bigl(1-\frac lm\bigr)=\frac{m^m}{m!}\,(1+s_m)$, the term $j=0$ being $1$. Multiplying by $e^{-m}$ gives $\mathfrak p(m)=P(m)\,(1+s_m)$.

**Step 2: the Poisson law as a function of its mean.** The following hold for all natural numbers $m$ and real $x$.

- $\Psi_m'(x)=-g_m(x)$: the derivative of $e^{-x}\sum_{i\le m}x^i/i!$ is $e^{-x}\bigl(\sum_{1\le i\le m}\frac{x^{i-1}}{(i-1)!}-\sum_{i\le m}\frac{x^i}{i!}\bigr)$, and the two sums cancel except for the term $x^m/m!$.
- $g_{m+1}'(x)=g_m(x)-g_{m+1}(x)$, and for $x\ne0$, $g_m(x)=g_{m+1}(x)\frac{m+1}{x}$. Hence for $m\ge1$ and $x>0$: $g_m'(x)=-g_m(x)\frac{x-m}{x}$.
- $\Psi_{m+1}=\Psi_m+g_{m+1}$, and $P(m+1)=g_m(m+1)$, because $\frac{(m+1)^{m+1}}{(m+1)!}=\frac{(m+1)^m}{m!}$. Hence $\mathfrak p(m+1)=\Psi_m(m+1)+P(m+1)$.

The steps below show three times that a function of one real variable does not increase on an interval, in this form: if $F$ has the derivative $F'(x)$ at every $x\ge a$, and $F'(x)\le0$ for $a<x<b$, then $F(b)\le F(a)$.

**Step 3: $P(m+1)\le P(m)$ for every $m\ge0$.** For $m\ge1$ the quotient $P(m+1)/P(m)=g_m(m+1)/g_m(m)$ is $e^{-1}(1+\frac1m)^m$, and $(1+\frac1m)^m\le e$. For $m=0$, $P(1)=e^{-1}\le1=P(0)$.

**Step 4: $\mathfrak p(m)\ge\frac12$ for every $m\ge0$.** First, $g_m(m-u)\le g_m(m+u)$ for $0\le u<m$. The inequality $\frac{2x}{x+2}\le\log(1+x)$ for $x\ge0$, at $x=\frac{2u}{m-u}$, reads $\frac{2u}{m}\le\log\frac{m+u}{m-u}$, that is, $e^{2u/m}(m-u)\le m+u$. Its $m$-th power is $e^{2u}(m-u)^m\le(m+u)^m$, and multiplying by $e^{-(m+u)}/m!$ gives the claim. Now consider $\varphi(u)=\Psi_m(m+u)+\Psi_m(m-u)$. By step 2, $\varphi'(u)=-g_m(m+u)+g_m(m-u)\le0$ for $0<u<m$, hence $\varphi(m)\le\varphi(0)$, which is $\Psi_m(2m)+\Psi_m(0)\le2\,\Psi_m(m)$. Since $\Psi_m(0)=1$ and $\Psi_m(2m)\ge0$, this gives $1\le2\,\mathfrak p(m)$.

**Step 5: one step of the sequence.** For $m\ge1$,
$$\Bigl(\mathfrak p(m+1)-\tfrac23P(m+1)\Bigr)-\Bigl(\mathfrak p(m)-\tfrac23P(m)\Bigr)\ \le\ \frac{2}{45}\cdot\frac{P(m)}{m^{2}}.\tag{1}$$

*(a) The pointwise estimate.* For $m\ge1$ and real $0\le s\le m$,
$$g_m(m)\Bigl(1-\frac{s^3/6+s^4/8}{m^{2}}\Bigr)\ \le\ g_m(m+s)\Bigl(1+\frac{s^{2}}{2\,(m+s)}\Bigr).\tag{2}$$
Since $g_m(m+s)=g_m(m)\,e^{-s}\,(1+\frac sm)^m$ and $g_m(m)>0$, it suffices to show
$$1-\frac{s^3/6+s^4/8}{m^{2}}\ \le\ e^{-s}\Bigl(1+\frac sm\Bigr)^{m}\Bigl(1+\frac{s^{2}}{2\,(m+s)}\Bigr).$$
Put $u=\frac sm\ge0$ and $w=\frac{s^{2}}{2(m+s)}\ge0$. By `Parking.log_one_add_ge4`, $u-\frac{u^2}{2}+\frac{u^3}{3}-\frac{u^4}{4}\le\log(1+u)$, so $\bigl(1+\frac sm\bigr)^m\ge\exp\bigl(m(u-\frac{u^2}{2}+\frac{u^3}{3}-\frac{u^4}{4})\bigr)$. By `Parking.log_one_add_ge2`, $w-\frac{w^2}{2}\le\log(1+w)$, so $1+w\ge\exp\bigl(w-\frac{w^2}{2}\bigr)$. And $1-t\le e^{-t}$ bounds the left side by $\exp\bigl(-\frac{s^3/6+s^4/8}{m^2}\bigr)$. So it suffices to compare exponents:
$$-\frac{s^3/6+s^4/8}{m^{2}}\ \le\ -s+m\Bigl(u-\frac{u^2}{2}+\frac{u^3}{3}-\frac{u^4}{4}\Bigr)+\Bigl(w-\frac{w^2}{2}\Bigr).$$
The right side minus the left side equals
$$s^{4}\Bigl(\frac{m-s}{4\,m^{3}\,(m+s)}+\frac{s\,(2m+s)}{8\,m^{2}\,(m+s)^{2}}\Bigr),$$
an identity between rational functions that is checked by bringing everything to a common denominator, and this is nonnegative for $0\le s\le m$. The hypothesis $s\le m$ is used here, in the sign of $m-s$.

*(b) The auxiliary function.* For $m\ge1$ let
$$\Gamma(s)=\Psi_m(m+s)+s\Bigl(\tfrac23\,g_m(m)+\tfrac13\,g_m(m+s)\Bigr)-\frac{g_m(m)}{m^{2}}\Bigl(\frac{s^{4}}{36}+\frac{s^{5}}{60}\Bigr).$$
The first two terms are $\Psi_m(m)$ plus the excess of the two-point rule $s\bigl(\frac23g_m(m)+\frac13g_m(m+s)\bigr)$ over the integral of $g_m$ on $[m,m+s]$, and the last term is the bound that is to be proved for this excess. By step 2, for $s\ge0$,
$$\Gamma'(s)=-g_m(m+s)+\tfrac23g_m(m)+\tfrac13g_m(m+s)-\tfrac13\,g_m(m+s)\frac{s^{2}}{m+s}-\frac{g_m(m)}{m^{2}}\Bigl(\frac{s^{3}}{9}+\frac{s^{4}}{12}\Bigr),$$
which is
$$\Gamma'(s)=\frac23\Bigl[g_m(m)\Bigl(1-\frac{s^3/6+s^4/8}{m^{2}}\Bigr)-g_m(m+s)\Bigl(1+\frac{s^{2}}{2\,(m+s)}\Bigr)\Bigr].$$
By (2), $\Gamma'(s)\le0$ for $0<s<1$, since $1\le m$. Hence $\Gamma(1)\le\Gamma(0)$.

*(c) Evaluation.* $\Gamma(0)=\Psi_m(m)=\mathfrak p(m)$. At $s=1$, $g_m(m+1)=P(m+1)$ and $\frac{1}{36}+\frac{1}{60}=\frac{2}{45}$, so $\Gamma(1)=\Psi_m(m+1)+\frac23P(m)+\frac13P(m+1)-\frac{2}{45}\frac{P(m)}{m^2}$. By step 2, $\Psi_m(m+1)=\mathfrak p(m+1)-P(m+1)$. So $\Gamma(1)\le\Gamma(0)$ is
$$\mathfrak p(m+1)-\tfrac23P(m+1)+\tfrac23P(m)-\frac{2}{45}\cdot\frac{P(m)}{m^{2}}\ \le\ \mathfrak p(m),$$
which is (1).

**Step 6: the monotone sequence.** Let $S(m)=\mathfrak p(m)-\frac23P(m)+\frac{P(m)}{15m}$. For $m\ge2$, $S(m+1)\le S(m)$. Indeed by (1) and by step 3,
$$S(m+1)\le\mathfrak p(m)-\tfrac23P(m)+\frac{2}{45}\cdot\frac{P(m)}{m^{2}}+\frac{P(m)}{15\,(m+1)},$$
and
$$\frac{P(m)}{15\,m}-\frac{2}{45}\cdot\frac{P(m)}{m^{2}}-\frac{P(m)}{15\,(m+1)}=\frac{P(m)\,(m-2)}{45\,m^{2}\,(m+1)}\ \ge\ 0 .$$

**Step 7: the limit.** Let $m\ge2$. By step 6 and induction, $S(M)\le S(m)$ for every $M\ge m$. By step 4 and $\frac{P(M)}{15M}\ge0$, $S(M)\ge\frac12-\frac23P(M)$. And $P(M)\to0$ as $M\to\infty$, because $0<P(M)\le c_0/\sqrt M$ with $c_0=1/\sqrt{2\pi}$ for $M\ge1$ (`Parking.poissonMass_pos`, `Parking.poissonMass_le_c0`). So $S(m)\ge\frac12-\frac23P(M)$ for all $M\ge m$, and letting $M\to\infty$ gives $S(m)\ge\frac12$, that is,
$$\mathfrak p(m)\ \ge\ \frac12+\frac23P(m)-\frac{P(m)}{15\,m}.$$

**Step 8: conclusion.** For $m\ge2$, by step 1 and step 7, dividing by $P(m)>0$,
$$s_m=\frac{\mathfrak p(m)}{P(m)}-1\ \ge\ \frac{\frac12+\frac23P(m)-\frac{P(m)}{15m}}{P(m)}-1=\frac{1}{2\,P(m)}-\frac13-\frac{1}{15\,m}.$$

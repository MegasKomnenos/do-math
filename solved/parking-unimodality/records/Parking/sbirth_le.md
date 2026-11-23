---
weight: unit
short: upper bound for the mean of the birthday law
---
## Description

The mean $s_r=\sum_{j=1}^{r}\prod_{i<j}(1-\frac ir)$ of the birthday law with $r$ boxes (Ramanujan's function $Q(r)$) satisfies $s_r\le\sqrt{\pi r/2}\;e^{1/(12r)}-\frac13$ for every $r\ge1$.

## Statement

For natural numbers $r$ and $j$ let $P_{r,j}=\prod_{i=0}^{j-1}\bigl(1-\frac ir\bigr)$ (`Parking.Pb`) and $s_r=\sum_{j=1}^{r}P_{r,j}$ (`Parking.sbirth`). Then for every natural number $r\ge1$,
$$s_r\le\sqrt{\frac{\pi r}{2}}\;e^{1/(12r)}-\frac13.$$

## Explanation

**The quantity.** $P_{r,j}$ is the probability that the first $j$ of a sequence of balls thrown independently and uniformly into $r$ boxes fall into distinct boxes. So $s_r$, the sum of these tail probabilities, is the mean of the number of balls thrown before the first repetition; it is the function $Q(r)=1+\frac{r-1}{r}+\frac{(r-1)(r-2)}{r^2}+\dots$ of Ramanujan. In this library $s_r$ enters through $D_r$ (`Parking.Dbirth`), which is an explicit function of $r$ and $s_r$ and which satisfies $D_r\le\frac32(s_r-1)$ for $r\ge2$ (`Parking.Dbirth_le`).

**Why the bound has this form.** Let $\rho_m=e^{-m}m^m/m!$ (`Parking.poissonMass`), the probability that a Poisson variable of mean $m$ equals $m$, and let $\mathfrak p(m)=e^{-m}\sum_{i=0}^{m}m^i/i!$, the probability that it is at most $m$. Multiplying out the products shows $1+s_r=\mathfrak p(r)/\rho_r$ (step 1 of the proof). For large $r$ the probability $\mathfrak p(r)$ is close to $\frac12$ and $1/\rho_r$ is close to $\sqrt{2\pi r}$ by Stirling's formula, which gives the main term $\sqrt{\pi r/2}$. The constant $-\frac13$ is the content of the next order: the proof shows
$$\mathfrak p(m)\le\frac12+\frac23\,\rho_m\qquad(m\ge1),$$
so that $s_r\le\frac{1}{2\rho_r}+\frac23-1$. In the classical notation $\frac12e^m=\sum_{i<m}\frac{m^i}{i!}+\theta_m\frac{m^m}{m!}$ this inequality is the statement $\theta_m\ge\frac13$ about the number $\theta_m$ that this equation defines. The library does not take it from the literature; the proof below is self-contained and uses no limit theorem for the Poisson law. The factor $e^{1/(12r)}$ comes from the form of Stirling's bound that is used, Robbins' bound $r!\le\sqrt{2\pi r}\,(r/e)^r\,e^{1/(12r)}$ (`Parking.factorial_le_robbins`). The bound is close already at $r=1$, where $s_1=1$ and the right side is $1.0289$ to four decimals.

**Why the constant is kept.** The bound is used once, in the proof of `Parking.Gfun_pos`, where it gives $s_r\le1.261\sqrt r-\frac13$ for $r\ge14$ and $s_{13}\le4.216$. The margin there is small: for $r\ge14$ the criterion function is shown to be at least $0.083\sqrt r-0.1533$, and the term $-\frac13$ of the present bound contributes about $+0.50$ to the constant of that lower bound. Without it that lower bound would be negative at $r=14$.

**The Lean form.** The right side is `Real.sqrt (Real.pi * r / 2) * Real.exp (1 / (12 * r)) - 1 / 3` with $r$ cast to a real number. The hypothesis $r\ge1$ is necessary: $s_0=0$ is an empty sum, while at $r=0$ the Lean expression on the right evaluates to $-\frac13$.

## Proof

Let $\rho_m$ and $\mathfrak p(m)$ be as in the explanation; $\rho_m>0$ (`Parking.poissonMass_pos`). The proof has five steps. Step 1 is the identity $1+s_r=\mathfrak p(r)/\rho_r$. Steps 2 to 4 prove $\mathfrak p(m)\le\frac12+\frac23\rho_m$ for $m\ge1$: the sequence $\mathfrak p(m)-\frac23\rho_m$ does not decrease (step 3); its term of index $M$ is at most $\frac12+\frac13\rho_M$, because a Poisson variable of mean $M$ is below $M$ with probability at most $\frac12$ (step 2); and $\rho_M\to0$, so that every term is at most $\frac12$ (step 4). Step 5 inserts Robbins' bound. Step 3 is where the argument could fail; the other steps are short.

**Step 1: $1+s_r=\mathfrak p(r)/\rho_r$ for $r\ge1$.** For $0\le j\le r$ one has $P_{r,j}\,(r-j)!\,r^j=r!$, by induction on $j$ from $P_{r,0}=1$ (`Parking.Pb_zero`) and $P_{r,j+1}=P_{r,j}(1-\frac jr)$ (`Parking.Pb_succ`). With $j=r-i$ this reads $\frac{r^i}{i!}=P_{r,r-i}\,\frac{r^r}{r!}$ for $0\le i\le r$. Summing over $i$ and reversing the order of summation, $\sum_{i=0}^{r}\frac{r^i}{i!}=\frac{r^r}{r!}\sum_{k=0}^{r}P_{r,k}=\frac{r^r}{r!}\,(1+s_r)$. Multiplying by $e^{-r}$ gives $\mathfrak p(r)=\rho_r\,(1+s_r)$.

**Step 2: a Poisson variable of mean $M$ is below $M$ with probability at most $\frac12$.** That is, $e^{-M}\sum_{i<M}M^i/i!\le\frac12$ for every natural number $M$. Pair the term of index $M-1-j$ with the term of index $M+j$, for $0\le j<M$. We have
$$\frac{M^{M-1-j}}{(M-1-j)!}\le\frac{M^{M+j}}{(M+j)!},$$
because the quotient $(M+j)!/(M-1-j)!$ is the product of the $2j+1$ integers from $M-j$ to $M+j$, which consists of $M$ and of the $j$ pairs $(M-i)(M+i)\le M^2$, so it is at most $M^{2j+1}$. (In Lean this is the inequality $(2j+1+d)!\le(j+1+d)^{2j+1}\,d!$ between natural numbers, with $d=M-1-j$, proved by induction on $j$.) Hence $\sum_{i<M}M^i/i!\le\sum_{M\le i<2M}M^i/i!$, so $2\sum_{i<M}M^i/i!\le\sum_{i<2M}M^i/i!\le e^{M}$, the last because the partial sums of the exponential series at a nonnegative argument are below its value.

**Step 3: $\mathfrak p(m)-\frac23\rho_m\le\mathfrak p(m+1)-\frac23\rho_{m+1}$ for $m\ge1$.** For a real variable $x$ put
$$\Psi_m(x)=e^{-x}\sum_{i=0}^{m}\frac{x^i}{i!},\qquad g_m(x)=e^{-x}\frac{x^m}{m!}.$$
Then $\Psi_m'=-g_m$ (the derivative of the sum telescopes; in Lean, an induction on $m$), and $\mathfrak p(m)=\Psi_m(m)$, $\rho_m=g_m(m)$, $\rho_{m+1}=g_m(m+1)$ because $(m+1)^{m+1}/(m+1)!=(m+1)^m/m!$, and $\mathfrak p(m+1)=\Psi_m(m+1)+\rho_{m+1}$. In these terms the claim is
$$\Psi_m(m)\le\Psi_m(m+1)+\frac23\,g_m(m)+\frac13\,g_m(m+1).$$
Since $\Psi_m(m)-\Psi_m(m+1)$ is the integral of $g_m$ over $[m,m+1]$, the claim says that this integral is at most the combination $\frac23g_m(m)+\frac13g_m(m+1)$ of the values at the two ends. The function $g_m$ decreases on this interval, so the left end value alone would be an upper bound and would give the constant $1$ in place of $\frac23$; the weights $\frac23$ and $\frac13$ are what the bound of the statement needs, and that they suffice is a property of $g_m$ which the following argument establishes without integrals. Consider on $x\ge m$ the function
$$H(x)=\Psi_m(x)+(x-m)\Bigl(\frac23\,g_m(m)+\frac13\,g_m(x)\Bigr).$$
Then $H(m)=\Psi_m(m)$ and $H(m+1)$ is the right side of the claim, so it is enough that $H'\ge0$ on $x\ge m$. Using $g_m'(x)=-(x-m)\,e^{-x}x^{m-1}/m!$, a routine differentiation gives
$$H'(x)=\frac{1}{3\,m!}\Bigl[\,2\,e^{-m}m^m-e^{-x}x^{m-1}\bigl(2x+(x-m)^2\bigr)\Bigr].$$
So the claim is reduced to the inequality
$$e^{-x}x^{m-1}\bigl(2x+(x-m)^2\bigr)\le2\,e^{-m}m^m\qquad(x\ge m),\tag{K}$$
in which the two sides are equal at $x=m$. Write $x=m(1+u)$ with $u\ge0$. The left side of (K) becomes $2e^{-m}m^m\cdot e^{-mu}(1+u)^m\bigl(1+\frac{m\,u^2}{2(1+u)}\bigr)$, so (K) is equivalent to
$$(1+u)^m\Bigl(1+\frac{m\,u^2}{2(1+u)}\Bigr)\le e^{mu}\qquad(u\ge0).$$
The bound $1+u\le e^u$ is too weak for this, since it leaves no room for the second factor. Instead put $\sigma=\frac{u(2+u)}{2(1+u)}=u-\frac{u^2}{2(1+u)}\ge0$. A direct computation gives $1+\sigma+\frac{\sigma^2}{2}=1+u+\frac{u^4}{8(1+u)^2}\ge1+u$, and $1+\sigma+\frac{\sigma^2}{2}\le e^{\sigma}$ for $\sigma\ge0$; hence $1+u\le e^{\sigma}$ and $(1+u)^m\le\exp\bigl(mu-\frac{m\,u^2}{2(1+u)}\bigr)$. The second factor is at most $\exp\bigl(\frac{m\,u^2}{2(1+u)}\bigr)$ by $1+c\le e^c$. The product of the two bounds is $e^{mu}$. This proves (K), hence $H'\ge0$ on $x\ge m$, hence $H(m)\le H(m+1)$, by the monotonicity of a function with nonnegative derivative on an interval.

**Step 4: $\mathfrak p(m)\le\frac12+\frac23\rho_m$ for $m\ge1$.** Let $M\ge m$. By step 3, applied $M-m$ times, $\mathfrak p(m)-\frac23\rho_m\le\mathfrak p(M)-\frac23\rho_M$. Since $\mathfrak p(M)=e^{-M}\sum_{i<M}M^i/i!+\rho_M$, step 2 gives $\mathfrak p(M)-\frac23\rho_M\le\frac12+\frac13\rho_M$, and $\rho_M\le1/\sqrt{2\pi M}$ by `Parking.poissonMass_le`. So $\mathfrak p(m)-\frac23\rho_m\le\frac12+\frac{1}{3\sqrt{2\pi M}}$ for every $M\ge m$. The left side does not depend on $M$ and the right side tends to $\frac12$ as $M\to\infty$, so $\mathfrak p(m)-\frac23\rho_m\le\frac12$.

**Step 5: the bound.** Let $r\ge1$. By steps 1 and 4,
$$s_r=\frac{\mathfrak p(r)}{\rho_r}-1\le\frac{\frac12+\frac23\rho_r}{\rho_r}-1=\frac{1}{2\rho_r}-\frac13.$$
By `Parking.poissonMass_eq`, $\rho_r=(r/e)^r/r!$, so $\frac{1}{2\rho_r}=\frac{r!}{2\,(r/e)^r}$, and `Parking.factorial_le_robbins`, $r!\le\sqrt{2\pi r}\,(r/e)^r\,e^{1/(12r)}$, gives $\frac{1}{2\rho_r}\le\frac{\sqrt{2\pi r}}{2}\,e^{1/(12r)}=\sqrt{\frac{\pi r}{2}}\;e^{1/(12r)}$.

---
weight: unit
short: positivity of the criterion function in the strip
---
## Description

The criterion function $\mathsf G(r,k)$ is positive for all integers $k\ge265$ and $r\ge2$ with $25r^3\le121k^2$.

## Statement

For natural numbers $r$ and $k$ let
$$\mathsf G(r,k)=k\Bigl(\frac{1}{2r}-\frac{1}{3r^2}\Bigr)-\frac52+\frac12\,\mu^0_r\Bigl(\frac{r(r+1)}{k-1}\Bigr)+2\Bigl(1-\frac1k\Bigr)\mu^0_r\Bigl(\frac{r(r+2)}{2k}\Bigr)-\frac{k}{k-1}\,D_r$$
(`Parking.Gfun`), where $\mu^0_r(X)=\frac13\bigl(\sqrt{(4+X)^2+12(r-1)}-(4+X)\bigr)$ (`Parking.mu0`), $D_r=\dfrac{3\,((r+2)\,s_r-3r)}{2\,(r-s_r)}$ (`Parking.Dbirth`), and $s_r=\sum_{j=1}^{r}\prod_{i=0}^{j-1}\bigl(1-\frac ir\bigr)$ (`Parking.sbirth`).

Let $k\ge265$ and $r\ge2$ be natural numbers with $25\,r^3\le121\,k^2$. Then $\mathsf G(r,k)>0$.

## Explanation

**What the statement is for.** Let $b(n,\ell)$ (`Parking.b`) be the number of parking functions of length $n$ with maximum displacement exactly $\ell$, and call $d_{n,k}=b(n,k)-b(n,k-1)$ the step of the column $k$ in the row $n$; the library works with the normalised step $d_{n,k}/n!$ (`Parking.dq`), which has the same sign. The criterion `Parking.step_neg_of_Gfun` says: at a position $n=k+r$ with $k\ge3$ and $2\le r\le k-1$ at which $\mathsf G(r,k)\ge0$, if the step of the column $k$ in the row $n$ is nonpositive, then the step of the column $k+1$ in the row $n$ is negative. The present statement supplies the hypothesis $\mathsf G(r,k)\ge0$ on a region of positions that is large enough for the columns $k\ge265$. The condition $25r^3\le121k^2$ says $r^{3/2}\le\frac{11}{5}k$, that is, $r\le(11k/5)^{2/3}$; the positions $(k+r,k)$ with such $r$ form the strip. In the proof of `Parking.mono265`, `Parking.crossing_strip` shows that a column $k\ge265$ has a positive step in some row $j>k$ with $25(j-k-1)^3\le121k^2$, so every row $k+r$ up to which the column has only nonpositive steps satisfies $25r^3\le121k^2$; `Parking.strip_end_le` shows $100(r+1)\le27k$ for such an $r$, so that $r\le k-1$; the present statement gives $\mathsf G(r,k)>0$; and the criterion then gives the conclusion of `Parking.mono265`. So the strip is the region in which two things have to hold together: the column $k$ becomes positive no later than just beyond it, and the criterion function is positive inside it.

**How the terms compare.** Write $x=\sqrt r$ and $\varphi(r)=\frac1{2r}-\frac1{3r^2}$. The function $\mathsf G$ has three positive contributions, the term $k\varphi(r)$ and the two terms with $\mu^0_r$, and two negative ones, the constant $\frac52$ and the term with $D_r$. They behave differently in the two ranges into which the proof divides the strip.

For $2\le r\le13$ the first term alone suffices. It is about $k/(2r)$, and since $k\ge265$ it is at least $265\,\varphi(13)\approx9.67$, while $\frac52+\frac{k}{k-1}D_r$ is at most about $7.34$. In this range the condition $25r^3\le121k^2$ is not used; it holds by itself when $r\le13$ and $k\ge265$.

For $r\ge14$ the term with $D_r$ grows like a multiple of $x$: $s_r$ is about $\sqrt{\pi r/2}\approx1.25\,x$, precisely $s_r\le1.261\,x-\frac13$ by `Parking.sbirth_le`, and from this bound the proof derives $D_r\le\frac32(s_r-\frac75)$ and then $D_r\le1.8915\,x-2.6$. It is balanced by the two terms with $\mu^0_r$, which also grow like multiples of $x$, but only as long as their arguments $X$ are at most multiples of $x$, because $\mu^0_r(X)$ does not increase when $X$ grows. This is where the strip enters: $X$ is about $r^2/k=x^4/k$, and $5x^3\le11k$ makes it at most a multiple of $x$. With the bounds of the proof the coefficients of $x$ are $0.314+1.668$ for the two positive terms against $1.899$ for the negative one, and the result is $\mathsf G(r,k)\ge0.083\,x-0.1533$, which is positive for $x\ge3.74$, with the value $0.157$ at $x=3.74$. The margin is therefore small, about four percent of either side. In particular the term $-\frac13$ in the bound `Parking.sbirth_le` for $s_r$ cannot be dropped in this proof: it contributes about $+0.50$ to the constant $-0.1533$.

**The Lean form.** $r$ and $k$ are natural numbers, the condition $25r^3\le121k^2$ is an inequality between natural numbers, and $\mathsf G(r,k)$ is a real number computed from the casts of $r$ and $k$. The proof works with a real number $x>0$ such that $x^2=r$ and uses the strip condition in the form $5x^3\le11k$.

## Proof

Throughout, $\varphi(r)=\frac1{2r}-\frac1{3r^2}=\frac{3r-2}{6r^2}$, $X_-=\frac{r(r+1)}{k-1}$ and $X_{\mathrm{mid}}=\frac{r(r+2)}{2k}$, so that $\mathsf G(r,k)=k\varphi(r)-\frac52+\frac12\mu^0_r(X_-)+2(1-\frac1k)\mu^0_r(X_{\mathrm{mid}})-\frac{k}{k-1}D_r$. The proof bounds each of the four variable terms separately and adds the bounds. It first collects six preparations and then treats the range $2\le r\le13$ (frame $\alpha$) and the range $r\ge14$ (frame $\beta$). Every numerical step is either an inequality between explicit rational numbers or an inequality between polynomials with rational coefficients that is a combination, with nonnegative coefficients, of products of factors known to be nonnegative; the factors are named below and the verification is routine.

### Preparations

**(P1) The first term.** For real numbers $R>0$, $K$ and $c$: if $6cR^2\le K(3R-2)$ then $c\le K\varphi(R)$. This is $\varphi(R)=\frac{3R-2}{6R^2}$ with the denominator cleared.

**(P2) A lower bound for $\mu^0_r$.** For real numbers $X$ and $m$: if $\frac32m^2+(4+X)m\le2(r-1)$, then $m\le\mu^0_r(X)$. Indeed the hypothesis is $(3m+4+X)^2\le(4+X)^2+12(r-1)$, hence $3m+4+X\le\sqrt{(4+X)^2+12(r-1)}$, which is the claim. No sign condition on $X$ or $m$ is needed.

**(P3) Linear lower bounds for $\mu^0_r$.** Let $r\ge1$, let $x$ be real with $x^2=r$, let $0\le X\le cx$, and let $a$, $b$ be real numbers with $\frac32(ax-b)^2+(4+cx)(ax-b)\le2(x^2-1)$. Then $ax-b\le\mu^0_r(X)$. If $ax-b\le0$ this holds because $\mu^0_r(X)\ge0$ (`Parking.mu0_nonneg`, for $r\ge1$ and $X\ge0$). If $ax-b>0$ then $(4+X)(ax-b)\le(4+cx)(ax-b)$ and (P2) applies with $m=ax-b$. The difference of the two sides of the hypothesis is the quadratic polynomial
$$P_{c,a,b}(x)=\Bigl(2-\frac32a^2-ca\Bigr)x^2+(3ab-4a+cb)\,x+\Bigl(4b-2-\frac32b^2\Bigr),$$
so the hypothesis is $P_{c,a,b}(x)\ge0$.

**(P4) A linear bound for $s_r$.** Let $1\le r_0\le r$ and let $\sigma\ge\frac{31333}{25000}\cdot\frac{1}{1-1/(12r_0)}$. Then $s_r\le\sigma\sqrt r-\frac13$. This follows from `Parking.sbirth_le`, $s_r\le\sqrt{\pi r/2}\,e^{1/(12r)}-\frac13$, with two estimates: $\sqrt{\pi r/2}\le\frac{31333}{25000}\sqrt r$, because $\pi<3.1416$ (a decimal bound for $\pi$ that the Lean proof takes from Mathlib) and $\frac{3.1416}{2}=1.5708\le(1.25332)^2$; and $e^{1/(12r)}\le e^{1/(12r_0)}\le\frac{1}{1-1/(12r_0)}$, by $e^t\le\frac{1}{1-t}$ for $0\le t<1$. It is used with $(r_0,\sigma)=(13,\,1.2615)$ and with $(r_0,\sigma)=(14,\,1.261)$; the two conditions on $\sigma$ are $1.25332\cdot\frac{156}{155}\le1.2615$ and $1.25332\cdot\frac{168}{167}\le1.261$.

**(P5) A linear bound for $D_r$.** Let $r\ge2$, let $x$ be real with $x^2=r$, and suppose $s_r\le1.261\,x-\frac13$. Then $D_r\le1.8915\,x-2.6$. Write $s=s_r$ and $\bar s=1.261\,x-\frac13$. We have $1\le s$ (`Parking.one_le_sbirth`) and $s<r$ (`Parking.sbirth_lt`, for $r\ge2$), so the denominator $2(r-s)$ of $D_r$ is positive, and $x>0$ because $\bar s\ge s\ge1$. Clearing the denominator, $D_r\le\frac32(s-\frac75)$ is equivalent to $(r+2)s-3r\le(s-\frac75)(r-s)$, that is, to $s^2+\frac35s\le\frac85r$. This holds: $s^2+\frac35s\le\bar s^2+\frac35\bar s$ because $0<s\le\bar s$, and $\bar s^2+\frac35\bar s=1.261^2x^2-\frac{1.261}{15}x-\frac{4}{45}\le1.590121\,x^2\le\frac85x^2$. Finally $\frac32(s-\frac75)\le\frac32(\bar s-\frac75)=1.8915\,x-2.6$.

**(P6) Assembling the bounds.** Let $k\ge265$ and $r\ge2$, and let $t$, $m_1$, $m_2$, $d$ be real numbers with $t\le k\varphi(r)$, $m_1\le\mu^0_r(X_-)$, $m_2\le\mu^0_r(X_{\mathrm{mid}})$ and $D_r\le d$. Then
$$t-\frac52+\frac12\,m_1+\frac{528}{265}\,m_2-\frac{265}{264}\,d\le\mathsf G(r,k).$$
Indeed $2(1-\frac1k)\ge\frac{528}{265}$ and $\frac{k}{k-1}\le\frac{265}{264}$ for $k\ge265$; since $\mu^0_r(X_{\mathrm{mid}})\ge0$ (`Parking.mu0_nonneg`) and $D_r\ge0$ (`Parking.Dbirth_nonneg`, for $r\ge2$), we get $2(1-\frac1k)\mu^0_r(X_{\mathrm{mid}})\ge\frac{528}{265}\mu^0_r(X_{\mathrm{mid}})\ge\frac{528}{265}m_2$ and $\frac{k}{k-1}D_r\le\frac{265}{264}D_r\le\frac{265}{264}d$.

### Frame $\alpha$: $2\le r\le13$

*The first term.* $k\varphi(r)\ge265\,\varphi(13)=265\cdot\frac{37}{1014}$. By (P1) this is $6\cdot265\cdot\frac{37}{1014}\,r^2\le k(3r-2)$, which follows from $k\ge265$, $3r-2>0$ and $265(3r-2)-265\cdot\frac{37}{169}\,r^2=\frac{265}{169}(13-r)(37r-26)\ge0$.

*The two terms with $\mu^0_r$* are nonnegative (`Parking.mu0_nonneg`; $X_-\ge0$ and $X_{\mathrm{mid}}\ge0$) and are bounded below by $0$.

*The term with $D_r$.* $D_r\le D_{13}$ because $D$ is nondecreasing from $2$ on (`Parking.Dbirth_mono`), and $D_{13}\le\frac32(s_{13}-1)$ (`Parking.Dbirth_le`). By (P4) with $(r_0,\sigma)=(13,\,1.2615)$ and $\sqrt{13}\le3.606$, $s_{13}\le1.2615\cdot3.606-\frac13\le4.216$. So $D_r\le\frac32\cdot3.216$.

*Conclusion.* By (P6) with $m_1=m_2=0$, $\mathsf G(r,k)\ge265\cdot\frac{37}{1014}-\frac52-\frac{265}{264}\cdot\frac32\cdot3.216$, a rational number that is greater than $2.32$.

### Frame $\beta$: $r\ge14$

Let $x=\sqrt r$. Then $x\ge3.74$ because $3.74^2\le14$, and the hypothesis $25r^3\le121k^2$ reads $(5x^3)^2\le(11k)^2$, that is, $5x^3\le11k$. By (P4) with $(r_0,\sigma)=(14,\,1.261)$, $s_r\le1.261\,x-\frac13$. The values $r\le69$ and $r\ge70$ are treated separately in ($\beta$1) and ($\beta$2) only: for $r\le69$ the bound $k\ge265$ is the stronger information on $k$, and for $r\ge70$ the bound $11k\ge5x^3$ is.

**($\beta$1) $k\varphi(r)\ge1.88$.** By (P1) this is $6\cdot\frac{47}{25}\,r^2\le k(3r-2)$. If $14\le r\le69$, then $k(3r-2)\ge265(3r-2)$, and the polynomial $265(3r-2)-\frac{282}{25}r^2$ is nonnegative on $[14,69]$: it is concave and positive at both ends (the Lean proof combines $(r-14)(69-r)\ge0$ with $r\le69$). In other words $k\varphi(r)\ge265\,\varphi(69)\approx1.90$. If $r\ge70$, then $x\ge8.36$ because $8.36^2\le70$, and $11k(3x^2-2)\ge5x^3(3x^2-2)$; the required inequality $5x^3(3x^2-2)\ge11\cdot\frac{282}{25}\,x^4$ is $x^3\bigl(15x^2-\frac{3102}{25}x-10\bigr)\ge0$, and $15x^2-\frac{3102}{25}x-10\ge0$ for $x\ge8.36$. In other words $k\varphi(r)\ge\frac{5}{11}x^3\varphi(x^2)=\frac{5}{11}\bigl(\frac x2-\frac{1}{3x}\bigr)$, which is at least $1.88$ at $x=8.36$ and increases with $x$.

**($\beta$2) $X_{\mathrm{mid}}\le1.1315\,x$ and $X_-\le2.24\,x$.** After clearing denominators and writing $r=x^2$ the claims are $x^2(x^2+2)\le2.263\,x\,k$ and $x^2(x^2+1)\le2.24\,x\,(k-1)$. If $r\le69$, then $x\le8.31$ because $69\le8.31^2$, and $k\ge265$; the claims follow from $x(x^2+2)\le8.31\cdot71=590.01\le2.263\cdot265$ and $x(x^2+1)\le8.31\cdot70=581.7\le2.24\cdot264$. If $r\ge70$, then $x^2\ge70$ and $k\ge\frac{5}{11}x^3$, so $X_{\mathrm{mid}}=\frac{x^2(x^2+2)}{2k}\le\frac{11}{10}\cdot\frac{x^2+2}{x^2}\,x\le\frac{11}{10}\cdot\frac{72}{70}\,x$, and, using also $k-1\ge\frac{264}{265}k$, $X_-\le\frac{11}{5}\cdot\frac{x^2+1}{x^2}\cdot\frac{265}{264}\,x\le\frac{11}{5}\cdot\frac{71}{70}\cdot\frac{265}{264}\,x$; the two constants are below $1.1315$ and $2.24$.

**($\beta$3) $\mu^0_r(X_{\mathrm{mid}})\ge0.837\,x-0.92$ and $\mu^0_r(X_-)\ge0.628\,x-0.62$.** Both are instances of (P3), with the bounds of ($\beta$2) as $X\le cx$. For $X_{\mathrm{mid}}$, $(c,a,b)=(1.1315,\,0.837,\,0.92)$ and $P_{c,a,b}(x)=0.002081\,x^2+0.0031\,x+0.4104$, which is positive for $x>0$. For $X_-$, $(c,a,b)=(2.24,\,0.628,\,0.62)$ and $P_{c,a,b}(x)=0.001704\,x^2+0.04488\,x-0.0966$, which is positive for $x\ge3.74$ because $0.04488\cdot3.74>0.0966$.

**($\beta$4) $D_r\le1.8915\,x-2.6$.** This is (P5), with $s_r\le1.261\,x-\frac13$ from above.

**($\beta$5) Conclusion.** By (P6) with $t=1.88$, $m_1=0.628\,x-0.62$, $m_2=0.837\,x-0.92$ and $d=1.8915\,x-2.6$,
$$\mathsf G(r,k)\ge1.88-\frac52+\frac12(0.628\,x-0.62)+\frac{528}{265}(0.837\,x-0.92)-\frac{265}{264}(1.8915\,x-2.6).$$
The right side is $0.083018\ldots\,x-0.153208\ldots$, which is at least $0.083\,x-0.1533$ for $x\ge0$, and $0.083\cdot3.74-0.1533>0.157>0$.

### The statement

If $r\le13$, frame $\alpha$ applies; it uses $k\ge265$ and $2\le r$ only. If $r\ge14$, frame $\beta$ applies.

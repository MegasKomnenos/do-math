---
weight: step
short: nonnegativity of the deficit bound in the strip
---
## Description

An inequality between real numbers which, for $k\ge265$ and $25(R-1)^3\le121k^2<25R^3$, says that the closed-form lower bound $\underline t(k,R)$ of the kernel deficit is nonnegative. It is stated in the scale variable $u$ with $ku^3=\frac{5}{11}$, in which $R u^2\in(1,1+u^2]$ and $u\le\frac{3}{25}$.

## Statement

Let $u,c,\rho,s_-,s_0,s_+,a,E$ be real numbers such that

- $0<u\le\frac{3}{25}$ and $c\ge\frac{19947}{50000}$;
- $\rho>0$ and $\rho\,u^2>1$;
- $a=\frac{11}{2}u^3$;
- $s_-\,u\le1$;
- $\rho\,u^2\cdot(s_0\,u)\le(1+u^2)\bigl(1+\frac{u^2}{2}\bigr)$;
- $s_+>0$ and $s_+\,u\le1+u^2$;
- $E\le\frac{106}{105}$.

Then
$$0\le\frac{2c\,\bigl(1-\frac{1}{12\rho}\bigr)}{s_+}-a\,\bigl(E+1+c\,(2s_--1)\bigr)-\frac{633}{1000}\,a^2\,\Bigl(1+c\,\Bigl(\frac23\,\rho\,s_0+2s_--1\Bigr)\Bigr).$$

## Explanation

**What the letters stand for.** The statement is about real numbers only, but it is made for one substitution: $\rho=R$, $c=c_0=1/\sqrt{2\pi}$ (`Parking.c0`), $s_-=\sqrt{R-1}$, $s_0=\sqrt R$, $s_+=\sqrt{R+1}$, $a=\bar a=5/(2k)$ (`Parking.abar`), $E=e^{\bar a}$. With it the right side is $e\cdot\underline t(k,R)$, where $\underline t$ is the closed form `Parking.tlow`. So the conclusion is the hypothesis $\underline t\ge0$ of `Parking.cross_of_bounds`. The statement for these numbers is `Parking.strip_tlow_nonneg`: its proof checks that for $k\ge265$ and $25(R-1)^3\le121k^2<25R^3$ the substituted numbers satisfy the hypotheses listed here, and `Parking.crossing_strip` uses it.

**Why the variable $u$.** Define $u>0$ by $ku^3=\frac{5}{11}$. Then $\bar a=\frac{11}{2}u^3$, the condition on $R$ becomes $1<Ru^2\le1+u^2$, and $k\ge265$ gives $u\le\frac3{25}$. In this variable $R$ is about $u^{-2}$, its square roots are about $u^{-1}$, and each of the three terms of $\underline t$ becomes $u$ times a polynomial in $u$ up to controlled errors. The inequality is thereby reduced to the nonnegativity of one polynomial on the interval $[0,\frac3{25}]$. The hypotheses keep from the substitution only the inequalities that the proof uses; for instance nothing says that $s_-^2=\rho-1$.

**How tight it is.** To leading order the first term is $2cu$ (the tail of the kernel) and the second is $11cu^2$ (the excess of mass at the diagonal tilt), so the expression is about $cu\,(2-11u)$, and the ratio of the two terms is $\frac{11}{2}u\approx0.66$ at $u=\frac3{25}$. With all terms, the polynomial lower bound obtained in the proof equals $u$ times a quantity that decreases from $2c$ at $u=0$ to about $0.053$ at $u=\frac{3}{25}$ (for $c=\frac{19947}{50000}$). The inequality is thus easy for large columns and close at the smallest ones; it is one of the two conditions that limit how small $k$ can be in `Parking.crossing_strip`.

## Proof

The three terms are bounded separately by polynomials in $u$ and $c$, and a polynomial inequality finishes the proof. Note $c\ge0$ and $u^2\le\frac{9}{625}$.

*First term, from below.* From $\rho u^2>1$ we get $\frac{1}{12\rho}\le\frac{u^2}{12}$, so $1-\frac{1}{12\rho}\ge1-\frac{u^2}{12}\ge0$. From $s_+u\le1+u^2$ we get $u\,(1-u^2)\,s_+\le(1+u^2)(1-u^2)\le1$, so $\frac{1}{s_+}\ge u\,(1-u^2)\ge0$. Hence
$$\frac{2c\,(1-\frac{1}{12\rho})}{s_+}\ge2c\,\Bigl(1-\frac{u^2}{12}\Bigr)\,u\,(1-u^2).$$

*Second term, from above.* With $a=\frac{11}{2}u^3$, $a\,(E+1+c(2s_--1))=\frac{11}{2}u^3(E+1-c)+11c\,u^2\,(s_-u)$, and $E\le\frac{106}{105}$, $s_-u\le1$ give
$$a\,\bigl(E+1+c\,(2s_--1)\bigr)\le\frac{11}{2}u^3\Bigl(\frac{106}{105}+1-c\Bigr)+11c\,u^2 .$$

*Third term, from above.* With $a^2=\frac{121}{4}u^6$, $a^2\bigl(1+c(\frac23\rho s_0+2s_--1)\bigr)=\frac{121}{4}\bigl[(1-c)u^6+\frac23c\,u^3\cdot\rho u^2(s_0u)+2c\,u^5(s_-u)\bigr]$, and the hypotheses on $\rho u^2(s_0u)$ and $s_-u$ give
$$a^2\Bigl(1+c\Bigl(\frac23\rho s_0+2s_--1\Bigr)\Bigr)\le\frac{121}{4}\Bigl[(1-c)\,u^6+\frac23c\,u^3(1+u^2)\Bigl(1+\frac{u^2}{2}\Bigr)+2c\,u^5\Bigr].$$

*The polynomial inequality.* It remains to show that the first bound minus the second minus $\frac{633}{1000}$ times the third is nonnegative. This expression is affine in $c$ and has the factor $u$: it equals $u\,\bigl(c\,A(u)-B(u)\bigr)$ with
$$A(u)=2\Bigl(1-\frac{u^2}{12}\Bigr)(1-u^2)+\frac{11}{2}u^2-11u-\frac{633}{1000}\cdot\frac{121}{4}\Bigl(-u^5+\frac23u^2(1+u^2)\Bigl(1+\frac{u^2}{2}\Bigr)+2u^4\Bigr),$$
$$B(u)=\frac{11}{2}u^2\Bigl(\frac{106}{105}+1\Bigr)+\frac{633}{1000}\cdot\frac{121}{4}\,u^5 .$$
On $0\le u\le\frac{3}{25}$ one has $A(u)\ge0$ and $\frac{19947}{50000}A(u)-B(u)\ge0$. Both are inequalities for a polynomial in one variable on an interval, and they are verified in the simplest way: each monomial with a negative coefficient is replaced by its largest value on the interval ($u^j\le(\frac{3}{25})^j$), each monomial with a positive coefficient by $0$, and the resulting number is nonnegative. Then, since $c\ge\frac{19947}{50000}$,
$$u\,\bigl(c\,A(u)-B(u)\bigr)=u\,\Bigl(c-\frac{19947}{50000}\Bigr)A(u)+u\,\Bigl(\frac{19947}{50000}A(u)-B(u)\Bigr)\ge0 .$$
The value of $\frac{19947}{50000}A(u)-B(u)$ at $u=\frac{3}{25}$ is about $0.0529$; this is the margin of the statement at the end of the interval.

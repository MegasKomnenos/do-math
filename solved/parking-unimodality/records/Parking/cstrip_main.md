---
weight: step
short: main inequality in the strip
---
## Description

An inequality between real numbers which, for $k\ge265$ and $25(R-1)^3\le121k^2<25R^3$, is the main hypothesis of the closed-form crossing criterion with its factor $e^{-1}$ removed: $\Theta\,\Psi<L$ for the closed forms $\Theta=e\,\bar t+e^{\bar a}\frac{R+1}{k+R}$, $\Psi=\bar H+\frac5k\bar G$, $L=\frac{R(R+1)}{k+R}-1-\bar S-\bar{\mathsf E}$. It is stated in the scale variable $u$ with $ku^3=\frac5{11}$.

## Statement

Let $u,c,K,\rho,s_-,s_0,a,b,E$ be real numbers such that

- $0<u\le\frac{3}{25}$ and $\frac{19947}{50000}\le c\le\frac{7979}{20000}$;
- $K\,u^3=\frac{5}{11}$ and $K\ge1$;
- $1<\rho\,u^2\le1+u^2$;
- $a=\frac{11}{2}u^3$ and $b=\frac{11}{2}u^3-\frac{484}{75}u^6$;
- $s_->0$, $s_-\,u\le1$ and $1\le s_-\,u\,\bigl(1+\frac{51}{100}u^2\bigr)$;
- $s_0\ge0$ and $1\le s_0\,u\le1+\frac{u^2}{2}$;
- $0\le E\le\frac{106}{105}$.

Put
$$\Theta=\frac{2c}{s_-}-b\,\Bigl(2+c\,\Bigl(2s_0-2-\frac14\Bigr)\Bigr)+\frac{E\,(\rho+1)}{K+\rho},$$
$$\Psi=(\rho-1)-K\log\frac{K+\rho+1}{K+2}+\frac5K\Bigl(\frac{\rho^2-1}{2}-(K-1)(\rho-1)+K(K-1)\log\frac{K+\rho}{K+1}\Bigr),$$
$$L=\frac{\rho\,(\rho+1)}{K+\rho}-1-\Bigl(1+c\,\Bigl(2s_--1+\frac{2a}{3}\,\rho\,s_0+\frac{2}{5}\cdot\frac{633}{1000}\,a^2\rho^2s_0\Bigr)\Bigr)-\frac{5\,(\rho-2)(\rho-1)\,\rho\,(\rho+1)}{24\,K^3}.$$
Then $\Theta\,\Psi<L$.

## Explanation

**What the letters stand for.** The statement is made for the substitution $K=k$, $\rho=R$, $c=c_0=1/\sqrt{2\pi}$ (`Parking.c0`), $s_-=\sqrt{R-1}$, $s_0=\sqrt R$, $a=\bar a=5/(2k)$ (`Parking.abar`), $b=\underline a=\frac{5}{2k}-\frac{4}{3k^2}$ (`Parking.alow`), $E=e^{\bar a}$. Then $\Theta=e\,\bigl(\bar t+e^{-1}e^{\bar a}\frac{R+1}{k+R}\bigr)$, $\Psi=\bar H+\frac5k\bar G$ and $L=\frac{R(R+1)}{k+R}-1-\bar S-\bar{\mathsf E}$, with the closed forms `Parking.tup`, `Parking.Hbar`, `Parking.Gbar`, `Parking.Sbar`, `Parking.Ebar`. So $\Theta\Psi<L$ is the third hypothesis of `Parking.cross_of_bounds` after division by $e^{-1}$. The statement for these numbers is `Parking.strip_main`: its proof checks that for $k\ge265$ and $25(R-1)^3\le121k^2<25R^3$ the substituted numbers satisfy the hypotheses listed here, and `Parking.crossing_strip` uses it. In that check $u$ is defined by $ku^3=\frac5{11}$, the condition on $R$ is $1<Ru^2\le1+u^2$, and $k\ge265$ gives $u\le\frac{3}{25}$. The record of `Parking.cstrip_tlow_core` explains the choice of the variable $u$.

**The shape of the inequality.** In the variable $u$, $R\approx u^{-2}$ and $k=\frac{5}{11}u^{-3}$, so $R/k\approx\frac{11}{5}u$. To leading order
$$\Theta\approx\Bigl(2c+\frac{11}{5}\Bigr)u,\qquad\Psi\approx\frac{R^2}{2k}\approx\frac{11}{10\,u},\qquad L\approx\frac{R^2}{k}-2c\sqrt R\approx\frac{\frac{11}{5}-2c}{u}.$$
The product $\Theta\Psi$ stays bounded (about $3.3$) while $L$ grows like $1.40/u$, that is like $k^{1/3}$. For large $k$ the inequality therefore holds with room to spare. The difficulty is at the small columns: the corrections of first order in $u$ are large, and in the polynomial form reached in the proof the difference of the two sides, multiplied by $u$, is $1.4021-11.22\,u-\dots$, which at $u=\frac{3}{25}$ has fallen to about $0.047$. The bounds of the proof therefore have to keep the first-order and second-order terms in $u$ exactly, which is why the polynomials below have the coefficients they have.

**Why exact constants.** The hypotheses ask for $c$ in an interval of length $10^{-5}$ around $c_0$ and for $E\le\frac{106}{105}$; the bounds of the proof are monotone in each, and the proof replaces them by the end of the interval that is unfavourable. The number $\frac{633}{1000}$ is the constant $q$ of the closed forms.

## Proof

**Organisation.** Write $\bar c=\frac{7979}{20000}$ and define the polynomials
$$T(u)=2\bar c\Bigl(1+\frac{51}{100}u^2\Bigr)-\Bigl[\Bigl(\frac{11}{2}u^2-\frac{484}{75}u^5\Bigr)\Bigl(2-\frac94\bar c\Bigr)+2\bar c\Bigl(\frac{11}{2}u-\frac{484}{75}u^4\Bigr)\Bigr]+\frac{106}{105}\,m(u),$$
$$m(u)=\frac{11}{5}\,(1+2u^2)\Bigl(1-\frac{11}{5}u+\frac{121}{25}u^2\Bigr),\qquad P(u)=\frac{11}{10}+\frac{484}{75}u+\frac{26}{25}u^2,$$
$$\Lambda(u)=Q(u)-2u-\bar c\Bigl[2-u+\frac{11}{3}u\,(1+u^2)\Bigl(1+\frac{u^2}{2}\Bigr)+\frac{121}{10}\cdot\frac{633}{1000}\,u^2(1+u^2)^2\Bigl(1+\frac{u^2}{2}\Bigr)\Bigr]-\frac{1331}{600}u^2(1+u^2)^2,$$
$$Q(u)=\frac{11}{5}-\frac{121}{25}u+\frac{1606}{125}u^2-\frac{17666}{625}u^3 .$$
The proof has four parts: (1) $0\le\Theta\le u\,T(u)$; (2) $u\,\Psi\le P(u)$; (3) $\Lambda(u)\le u\,L$; (4) $u\,T(u)\,P(u)<\Lambda(u)$ for $0\le u\le\frac3{25}$. Since $P(u)\ge0$, they give
$$u\,\Theta\,\Psi=\Theta\cdot(u\Psi)\le\Theta\,P(u)\le u\,T(u)\,P(u)<\Lambda(u)\le u\,L,$$
and division by $u>0$ gives $\Theta\Psi<L$. Throughout, $r=\rho u^2\in(1,1+u^2]$; since $u^2<1$ this gives $\rho\ge1$. The relation $Ku^3=\frac{5}{11}$ is used to eliminate $K$: $(K+\rho)u^3=\frac5{11}+ru$, $\frac5K=11u^3$, $K^2u^6=\frac{25}{121}$, $K^3u^9=\frac{125}{1331}$.

**(1) $0\le\Theta\le uT(u)$.** The three terms of $\Theta$ are treated one by one.

- From $s_-u\le1$ and $1\le s_-u(1+\frac{51}{100}u^2)$: $\ 2cu\le\frac{2c}{s_-}\le2cu\,(1+\frac{51}{100}u^2)$.
- Note $b=u\cdot(\frac{11}{2}u^2-\frac{484}{75}u^5)$ with $\frac{11}{2}u^2-\frac{484}{75}u^5\ge0$, and $0\le b\le\frac{11}{2}u^3$. From $s_0u\ge1$: $\ b\,(2+c(2s_0-\frac94))\ge b\,(2-\frac94c)+2c\,(\frac{11}{2}u^2-\frac{484}{75}u^5)$. From $s_0u\le1+\frac{u^2}{2}$: $\ b\,(2+c(2s_0-\frac94))\le\frac{11}{2}u^3(2+2cs_0)\le11u^3+11c\,u^2(1+\frac{u^2}{2})$.
- For the last term, $\frac{\rho+1}{K+\rho}=\frac{u\,(r+u^2)}{\frac5{11}+ru}$, and
$$r+u^2\le m(u)\Bigl(\frac{5}{11}+ru\Bigr).$$
Indeed, since $r\ge1$ and $m(u)\ge0$, the right side is at least $m(u)(\frac5{11}+u)=(1+2u^2)(1-y+y^2)(1+y)=(1+2u^2)(1+y^3)$ with $y=\frac{11}{5}u$, which is at least $1+2u^2\ge r+u^2$. Hence $0\le\frac{E(\rho+1)}{K+\rho}\le\frac{106}{105}\,u\,m(u)$.

*Lower bound.* $\Theta\ge2cu-11u^3-11c\,u^2(1+\frac{u^2}{2})=u\,\bigl[c\,(2-11u-\frac{11}{2}u^3)-11u^2\bigr]$, and for $c\ge\frac{19947}{50000}$ and $0\le u\le\frac{3}{25}$ the bracket is nonnegative (the bracket is increasing in $c$ because $2-11u-\frac{11}{2}u^3\ge0$, and at $c=\frac{19947}{50000}$ it is nonnegative on the interval; both are checked monomial by monomial).

*Upper bound.* $\Theta\le2cu(1+\frac{51}{100}u^2)-\bigl[b(2-\frac94c)+2c(\frac{11}{2}u^2-\frac{484}{75}u^5)\bigr]+\frac{106}{105}u\,m(u)$. The right side is affine in $c$, with slope $u\,\bigl[2(1+\frac{51}{100}u^2)+\frac94(\frac{11}{2}u^2-\frac{484}{75}u^5)-2(\frac{11}{2}u-\frac{484}{75}u^4)\bigr]\ge0$ on the interval. So it is largest at $c=\bar c$, where it equals $u\,T(u)$.

**(2) $u\Psi\le P(u)$.** Put $X=\frac{11}{5}u\le1$. *The first part of $\Psi$.* Let $x'=\frac{\rho-1}{K+2}\ge0$, so that $\frac{K+\rho+1}{K+2}=1+x'$ and $(\rho-1)-Kx'=2x'$. Also $x'\le X$, because $(\rho-1)u^2\le1\le\frac{11}{5}u\,(K+2)\,u^2$. The lower Taylor bound of degree $4$ (`Parking.log_one_add_ge4`) gives
$$(\rho-1)-K\log(1+x')\le2x'+K\Bigl(\frac{x'^2}{2}-\frac{x'^3}{3}+\frac{x'^4}{4}\Bigr)\le2X+K\Bigl(\frac{X^2}{2}-\frac{X^3}{3}+\frac{X^4}{4}\Bigr),$$
the second step because $t\mapsto\frac{t^2}2-\frac{t^3}3+\frac{t^4}4$ is nondecreasing on $[0,1]$. Multiplying by $u$ and eliminating $K$,
$$u\,\Bigl[(\rho-1)-K\log\frac{K+\rho+1}{K+2}\Bigr]\le\frac{11}{10}-\frac{121}{75}u+\frac{3531}{500}u^2 .$$
*The second part.* Let $z=\frac{\rho-1}{K+1}\ge0$, so that $\frac{K+\rho}{K+1}=1+z$; again $z\le X$. Substituting $\rho-1=z(K+1)$ and using the upper Taylor bound of degree $5$ (`Parking.log_one_add_le5`, with $K(K-1)\ge0$),
$$\frac{\rho^2-1}{2}-(K-1)(\rho-1)+K(K-1)\log(1+z)\le2z+\frac{3K+1}{2}z^2+K(K-1)\Bigl(\frac{z^3}{3}-\frac{z^4}{4}+\frac{z^5}{5}\Bigr);$$
the terms of first order in $z$ cancel up to $2z$ and those of second order combine to $\frac{3K+1}{2}z^2$. The right side is nondecreasing in $z$ on $[0,1]$ (the last polynomial is), so $z$ can be replaced by $X$. Multiplying by $u\cdot\frac5K=11u^4$ and eliminating $K$ gives, with $\nu(u)=\frac{1331}{375}-\frac{14641}{2500}u+\frac{161051}{15625}u^2\ge0$,
$$u\cdot\frac5K\Bigl[\dots\Bigr]\le\frac{25}{11}u\,\nu(u)+\frac{363}{10}u^3+\frac{242}{5}u^5+\frac{1331}{50}u^6,$$
where a term $-5u^4\nu(u)\le0$ has been dropped. *Sum.* The sum of the two bounds is at most $P(u)$ on $[0,\frac{3}{25}]$: the constant terms and the terms of first order agree ($\frac{11}{10}$ and $-\frac{121}{75}+\frac{25}{11}\cdot\frac{1331}{375}=\frac{484}{75}$), and the coefficient $\frac{26}{25}$ of $u^2$ in $P$ is chosen so that the remaining terms are absorbed: $P(u)$ minus the sum of the two bounds equals
$$u^2\Bigl(\frac{911}{125}-\frac{74657}{1250}u-\frac{242}{5}u^3-\frac{1331}{50}u^4\Bigr),$$
and the bracket is nonnegative for $0\le u\le\frac3{25}$ (it is decreasing, and at $u=\frac{3}{25}$ it is about $0.03$).

**(3) $\Lambda(u)\le uL$.** The four terms of $L$ are treated one by one.

- *Main term.* $u\,\frac{\rho(\rho+1)}{K+\rho}=\frac{r\,(r+u^2)}{\frac5{11}+ru}$, and $Q(u)\bigl(\frac{5}{11}+ru\bigr)\le r\,(r+u^2)$ for $r\ge1$ and $0\le u\le\frac{3}{25}$. (At $r=1$ the right side minus the left side is exactly $\frac{17666}{625}u^4\ge0$, because $Q$ is the Taylor polynomial of degree $3$ of $\frac{11}{5}(1+u^2)/(1+\frac{11}{5}u)$. For $r>1$ the difference equals its value at $r=1$ plus $(r-1)^2+(r-1)\,(2+u^2-uQ(u))$, and $2+u^2-uQ(u)\ge0$ on the interval.) Hence $u\,\frac{\rho(\rho+1)}{K+\rho}\ge Q(u)$.
- *The term $-1$* contributes $-u$.
- *The sum $\bar S$.* With $a=\frac{11}{2}u^3$,
$$u\,\Bigl(1+c\,\Bigl(2s_--1+\frac{2a}{3}\rho s_0+\frac{2}{5}q\,a^2\rho^2s_0\Bigr)\Bigr)=u+c\,\Bigl(2(s_-u)-u+\frac{11}{3}u\,r\,(s_0u)+\frac{121}{10}q\,u^2r^2(s_0u)\Bigr),\qquad q=\frac{633}{1000},$$
and $s_-u\le1$, $r\le1+u^2$, $s_0u\le1+\frac{u^2}{2}$, $c\le\bar c$ bound this by $u+\bar c\,[\dots]$ with the bracket of $\Lambda$ (the bracket is nonnegative, so $c$ may be replaced by $\bar c$).
- *The term $\bar{\mathsf E}$.* $u\cdot\frac{5(\rho-2)(\rho-1)\rho(\rho+1)}{24K^3}=\frac{1331}{600}\,u^2\,(r-2u^2)(r-u^2)\,r\,(r+u^2)$ after elimination of $K$, and $(r-2u^2)(r-u^2)\,r\,(r+u^2)\le(1+u^2)^2$: indeed $0\le r(r-u^2)\le1+u^2$, and $(r-2u^2)(r+u^2)\le r(r-u^2)$.

Adding the four bounds gives $uL\ge Q(u)-u-u-\bar c\,[\dots]-\frac{1331}{600}u^2(1+u^2)^2=\Lambda(u)$.

**(4) $uT(u)P(u)<\Lambda(u)$ on $[0,\frac3{25}]$.** This is an inequality for one polynomial of degree $8$:
$$\Lambda(u)-u\,T(u)\,P(u)=1.4021-11.2246\,u-1.7057\,u^2+15.76\,u^3-53.2\,u^4+23.1\,u^5-178.0\,u^6-73.6\,u^7-8.9\,u^8$$
(coefficients rounded; the exact coefficients are rational numbers). The constant term is $\frac{11}{5}-2\bar c$. The inequality is verified monomial by monomial: the monomials with positive coefficients are dropped, and those with negative coefficients are replaced by their values at $u=\frac{3}{25}$. What remains is about $0.0190>0$. The actual value of the difference at $u=\frac3{25}$ is about $0.0468$.

**Where the argument is sensitive.** Parts (1) to (3) lose nothing at leading order and little at first order in $u$: the constants $\frac{11}{5}$, $\frac{121}{25}$, $\frac{484}{75}$ and $2\bar c$ are the exact coefficients of the expansions. Part (4) is the only strict inequality, and its margin at the end of the interval is about one tenth of either side ($uTP\approx0.461$, $\Lambda\approx0.508$ at $u=\frac{3}{25}$). In terms of the expansion in (4), the margin $0.047$ at $u=\frac{3}{25}$ corresponds to a change of only about $0.4$ in the coefficient $11.22$ of $u$, so a cruder treatment of a first-order term in any of the parts (1) to (3) would lose the inequality at the small columns. For this reason the bound for $\Psi$ keeps the logarithms up to the Taylor degrees $4$ and $5$ and uses the monotonicity of the resulting polynomials in $x'$ and $z$, instead of bounding the negative terms separately.

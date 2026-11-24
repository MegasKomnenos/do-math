---
weight: step
short: the deficit bound is nonnegative at the end of the strip
---
## Description

For a column $k\ge265$ and the least positive integer $R$ with $121k^2<25R^3$, the closed-form lower bound $\underline t(k,R)$ of the kernel deficit is nonnegative. This is one of the two inequalities that the crossing theorem `Parking.crossing_strip` needs at this $R$.

## Statement

Let $k\ge265$ be a natural number, and let $R$ be the least positive integer with $121\,k^2<25\,R^3$. Then
$$\underline t(k,R)\ge0,$$
where
$$\underline t(k,R)=\frac{2e^{-1}c_0\bigl(1-\frac{1}{12R}\bigr)}{\sqrt{R+1}}-e^{-1}\,\bar a\,\Bigl[e^{\bar a}+1+c_0\bigl(2\sqrt{R-1}-1\bigr)\Bigr]-e^{-1}\,\frac{633}{1000}\,\bar a^{2}\,\Bigl[1+c_0\Bigl(\frac23R\sqrt R+2\sqrt{R-1}-1\Bigr)\Bigr]$$
is the closed form `Parking.tlow`, with $c_0=1/\sqrt{2\pi}$ (`Parking.c0`) and $\bar a=5/(2k)$ (`Parking.abar`).

The condition on $R$ is stated as the pair of inequalities
$$25\,(R-1)^3\le121\,k^2<25\,R^3 .$$
The pair says exactly that $R$ is the least positive integer with $121k^2<25R^3$. The right inequality is the property itself, and it excludes $R=0$. The left inequality says that $R-1$ does not have the property, and then no smaller number has it, because $25m^3$ does not decrease in $m$. For every $k$ there is exactly one such $R$, namely $R=\lfloor(11k/5)^{2/3}\rfloor+1$.

## Explanation

**What it is for.** The closed-form crossing criterion `Parking.cross_of_bounds` has, besides the conditions $2\le R\le k-1$ and $\bar aR\le\frac{6679}{10000}$, two hypotheses on the closed forms: $\underline t\ge0$ and a strict inequality between products. `Parking.crossing_strip` applies the criterion to a column $k\ge265$ with the $R$ of this statement. The present statement is the first of the two hypotheses for that $R$, and `Parking.strip_main` is the second. In the criterion, $\underline t\ge0$ takes the place of the nonnegativity of the kernel deficit $\bar\kappa_R$ of the column (`Parking.kbar`), which $\underline t$ bounds from below (part (v) of the proof of `Parking.cross_of_bounds`).

**Why it is delicate.** The first term of $\underline t$ bounds the tail of the kernel from below and is of order $R^{-1/2}$. The two terms that are subtracted bound the excess of mass at the diagonal tilt from above; the larger of them is of order $\sqrt R/k$. The inequality therefore asks for $R$ not too large, while `Parking.strip_main` asks for $R$ large, and the $R$ of the statement, of order $k^{2/3}$, lies between. For large $k$ there is room: with the scale $u$ defined by $ku^3=\frac{5}{11}$ the expression $e\,\underline t$ is about $c_0u\,(2-11u)$. At the smallest column the terms nearly cancel: for $k=265$, $R=70$ the three terms of $\underline t$ are about $0.03479$, $0.02859$ and $0.00338$ (floating-point evaluation of the definition, not part of the proof).

**How the proof is divided.** The proof has two parts. The first translates the conditions on $k$ and $R$ into inequalities in the variable $u$; in Lean this is the private lemma `strip_relations` of the module `Parking.Crossing.Strip`, and the proofs of `Parking.strip_main` and `Parking.crossing_strip` start from the same lemma. The second part is the inequality between real numbers `Parking.cstrip_tlow_core`, which is stated for arbitrary real numbers that satisfy these inequalities and is applied here to $R$, its square roots, $\bar a$, $e^{\bar a}$ and $c_0$.

**The Lean form.** The statement is `0 ≤ tlow k R` under the hypotheses `265 ≤ k`, `25 * (R - 1) ^ 3 ≤ 121 * k ^ 2` and `121 * k ^ 2 < 25 * R ^ 3`, for natural numbers `k` and `R`. The subtraction $R-1$ is that of natural numbers; it is the ordinary one because the last hypothesis gives $R\ge1$.

## Proof

**Step 1: the relations in the scale variable** (the private lemma `strip_relations`). Let $k\ge265$ and $25(R-1)^3\le121k^2<25R^3$. Since $R=0$ would make the right inequality $121k^2<0$, we have $R\ge1$, and the three inequalities hold between real numbers with the ordinary $R-1$. We show that there is a real number $u>0$ with
$$k\,u^3=\frac{5}{11},\qquad u\le0.119705,\qquad R\ge2,\qquad1<R\,u^2\le1+u^2,$$
$$\bar a=\frac{11}{2}u^3,\qquad\underline a=\frac{11}{2}u^3-\frac{484}{75}u^6,\qquad e^{\bar a}\le\frac{106}{105},$$
$$\sqrt{R-1}\,u\le1\le\sqrt{R-1}\,u\,\Bigl(1+\frac{51}{100}u^2\Bigr),\qquad1\le\sqrt R\,u\le1+\frac{u^2}{2},\qquad\sqrt{R+1}\,u\le1+u^2,$$
where $\underline a=\frac{5}{2k}-\frac{4}{3k^2}$ (`Parking.alow`).

*(a) The scale.* Put $u=\exp\bigl(\frac13\log\frac{5}{11k}\bigr)>0$. Then $u^3=\frac{5}{11k}$, so $k\,u^3=\frac{5}{11}$, and squaring gives $121\,k^2u^6=25$.

*(b) $1<Ru^2\le1+u^2$.* If $Ru^2\le1$, then $R^3u^6\le1$; but $121k^2<25R^3$ multiplied by $u^6>0$ gives $25<25\,R^3u^6$. If $Ru^2>1+u^2$, then $(R-1)u^2>1$ and $(R-1)^3u^6>1$; but $25(R-1)^3\le121k^2$ multiplied by $u^6$ gives $25\,(R-1)^3u^6\le25$.

*(c) $u\le0.119705$.* If $u>0.119705$, then $265\,u^3>265\cdot0.119705^3>\frac{5}{11}$ (the two numbers are $0.454551\ldots$ and $0.454545\ldots$), while $265\,u^3\le k\,u^3=\frac{5}{11}$. In particular $u\le\frac{3}{25}$ and $u^2\le\frac{9}{625}$.

*(d) $R\ge2$.* If $R\le1$, then $Ru^2\le u^2\le\frac{9}{625}<1$, against (b).

*(e) The tilt exponents.* From $ku^3=\frac{5}{11}$ we get $\frac{5}{2k}=\frac{11}{2}u^3$, and from $121k^2u^6=25$ we get $\frac{4}{3k^2}=\frac{484}{75}u^6$. Hence $\bar a=\frac{11}{2}u^3$ and $\underline a=\frac{11}{2}u^3-\frac{484}{75}u^6$.

*(f) $e^{\bar a}\le\frac{106}{105}$.* Since $k\ge265$, $0\le\bar a\le\frac{5}{530}=\frac{1}{106}$. For $0\le s<1$ one has $e^s\le\frac{1}{1-s}$, and $\frac{1}{1-s}\le\frac{106}{105}$ for $s\le\frac1{106}$.

*(g) The square roots.* For real $x\ge0$, $u\ge0$ and $\beta\ge0$ the number $\sqrt x\,u$ is nonnegative with square $x\,u^2$, so $x\,u^2\le\beta^2$ gives $\sqrt x\,u\le\beta$, and $\beta^2\le x\,u^2$ gives $\beta\le\sqrt x\,u$. By (b), $1-u^2<(R-1)u^2\le1$, $1<Ru^2\le1+u^2$ and $(R+1)u^2\le1+2u^2$. Therefore:

- $\sqrt{R-1}\,u\le1$, because $(R-1)u^2\le1$;
- $1-\frac{101}{200}u^2\le\sqrt{R-1}\,u$, because $\bigl(1-\frac{101}{200}u^2\bigr)^2=1-\frac{101}{100}u^2+\frac{10201}{40000}u^4\le1-u^2$, which holds since $u^2\le\frac{9}{625}$;
- $1\le\sqrt{R-1}\,u\,\bigl(1+\frac{51}{100}u^2\bigr)$, because the product is at least $\bigl(1-\frac{101}{200}u^2\bigr)\bigl(1+\frac{51}{100}u^2\bigr)=1+\frac{u^2}{200}-\frac{5151}{20000}u^4$, and this is at least $1$ since $u^2\le\frac{9}{625}$;
- $1\le\sqrt R\,u$, because $1\le Ru^2$;
- $\sqrt R\,u\le1+\frac{u^2}{2}$, because $Ru^2\le1+u^2\le\bigl(1+\frac{u^2}{2}\bigr)^2$;
- $\sqrt{R+1}\,u\le1+u^2$, because $(R+1)u^2\le1+2u^2\le(1+u^2)^2$.

**Step 2: the real-variable inequality.** We apply `Parking.cstrip_tlow_core` to the real numbers
$$u,\qquad c=c_0,\qquad\rho=R,\qquad s_-=\sqrt{R-1},\qquad s_0=\sqrt R,\qquad s_+=\sqrt{R+1},\qquad a=\bar a,\qquad E=e^{\bar a}.$$
Its hypotheses hold:

- $0<u\le\frac{3}{25}$ by (a) and (c), and $c_0\ge\frac{19947}{50000}$ by `Parking.c0_bounds`;
- $\rho>0$ and $\rho\,u^2>1$ by (d) and (b);
- $a=\frac{11}{2}u^3$ by (e);
- $s_-\,u\le1$ by (g);
- $\rho\,u^2\cdot(s_0\,u)\le(1+u^2)\bigl(1+\frac{u^2}{2}\bigr)$, the product of the two upper bounds $Ru^2\le1+u^2$ and $\sqrt R\,u\le1+\frac{u^2}{2}$ of nonnegative numbers;
- $s_+>0$, because $R+1>0$, and $s_+\,u\le1+u^2$ by (g);
- $E\le\frac{106}{105}$ by (f).

Its conclusion is
$$0\le\frac{2c_0\bigl(1-\frac{1}{12R}\bigr)}{\sqrt{R+1}}-\bar a\,\bigl(e^{\bar a}+1+c_0\,(2\sqrt{R-1}-1)\bigr)-\frac{633}{1000}\,\bar a^{2}\Bigl(1+c_0\Bigl(\frac23R\sqrt R+2\sqrt{R-1}-1\Bigr)\Bigr).$$

**Step 3: conclusion.** Each of the three terms of $\underline t(k,R)$ carries the factor $e^{-1}$, so $\underline t(k,R)$ is $e^{-1}$ times the right side of the last display. Since $e^{-1}>0$, we get $\underline t(k,R)\ge0$.

**Where the argument is sensitive.** Step 1 contains no idea beyond the change of variable; its bound (c) is the value of $u$ at $k=265$ rounded up in the sixth decimal. The margin is in `Parking.cstrip_tlow_core`: the polynomial lower bound obtained there is $u$ times a quantity that falls to about $0.053$ at $u=\frac{3}{25}$ (see its record).

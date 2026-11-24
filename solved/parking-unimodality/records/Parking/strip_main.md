---
weight: step
short: the main inequality at the end of the strip
---
## Description

For a column $k\ge265$ and the least positive integer $R$ with $121k^2<25R^3$, the closed forms satisfy $\mathsf A\,\mathsf B<\mathsf C$, where $\mathsf A=e\,\bar t+e^{\bar a}\frac{R+1}{k+R}$, $\mathsf B=\bar H+\frac5k\bar G$ and $\mathsf C=\frac{R(R+1)}{k+R}-1-\bar S-\bar{\mathsf E}$. Multiplied by $e^{-1}$, this is the main hypothesis of the closed-form crossing criterion at this $R$.

## Statement

Let $k\ge265$ be a natural number, let $R$ be the least positive integer with $121\,k^2<25\,R^3$, and put $N=k+R$. Put
$$\mathsf A=e\,\bar t+e^{\bar a}\,\frac{R+1}{N},\qquad\mathsf B=\bar H+\frac5k\,\bar G,\qquad\mathsf C=\frac{R\,(R+1)}{N}-1-\bar S-\bar{\mathsf E}.$$
Then
$$\mathsf A\,\mathsf B<\mathsf C .$$
Here $e=\exp(1)$, $\bar a=5/(2k)$ (`Parking.abar`), and $\bar t$, $\bar H$, $\bar G$, $\bar S$, $\bar{\mathsf E}$ are the closed forms `Parking.tup`, `Parking.Hbar`, `Parking.Gbar`, `Parking.Sbar`, `Parking.Ebar` at $(k,R)$:
$$\bar t=\frac{2e^{-1}c_0}{\sqrt{R-1}}-e^{-1}\,\underline a\,\Bigl[2+c_0\Bigl(2\sqrt R-2-\frac14\Bigr)\Bigr],\qquad\bar H=(R-1)-k\log\frac{k+R+1}{k+2},$$
$$\bar G=\frac{R^2-1}{2}-(k-1)(R-1)+k\,(k-1)\log\frac{k+R}{k+1},\qquad\bar{\mathsf E}=\frac{5\,(R-2)(R-1)\,R\,(R+1)}{24\,k^3},$$
$$\bar S=1+c_0\Bigl[2\sqrt{R-1}-1+\frac{2\bar a}{3}\,R\sqrt R+\frac25\cdot\frac{633}{1000}\,\bar a^{2}R^{2}\sqrt R\Bigr],$$
with $c_0=1/\sqrt{2\pi}$ (`Parking.c0`) and $\underline a=\frac{5}{2k}-\frac{4}{3k^2}$ (`Parking.alow`).

The condition on $R$ is stated as the pair of inequalities $25\,(R-1)^3\le121\,k^2<25\,R^3$, which says exactly that $R$ is the least positive integer with $121k^2<25R^3$; the record of `Parking.strip_tlow_nonneg` gives the reason.

## Explanation

**What it is for.** The closed-form crossing criterion `Parking.cross_of_bounds` has as its last hypothesis the inequality
$$\Bigl(\bar t+e^{-1}e^{\bar a}\,\frac{R+1}{N}\Bigr)\Bigl(\bar H+\frac5k\,\bar G\Bigr)<e^{-1}\Bigl(\frac{R(R+1)}{N}-1-\bar S-\bar{\mathsf E}\Bigr).$$
Its left side is $e^{-1}\mathsf A\,\mathsf B$ and its right side is $e^{-1}\mathsf C$, so it is the present inequality multiplied by the positive number $e^{-1}$. `Parking.crossing_strip` applies the criterion to a column $k\ge265$ with the $R$ of this statement and obtains this hypothesis from the present statement in that way. The companion statement `Parking.strip_tlow_nonneg` gives the hypothesis $\underline t\ge0$ for the same $R$.

**Why the factor $e$ is put on $\bar t$.** The two terms of $\bar t$ carry the factor $e^{-1}$, and the diagonal tilt of the column is $e^{-1}$ times a number between $1$ and $e^{\bar a}$. Without the common factor $e^{-1}$ the three quantities are expressions in $k$, $R$, $c_0$, square roots, $e^{\bar a}$ and two logarithms only: $\mathsf A=\frac{2c_0}{\sqrt{R-1}}-\underline a\,\bigl[2+c_0\bigl(2\sqrt R-\frac94\bigr)\bigr]+e^{\bar a}\frac{R+1}{N}$.

**The shape of the inequality.** With the scale $u$ defined by $ku^3=\frac{5}{11}$ one has $R\approx u^{-2}$ and $R/k\approx\frac{11}{5}u$, and to leading order
$$\mathsf A\approx\Bigl(2c_0+\frac{11}{5}\Bigr)u,\qquad\mathsf B\approx\frac{11}{10\,u},\qquad\mathsf C\approx\frac{1}{u}\Bigl(\frac{11}{5}-2c_0\Bigr).$$
The product $\mathsf A\,\mathsf B$ stays near $3.3$ while $\mathsf C$ grows like $1.40/u$, that is like $k^{1/3}$. The inequality needs $R$ large, because the term $R(R+1)/N$ of $\mathsf C$, of order $R^2/k$, has to exceed $\bar S$, of order $\sqrt R$; the companion inequality $\underline t\ge0$ needs $R$ small. At the smallest column, $k=265$ with $R=70$, a floating-point evaluation of the definitions (not part of the proof) gives $\mathsf A\approx0.2368$, $\mathsf B\approx15.04$, $\mathsf A\,\mathsf B\approx3.56$ and $\mathsf C\approx4.51$.

**How the proof is divided.** As for `Parking.strip_tlow_nonneg`, the conditions on $k$ and $R$ are first translated into inequalities in the variable $u$ (in Lean the private lemma `strip_relations` of the module `Parking.Crossing.Strip`), and then the inequality between real numbers `Parking.cstrip_main`, which is stated for arbitrary real numbers that satisfy these inequalities, is applied to $k$, $R$, the square roots of $R-1$ and $R$, $\bar a$, $\underline a$, $e^{\bar a}$ and $c_0$.

**The Lean form.** The statement is

`(Real.exp 1 * tup k R + Real.exp (abar k) * (R + 1) / (k + R)) * (Hbar k R + 5 / k * Gbar k R) < R * (R + 1) / (k + R) - 1 - Sbar k R - Ebar k R`

for natural numbers `k` and `R`, read as real numbers, under the hypotheses `265 ≤ k`, `25 * (R - 1) ^ 3 ≤ 121 * k ^ 2` and `121 * k ^ 2 < 25 * R ^ 3`. The subtraction $R-1$ in the hypothesis is that of natural numbers; it is the ordinary one because the last hypothesis gives $R\ge1$.

## Proof

**Step 1: the relations in the scale variable.** By Step 1 of the proof of `Parking.strip_tlow_nonneg` (the lemma `strip_relations`), there is a real number $u>0$ with
$$k\,u^3=\frac{5}{11},\qquad u\le0.119705,\qquad R\ge2,\qquad1<R\,u^2\le1+u^2,$$
$$\bar a=\frac{11}{2}u^3,\qquad\underline a=\frac{11}{2}u^3-\frac{484}{75}u^6,\qquad e^{\bar a}\le\frac{106}{105},$$
$$\sqrt{R-1}\,u\le1\le\sqrt{R-1}\,u\,\Bigl(1+\frac{51}{100}u^2\Bigr),\qquad1\le\sqrt R\,u\le1+\frac{u^2}{2}.$$

**Step 2: the real-variable inequality.** We apply `Parking.cstrip_main` to the real numbers
$$u,\qquad c=c_0,\qquad K=k,\qquad\rho=R,\qquad s_-=\sqrt{R-1},\qquad s_0=\sqrt R,\qquad a=\bar a,\qquad b=\underline a,\qquad E=e^{\bar a}.$$
Its hypotheses hold:

- $0<u\le\frac{3}{25}$ by Step 1, since $0.119705\le\frac{3}{25}$, and $\frac{19947}{50000}\le c_0\le\frac{7979}{20000}$ by `Parking.c0_bounds`;
- $K\,u^3=\frac{5}{11}$ by Step 1, and $K\ge1$ because $k\ge265$;
- $1<\rho\,u^2\le1+u^2$ by Step 1;
- $a=\frac{11}{2}u^3$ and $b=\frac{11}{2}u^3-\frac{484}{75}u^6$ by Step 1;
- $s_->0$, because $R\ge2$ gives $R-1>0$; $s_-\,u\le1$ and $1\le s_-\,u\,\bigl(1+\frac{51}{100}u^2\bigr)$ by Step 1;
- $s_0\ge0$, and $1\le s_0\,u\le1+\frac{u^2}{2}$ by Step 1;
- $0\le E$, and $E\le\frac{106}{105}$ by Step 1.

Its conclusion is $\Theta\,\Psi<L$ with
$$\Theta=\frac{2c_0}{\sqrt{R-1}}-\underline a\,\Bigl(2+c_0\Bigl(2\sqrt R-2-\frac14\Bigr)\Bigr)+\frac{e^{\bar a}\,(R+1)}{k+R},$$
$$\Psi=(R-1)-k\log\frac{k+R+1}{k+2}+\frac5k\Bigl(\frac{R^2-1}{2}-(k-1)(R-1)+k(k-1)\log\frac{k+R}{k+1}\Bigr),$$
$$L=\frac{R\,(R+1)}{k+R}-1-\Bigl(1+c_0\Bigl(2\sqrt{R-1}-1+\frac{2\bar a}{3}\,R\sqrt R+\frac25\cdot\frac{633}{1000}\,\bar a^2R^2\sqrt R\Bigr)\Bigr)-\frac{5\,(R-2)(R-1)\,R\,(R+1)}{24\,k^3}.$$

**Step 3: conclusion.** By the definitions of $\bar H$, $\bar G$, $\bar S$ and $\bar{\mathsf E}$, the numbers $\Psi$ and $L$ are $\mathsf B$ and $\mathsf C$ written out. By the definition of $\bar t$ and by $e\cdot e^{-1}=1$,
$$e\,\bar t=\frac{2c_0}{\sqrt{R-1}}-\underline a\,\Bigl(2+c_0\Bigl(2\sqrt R-2-\frac14\Bigr)\Bigr),$$
so that $\Theta=\mathsf A$. Hence $\mathsf A\,\mathsf B<\mathsf C$.

**Where the argument is sensitive.** All the difficulty is in `Parking.cstrip_main`, at the columns just above $265$, where $u$ is close to $\frac{3}{25}$: the polynomial inequality to which that statement is reduced has a margin of about $0.047$ at $u=\frac{3}{25}$ (see its record). For large $k$ every estimate has room.

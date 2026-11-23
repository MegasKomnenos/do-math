---
weight: unit
short: crossing inside the strip
---
## Description

Every column $k\ge265$ is positive in some row $j>k$ with $25\,(j-k-1)^3\le121\,k^2$: there is a row $j$ with $k<j\le k+\lfloor(11k/5)^{2/3}\rfloor+1$ and $b(j,k)>b(j,k-1)$.

## Statement

Let $k\ge265$ be a natural number. Then there is a natural number $j$ with
$$k<j,\qquad25\,(j-k-1)^3\le121\,k^2,\qquad d_{j,k}>0,$$
where $d_{j,k}=b(j,k)-b(j,k-1)$ and $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`).

Since $25s^3\le121k^2$ is equivalent to $s\le(11k/5)^{2/3}$, the second condition says $j\le k+\varrho(k)+1$ with $\varrho(k)=\lfloor(11k/5)^{2/3}\rfloor$.

## Explanation

**What the statement gives.** The step of the column $k$ is negative in the diagonal row $j=k$. The theorem bounds the first row in which it is positive: at most $\varrho(k)+1$ rows below the diagonal. Call the positions of the column $k$ in the rows $k+r$ with $25r^3\le121k^2$, that is $r\le\varrho(k)$, the *strip* of the column. Then every row $n>k$ such that the column is not positive in any of the rows $k+1,\dots,n$ lies in the strip: the row $j$ of the theorem is larger than $n$, so $n-k\le j-k-1$.

**What it is used for.** There are two uses.

- In `Parking.mono265`: if $n\ge k+2$ and the column $k\ge265$ is not positive in the rows $k+1,\dots,n$, then $(n,k)$ lies in the strip, where the criterion function of the next-column argument is positive (`Parking.Gfun_pos`, stated for the positions $r\ge2$ of exactly this strip), and therefore the column $k+1$ is negative in the row $n$. The strip is the common ground of the two arguments: this theorem shows that the rows before the crossing are inside it, and the next-column argument works inside it.
- In `Parking.crossing_row`: together with `Parking.strip_end_le` it gives, for $k\ge265$, a positive row $k+r$ with $100r\le27k$; for $82\le k\le264$ such a row is read from the table `Parking.Tab.two_signs`.

**How it is proved, and why with these constants.** The theorem is the closed-form crossing criterion `Parking.cross_of_bounds` applied with $R=\varrho(k)+1$, the least natural number with $121k^2<25R^3$. What has to be checked is that this $R$ satisfies the three hypotheses of that criterion for every $k\ge265$, and this is done once for all $k$ by passing to the scale variable $u$ with $ku^3=\frac{5}{11}$: then $R$ is about $u^{-2}$, $u\le\frac{3}{25}$, and the hypotheses become polynomial inequalities on the interval $[0,\frac3{25}]$ (`Parking.cstrip_tlow_core`, `Parking.cstrip_main`).

The hypotheses of `Parking.cross_of_bounds` pull in opposite directions. Its main inequality needs $R$ large, because the main term $R(R+1)/(k+R)$ has to exceed a quantity of order $\sqrt R$. The two others, $\bar aR\le0.6679$ and $\underline t\ge0$, need $R$ small, because the kernel deficit decreases as $R$ grows. A floating-point evaluation of the closed forms (not part of the proof) shows how narrow the window is at the smallest column: for $k=265$ the three hypotheses hold together exactly for $64\le R\le70$, and $\varrho(265)+1=70$. At the larger columns that were evaluated ($k=280$, $300$, $400$, $1000$) the window is wider, as one expects since in the variable $u$ the main inequality has the form "bounded quantity $<1.40/u$" and the deficit bound the form "$2-11u+\dots\ge0$". The width $\frac{11}{5}$ of the strip has no intrinsic meaning. According to the notes of the research it was chosen so that the end of the strip falls into this window at $k=265$ while the criterion function of the next-column argument is still positive up to the end of the strip. The threshold $265$ is the column from which the analytic argument takes over; the columns below it are covered by a table.

**The bound is not sharp.** For $k=265$ the first positive row is $k+36=301$ (computed from the last-car recursion `Parking.A_succ` with exact integers; this computation is not part of the proof), while the theorem gives $j\le k+70$. The theorem does not try to locate the crossing. Its purpose is to confine the rows before the crossing to the strip, and the criterion behind it, which replaces the profile of the column $k-1$ by its largest value throughout, is not designed to find the exact row.

**The Lean form.** The statement is `∃ j, k < j ∧ 25 * (j - k - 1) ^ 3 ≤ 121 * k ^ 2 ∧ 0 < dq k j`. The subtraction $j-k-1$ is that of natural numbers, which is the ordinary one because $k<j$. `dq k j` is the normalised step $d_{j,k}/j!$ (`Parking.dq`), and its positivity is $b(j,k-1)<b(j,k)$ by `Parking.dq_pos_iff`. The condition on $j$ is kept as an inequality between integers and the function $\varrho$ is not defined in the library.

## Proof

**Organisation.** Step 1 chooses $R$. Step 2 shows that $(k,R)$ satisfies the hypotheses of `Parking.cross_of_bounds`; this is where the work is, and it consists of translating the conditions on $k$ and $R$ into the scale variable $u$ and applying the two real-variable inequalities `Parking.cstrip_tlow_core` and `Parking.cstrip_main`. Step 3 concludes.

**Step 1: the choice of $R$.** The set of natural numbers $R$ with $121k^2<25R^3$ contains $k$ (because $121<25k$), so it has a least element $R$. Then $R\ge1$ and, by minimality,
$$25\,(R-1)^3\le121\,k^2<25\,R^3 .$$

**Step 2: the hypotheses of the closed-form criterion.** We show that for $k\ge265$ and $R$ as in Step 1,
$$2\le R\le k-1,\qquad\bar a\,R\le\frac{6679}{10000},\qquad\underline t\ge0,\qquad\Bigl(\bar t+e^{-1}e^{\bar a}\frac{R+1}{k+R}\Bigr)\Bigl(\bar H+\frac5k\bar G\Bigr)<e^{-1}\Bigl(\frac{R(R+1)}{k+R}-1-\bar S-\bar{\mathsf E}\Bigr),$$
with $\bar a=5/(2k)$ and the closed forms `Parking.tlow`, `Parking.tup`, `Parking.Hbar`, `Parking.Gbar`, `Parking.Sbar`, `Parking.Ebar` at $(k,R)$.

*(a) The scale.* Let $u>0$ be the real number with $k\,u^3=\frac{5}{11}$. Then $121\,k^2u^6=25$.

*(b) $1<Ru^2\le1+u^2$.* Multiply the two inequalities of Step 1 by $u^6$: $25\,(Ru^2)^3>25$ and $25\,((R-1)u^2)^3\le25$. Hence $Ru^2>1$ and $(R-1)u^2\le1$.

*(c) $u\le0.119705\le\frac{3}{25}$.* Since $265\,u^3\le k\,u^3=\frac{5}{11}$ and $265\cdot0.119705^3>\frac{5}{11}$. (The two numbers are $0.454551\ldots$ and $0.454545\ldots$; the bound for $u$ is the value at $k=265$ rounded up in the sixth decimal.)

*(d) $2\le R\le k-1$.* If $R\le1$ then $Ru^2\le u^2<1$, against (b). And $(R+1)u^3=u\cdot Ru^2+u^3\le u\,(1+u^2)+u^3<\frac{5}{11}=k\,u^3$, so $R+1<k$.

*(e) The tilt exponents.* From $ku^3=\frac{5}{11}$: $\bar a=\frac{5}{2k}=\frac{11}{2}u^3$ and $\underline a=\frac{5}{2k}-\frac{4}{3k^2}=\frac{11}{2}u^3-\frac{484}{75}u^6$ (`Parking.abar`, `Parking.alow`).

*(f) $\bar aR\le0.6679$.* By (e) and (b), $\bar aR=\frac{11}{2}u\cdot Ru^2\le\frac{11}{2}u\,(1+u^2)$, and by (c) this is at most $\frac{11}{2}\cdot0.119705\cdot(1+0.119705^2)=0.66781\ldots$. This estimate has almost no room: the threshold $0.6679$ of `Parking.cross_of_bounds` was fitted to the column $k=265$.

*(g) $1\le e^{\bar a}\le\frac{106}{105}$.* Since $k\ge265$, $0\le\bar a\le\frac{1}{106}$, and $e^{s}\le\frac{1}{1-s}$ for $0\le s<1$.

*(h) The Stirling constant.* $\frac{19947}{50000}\le c_0\le\frac{7979}{20000}$ for $c_0=1/\sqrt{2\pi}$ (`Parking.c0_bounds`).

*(i) The square roots.* From (b), $1-u^2<(R-1)u^2\le1$, $1<Ru^2\le1+u^2$ and $(R+1)u^2\le1+2u^2$. Comparing squares, and using $u^2\le\frac{9}{625}$,
$$1-\frac{101}{200}u^2\le\sqrt{R-1}\,u\le1,\qquad1\le\sqrt R\,u\le1+\frac{u^2}{2},\qquad\sqrt{R+1}\,u\le1+u^2 .$$
The first lower bound gives $\sqrt{R-1}\,u\,\bigl(1+\frac{51}{100}u^2\bigr)\ge1$, and the middle bounds give $Ru^2\cdot\sqrt R\,u\le(1+u^2)(1+\frac{u^2}{2})$. These are routine.

*(j) The two inequalities.* By (b), (c), (e), (g), (h), (i), the numbers $u$, $c=c_0$, $\rho=R$, $s_-=\sqrt{R-1}$, $s_0=\sqrt R$, $s_+=\sqrt{R+1}$, $a=\bar a$, $E=e^{\bar a}$ satisfy the hypotheses of `Parking.cstrip_tlow_core`. Its conclusion is that $e\cdot\underline t(k,R)\ge0$, because $\underline t$ is $e^{-1}$ times the expression in that statement; hence $\underline t\ge0$. In the same way, with in addition $K=k$ and $b=\underline a$, the hypotheses of `Parking.cstrip_main` hold, and its conclusion $\Theta\Psi<L$ is the main inequality multiplied by $e$: there $\Theta=e\,\bar t+e^{\bar a}\frac{R+1}{k+R}$, $\Psi=\bar H+\frac5k\bar G$ and $L=\frac{R(R+1)}{k+R}-1-\bar S-\bar{\mathsf E}$. Multiplying by $e^{-1}>0$ gives the main inequality.

**Step 3: conclusion.** By Step 2, `Parking.cross_of_bounds` applies to $(k,R)$ and gives a natural number $j$ with $k<j\le k+R$ and $d_{j,k}>0$. Then $j-k-1\le R-1$, so $25\,(j-k-1)^3\le25\,(R-1)^3\le121\,k^2$ by Step 1.

**Where the argument is sensitive.** Step 2 contains no idea beyond the change of variable, but two of its estimates are exact to several digits by design, (c) and (f), and the two inequalities invoked in (j) have small margins at $u=\frac{3}{25}$ (see their records). All the difficulty of the theorem is thus concentrated at the columns just above $265$; for large $k$ every estimate has room.

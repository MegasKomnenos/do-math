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

**What it is used for.** There are three uses. The first two belong to the proof of `Parking.root_unimodal`; the third does not.

- In `Parking.mono265`: if $n\ge k+2$ and the column $k\ge265$ is not positive in the rows $k+1,\dots,n$, then $(n,k)$ lies in the strip, where the criterion function of the next-column argument is positive (`Parking.Gfun_pos`, stated for the positions $r\ge2$ of exactly this strip), and therefore the column $k+1$ is negative in the row $n$. The strip is the common ground of the two arguments: this theorem shows that the rows before the crossing are inside it, and the next-column argument works inside it.
- In `Parking.crossing_row`: together with `Parking.strip_end_le` it gives, for $k\ge265$, a positive row $k+r$ with $100r\le27k$; for $82\le k\le264$ such a row is read from the table `Parking.Tab.two_signs`.
- In `Parking.beyond_strip`: the positive row $j$ of the theorem is at or before every row beyond the strip, and from it the column stays positive, up to the row $2k-1$ by `Parking.chain_column_iter` and from the row $2k$ on by `Parking.big_columns`. So a column $k\ge265$ is positive in every row beyond its strip, and `Parking.row_peak` uses this to bound the position of the maximum of a row $n\ge335$.

**How it is proved, and why with these constants.** The theorem is the closed-form crossing criterion `Parking.cross_of_bounds` applied with $R=\varrho(k)+1$, the least natural number with $121k^2<25R^3$. What has to be checked is that this $R$ satisfies the hypotheses of that criterion for every $k\ge265$: the range $2\le R\le k-1$, the bound $\bar aR\le0.6679$, and two inequalities between the closed forms. The two inequalities are statements of their own, `Parking.strip_tlow_nonneg` and `Parking.strip_main`. Everything is done once for all $k$ by passing to the scale variable $u$ with $ku^3=\frac{5}{11}$: then $R$ is about $u^{-2}$, $u\le\frac{3}{25}$, and the two inequalities become polynomial inequalities on the interval $[0,\frac3{25}]$ (`Parking.cstrip_tlow_core`, `Parking.cstrip_main`).

The hypotheses of `Parking.cross_of_bounds` pull in opposite directions. Its main inequality needs $R$ large, because the main term $R(R+1)/(k+R)$ has to exceed a quantity of order $\sqrt R$. The two others, $\bar aR\le0.6679$ and $\underline t\ge0$, need $R$ small, because the kernel deficit decreases as $R$ grows. A floating-point evaluation of the closed forms (not part of the proof) shows how narrow the window is at the smallest column: for $k=265$ the three hypotheses hold together exactly for $64\le R\le70$, and $\varrho(265)+1=70$. At the larger columns that were evaluated ($k=280$, $300$, $400$, $1000$) the window is wider, as one expects since in the variable $u$ the main inequality has the form "bounded quantity $<1.40/u$" and the deficit bound the form "$2-11u+\dots\ge0$". The width $\frac{11}{5}$ of the strip has no intrinsic meaning. According to the notes of the research it was chosen so that the end of the strip falls into this window at $k=265$ while the criterion function of the next-column argument is still positive up to the end of the strip. The threshold $265$ is the column from which the analytic argument takes over; the columns below it are covered by a table.

**The bound is not sharp.** For $k=265$ the first positive row is $k+36=301$ (computed from the last-car recursion `Parking.A_succ` with exact integers; this computation is not part of the proof), while the theorem gives $j\le k+70$. The theorem does not try to locate the crossing. Its purpose is to confine the rows before the crossing to the strip, and the criterion behind it, which replaces the profile of the column $k-1$ by its largest value throughout, is not designed to find the exact row.

**The Lean form.** The statement is `∃ j, k < j ∧ 25 * (j - k - 1) ^ 3 ≤ 121 * k ^ 2 ∧ 0 < dq k j`. The subtraction $j-k-1$ is that of natural numbers, which is the ordinary one because $k<j$. `dq k j` is the normalised step $d_{j,k}/j!$ (`Parking.dq`), and its positivity is $b(j,k-1)<b(j,k)$ by `Parking.dq_pos_iff`. The condition on $j$ is kept as an inequality between integers and the function $\varrho$ is not defined in the library.

## Proof

**Organisation.** Step 1 chooses $R$. Step 2 shows that $(k,R)$ satisfies the hypotheses of `Parking.cross_of_bounds`: the range of $R$ and the bound for $\bar aR$ are obtained here in the scale variable $u$, and the two inequalities between the closed forms are `Parking.strip_tlow_nonneg` and `Parking.strip_main`. Step 3 concludes.

**Step 1: the choice of $R$.** The set of natural numbers $R$ with $121k^2<25R^3$ contains $k$ (because $121<25k$), so it has a least element $R$. Then $R\ge1$ and, by minimality,
$$25\,(R-1)^3\le121\,k^2<25\,R^3 .$$

**Step 2: the hypotheses of the closed-form criterion.** We show that for $k\ge265$ and $R$ as in Step 1,
$$2\le R\le k-1,\qquad\bar a\,R\le\frac{6679}{10000},\qquad\underline t\ge0,\qquad\Bigl(\bar t+e^{-1}e^{\bar a}\frac{R+1}{k+R}\Bigr)\Bigl(\bar H+\frac5k\bar G\Bigr)<e^{-1}\Bigl(\frac{R(R+1)}{k+R}-1-\bar S-\bar{\mathsf E}\Bigr),$$
with $\bar a=5/(2k)$ and the closed forms `Parking.tlow`, `Parking.tup`, `Parking.Hbar`, `Parking.Gbar`, `Parking.Sbar`, `Parking.Ebar` at $(k,R)$.

*(a) The scale.* By Step 1 of the proof of `Parking.strip_tlow_nonneg` (in Lean the private lemma `strip_relations` of this module, from which the proofs of `Parking.strip_tlow_nonneg` and `Parking.strip_main` start as well), there is a real number $u>0$ with
$$k\,u^3=\frac{5}{11},\qquad u\le0.119705\le\frac{3}{25},\qquad R\ge2,\qquad R\,u^2\le1+u^2,\qquad\bar a=\frac{11}{2}u^3 .$$
The bound for $u$ is the value at $k=265$ rounded up in the sixth decimal.

*(b) $2\le R\le k-1$.* $R\ge2$ is in (a). And $(R+1)u^3=u\cdot Ru^2+u^3\le u\,(1+u^2)+u^3=u+2u^3\le\frac{3}{25}+2\cdot\frac{27}{15625}<\frac{5}{11}=k\,u^3$, so $R+1<k$.

*(c) $\bar aR\le0.6679$.* By (a), $\bar aR=\frac{11}{2}u\cdot Ru^2\le\frac{11}{2}u\,(1+u^2)$, and this is at most $\frac{11}{2}\cdot0.119705\cdot(1+0.119705^2)=0.66781\ldots$. This estimate has almost no room: the threshold $0.6679$ of `Parking.cross_of_bounds` was fitted to the column $k=265$.

*(d) $\underline t\ge0$.* This is `Parking.strip_tlow_nonneg` for $k$ and $R$; its hypothesis on $R$ is the pair of inequalities of Step 1.

*(e) The main inequality.* `Parking.strip_main` for $k$ and $R$ gives $\mathsf A\,\mathsf B<\mathsf C$ with
$$\mathsf A=e\,\bar t+e^{\bar a}\frac{R+1}{k+R},\qquad\mathsf B=\bar H+\frac5k\bar G,\qquad\mathsf C=\frac{R(R+1)}{k+R}-1-\bar S-\bar{\mathsf E}.$$
Multiplying by $e^{-1}>0$ gives $e^{-1}\mathsf A\,\mathsf B<e^{-1}\mathsf C$, and $e^{-1}\mathsf A=\bar t+e^{-1}e^{\bar a}\frac{R+1}{k+R}$ because $e^{-1}e=1$. This is the main inequality.

**Step 3: conclusion.** By Step 2, `Parking.cross_of_bounds` applies to $(k,R)$ and gives a natural number $j$ with $k<j\le k+R$ and $d_{j,k}>0$. Then $j-k-1\le R-1$, so $25\,(j-k-1)^3\le25\,(R-1)^3\le121\,k^2$ by Step 1.

**Where the argument is sensitive.** Step 2 contains no idea beyond the change of variable, but two of its estimates are exact to several digits by design, the bound for $u$ in (a) and the estimate (c), and the two inequalities invoked in (d) and (e) have small margins at $u=\frac{3}{25}$ (see the records of `Parking.cstrip_tlow_core` and `Parking.cstrip_main`, on which they rest). All the difficulty of the theorem is thus concentrated at the columns just above $265$; for large $k$ every estimate has room.

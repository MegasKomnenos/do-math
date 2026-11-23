---
weight: unit
short: single-chain formula, quotient form
---
## Description

Single-chain formula, quotient form. If $W$ solves the weighted last-car recursion with a weight that satisfies $\omega(t)=t$ for $1\le t\le k$, then for $1\le n\le 2k+1$ the quantity $W_n-\sum_{m=1}^{n}\varepsilon_mW_{n-m}$ is $0$ for $n\le k$ and $\frac{\omega(n)}{n}W_{n-1}-c_{n-1}$ for $n>k$.

## Statement

Let $\omega$ and $W$ be real sequences such that $W$ is a solution of the weighted last-car recursion with weight $\omega$ (`Parking.IsWSol`), and let $k$ be a natural number such that $\omega(t)=t$ for every $t$ with $1\le t\le k$. Then for every $n$ with $1\le n\le 2k+1$,
$$W_n-\sum_{m=1}^{n}\varepsilon_m\,W_{n-m}\;=\;\begin{cases}0,& n\le k,\\[2pt] \dfrac{\omega(n)}{n}\,W_{n-1}-c_{n-1},& n>k.\end{cases}$$
Here $c_n=(n+1)^{n-1}/n!$ (`Parking.cc`) and $\varepsilon_m=(m-1)^{m-1}/m!$ for $m\ge1$, with $\varepsilon_1=1$ (`Parking.eps`).

## Explanation

**What the formula says.** Let $P=\sum_nc_nX^n$ (`Parking.TreeSeries.Pser`) be the generating series of the solution $c$ for the weight $\omega(t)=t$, and $\mathbf W=\sum_nW_nX^n$. The left-hand side is the coefficient of $X^n$ in the quotient $\mathbf W/P$, because $1/P=1-\sum_{m\ge1}\varepsilon_mX^m$ (`Parking.TreeSeries.coeff_Eser_mul`). With the series $G=\sum_{t\ge1}\frac{\omega(t)}tW_{t-1}X^t$ of `Parking.SingleChain.Gser`, the tree series $T=XP=\sum_ja_jX^j$, $a_j=c_{j-1}$, and $D=T-G=\sum_{t\ge1}\bigl(c_{t-1}-\frac{\omega(t)}{t}W_{t-1}\bigr)X^t$, the statement is
$$\frac{\mathbf W}{P}\equiv 1-D \pmod{X^{2k+2}},$$
read at the coefficients $1\le n\le 2k+1$; the case $n\le k$ records that $D$ has no terms of degree at most $k$.

**Why it holds.** The two recursions are $\mathbf W'=G'\mathbf W$ and $P'=T'P$, so the quotient $V=\mathbf W/P$ satisfies $V'=-D'V$ with $V(0)=1$; that is, $V=\exp(-D)$. If $\omega(t)=t$ for $t\le k$, then $W$ agrees with $c$ up to the index $k$ and $D$ begins in degree $k+1$. The series $\exp(-D)-(1-D)$ consists of the powers $D^2,D^3,\dots$, which begin in degree $2k+2$. So up to degree $2k+1$ the quotient is linear in $D$. The Lean proof does not use the exponential; it obtains the same conclusion from the coefficient recursion of $V'=-D'V$.

**What it is for.** The solution $W$ of a weight that deviates from $t$ only beyond $k$ is given, in the rows $n\le 2k+1$, by a *linear* relation with the known kernel $\varepsilon$: the quadratic recursion has become linear. For the threshold weight $\omega(t)=\min(t,y)$ and $k=y$ this is the relation from which the column equations `Parking.bq_L0` and `Parking.dq_col` are obtained by subtracting neighbouring thresholds. The range $n\le 2k+1$ is called the single-chain range. The name comes from the description of the solutions by rooted forests that the research used before the formalisation, in which the vertices whose subtree has more than $k$ vertices lie on a single chain when $n\le2k+1$; no declaration of the library uses that description, and the fact appears only as the vanishing of $D^2$ below degree $2k+2$. The companion statement `Parking.IsWSol.fwd` is the same congruence multiplied by $P$.

**The Lean form.** The sum runs over `Icc 1 n`; the right-hand side is an `if n ≤ k then … else …`; `ω n / n` is a division of real numbers with $n\ge1$; `W (n - 1)` and `cc (n - 1)` use the subtraction of natural numbers, exact because $n\ge1$. The value $\omega(0)$ does not enter.

## Proof

Write $E=1/P$ (`Parking.TreeSeries.Eser`), $\mathbf W=\sum_nW_nX^n$, $V=E\,\mathbf W$, and $D=T-G$ as above, and write $V_i$, $D_i$ for the coefficients of $X^i$. The proof has five steps; the fourth is the one that uses the range $n\le2k+1$.

*Step 1: $W_n=c_n$ for $n\le k$.* The sequence $c$ solves the recursion with the weight $t\mapsto t$; this is `Parking.cc_rec` together with $c_0=1$ (`Parking.cc_zero`). Two solutions whose weights agree on $1\le t\le N$ agree up to the index $N$: by strong induction on $m\le N$, the value at $m+1$ is determined through the recursion by the weights $\omega(1),\dots,\omega(m+1)$ and the values at $0,\dots,m$, after division by $m+1\ne0$. Applied to $W$ and $c$ with $N=k$ this gives the claim.

*Step 2: the coefficients of $D$.* By `Parking.TreeSeries.coeff_Tser` the coefficient of $X^t$ in $T$ is $a_t$, and $a_t=c_{t-1}$ for $t\ge1$, $a_0=0$. Hence $D_0=0$ and $D_t=c_{t-1}-\frac{\omega(t)}{t}W_{t-1}$ for $t\ge1$. For $1\le t\le k$ the hypothesis gives $\omega(t)/t=1$ and Step 1 gives $W_{t-1}=c_{t-1}$, so $D_t=0$ for all $t\le k$.

*Step 3: the equation of $V$.* By the product rule, $V'=E\,\mathbf W'+\mathbf W\,E'$. By `Parking.SingleChain.deriv_mk`, $\mathbf W'=G'\mathbf W$, and by `Parking.TreeSeries.deriv_Eser`, $E'=-E\,T'$. Hence $V'=E\,G'\,\mathbf W-E\,T'\,\mathbf W=-D'\,V$. Reading the coefficient of $X^i$ (`Parking.TreeSeries.coeff_mul_range`),
$$(i+1)\,V_{i+1}=-\sum_{j=0}^{i}(j+1)\,D_{j+1}\,V_{i-j}\qquad(i\ge0). \tag{1}$$
Moreover $V_0=1$, since the constant coefficients of $E$ and of $\mathbf W$ are $1$ (`Parking.TreeSeries.coeff_Eser_zero`, and $W_0=1$).

*Step 4: $V_i=0$ for $1\le i\le k$, and $V_i=-D_i$ for $1\le i\le 2k+1$.* Let $1\le i\le k$ and apply (1) with $i-1$ in place of $i$: every $D_{j+1}$ that occurs has $j+1\le i\le k$ and vanishes by Step 2, so $i\,V_i=0$ and $V_i=0$. Now let $1\le i\le 2k+1$ and apply (1) with $i-1$ again. In the term of index $j<i-1$, either $j+1\le k$, and then $D_{j+1}=0$; or $j\ge k$, and then $1\le i-1-j\le 2k-k=k$, so $V_{i-1-j}=0$ by what was just shown. Only the term $j=i-1$ remains, and it is $i\,D_i\,V_0=i\,D_i$. Hence $i\,V_i=-i\,D_i$, and $V_i=-D_i$. This is the step in which a product of two coefficients of $D$ would appear for $i\ge 2k+2$: there the term with $j+1=k+1$ and $i-1-j=k+1$ is no longer excluded.

*Step 5: conclusion.* By `Parking.TreeSeries.coeff_Eser_mul`, applied to the series $\mathbf W$, $V_n=W_n-\sum_{m=1}^{n}\varepsilon_mW_{n-m}$. For $n\le k$ this is $0$ by Step 4. For $k<n\le2k+1$ it is $-D_n=\frac{\omega(n)}{n}W_{n-1}-c_{n-1}$ by Steps 4 and 2.

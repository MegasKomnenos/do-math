---
weight: unit
short: column equation of the step
---
## Description

The column equation of the step of the column $k\ge2$ on the rows $k+1\le n\le 2k-1$: $\delta_n=\frac{k+1}{n}\delta_{n-1}+\frac2n\beta^{(k-1)}_{n-1}+\sum_{m=1}^{n-k}\varepsilon_m\delta_{n-m}$, where $\delta_n=(b(n,k)-b(n,k-1))/n!$.

## Statement

Let $k\ge2$ and $n$ be natural numbers with $k+1\le n\le 2k-1$, and write $\delta_i=\delta^{(k)}_i=(b(i,k)-b(i,k-1))/i!$ (`Parking.dq`). Then
$$\delta_n=\frac{k+1}{n}\,\delta_{n-1}+\frac{2}{n}\,\beta^{(k-1)}_{n-1}+\sum_{m=1}^{n-k}\varepsilon_m\,\delta_{n-m},$$
where $\beta^{(k-1)}_i=b(i,k-1)/i!$ (`Parking.bq`) and $\varepsilon_m=(m-1)^{m-1}/m!$ (`Parking.eps`).

## Explanation

**What the equation says.** In the rows $k+1\le n\le2k-1$, which the other parts call the chain range of the column $k$, the step of the column satisfies a linear recursion in the row index. The step in the row $n$ is the sum of three contributions: the step in the previous row, with the factor $(k+1)/n$; a source term $\frac2n\beta^{(k-1)}_{n-1}$, which is nonnegative (`Parking.bq_nonneg`) and comes from the neighbouring column $k-1$ one row earlier; and a feedback sum over the earlier rows down to the row $k$, with the nonnegative kernel $\varepsilon$. The recursion starts from the negative value $\delta_k=-a_k/k$ (`Parking.dq_base`). Multiplied by $n!$ it is an identity between integers,
$$d_{n,k}=(k+1)\,d_{n-1,k}+2\,b(n-1,k-1)+\sum_{m=1}^{n-k}\binom nm(m-1)^{m-1}\,d_{n-m,k},\qquad d_{n,k}=b(n,k)-b(n,k-1).$$

**Why it has this form.** For $k\ge2$ the step is the second difference of the environments in the threshold, $\delta_i=z^{(k+1)}_i-2z^{(k)}_i+z^{(k-1)}_i$ (`Parking.bq_eq`). For each of the three thresholds $y$ the single-chain formula `Parking.IsWSol.ez` gives $z^{(y)}_n-\sum_{m=1}^{n}\varepsilon_mz^{(y)}_{n-m}=\frac yn z^{(y)}_{n-1}-c_{n-1}$ in the rows $y\le n\le 2y+1$, and the equation is the second difference of these three relations. The term $c_{n-1}$, which does not depend on $y$, cancels; the second difference of $y\,z^{(y)}_{n-1}$ in $y$ is $(k+1)\delta_{n-1}+2\beta^{(k-1)}_{n-1}$, which is where the factor $k+1$ and the source term come from. The upper limit $n\le 2k-1$ is the single-chain range $n\le2y+1$ of the smallest threshold $y=k-1$, and the lower limit $n\ge k+1$ is the requirement $y\le n$ for the largest threshold $y=k+1$.

**How it is used.** The equation is the tool for following the sign of the step along the chain range: it is the hypothesis "column equation" of the persistence arguments of the chain range (`Parking.caseA`, `Parking.caseFar`), and in the first of them it is tilted by the powers of $x=1/\gamma_k$. With the tree curvature of `Parking.xi` it reads $\delta_n-\sum_{m=1}^{n-k}\varepsilon_m\delta_{n-m}=\xi_n$ (by `Parking.succ_mul_xi_succ`). Beyond the row $2k-1$ the equation becomes an inequality, with the prime kernel of the threshold $k$ in place of $\varepsilon$ (`Parking.col_eq_all`).

**The Lean form.** The upper limit of the sum is `n - k`, and $\beta^{(k-1)}$ is `bq (k - 1)`, with the subtraction of natural numbers, exact because $n>k\ge2$; the hypothesis $n\le2k-1$ is written `n ≤ 2 * k - 1`.

## Proof

*The single-chain formula for one threshold.* For a threshold $y\ge1$ and $y\le n\le2y+1$,
$$z^{(y)}_n-\sum_{m=1}^{n}\varepsilon_m\,z^{(y)}_{n-m}=\frac yn\,z^{(y)}_{n-1}-c_{n-1}, \tag{1}$$
where $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`) and $c_n=(n+1)^{n-1}/n!$ (`Parking.cc`). (This is a private lemma of the module, also used for `Parking.bq_L0`.) By `Parking.zr_isWSol`, $z^{(y)}$ solves the weighted last-car recursion with the weight $\min(t,y)$, which equals $t$ for $t\le y$, so `Parking.IsWSol.ez` applies with its parameter $k$ equal to $y$. For $y<n\le 2y+1$ it gives (1), because $\min(n,y)=y$. For $n=y$ it gives that the left-hand side is $0$, and the right-hand side is $z^{(y)}_{y-1}-c_{y-1}=0$ by `Parking.zr_eq_cc`.

*The step as a second difference.* Since $k\ge2$, `Parking.bq_eq` applies to the columns $k$ and $k-1$ and gives, for every $i$,
$$\delta_i=\bigl(z^{(k+1)}_i-z^{(k)}_i\bigr)-\bigl(z^{(k)}_i-z^{(k-1)}_i\bigr)=z^{(k+1)}_i-2z^{(k)}_i+z^{(k-1)}_i. \tag{2}$$

*Second difference of the three relations.* The hypotheses $k+1\le n\le 2k-1$ give $y\le n\le 2y+1$ for each of $y=k+1,\,k,\,k-1$; the binding conditions are $k+1\le n$ for $y=k+1$ and $n\le 2(k-1)+1$ for $y=k-1$. Take (1) for $y=k+1$, minus twice (1) for $y=k$, plus (1) for $y=k-1$. By (2) the left-hand side is $\delta_n-\sum_{m=1}^{n}\varepsilon_m\delta_{n-m}$. On the right the terms $c_{n-1}$ cancel, and
$$\frac{k+1}{n}z^{(k+1)}_{n-1}-\frac{2k}{n}z^{(k)}_{n-1}+\frac{k-1}{n}z^{(k-1)}_{n-1}=\frac{k+1}{n}\,\delta_{n-1}+\frac2n\bigl(z^{(k)}_{n-1}-z^{(k-1)}_{n-1}\bigr)=\frac{k+1}{n}\,\delta_{n-1}+\frac2n\,\beta^{(k-1)}_{n-1},$$
by (2) and `Parking.bq_eq`; this is a routine rearrangement.

*Truncation.* For $m>n-k$ we have $n-m<k$ and $\delta_{n-m}=0$ by `Parking.dq_eq_zero`, so the sum over $1\le m\le n$ equals the sum over $1\le m\le n-k$ (`Parking.sum_Icc_trunc`). Moving the sum to the right gives the statement.

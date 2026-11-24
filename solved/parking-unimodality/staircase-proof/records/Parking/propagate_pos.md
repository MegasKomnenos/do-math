---
weight: unit
short: propagation of a positive step down a column
---
## Description

For a column $k\ge2$ and a tilt $0<x<1$ at which the tilted environment $z^{(k)}_Nx^N$ does not increase in $N$: if the step of the column $k$ is positive in a row $m\ge k$, and all the sums $\sum_{t=s}^{m+1}\xi_tx^t$, $k\le s\le m+1$, of the tree curvature $\xi$ of the column are nonnegative, then the step of the column $k$ is positive in every row $n\ge m$.

## Statement

Let $A(N,l)$ be the number of parking functions of length $N$ with maximum displacement at most $l$ (`Parking.A`) and $b(n,\ell)$ the number of those of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k\ge2$ and $m\ge k$ be natural numbers and $x$ a real number with $0<x<1$. Write $z^{(y)}_N=A(N,y-1)/N!$ (`Parking.zr`), $\delta_n=(b(n,k)-b(n,k-1))/n!$ for the normalised step of the column $k$ in the row $n$ (`Parking.dq`), and $\xi_t$ for the tree curvature of the column $k$ (`Parking.xi`): $\xi_0=0$ and, for $t\ge1$,
$$t\,\xi_t=\min(t,k+1)\,z^{(k+1)}_{t-1}-2\min(t,k)\,z^{(k)}_{t-1}+\min(t,k-1)\,z^{(k-1)}_{t-1}.$$
Assume

1. $z^{(k)}_{N+1}\,x^{N+1}\le z^{(k)}_N\,x^N$ for every $N\ge0$;
2. $\displaystyle\sum_{t=s}^{m+1}\xi_t\,x^t\ge0$ for every $s$ with $k\le s\le m+1$;
3. $\delta_m>0$.

Then $\delta_n>0$ for every $n\ge m$; that is, $b(n,k-1)<b(n,k)$ for every $n\ge m$.

## Explanation

**What it is.** The statement turns finitely many inequalities at one row into a sign in infinitely many rows, and it is the means by which the columns $2\le k\le81$ are treated beyond the rows that a table can compute. Its conclusion is a positive step, and for it the statement asks, besides hypotheses 1 and 2, that the tilt be smaller than $1$ and that the step be positive in the row directly before the row at which the sums are known.

**Why a positive step is needed to start.** The sums of hypothesis 2 are an invariant that passes from row to row as long as the new curvature $\xi_{n+1}$ is nonnegative, and they give $\delta_n\ge0$. They do not exclude $\delta_n=0$. The step bound `Parking.step_bound` sharpens the conclusion to $\delta_n\ge(1-x)\,\xi_n$, which is positive when $\xi_n$ is, and $\xi_n$ is positive when the step of the row $n-1$ is: for $n-1\ge k$, $n\,\xi_n=(k+1)\,\delta_{n-1}+2\beta^{(k-1)}_{n-1}$ with $\beta^{(k-1)}_{n-1}=b(n-1,k-1)/(n-1)!\ge0$. So positivity moves in a cycle, from the step of a row to the curvature of the next row and from that curvature to the step of that row, and the cycle has to be entered once. Hypothesis 3 is that entry. The condition $x<1$ makes the factor $1-x$ of the step bound positive.

**How it is used.** In `Parking.step_pos_beyond`, for a column $2\le k\le81$: the tilt is the critical tilt $x_k=(k/(k+1))^{k-1}$, the row $m+1$ is the row $n_0(k)$ listed for the column (`Parking.Tab.n0`), hypothesis 1 is `Parking.zrT_anti_crit`, hypothesis 2 is the fourth part of the table `Parking.Tab.small_table`, and hypothesis 3 is the last cell $(n_0(k)-1,k)$ of the junction table `Parking.Tab.junction_table`.

**The row $m=k$.** The statement admits $m=k$, but hypothesis 3 cannot hold there: the step of the column $k$ in the row $k$ is negative, $\delta_k=-a_k/k$ with $a_k=k^{k-1}/k!$, as the record of `Parking.dq` notes. The statement has content for $m\ge k+1$.

**The Lean form.** The hypotheses are stated with the row $m$ of the positive step and the row $m+1$ of the sums, so that no subtraction of natural numbers occurs. Hypothesis 1 is `∀ N, zrT k x (N + 1) ≤ zrT k x N` with `zrT k x N = zr k N * x ^ N` (`Parking.zrT`); the sums run over `Finset.Icc s (m + 1)`; hypothesis 3 and the conclusion are `0 < dq k m` and `0 < dq k n`. The equivalence of $\delta_n>0$ with $b(n,k-1)<b(n,k)$ is `Parking.dq_pos_iff`.

## Proof

For $n\ge k$ let $I(n)$ be the assertion that $\sum_{t=s}^{n}\xi_tx^t\ge0$ for every $s$ with $k\le s\le n$. We show by induction on $n\ge m$ that $I(n+1)$ holds and $\delta_n>0$. For $n=m$ these are hypotheses 2 and 3.

Two facts are used in the induction step.

*(a) A positive step makes the next curvature positive.* If $n\ge k$ and $\delta_n>0$, then $\xi_{n+1}>0$. Indeed `Parking.succ_mul_xi_succ` states $(n+1)\,\xi_{n+1}=(k+1)\,\delta_n+2\beta^{(k-1)}_n$ for $k\ge2$ and $n\ge k$, where $\beta^{(k-1)}_n=b(n,k-1)/n!$ (`Parking.bq`) is nonnegative (`Parking.bq_nonneg`). The right-hand side is positive, and so is $\xi_{n+1}$.

*(b) The step bound.* If $n\ge k$ and $I(n)$ holds, then $(1-x)\,\xi_n\le\delta_n$. This is `Parking.step_bound`, whose hypotheses are $k\ge2$, $n\ge k$, $x>0$, hypothesis 1 and $I(n)$.

*Induction step.* Let $n\ge m$, and suppose $I(n+1)$ and $\delta_n>0$. By (a), $\xi_{n+1}>0$. By (b) at the row $n+1$ and $1-x>0$,
$$\delta_{n+1}\ \ge\ (1-x)\,\xi_{n+1}\ >\ 0 .$$
By (a) again, now at the row $n+1\ge k$, $\xi_{n+2}>0$, hence $\xi_{n+2}\,x^{n+2}\ge0$. This gives $I(n+2)$: for $s\le n+1$ the sum from $s$ to $n+2$ is the sum from $s$ to $n+1$, which is nonnegative by $I(n+1)$, plus the term $\xi_{n+2}x^{n+2}$; for $s=n+2$ the sum is that term alone. So $I(n+2)$ holds and $\delta_{n+1}>0$, which completes the induction.

The second half of what was shown is the claim: $\delta_n>0$ for every $n\ge m$.

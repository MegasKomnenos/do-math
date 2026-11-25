---
weight: unit
short: tree curvature of a column
---
## Description

The tree curvature coefficients $\xi_t$ of the column $k$: $\xi_0=0$ and, for $t\ge1$, $t\,\xi_t=\min(t,k+1)\,z^{(k+1)}_{t-1}-2\min(t,k)\,z^{(k)}_{t-1}+\min(t,k-1)\,z^{(k-1)}_{t-1}$.

## Statement

Let $k\ge2$ be a natural number. The *tree curvature* of the column $k$ is the real sequence $\xi_t=\xi^{(k)}_t$, $t\ge0$, with $\xi_0=0$ and, for $t\ge1$,
$$\xi_t=\frac{1}{t}\Bigl(\min(t,k+1)\,z^{(k+1)}_{t-1}-2\,\min(t,k)\,z^{(k)}_{t-1}+\min(t,k-1)\,z^{(k-1)}_{t-1}\Bigr),$$
where $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`). The Lean definition `xi k t` is written for all natural numbers $k$, with $k-1$ the truncated difference; it is used only for $k\ge2$.

## Explanation

**What the coefficients are.** For a threshold $y$ let $G_y=\sum_{t\ge1}\frac{\min(t,y)}{t}z^{(y)}_{t-1}X^t$ be the series `Parking.SingleChain.Gser` of the weight $\min(t,y)$ and its solution $z^{(y)}$. By `Parking.SingleChain.deriv_mk` the series $Z_y=\sum_nz^{(y)}_nX^n$ of the threshold satisfies $Z_y'=G_y'Z_y$ with $Z_y(0)=1$, so $G_y$ is the logarithm of $Z_y$. The definition says exactly that
$$\xi_t=[X^t]\bigl(G_{k+1}-2G_k+G_{k-1}\bigr):$$
$\xi$ is the second difference in the threshold, at $y=k$, of the logarithm of the series of the threshold. The step of the column is the same second difference of the series itself, $\delta_n=[X^n](Z_{k+1}-2Z_k+Z_{k-1})$ (`Parking.dq`, by `Parking.bq_eq`). The word "tree" refers to the reading of an exponential generating series as a count of forests and of its logarithm as the count of the trees of which the forests are made; no declaration of the library uses forests, and for it $\xi$ is the sequence defined by the formula above.

**Its properties.** $\xi_t=0$ for $t<k$, because below the column index the three thresholds are in their free range (`Parking.xi_eq_zero`). Beyond it, $(n+1)\xi_{n+1}=(k+1)\delta_n+2\beta^{(k-1)}_n$ for $n\ge k$ (`Parking.succ_mul_xi_succ`), which is $n+1$ times the first two terms on the right of the column equation `Parking.dq_col`; so in the chain range the column equation reads $\delta_n-\sum_{m=1}^{n-k}\varepsilon_m\delta_{n-m}=\xi_n$. The first nonzero coefficient is $\xi_k=-a_k/k$, by a direct computation from the definition and `Parking.zr_eq_cc`; it equals $\delta_k$ (`Parking.dq_base`).

**What it is for.** On all rows the step is bounded below by the tree curvature convolved with the environment of the threshold $k$, $\sum_{t\le n}\xi_t\,z^{(k)}_{n-t}\le\delta_n$ (`Parking.one_tree_bound`). From this bound the step bound `Parking.step_bound` derives $(1-x)\,\xi_n\le\delta_n$ at a row $n\ge k$, provided that the tilted sums $\sum_{s\le t\le n}\xi_t\,x^t$, $k\le s\le n$, are nonnegative and the tilted environment $z^{(k)}_Nx^N$ does not increase in $N$. With it `Parking.propagate_pos` derives $\delta_n>0$ for all rows $n\ge m$ from a positive step in a row $m\ge k$, provided that $x<1$, the tilted environment does not increase, and the tilted sums are nonnegative at the row $m+1$. `Parking.step_pos_beyond` applies this to the columns $2\le k\le81$ at the critical tilt, where the table `Parking.Tab.small_table` checks the sums.

**The Lean form.** `xi k t` is defined by a case distinction on $t=0$; the minima are taken in the natural numbers and then cast to the real numbers; the division is by the real number $t$. `Parking.xi_succ` restates the definition at $t+1$ without the case distinction.

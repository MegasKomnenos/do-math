---
weight: unit
short: the columns 2 ≤ k ≤ 81 in the rows n ≥ max(2k, 17)
---
## Description

For $2\le k\le 81$ and every $n$ with $n\ge 2k$ and $n\ge 17$: $b(n,k-1)\le b(n,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $k$ and $n$ be natural numbers with $2\le k\le 81$, $2k\le n$ and $17\le n$. Then $b(n,k-1)\le b(n,k)$.

## Explanation

This is the left half (`Parking.left_half`) for the columns for which the analytic argument of `Parking.big_columns` is not available. Each such column is settled by a finite computation followed by an argument that reaches all rows. For every $k$ the table fixes a row $n_0(k)\ge 2k$. Below that row the inequality is read from the table. At that row the table certifies that the suffix sums of the tilted tree curvature are nonnegative, and from this the propagation theorem derives the inequality in every later row. So an infinite family of inequalities per column rests on finitely many computed ones.

The condition $n\ge 17$ is the range of the table, whose checks of a column $k$ start at the row $\max(2k,17)$. The rows $n\le 16$ are not covered by this statement; they are handled separately in the proof of the main theorem (`Parking.Tab.small_rows`).

## Proof

`Parking.Tab.small_table`, for $2\le k\le 81$, provides with $n_0=n_0(k)$ (`Parking.Tab.n0`): (a) $2k\le n_0$; (b) $b(n,k-1)\le b(n,k)$ for all $n$ with $2k\le n$, $17\le n$, $n<n_0$; (c) $\sum_{t=s}^{n_0}\xi_t\,x_k^{\,t}\ge 0$ for all $k\le s\le n_0$, where $\xi_t$ is the tree curvature of column $k$ (`Parking.xi`) and $x_k=(k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`). (It also provides a statement about the chain range that is not used here.) How the table is computed and why the computation is sound is the content of the record of `Parking.Tab.small_table`.

If $n<n_0$, the claim is (b). If $n\ge n_0$, apply `Parking.propagate` with the row $n_0\ge k$ and the tilt $x_k>0$ (`Parking.xcrit_pos`): its first hypothesis, that $z^{(k)}_Nx_k^{\,N}$ does not increase in $N$, is `Parking.zrT_anti_crit`, and its second hypothesis is (c). It gives $\delta_n\ge 0$ for the normalised step $\delta_n=(b(n,k)-b(n,k-1))/n!$, which is $b(n,k-1)\le b(n,k)$ by `Parking.dq_nonneg_iff`.

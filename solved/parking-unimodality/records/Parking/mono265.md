---
weight: unit
short: the next column for columns from 265 on
---
## Description

For $k \ge 265$ and $n \ge k + 2$: if column $k$ has no positive step in the rows $k+1, \dots, n$, that is, $b(j,k) \le b(j,k-1)$ for $k + 1 \le j \le n$, then column $k + 1$ has a negative step in the row $n$: $b(n,k+1) < b(n,k)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k \ge 265$ and $n \ge k + 2$ be natural numbers. If $b(j,k) \le b(j,k-1)$ for every $j$ with $k + 1 \le j \le n$, then $b(n,k+1) < b(n,k)$.

With the steps $d_{n,k} = b(n,k) - b(n,k-1)$: if $d_{j,k} \le 0$ for all $k + 1 \le j \le n$, then $d_{n,k+1} < 0$.

## Explanation

The statement says that the columns turn positive in order: as long as column $k$ has not yet had a positive step, the next column is still strictly decreasing in the same row. In the proof of unimodality this is what propagates a nonpositive step to the right along a row; it enters through `Parking.mono`, which adds the columns $9 \le k \le 264$ by a table.

The hypothesis concerns all the rows from $k + 1$ to $n$ and not only the row $n$, but it is used in two ways only. At the row $n$ it is the input of the criterion `Parking.step_neg_of_Gfun`. And it places $n$ below the rows in which column $k$ is positive: column $k$ is known to be positive in some row $j$ of the strip $25(j-k-1)^3 \le 121k^2$ (`Parking.crossing_strip`), the hypothesis excludes a positive step in the rows up to $n$, so $n < j$, and the distance $r = n - k$ then satisfies $25r^3 \le 121k^2$. In this strip the position $(n,k)$ is a first-layer position and the criterion function is positive (`Parking.Gfun_pos`). The bound $k \ge 265$ is the range of `Parking.crossing_strip` and of `Parking.Gfun_pos`. The row $n = k + 1$ is excluded because the criterion needs $r \ge 2$.

## Proof

By `Parking.crossing_strip` there is a row $j > k$ with $25(j-k-1)^3 \le 121k^2$ in which the step of column $k$ is positive, $b(j,k-1) < b(j,k)$. If $j \le n$, the hypothesis at $j$ would give $b(j,k) \le b(j,k-1)$; hence $j > n$.

Write $n = k + r$. Then $r \ge 2$ and $r \le j - k - 1$, so $25r^3 \le 25(j-k-1)^3 \le 121k^2$. By `Parking.strip_end_le`, which states that $25s^3 \le 121k^2$ implies $100(s+1) \le 27k$ for $k \ge 265$, we get $r \le k - 1$. By `Parking.Gfun_pos` the criterion function satisfies $\mathsf{G}(r,k) > 0$ (`Parking.Gfun`).

The hypothesis at the row $n$ says, by `Parking.dq_nonpos_iff`, that the normalised step $\delta^{(k)}_n = d_{n,k}/n!$ (`Parking.dq`) is nonpositive. Now `Parking.step_neg_of_Gfun`, whose hypotheses $k \ge 3$, $2 \le r \le k - 1$ and $\mathsf{G}(r,k) \ge 0$ hold, gives $\delta^{(k+1)}_n < 0$, which is $b(n,k+1) < b(n,k)$ by `Parking.dq_neg_iff`.

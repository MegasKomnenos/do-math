---
weight: unit
short: a column k ≥ 265 is positive in every row beyond its strip
---
## Description

For $k \ge 265$ and $r$ with $121k^2 < 25r^3$: $b(k+r,k-1) < b(k+r,k)$. In words: a column $k \ge 265$ has a positive step in every row beyond its strip, the strip of the column $k$ being the rows $k+r$ with $r \ge 1$ and $25r^3 \le 121k^2$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k \ge 265$ and $r$ be natural numbers with $121\,k^2 < 25\,r^3$. Then
$$b(k+r,k-1) < b(k+r,k).$$

With the steps $d_{n,k} = b(n,k) - b(n,k-1)$ the conclusion is $d_{k+r,k} > 0$.

The *strip* of the column $k$ consists, as said, of the rows $k+r$ with $r \ge 1$ and $25r^3 \le 121k^2$, that is, with $1 \le r \le \varrho(k)$ for $\varrho(k) = \lfloor (11k/5)^{2/3} \rfloor$. The hypothesis $121k^2 < 25r^3$ says $r \ge \varrho(k)+1$: the row $k+r$ lies beyond the strip.

## Explanation

**What the statement adds.** `Parking.crossing_strip` finds one positive row of a column $k \ge 265$, and it places that row in the strip or in the first row beyond it. The present statement says that every row beyond the strip is positive, without an upper limit on the row. So for a column $k \ge 265$ the sign of the step is known in all the rows $n \ge k + \varrho(k) + 1$, and it is positive there. Inside the strip the library does not determine the sign: the first positive row lies somewhere in the strip or in the row after it.

The statement joins three results about a column, each of which covers a different range of rows. `Parking.crossing_strip` supplies a positive row $j \le k + \varrho(k) + 1$. From there the persistence of the sign (`Parking.chain_column_iter`) keeps the column positive up to the row $2k-1$, the end of its chain range. From the row $2k$ on the column is positive by `Parking.big_columns`.

**What it is used for.** Read along a row $n$, the statement says that a column $k \ge 265$ with $121k^2 < 25(n-k)^3$ is positive in the row $n$. In `Parking.row_peak` this is used in the contrapositive: if a column $k$ with $265 \le k \le n-1$ is not positive in the row $n$, then $25(n-k)^3 \le 121k^2$, that is, the row $n$ lies in the strip of the column $k$. This bounds how far from the end of the row such a column can stand. The proof of `Parking.root_unimodal` does not use the statement.

**The constants.** The bound $k \ge 265$ is the range of `Parking.crossing_strip`; the two other results hold from smaller columns on. The constant $\frac{121}{25}$ is that of the strip of `Parking.crossing_strip`. It comes from the estimates of that theorem and of `Parking.Gfun_pos`, and the end of the strip is not the row in which the column turns positive. The record of `Parking.crossing_strip` gives the case $k = 265$: the first positive row, found by an exact computation that is not part of the proof, is $k + 36$, the strip ends at the row $k + 69$, and the present statement begins at the row $k + 70$.

**The Lean form.** The row is written `k + r`, so that the distance $r$ of the row from the row $k$ appears without a subtraction, and `b (k + r) (k - 1)` uses the subtraction of natural numbers, which is exact because $k \ge 265$. No lower bound for $r$ is assumed; the hypothesis $121k^2 < 25r^3$ with $k \ge 265$ forces $r \ge 70$.

## Proof

By `Parking.crossing_strip` there is a row $j > k$ with $25\,(j-k-1)^3 \le 121\,k^2$ in which the step of the column $k$ is positive. That statement is written with the normalised step $d_{j,k}/j!$ (`Parking.dq`), and by `Parking.dq_pos_iff` its positivity is $b(j,k-1) < b(j,k)$.

*The row $j$ is at or before the row $k+r$.* Suppose $j > k + r$. Then $r \le j - k - 1$, so $25r^3 \le 25\,(j-k-1)^3 \le 121k^2$, against the hypothesis $121k^2 < 25r^3$. Hence $j \le k + r$, and since $j > k$ we have $k + 1 \le j \le k + r$.

Put $n = k + r$ and distinguish two cases.

*The case $n \le 2k - 1$.* Then $k+1 \le j \le n \le 2k-1$. `Parking.chain_column_iter` says that a column $k \ge 2$ which is positive in a row $m \ge k+1$ is positive in every row from $m$ to $2k-1$. It applies because $k \ge 265$, and with $m = j$ it gives $b(n,k-1) < b(n,k)$.

*The case $n \ge 2k$.* `Parking.big_columns` says that $b(n,k-1) < b(n,k)$ for every $k \ge 82$ and every $n \ge 2k$. It applies because $k \ge 265$.

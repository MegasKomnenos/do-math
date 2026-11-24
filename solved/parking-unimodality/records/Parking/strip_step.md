---
weight: unit
short: in the strip a nonpositive step is followed by a negative step
---
## Description

For $k \ge 265$ and $r \ge 2$ with $25r^3 \le 121k^2$: if $b(k+r,k) \le b(k+r,k-1)$, then $b(k+r,k+1) < b(k+r,k)$. In words: in a row of the strip of a column $k \ge 265$, other than the first, a nonpositive step of the column $k$ is followed by a negative step of the column $k+1$; the strip of the column $k$ consists of the rows $k+r$ with $r \ge 1$ and $25r^3 \le 121k^2$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k \ge 265$ and $r \ge 2$ be natural numbers with $25\,r^3 \le 121\,k^2$, and put $n = k + r$. If $b(n,k) \le b(n,k-1)$, then
$$b(n,k+1) < b(n,k).$$

With the steps $d_{n,k} = b(n,k) - b(n,k-1)$: if $d_{n,k} \le 0$, then $d_{n,k+1} < 0$.

The statement concerns the rows of the *strip* of the column $k$, the rows $k+r$ with $r \ge 1$ and $25r^3 \le 121k^2$, from the second on.

## Explanation

**What the statement is.** The criterion for the next column (`Parking.step_neg_of_Gfun`) says: at a position $n = k + r$ with $k \ge 3$ and $2 \le r \le k-1$, if $\mathsf{G}(r,k) \ge 0$ and the step of the column $k$ in the row $n$ is nonpositive, then the step of the column $k+1$ in the row $n$ is negative. Here $\mathsf{G}(r,k)$ is the *criterion function*, an explicit real function of $r$ and $k$ (`Parking.Gfun`); only its sign matters in this record. `Parking.Gfun_pos` shows that $\mathsf{G}(r,k) > 0$ for $k \ge 265$ and $r \ge 2$ with $25r^3 \le 121k^2$. The present statement is the criterion on that region, written for the counts and without the function $\mathsf{G}$. Both steps are taken in the same row $n$, and nothing is assumed about any other row.

**How it differs from `Parking.mono265`.** That statement has the same conclusion, $b(n,k+1) < b(n,k)$, and it assumes that the column $k$ is nonpositive in all the rows $k+1, \dots, n$. Its proof uses this assumption in two ways only: at the row $n$, and to place the row $n$ in the strip, since by `Parking.crossing_strip` a row before which the column has not turned positive lies in the strip. The present statement takes the place in the strip as its hypothesis and keeps the assumption at the row $n$ alone. It therefore applies wherever the row is known to lie in the strip by other means. This is the situation in `Parking.row_peak`, which moves along one row from a column to the next: there the strip is reached through `Parking.beyond_strip`, and what is known about the column is its sign in that one row. The proof uses neither a bound for the crossing row nor the persistence of the sign. The proof of `Parking.root_unimodal` does not use the statement.

**The hypotheses.** The bound $k \ge 265$ and the conditions $r \ge 2$ and $25r^3 \le 121k^2$ are the range of `Parking.Gfun_pos`. The first row of the strip, $r = 1$, is excluded because both `Parking.Gfun_pos` and the criterion are stated for $r \ge 2$. Nothing about a row is lost by this: the row $k+1$ has the columns $0, \dots, k$, so that the column $k+1$ is not one of its columns.

**The Lean form.** The row is written `k + r`, and `b (k + r) (k - 1)` uses the subtraction of natural numbers, which is exact because $k \ge 265$.

## Proof

By `Parking.strip_end_le`, which states that $25s^3 \le 121k^2$ implies $100\,(s+1) \le 27k$ for $k \ge 265$, we get $100\,(r+1) \le 27k$ and hence $r \le k - 1$. So $2 \le r \le k-1$.

By `Parking.Gfun_pos` the criterion function satisfies $\mathsf{G}(r,k) > 0$ (`Parking.Gfun`), and in particular $\mathsf{G}(r,k) \ge 0$.

The hypothesis $b(n,k) \le b(n,k-1)$ says, by `Parking.dq_nonpos_iff`, that the normalised step $\delta^{(k)}_n = d_{n,k}/n!$ (`Parking.dq`) is nonpositive. Now `Parking.step_neg_of_Gfun`, whose hypotheses $k \ge 3$ (as $k \ge 265$), $2 \le r \le k-1$ and $\mathsf{G}(r,k) \ge 0$ hold, gives $\delta^{(k+1)}_n < 0$. By `Parking.dq_neg_iff`, applied to the column $k+1$, this is $b(n,k+1) < b(n,(k+1)-1)$, that is, $b(n,k+1) < b(n,k)$.

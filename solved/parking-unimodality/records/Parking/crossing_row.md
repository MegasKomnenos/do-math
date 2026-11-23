---
weight: unit
short: an early positive row in every column k ≥ 82
---
## Description

For every $k \ge 82$ there is a row $k + r$ with $1 \le r \le 0.27k$ at which $b(k+r,k-1) < b(k+r,k)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`), and $d_{n,k} = b(n,k) - b(n,k-1)$. For every natural number $k \ge 82$ there is a natural number $r$ with

$$1 \le r, \qquad 100\,r \le 27\,k, \qquad d_{k+r,\,k} > 0.$$

The Lean statement is written with the normalised step $\delta_n = d_{n,k}/n!$ (`Parking.dq`), which has the same sign.

## Explanation

The statement locates a positive row of the column $k$ early in its chain range $k+1 \le n \le 2k-1$. What matters for its use is that $0.27 < \frac13$: the persistence statement `Parking.persist` requires the first positive row to have offset at most $k/3$, and `Parking.single_crossing` combines the two. The row found here need not be the first positive row; it is an upper bound for it.

The statement gathers two sources. For $82 \le k \le 264$ the row is taken from the table of two signs (`Parking.Tab.two_signs`), an exact computation that lists for each column $9 \le k \le 264$ a number $z(k)$ with $d_{k+z(k)+1,\,k} > 0$. For $k \ge 265$ it comes from the analytic result `Parking.crossing_strip`, which finds a positive row $j > k$ with $25\,(j-k-1)^3 \le 121\,k^2$, an offset of the order $k^{2/3}$. The constant $0.27$ is a common bound for the two: it holds for the tabulated values from $k = 82$ on and for the strip from $k = 265$ on.

## Proof

*Columns $82 \le k \le 264$.* `Parking.Tab.two_signs` gives, with $z = z(k)$ the tabulated value `Parking.Tab.ztab`, the inequality $b(k+z+1,k-1) < b(k+z+1,k)$. Take $r = z + 1 \ge 1$. The bound $100\,(z(k)+1) \le 27\,k$ for $82 \le k \le 264$ is `Parking.Tab.ztab_27`, a finite check on the table. The passage to $\delta$ is `Parking.dq_pos_iff`.

*Columns $k \ge 265$.* `Parking.crossing_strip` gives $j > k$ with $25\,(j-k-1)^3 \le 121\,k^2$ and $\delta_j > 0$. Take $r = j - k \ge 1$. By `Parking.strip_end_le`, for $k \ge 265$ the inequality $25\,s^3 \le 121\,k^2$ implies $100\,(s+1) \le 27\,k$; with $s = j - k - 1$ this is $100\,r \le 27\,k$.

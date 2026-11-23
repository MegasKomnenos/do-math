---
weight: unit
short: persistence after an early crossing
---
## Description

Let $k \ge 82$ and $1 \le r_q \le k/3$. If $d_{j,k} = b(j,k) - b(j,k-1)$ is nonpositive on the rows $k \le j < k + r_q$ and positive at the row $k + r_q$, then $d_{n,k} > 0$ for every row $k + r_q \le n \le 2k-1$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`), and $d_{j,k} = b(j,k) - b(j,k-1)$. Let $k \ge 82$ and $r_q \ge 1$ be natural numbers with $3\,r_q \le k$. Assume

- $d_{j,k} \le 0$ for every $j$ with $k \le j < k + r_q$, and
- $d_{k+r_q,\,k} > 0$.

Then $d_{n,k} > 0$ for every $n$ with $k + r_q \le n \le 2k-1$.

The Lean statement is written with the normalised step $\delta_j = d_{j,k}/j!$ (`Parking.dq`, as `dq k j`), which has the same sign as $d_{j,k}$.

## Explanation

The row $q = k + r_q$ is the crossing row of the column $k$: the first row at which the column is positive. The statement says that a column which crosses within the first third of its chain range $k+1 \le n \le 2k-1$ never becomes nonpositive again inside that range. Together with the existence of such a crossing (`Parking.crossing_row`) it gives the single crossing of the column (`Parking.single_crossing`).

The proof is an induction along the column: to show $d_{n,k} > 0$ it may use that all rows from $q$ to $n-1$ are positive. Writing $n = k + r$, where $r$ is the offset of the row, it uses one of two arguments, and each covers what the other cannot.

*Near rows, $r \le 0.47k$* (`Parking.caseA`). The two-point argument compares the column equation at the row $n$ with the column equation at the crossing row $q$. It needs no positive rows between $q$ and $n$ beyond the fact that they are positive, so it works from the row $q + 1$ on. It needs the tilted kernel to be nonincreasing and a comparison of the kernel with the source coefficient at the two rows; the library proves this comparison up to the offset $0.47k$, and the estimate behind it does not extend beyond the offset $\frac{\sqrt{19}-2}{5}k = 0.4718\ldots k$ (`Parking.Fk_anti`).

*Far rows, $0.47k < r \le k-1$* (`Parking.caseFar`). The persistence inequality bounds the column at the row $n$ from below by the profile of the level $k-1$, at the price of a loss that is small only when many rows immediately before $n$ are known to be positive. Just after the crossing no such run exists. For $r > 0.47k$ it does, because the crossing is early: the rows $q,\dots,n-1$ are more than $(0.47 - \frac13)k$ in number. This is where the hypothesis $3r_q \le k$ is used. Inside the far rows there is a further division at $r = \frac35k$, where the coefficients of the persistence inequality stop being nonnegative and a bound for a renewal sequence takes over, and at $r = \frac45k$ for numerical reasons; the record of `Parking.caseFar` describes them.

The division at $0.47k$ is dictated by the near rows: it is as far as the two-point argument reaches. The far argument does not need the offset to be large in itself; it needs a long run of positive rows before $n$, and for $r > 0.47k$ the hypothesis $r_q \le k/3$ guarantees a run of more than $\frac{41}{300}k$ rows, which the bookkeeping of `Parking.caseFar` shows to be enough when $k \ge 82$. The upper end, the row $2k-1$, is the end of the chain range, beyond which the column equation `Parking.dq_col` on which both arguments rest is no longer available in this form. The threshold $k \ge 82$ comes from the numerical bookkeeping of the far rows; the near rows need only $k \ge 42$. For the columns $k \le 81$ the corresponding statement is read from a table (`Parking.Tab.small_table`).

The hypothesis on the rows $k \le j < q$ is used only by the near rows. It includes the bottom row $j = k$, where $d_{k,k} < 0$ holds for every $k \ge 2$ (`Parking.dq_base`: $d_{k,k}/k! = -a_k/k$ with $a_k = k^{k-1}/k!$).

## Proof

By strong induction on $n$. Let $k + r_q \le n \le 2k-1$ and suppose the claim holds for all smaller rows in the range.

If $n = k + r_q$, the claim is the second assumption.

Otherwise write $n = k + r_q + t$ with $t \ge 1$. By the induction hypothesis $d_{j,k} > 0$ for all $j$ with $k + r_q \le j < n$. Put $r = r_q + t$; from $n \le 2k-1$, $r \le k-1$.

- If $100\,r > 47\,k$, apply `Parking.caseFar` with this $r$ and $r_q$: its hypotheses are $k \ge 82$, $47k < 100r$, $r + 1 \le k$, $3r_q \le k$ and the positivity on the rows $k + r_q \le j < k + r$. It gives $d_{k+r,k} > 0$.
- If $100\,r \le 47\,k$, apply `Parking.caseA` with $r_q$ and $t$: its hypotheses are $k \ge 42$, $r_q \ge 1$, $t \ge 1$, $100(r_q + t) \le 47k$, the first assumption, and the positivity on the rows $k + r_q \le j < k + r_q + t$. It gives $d_{k+r_q+t,k} > 0$.

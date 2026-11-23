---
weight: unit
short: single crossing of a column k ≥ 82 in its chain range
---
## Description

Every column $k \ge 82$ has a row $q$ with $k+1 \le q \le k + 0.27k$ such that $b(j,k) \le b(j,k-1)$ for $k \le j < q$ and $b(n,k-1) < b(n,k)$ for $q \le n \le 2k-1$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`), and $d_{n,k} = b(n,k) - b(n,k-1)$. For every natural number $k \ge 82$ there is a natural number $q$ such that

- $k + 1 \le q$ and $100\,(q-k) \le 27\,k$;
- $d_{j,k} \le 0$ for every $j$ with $k \le j < q$;
- $d_{n,k} > 0$ for every $n$ with $q \le n \le 2k-1$.

The Lean statement is written with the normalised step $\delta_n = d_{n,k}/n!$ (`Parking.dq`), which has the same sign.

## Explanation

Read along the column $k$, from the row $k$ to the row $2k-1$, the step $d_{n,k}$ changes its sign exactly once, from nonpositive to positive, and the change happens within the first $0.27k$ rows. The row $q$ is the crossing row of the column.

The statement is used in two places. Inside this part it gives the persistence of the sign in the chain range for the columns $k \ge 82$ (`Parking.chain_column`). In the left half of the argument, `Parking.big_columns` starts from it to show that a column $k \ge 82$ remains positive on all rows $n \ge 2k$; there the bound $q \le k + 0.27k$ on the crossing row is used as well, to compare the weights of the nonpositive and the positive rows.

The range of rows ends at $2k-1$ because that is where the persistence statement `Parking.persist` ends.

## Proof

By `Parking.crossing_row` there is $r \ge 1$ with $100\,r \le 27\,k$ and $d_{k+r,k} > 0$. So the set of rows $j \ge k+1$ with $d_{j,k} > 0$ is nonempty; let $q$ be its least element. Then $k + 1 \le q \le k + r$, hence $100\,(q-k) \le 27\,k$, and $d_{q,k} > 0$.

For $k \le j < q$ we have $d_{j,k} \le 0$: at $j = k$ because $\delta_k = -a_k/k \le 0$ with $a_k = k^{k-1}/k!$ (`Parking.dq_base`), and for $k + 1 \le j < q$ because $q$ is the least positive row.

Put $r_q = q - k$. Then $r_q \ge 1$ and $3\,r_q \le k$, since $100\,r_q \le 27\,k$. The hypotheses of `Parking.persist` are satisfied, and it gives $d_{n,k} > 0$ for $q \le n \le 2k-1$.

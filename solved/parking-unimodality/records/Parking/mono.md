---
weight: unit
short: the next column
---
## Description

For $k \ge 9$ and $n \ge k + 2$: if column $k$ has no positive step in the rows $k+1, \dots, n$, that is, $b(j,k) \le b(j,k-1)$ for $k + 1 \le j \le n$, then column $k + 1$ has no positive step in the row $n$: $b(n,k+1) \le b(n,k)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k \ge 9$ and $n \ge k + 2$ be natural numbers. If $b(j,k) \le b(j,k-1)$ for every $j$ with $k + 1 \le j \le n$, then $b(n,k+1) \le b(n,k)$.

With the steps $d_{n,k} = b(n,k) - b(n,k-1)$: if $d_{j,k} \le 0$ for all $k + 1 \le j \le n$, then $d_{n,k+1} \le 0$.

## Explanation

In words: as long as column $k$ has not turned positive, column $k + 1$ has not turned positive either. Together with the persistence of the sign in the chain range this gives the right half of the unimodality. In `Parking.right_tail` a nonpositive step of a column $i \ge 9$ in a row $n \le 2i - 1$ is first spread to all the rows $i + 1 \le m \le n$ of that column by `Parking.chain_column_iter`, and the present statement then passes it from each column to the next, so that every step to the right of $i$ in the row $n$ is nonpositive.

The two ranges of columns are handled by different means. For $k \ge 265$ the statement is `Parking.mono265`, proved through the criterion function, and there the conclusion is strict. For $9 \le k \le 264$ it rests on a table of two signs per column, checked by exact computation (`Parking.Tab.two_signs`), and on the persistence in the chain range of column $k + 1$; this argument yields the non-strict conclusion only. The lower bound $k \ge 9$ is the range of the table.

## Proof

**Columns $9 \le k \le 264$.** `Parking.Tab.two_signs` provides a number $z = z(k)$ with $z + 2 \le k$ such that column $k$ is positive in the row $k + z + 1$, $b(k+z+1,k-1) < b(k+z+1,k)$, and column $k + 1$ is negative in the row $k + z$, $b(k+z,k+1) < b(k+z,k)$. If $n \ge k + z + 1$, the hypothesis at the row $k + z + 1$ would contradict the first sign; hence $n \le k + z$. Suppose now that $b(n,k) < b(n,k+1)$. The rows $n, \dots, k + z$ lie in the chain range of column $k + 1$: $n \ge (k+1) + 1$ and $k + z \le 2(k+1) - 1$, because $z \le k - 2$. By `Parking.chain_column_iter`, a column that is positive in a row of its chain range is positive in all later rows of that range, so $b(k+z,k) < b(k+z,k+1)$, against the second sign. Hence $b(n,k+1) \le b(n,k)$.

**Columns $k \ge 265$.** `Parking.mono265` gives $b(n,k+1) < b(n,k)$ under the same hypotheses.

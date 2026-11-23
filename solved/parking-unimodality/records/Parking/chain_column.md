---
weight: unit
short: persistence of the sign along a column in the chain range
---
## Description

For $k \ge 2$ and $k + 1 \le n \le 2k-2$: if $b(n,k-1) < b(n,k)$, then $b(n+1,k-1) < b(n+1,k)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k \ge 2$ and $n$ be natural numbers with $k + 1 \le n \le 2k-2$. If $b(n,k-1) < b(n,k)$, then $b(n+1,k-1) < b(n+1,k)$.

## Explanation

Write $d_{n,k} = b(n,k) - b(n,k-1)$ for the step of the row $n$ between the columns $k-1$ and $k$. The statement says that along a column, once the step is positive in a row of the chain range $k+1 \le n \le 2k-1$, it is positive in the next row of that range. Iterated, it gives `Parking.chain_column_iter`, which is the form the rest of the library uses: a nonpositive step $d_{n,k} \le 0$ at a row of the chain range forces $d_{m,k} \le 0$ at all earlier rows $k+1 \le m \le n$.

The chain range is the range of rows in which the step of the column $k$ satisfies the column equation `Parking.dq_col`, a linear recursion along the column with a positive source and a feedback through the prime kernel. Persistence is not a formal consequence of that recursion, because the rows before the crossing contribute a negative feedback for a long time; the content of the statement is that the source always wins.

The proof treats the columns in two groups. For $2 \le k \le 81$ the statement is one of the facts established by an exact computation of the columns up to $81$ (`Parking.Tab.small_table`). For $k \ge 82$ it follows from the single crossing of the column (`Parking.single_crossing`), which rests on an early positive row and on the persistence arguments `Parking.caseA` and `Parking.caseFar`; these close numerically only from $k = 82$ on, which is why the table goes up to $81$.

The Lean statement is about the counts $b$ themselves; the proof passes to the normalised step $\delta_n = d_{n,k}/n!$ (`Parking.dq`) by `Parking.dq_pos_iff`. The bound $n \le 2k-2$ is written with truncated subtraction, which is the ordinary one since $k \ge 2$.

## Proof

*Columns $k \le 81$.* The second assertion of `Parking.Tab.small_table` is exactly the claim: for $2 \le k \le 81$ and $k+1 \le n \le 2k-2$, $b(n,k-1) < b(n,k)$ implies $b(n+1,k-1) < b(n+1,k)$.

*Columns $k \ge 82$.* By `Parking.single_crossing` there is a row $q$ such that $d_{j,k} \le 0$ for $k \le j < q$ and $d_{m,k} > 0$ for $q \le m \le 2k-1$. Since $d_{n,k} > 0$ by assumption and $n \ge k$, the row $n$ cannot lie below $q$; hence $q \le n$. Then $q \le n + 1 \le 2k-1$, so $d_{n+1,k} > 0$.

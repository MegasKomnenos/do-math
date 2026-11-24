---
weight: unit
short: the forty-five negative cells of the columns 2 to 9
---
## Description

Forty-five computed negative steps in the columns $2\le k\le9$: $b(n,k)<b(n,k-1)$ in every row $n\ge k+1$ with $n\le2k+1$ when $k\le5$, with $n\le2k$ when $k\le7$, with $n\le2k-1$ when $k\le8$, and with $n\le2k-2$ when $k\le9$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k\ge2$ and $n\ge k+1$ be natural numbers such that one of the following holds:

- $n\le2k+1$ and $k\le5$;
- $n\le2k$ and $k\le7$;
- $n\le2k-1$ and $k\le8$;
- $n\le2k-2$ and $k\le9$.

Then $b(n,k)<b(n,k-1)$.

In a given column the four conditions together admit the rows from $k+1$ up to a last row, which is $2k+1$ for $2\le k\le5$, $2k$ for $k=6,7$, $2k-1$ for $k=8$, and $2k-2$ for $k=9$. The positions $(n,k)$ concerned are therefore the forty-five positions of the following table.

| column $k$ | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| rows $n$ | 3–5 | 4–7 | 5–9 | 6–11 | 7–12 | 8–14 | 9–15 | 10–16 |
| number of rows | 3 | 4 | 5 | 6 | 6 | 7 | 7 | 7 |

## Explanation

**Where the cells lie.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The first layer of the column $k$ consists of the rows $k+1\le n\le2k-1$. The statement says that each column $2\le k\le8$ is negative in every row of its first layer, and that beyond the first layer it is still negative in the row $2k$ for $k\le7$ and in the row $2k+1$ for $k\le5$. In terms of the row $\operatorname{lo}(k)$, which is $2k+2$ for $k\le5$, $2k+1$ for $k=6,7$ and $2k$ for $k=8$, the cells of a column $k\le8$ are the rows $k+1\le n<\operatorname{lo}(k)$. The junction table `Parking.Tab.junction_table` continues each of these columns: the step is positive in the rows $\operatorname{lo}(k)\le n<n_0(k)$, up to the row $n_0(k)$ listed for the column (`Parking.Tab.n0`), and `Parking.step_pos_beyond` shows that it is positive in all later rows as well. So for $2\le k\le8$ the row $\operatorname{lo}(k)$ is the first row in which the column is positive. Ten of the cells, those in the rows $2k$ and $2k+1$, are exactly the positions that the junction table excepts.

For the column $9$ the statement gives the rows $10\le n\le16$. These are the first layer of that column without its last row $17$, and in the row $17$ the column $9$ is positive: the number listed for the column $9$ is $7$ (`Parking.Tab.ztab`), and the table of two signs `Parking.Tab.two_signs` shows that the column is positive in the row $9+7+1$.

**What the cells are used for.** The staircase theorem (`Parking.staircase`) is derived from two rules. The column rule says that a positive step stays positive one row down in the same column, and the diagonal rule says that a step that is not positive is followed by a negative step one row down and one column to the right. Three statements from which the rules are assembled take negative signs from the cells.

- Beyond the first layer the step of a column is positive except at eleven positions (`Parking.step_pos_beyond`). The column rule beyond the first layer (`Parking.column_rule_beyond`) has to exclude that its hypothesis, a positive step at $(n,k)$, holds when $(n+1,k)$ is one of the eleven positions. It uses the cells $(2k-1,k)$ for $2\le k\le7$ and $(2k,k)$ for $2\le k\le5$.
- The diagonal rule beyond the first layer (`Parking.diagonal_rule_beyond`) needs a negative step at the position one row down and one column to the right of each of the eleven positions. It uses the cells $(2k-1,k)$ for $2\le k\le8$ and $(2k,k)$ for $3\le k\le6$.
- The diagonal rule in the first layer of the columns $2\le k\le8$ (`Parking.diagonal_rule_small`) needs, for every row $n$ of the first layer $k+1\le n\le2k-1$ of the column $k$, a negative step at the position $(n+1,k+1)$. With $c=k+1$ these are the cells in the rows $c+1\le n\le2c-2$ of the columns $3\le c\le9$, which number $1+2+\dots+7=28$. For the columns $k\ge9$ the corresponding table, `Parking.Tab.next_column_neg`, reaches only to a row in which the column $k$ is positive, because a positive step of the first layer persists in the later rows of the layer. A column $k\le8$ has no such row: it is negative in its whole first layer, so the hypothesis of the diagonal rule holds in every row of the layer, and the sign of the column $k+1$ is needed in all the rows $k+2,\dots,2k$. This use is the reason why the column $9$ belongs to the statement, and why its cells end at the row $16=2\cdot8$.

These are forty different cells. The other five, $(5,2)$, $(7,3)$, $(9,4)$, $(11,5)$ and $(14,7)$, are used by no proof of the library. With them the statement gives the sign at every position that the junction table excepts.

**Why they are computed.** The cells lie in the rows $3$ to $16$. The numbers involved are small, and the signs are read from their exact values. For instance, at the position $(3,2)$ the values are $b(3,1)=7$ and $b(3,2)=3$, from $A(3,0)=6$, $A(3,1)=13$, $A(3,2)=16$, where $A(n,l)$ is the number of parking functions of length $n$ with maximum displacement at most $l$.

**The Lean form.** The first row of a column is the hypothesis `k + 1 ≤ n`. The condition on the last row is the disjunction `n ≤ 2 * k + 1 ∧ k ≤ 5 ∨ n ≤ 2 * k ∧ k ≤ 7 ∨ n + 1 ≤ 2 * k ∧ k ≤ 8 ∨ n + 2 ≤ 2 * k ∧ k ≤ 9`; the bounds $n\le2k-1$ and $n\le2k-2$ are written as $n+1\le2k$ and $n+2\le2k$ to avoid a subtraction of natural numbers. The four alternatives overlap: a column $k$ that meets the condition on $k$ of one alternative meets that of every alternative after it, and the rows admitted in a column are those up to the largest row that one of its alternatives allows. The sign is the comparison `b n k < b n (k - 1)`.

## Proof

The statement is established by an exact computation, which the kernel of the proof assistant performs, and by a proof of what the computation means.

**The numbers computed.** Let $A(n,l)$ be the number of parking functions of length $n$ with maximum displacement at most $l$ (`Parking.A`). The function $\operatorname{hd}(l,n)$ of `Parking.Tab.hd` produces a natural number by running the last-car recursion $x_0=1$, $x_{m+1}=\sum_{j=0}^{m}\min(j+1,l+1)\binom mj x_jx_{m-j}$ for the level $l$ up to the row $n$, in exact arithmetic of natural numbers, and $\operatorname{hd}(l,n)=A(n,l)$ by `Parking.Tab.hd_eq`.

**One cell.** For a column $k\ge2$ and a row $n$ the cell is the truth value of the comparison
$$A(n,k)+A(n,k-2)+1\ \le\ 2\,A(n,k-1),$$
formed from the computed numbers $\operatorname{hd}(k,n)$, $\operatorname{hd}(k-2,n)$, $\operatorname{hd}(k-1,n)$. By `Parking.d_eq_A`, $b(n,k)-b(n,k-1)=A(n,k)-2A(n,k-1)+A(n,k-2)$ as integers for $k\ge2$, so the cell is true exactly when $b(n,k)<b(n,k-1)$.

**The evaluation.** Let $\operatorname{lo}(k)=2k+2$ for $k\le5$, $2k+1$ for $k=6,7$, and $2k$ for $k\ge8$. For a column $k$ the check is the conjunction of the cells of the rows $k+1\le n\le\min(\operatorname{lo}(k),17)-1$. The bound $17$ takes effect in the column $9$ only, where $\operatorname{lo}(9)=18$; so the rows of a column $k\le8$ are $k+1\le n\le\operatorname{lo}(k)-1$ and those of the column $9$ are $10\le n\le16$. These are $3,4,5,6,6,7,7,7$ rows in the columns $k=2,\dots,9$. The kernel reduces the conjunction of the checks of the eight columns $2\le k\le9$ (`Parking.Tab.allRange`) to true, in one evaluation of $45$ cells; the numbers $A(n,l)$ that occur have $n\le16$ and $l\le9$. As in the junction table, the numbers are handed to the kernel through a private auxiliary function that equals $\operatorname{hd}$ by definition and changes nothing in what is evaluated.

**From the value true to the statement.** `Parking.Tab.allRange_sound` gives the value true for the check of each column $2\le k\le9$. Let $k\ge2$ and $n\ge k+1$ satisfy one of the four conditions. Then $k\le9$, and $n<\min(\operatorname{lo}(k),17)$:

- if $n\le2k+1$ and $k\le5$, then $n<2k+2=\operatorname{lo}(k)$ and $n\le11$;
- if $n\le2k$ and $k\le7$, then $n<2k+1\le\operatorname{lo}(k)$ and $n\le14$;
- if $n\le2k-1$ and $k\le8$, then $n<2k\le\operatorname{lo}(k)$ and $n\le15$;
- if $n\le2k-2$ and $k\le9$, then $n<2k\le\operatorname{lo}(k)$ and $n\le16$.

So $(n,k)$ is one of the cells of the column $k$, its value is true by `Parking.Tab.allRange_sound` applied to the rows, and therefore $b(n,k)<b(n,k-1)$.

---
weight: unit
short: the junction table of the columns 2 to 81
---
## Description

The computed signs of the steps in the rows between the first layer and the listed row $n_0(k)$ of each column $2\le k\le81$: $n_0(k)\ge2k+3$, and $b(n,k-1)<b(n,k)$ in every row $2k\le n<n_0(k)$, except in the row $2k$ when $k\le7$ and in the row $2k+1$ when $k\le5$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k$ be an integer with $2\le k\le81$, and let $n_0(k)$ be the row listed for the column $k$ (`Parking.Tab.n0`). Then:

1. $2k+3\le n_0(k)$;
2. for every $n$ with $2k\le n<n_0(k)$, other than $n=2k$ when $k\le7$ and $n=2k+1$ when $k\le5$: $b(n,k-1)<b(n,k)$.

## Explanation

**The junction of a column.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The first layer of the column $k$ consists of the rows $k+1\le n\le2k-1$ (also called the chain range of the column), and the rows $n\ge2k$ lie beyond it. For a column $2\le k\le81$ a row $n_0(k)$ is listed (`Parking.Tab.n0`) from which on the sign of the step is controlled by an argument that reaches all later rows, the propagation. The rows $2k\le n<n_0(k)$, between the first layer and that row, are the *junction* of the column; there are between $3$ and $14$ of them. The statement gives the sign of the step in every row of every junction: it is positive, except at ten positions, $(n,k)=(2k,k)$ for $2\le k\le7$ and $(2k+1,k)$ for $2\le k\le5$. At these ten the step is negative (`Parking.Tab.negative_cells`).

**Why these signs are computed again.** The table of the same columns, `Parking.Tab.small_table`, computes the same numbers and compares them in the junction rows, but with $\le$: its third part states $b(n,k-1)\le b(n,k)$, and only from the row $\max(2k,17)$ on; the proof of the staircase does not use that part. The staircase theorem (`Parking.staircase`) needs the strict inequality, since the two rules from which it is derived conclude with strict inequalities, and the computed $\le$ does not give $<$. So the comparisons are evaluated once more, with $<$ and in all junction rows from $2k$ on.

**Why part 1 is there.** The strict form of the propagation, `Parking.propagate_pos`, starts from a positive step in the row $n_0(k)-1$. That row has to be one of the rows of part 2, so it has to lie beyond the exceptional rows $2k$ and $2k+1$: $n_0(k)-1\ge2k+2$. The table `Parking.Tab.small_table` states only $2k\le n_0(k)$. For $k=2$ the bound is attained, $n_0(2)=7$.

**The count of cells.** Let $\operatorname{lo}(k)$ be the first row from which the junction of the column $k$ is positive: $\operatorname{lo}(k)=2k+2$ for $k\le5$, $2k+1$ for $k=6,7$, and $2k$ for $k\ge8$. Part 2 concerns the rows $\operatorname{lo}(k)\le n<n_0(k)$, and each such position is one cell of the table. There are $\sum_{k=2}^{81}\bigl(n_0(k)-\operatorname{lo}(k)\bigr)=933$ cells, $26$ in the columns $2$ to $8$ and $907$ in the columns $9$ to $81$, in the rows from $6$ to $174$.

**What it is used for.** `Parking.step_pos_beyond` uses both parts: part 2 for the rows below $n_0(k)$, and part 1 with the cell of the row $n_0(k)-1$ to start the propagation that covers the rows from $n_0(k)$ on.

**The Lean form.** The sign is a comparison of natural numbers, `b n (k - 1) < b n k`, where `k - 1` is exact because $k\ge2$. The two exceptions are a hypothesis: the row $n$ must satisfy `¬(n = 2 * k ∧ k ≤ 7 ∨ n = 2 * k + 1 ∧ k ≤ 5)`. The function $\operatorname{lo}$ is a private definition of the module; the statement does not mention it.

## Proof

The statement is established by an exact computation, which the kernel of the proof assistant performs, and by a proof of what the computation means.

**The numbers computed.** Let $A(n,l)$ be the number of parking functions of length $n$ with maximum displacement at most $l$ (`Parking.A`). The computation uses the function $\operatorname{hd}(l,n)$ of `Parking.Tab.hd`, which produces a natural number by running the last-car recursion for the level $l$ from the row $0$ up to the row $n$:
$$x_0=1,\qquad x_{m+1}=\sum_{j=0}^{m}\min(j+1,l+1)\binom mj\,x_j\,x_{m-j},\qquad\operatorname{hd}(l,n)=x_n ,$$
the binomial coefficients being carried along as a running product with an exact division. By `Parking.Tab.hd_eq`, $\operatorname{hd}(l,n)=A(n,l)$. All arithmetic is that of natural numbers of arbitrary size and is exact. (As an indication of the sizes, from a computation made for this record outside the library: the largest number that occurs, $A(174,81)$, has $387$ decimal digits.)

**One cell.** For a column $k\ge2$ and a row $n$, the cell $(n,k)$ is the truth value of the comparison
$$2\,A(n,k-1)+1\ \le\ A(n,k)+A(n,k-2),$$
formed from the three computed numbers $\operatorname{hd}(k-1,n)$, $\operatorname{hd}(k,n)$, $\operatorname{hd}(k-2,n)$. By `Parking.d_eq_A`, for $k\ge2$,
$$b(n,k)-b(n,k-1)=A(n,k)-2A(n,k-1)+A(n,k-2)$$
as integers. So the cell is true exactly when $d_{n,k}>0$, that is, when $b(n,k-1)<b(n,k)$.

**The check of a column.** For a column $k$ the computation forms the conjunction of the comparison $2k+3\le n_0(k)$, with $n_0(k)$ read from the list `Parking.Tab.n0tab`, and of the cells $(n,k)$ for all rows $n$ with $\operatorname{lo}(k)\le n\le n_0(k)-1$. If this value is true, then $2k+3\le n_0(k)$ and $b(n,k-1)<b(n,k)$ for every such row.

**The evaluation.** The eighty columns, with their $933$ cells and the eighty comparisons $2k+3\le n_0(k)$, are evaluated in four blocks of consecutive columns: $2$–$55$ ($572$ cells, rows up to $123$), $56$–$66$ ($154$ cells, rows up to $145$), $67$–$74$ ($112$ cells, rows up to $161$) and $75$–$81$ ($95$ cells, rows up to $174$). For each block the kernel reduces the conjunction of the checks of its columns (`Parking.Tab.allRange`) to true. No compiled code and no external program is involved: the definitions are part of the Lean source, and the evaluation is a step of the type checking of that source.

Neighbouring cells need the same numbers: the cells $(n,k)$ and $(n,k+1)$ both need $A(n,k)$ and $A(n,k-1)$, so that the $933$ cells ask for $2{,}799$ values of which $1{,}341$ are different, a number $A(n,l)$ being counted once for each block in which it occurs. The module reads each number through a private auxiliary function that hands $\operatorname{hd}(l,n)$ to the kernel in one fixed form wherever it occurs, so that the kernel can take a value it has already computed in the same evaluation. This changes nothing in what is evaluated: the auxiliary function equals $\operatorname{hd}(l,n)$ by definition, and the meaning of a cell is as stated above. It is the reason why the blocks are large; their boundaries have no mathematical meaning.

**From the value true to the statement.** `Parking.Tab.allRange_sound` gives the value true for the check of each column of a block, and `Parking.Tab.glue` joins the four ranges to $2\le k<82$. Let $2\le k\le81$. The first conjunct of the check of the column $k$ is part 1. For part 2, let $2k\le n<n_0(k)$ and suppose that $n$ is not one of the excepted rows. Then $n\ge\operatorname{lo}(k)$: for $k\le5$ because $n\ne2k$ and $n\ne2k+1$, for $k=6,7$ because $n\ne2k$, and for $k\ge8$ because $n\ge2k$. So $(n,k)$ is one of the cells of the column, its value is true by `Parking.Tab.allRange_sound` applied to the rows, and therefore $b(n,k-1)<b(n,k)$.

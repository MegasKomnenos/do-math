---
weight: unit
short: the left half of a row n ≥ 17 is nondecreasing
---
## Description

For $n\ge 17$ and $k\ge 1$ with $2k\le n$: $b(n,k-1)\le b(n,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $n$ and $k$ be natural numbers with $n\ge 17$, $k\ge 1$ and $2k\le n$. Then $b(n,k-1)\le b(n,k)$.

## Explanation

In a row $n\ge 17$ the sequence $b(n,0),b(n,1),\dots$ does not decrease up to the index $\lfloor n/2\rfloor$. In the proof of unimodality (`Parking.root_unimodal`, through `Parking.no_descent_ascent`) this excludes a strict descent at any index $i$ with $2i\le n$; a strict descent at an index $i$ with $n\le 2i-1$ is shown there to be followed by no ascent. The rows $n\le 16$ are checked directly (`Parking.Tab.small_rows`), which is why the statement starts at $17$.

The condition $2k\le n$ describes the region in which the statement is proved, column by column: in the column $k$ the rows $n\ge 2k$ are those beyond the chain range $k+1\le n\le 2k-1$ of the column. The proof is a division into three ranges of columns, each with its own method: the column $1$ by a direct comparison of two recursions, the columns $2$ to $81$ by a table and the propagation theorem, and the columns from $82$ on by the weighted argument on the kernel of the column equation, which needs no table beyond the position of the crossing row.

## Proof

If $k=1$: `Parking.column_one`, applicable since $n\ge 3$. If $2\le k\le 81$: `Parking.small_columns`, whose hypotheses $2k\le n$ and $17\le n$ are given. If $k\ge 82$: `Parking.big_columns` gives the strict inequality $b(n,k-1)<b(n,k)$ for $n\ge 2k$.

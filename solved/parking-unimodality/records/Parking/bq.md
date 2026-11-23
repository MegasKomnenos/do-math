---
weight: unit
short: normalised count of a column
---
## Description

The normalised count $\beta^{(k)}_n=b(n,k)/n!$: the number of parking functions of length $n$ with maximum displacement exactly $k$, divided by $n!$.

## Statement

For natural numbers $k$ and $n$,
$$\beta^{(k)}_n=\frac{b(n,k)}{n!},$$
a real number, where $b(n,k)$ (`Parking.b`) is the number of parking functions of length $n$ whose maximum displacement is exactly $k$.

## Explanation

For a fixed $k$ the sequence $n\mapsto\beta^{(k)}_n$ is the *column* $k$ of the array $b(n,k)$, normalised row by row; the main theorem concerns the rows of this array, and the proof studies it column by column. The division by $n!$ is the one of `Parking.zr`, and for $k\ge1$ the column is the difference of two neighbouring environments, $\beta^{(k)}_n=z^{(k+1)}_n-z^{(k)}_n$ (`Parking.bq_eq`). The column vanishes for $n\le k$ when $k\ge1$ (`Parking.bq_eq_zero`), and in the rows $k+1\le n\le2k+1$ it satisfies the linear equation `Parking.bq_L0`. The difference of two neighbouring columns in the same row is the normalised step `Parking.dq`.

In Lean, `bq k n` is the quotient of the casts of `b n k` and `n.factorial` to the real numbers; note the order of the arguments, column first.

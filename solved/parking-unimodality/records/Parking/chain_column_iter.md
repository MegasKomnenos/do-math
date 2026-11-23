---
weight: unit
short: persistence of the sign in the chain range, iterated
---
## Description

For $k \ge 2$ and $k + 1 \le m \le n \le 2k-1$: if $b(m,k-1) < b(m,k)$, then $b(n,k-1) < b(n,k)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k \ge 2$, $m$ and $n$ be natural numbers with $k + 1 \le m \le n \le 2k-1$. If $b(m,k-1) < b(m,k)$, then $b(n,k-1) < b(n,k)$.

## Explanation

This is `Parking.chain_column` applied repeatedly: a column that is positive in one row of its chain range $k+1 \le n \le 2k-1$ is positive in all later rows of that range. It is the form in which the persistence of the sign leaves this part of the library, and it is used in contrapositive form: if $b(n,k) \le b(n,k-1)$ at a row $n \le 2k-1$, then $b(m,k) \le b(m,k-1)$ at every row $k+1 \le m \le n$.

Two results use it. In `Parking.mono`, a positive step of the column $k+1$ at a row would persist up to a row at which the table of two signs shows a negative step, a contradiction. In `Parking.right_tail`, a nonpositive step of a column at the row $n$ is carried back to all earlier rows of the chain range, which starts the induction over the columns to the right.

## Proof

By induction on $n$ from $n = m$, where the claim is the assumption. If the claim holds for some $n$ with $m \le n$ and $n + 1 \le 2k-1$, then $k + 1 \le n \le 2k-2$ and $b(n,k-1) < b(n,k)$, so `Parking.chain_column` gives $b(n+1,k-1) < b(n+1,k)$.

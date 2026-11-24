---
weight: step
short: the tilted cell as a tilted count
---
## Description

For a column $k \ge 2$ the tilted cell is the tilted normalised count of the level $k-1$: $U_N = \beta^{(k-1)}_N x^N$ with $\beta^{(k-1)}_N = b(N,k-1)/N!$.

## Statement

For every natural number $k \ge 2$, every real number $x$ and every natural number $N$,
$$z^{(k)}_N\, x^N - z^{(k-1)}_N\, x^N \;=\; \beta^{(k-1)}_N\, x^N ,$$
where the left-hand side is the tilted cell $U_N$ of the column $k$ (`Parking.Ut`; $z^{(y)}_N = A(N,y-1)/N!$) and $\beta^{(k-1)}_N = b(N,k-1)/N!$ (`Parking.bq`), with $b(n,\ell)$ the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$.

## Explanation

The identity translates between the two ways of writing the same quantity: the argument for the rows $n\ge2k$ of the columns $k\ge82$ (`Parking.step_pos_large`) computes with tilted environments, and its conclusions are about the counts $b(n,\ell)$.

## Proof

By `Parking.bq_eq` applied to the level $k-1 \ge 1$, $\beta^{(k-1)}_N = z^{(k)}_N - z^{(k-1)}_N$; this is $b(N,k-1) = A(N,k-1) - A(N,k-2)$ divided by $N!$. Multiply by $x^N$.

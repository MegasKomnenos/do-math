---
weight: unit
short: environment of a threshold
---
## Description

The normalised cumulative count $z^{(y)}_n=A(n,y-1)/n!$: the number of parking functions of length $n$ all of whose displacements are smaller than the threshold $y$, divided by $n!$.

## Statement

For natural numbers $y\ge1$ and $n$,
$$z^{(y)}_n=\frac{A(n,y-1)}{n!},$$
a real number, where $A(n,k)$ (`Parking.A`) is the number of parking functions of length $n$ with maximum displacement at most $k$. The Lean definition `zr y n` is also defined for $y=0$, where the subtraction of natural numbers gives $y-1=0$, so that $z^{(0)}_n=z^{(1)}_n$.

## Explanation

**Why the count is normalised.** The last-car recursion `Parking.A_succ` contains the binomial coefficient $\binom nj$. Dividing by $n!$ removes it: $z^{(y)}$ satisfies $(n+1)z^{(y)}_{n+1}=\sum_{j\le n}\min(j+1,y)z^{(y)}_jz^{(y)}_{n-j}$ (`Parking.zr_isWSol`), a recursion with real coefficients that can be written as a differential equation of the generating series $\sum_nz^{(y)}_nX^n$ and compared with the sequence $c_n=(n+1)^{n-1}/n!$ (`Parking.cc`), which satisfies the same recursion without the minimum. All later analytic arguments work with these real numbers. The counts are recovered by multiplying by $n!$, and inequalities between counts of the same length $n$ are equivalent to the inequalities between the normalised quantities.

**Why the threshold is $y=k+1$.** The index is the number $y$ such that all displacements are *smaller than* $y$, not the bound $k=y-1$ on the maximum displacement. With this choice the weight of the recursion is $\min(t,y)$ and the free range, in which $z^{(y)}_n=c_n$, is $n\le y$ (`Parking.zr_eq_cc`). The quantities of one column $k$ involve the three thresholds $k+1$, $k$, $k-1$: $b(n,k)/n!=z^{(k+1)}_n-z^{(k)}_n$ (`Parking.bq_eq`).

**Name and reading.** The other parts call the sequence $z^{(y)}$ the *environment* of the threshold $y$. Since $c_n\,n!=(n+1)^{n-1}$ is the number of all parking functions of length $n$ (the classical count: the library proves $A(n,k)=(n+1)^{n-1}$ for $k\ge n-1$, `Parking.A_eq_pow`, and this is the number of all parking functions because no displacement exceeds $n-1$, a fact that the library does not state), the ratio $z^{(y)}_n/c_n$ is the probability that a uniformly chosen parking function of length $n$ has maximum displacement smaller than $y$ (see `Parking.zr_diag_mono`).

**The Lean form.** `zr y n` is the quotient of the casts of `A n (y - 1)` and `n.factorial` to the real numbers. The value at $y=0$ is an artefact of the truncated subtraction; the statements in which the threshold matters assume $y\ge1$, and `Parking.zr_nonneg` and `Parking.zr_mono` hold for $y=0$ as well.

---
weight: step
short: the environment at length zero
---
## Description

For a threshold $y \ge 1$, $z^{(y)}_0 = 1$, where $z^{(y)}_n = A(n,y-1)/n!$.

## Statement

For every natural number $y \ge 1$, $z^{(y)}_0 = 1$. Here $z^{(y)}_n = A(n,y-1)/n!$ (`Parking.zr`), with $A(n,k)$ the number of parking functions of length $n$ whose maximum displacement is at most $k$.

## Explanation

The statement says that the empty parking function is counted once. It makes the constant term of the series $Z_y$ (`Parking.Zs`) equal to $1$, which is what allows the inverse $1/Z_y$ and the prime kernel series $K_y = 1 - 1/Z_y$ (`Parking.Ks`) to be formed. The hypothesis $y \ge 1$ is the one under which `Parking.zr_isWSol` is stated; the value itself does not depend on it.

## Proof

By `Parking.zr_isWSol`, for $y \ge 1$ the sequence $z^{(y)}$ solves the weighted last-car recursion with the weight $\min(t,y)$, and the first condition in the definition of a solution (`Parking.IsWSol`) is $z^{(y)}_0 = 1$.

---
weight: unit
short: the tilted Cayley masses do not decrease from the critical index on
---
## Description

At the critical tilt $x_k$, $k \ge 1$, the tilted Cayley masses do not decrease from the index $k-1$ on: $c_n x_k^n \le c_{n+1} x_k^{n+1}$ whenever $n + 1 \ge k$.

## Statement

For all natural numbers $k \ge 1$ and $n$ with $k \le n + 1$,
$$c_n\, x_k^{\,n} \;\le\; c_{n+1}\, x_k^{\,n+1} ,$$
where $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`, tilted: `Parking.ccT`) and $x_k = (k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`).

## Explanation

Together with `Parking.ccT_succ_le` this locates the minimum of the tilted Cayley masses at the critical tilt: they do not increase up to the index $k$, do not decrease from the index $k-1$ on, and the two statements overlap in $c_{k-1} x_k^{k-1} = c_k x_k^k$. Beyond the index $k$ the unrestricted masses grow again, while the tilted environment of the threshold $k$, which agrees with them up to $k$, does not (`Parking.zrT_anti_crit`); the threshold is what prevents the growth. In the argument for the rows $n\ge2k$ of the columns $k\ge82$ the statement is combined with the stochastic monotonicity `Parking.zr_diag_mono` to show that, at the critical tilt, the tilted environment does not decrease along a diagonal step from (threshold $y$, length $n$) to (threshold $y+1$, length $n+1$) when $n + 1 \ge k$; this enters the proofs of `Parking.DeltaId_nonneg` and `Parking.weighted_debt`.

## Proof

By `Parking.ccT_succ`, $c_{n+1} x_k^{n+1} = x_k\,(1+1/(n+1))^{n}\, c_n x_k^n$, and $c_n x_k^n > 0$ (`Parking.ccT_pos`, `Parking.xcrit_pos`). It suffices that the factor $x_k (1+1/(n+1))^n$ is at least $1$. Since $(1+1/i)^{i-1}$ is nondecreasing in $i \ge 1$ (`Parking.psi_mono`) and $k \le n+1$, $(1+1/k)^{k-1} \le (1+1/(n+1))^{n}$; multiplying by $x_k > 0$ and using $x_k (1+1/k)^{k-1} = 1$ (`Parking.xcrit_mul_psi`) gives $1 \le x_k (1+1/(n+1))^n$.

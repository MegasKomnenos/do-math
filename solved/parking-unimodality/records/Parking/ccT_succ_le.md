---
weight: unit
short: the tilted Cayley masses do not increase up to the critical index
---
## Description

At the critical tilt $x_k$ the tilted Cayley masses do not increase up to the index $k$: $c_{n+1} x_k^{n+1} \le c_n x_k^n$ whenever $n + 1 \le k$.

## Statement

For all natural numbers $k$ and $n$ with $n + 1 \le k$,
$$c_{n+1}\, x_k^{\,n+1} \;\le\; c_n\, x_k^{\,n} ,$$
where $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`, tilted: `Parking.ccT`) and $x_k = (k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`).

## Explanation

On the free range $N \le k$ the tilted environment of the threshold $k$ is $c_N x^N$ (`Parking.zrT_eq_ccT`). The statement says that at the critical tilt this explicit beginning of the environment is nonincreasing, with equality in the last step $n + 1 = k$. It is the first of the two hypotheses from which the monotonicity of the whole tilted environment is derived (`Parking.zrT_anti_crit`). It also gives the monotonicity of the tilted tree numbers used in `Parking.epsT_succ_le`, and it is used in the first-layer analysis of the left half. The companion statement for indices beyond $k-1$ is `Parking.ccT_le_succ`.

## Proof

By `Parking.ccT_succ`, $c_{n+1} x_k^{n+1} = x_k\,(1+1/(n+1))^{n}\, c_n x_k^n$, and $c_n x_k^n > 0$ (`Parking.ccT_pos`, `Parking.xcrit_pos`). It therefore suffices that the factor $x_k (1+1/(n+1))^n$ is at most $1$. The expression $(1+1/i)^{i-1}$ is nondecreasing in $i \ge 1$ (`Parking.psi_mono`); with $i = n+1 \le k$ this gives $(1+1/(n+1))^{n} \le (1+1/k)^{k-1}$, and $x_k (1+1/k)^{k-1} = 1$ by `Parking.xcrit_mul_psi`.

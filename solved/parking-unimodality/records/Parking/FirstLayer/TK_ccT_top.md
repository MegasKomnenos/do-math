---
weight: unit
short: property K of the Cayley masses at the top
---
## Description

At the critical tilt of a column $k\ge 3$, the triple $(\omega_{k-1},\omega_k,\omega_{k+1})$ of tilted Cayley masses $\omega_n=c_nx_k^{\,n}$ has property K at $k$.

## Statement

Let $k\ge 3$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $\omega_n=c_nx_k^{\,n}$, $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). Then the triple $(\omega_{k-1},\omega_k,\omega_{k+1})$ has property K at $k$ (`Parking.FirstLayer.TK`): for every real $\mu\ge 0$,
$$2\,e^{\mu/k}\,\omega_k\le e^{\mu}\,\omega_{k+1}+e^{-\mu}\,\omega_{k-1}.$$

## Explanation

For a size $N\le y$ every parking function of length $N$ has all displacements below $y$, so the tilted mass $z^{(y)}_Nx_k^{\,N}$ of the threshold $y$ is $\omega_N$. The triple of the statement is therefore the diagonal triple $\big(z^{(k-1)}_{k-1}x_k^{\,k-1},\,z^{(k)}_kx_k^{\,k},\,z^{(k+1)}_{k+1}x_k^{\,k+1}\big)$ of excess $0$, and the statement is the base case of the induction on the excess in `Parking.FirstLayer.kernel_TK`.

It complements `Parking.FirstLayer.ccT_tilt_mid`, which gives the same inequality for the triples $(\omega_j,\omega_{j+1},\omega_{j+2})$ with $j+2\le k$. At the top the argument is different, because the lower ratio $\omega_{k-1}/\omega_k$ is exactly $1$; the inequality holds with a positive surplus, which `Parking.FirstLayer.ccT_tilt_top` records. The proof needs $k\ge 3$: the lower bound of that record contains the factor $k^2-2k-1$, which is negative for $k=2$.

## Proof

`Parking.FirstLayer.ccT_tilt_top` gives, for every real $\mu$,
$$e^{\mu}\omega_{k+1}+e^{-\mu}\omega_{k-1}-2e^{\mu/k}\omega_k\ \ge\ \omega_k\,e^{\mu/k}\cdot\frac1k\cdot\frac{k^2-2k-1}{2k(k+1)(k+2)} .$$
The right side is nonnegative: $\omega_k>0$, and $k^2-2k-1\ge 0$ for $k\ge 3$.

---
weight: step
short: the Cayley masses do not increase up to the index k
---
## Description

At the critical tilt $x_k$, the tilted Cayley masses $\omega_n=c_nx_k^{\,n}$ do not increase on the indices $0,\dots,k$: $\omega_j\le\omega_i$ for $i\le j\le k$.

## Statement

Let $k$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $\omega_n=c_nx_k^{\,n}$, $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). For natural numbers $i\le j\le k$, $\omega_j\le\omega_i$.

## Explanation

The many-step form of `Parking.ccT_succ_le`, which gives the single step $\omega_{n+1}\le\omega_n$ for $n+1\le k$. It supplies the hypothesis of `Parking.FirstLayer.conv_TK` that the value at the last inner index is the smallest (`Parking.FirstLayer.pairT_TK`).

## Proof

Induction on $j$ from $i$, with `Parking.ccT_succ_le` at each step.

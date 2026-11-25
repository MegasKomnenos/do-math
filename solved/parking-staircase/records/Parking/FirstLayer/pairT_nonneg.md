---
weight: step
short: the pair sums are nonnegative
---
## Description

The pair sums $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\,\omega_{\rho+j-a}$ of tilted Cayley masses are nonnegative.

## Statement

For natural numbers $k$, $\rho$, $j$, the pair sum $Q_\rho(j)$ of `Parking.FirstLayer.pairT` (formed with $\omega_n=c_nx_k^{\,n}$ at the critical tilt $x_k$) satisfies $Q_\rho(j)\ge 0$.

## Explanation

In fact $Q_\rho(j)>0$; nonnegativity is what the applications need, namely the hypothesis "middle value nonnegative" in the closure statements for property K and the sign conditions in `Parking.FirstLayer.Sdir_TK`.

## Proof

Each term is a product of two positive numbers: $x_k>0$ (`Parking.xcrit_pos`) and hence $\omega_n>0$ (`Parking.ccT_pos`).

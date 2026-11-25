---
weight: step
short: the pair sum written out
---
## Description

The pair sum of `Parking.FirstLayer.pairT` written as an explicit sum: $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\,\omega_{\rho+(j-a)}$.

## Statement

For natural numbers $k$, $\rho$, $j$, with $\omega_n=c_nx_k^{\,n}$ the tilted Cayley masses at the critical tilt $x_k$ (`Parking.ccT`, `Parking.xcrit`), the pair sum $Q_\rho(j)$ (`Parking.FirstLayer.pairT`) equals $\sum_{a=0}^{j}\omega_{\rho+a}\,\omega_{\rho+(j-a)}$.

## Explanation

`Parking.FirstLayer.pairT` is defined as a self-convolution of the shifted sequence $a\mapsto\omega_{\rho+a}$; this statement unfolds that definition so that the sum can be manipulated term by term. It carries no mathematical content beyond the definition, and in a written account the two coincide.

## Proof

By the definitions of `Parking.FirstLayer.pairT` and `Parking.FirstLayer.conv`; in Lean the two sides are definitionally equal.

---
weight: step
short: pair sum of tilted Cayley masses
---
## Description

The pair sum $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\,\omega_{\rho+j-a}$ of the tilted Cayley masses $\omega_n=c_nx_k^{\,n}$ at the critical tilt of the column $k$.

## Statement

Let $k$, $\rho$, $j$ be natural numbers, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $\omega_n=c_nx_k^{\,n}$, $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). The pair sum is
$$Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\,\omega_{\rho+j-a}.$$
It is the self-convolution (`Parking.FirstLayer.conv`) at the length $j$ of the shifted sequence $a\mapsto\omega_{\rho+a}$.

## Explanation

$Q_\rho(j)$ is the sum of the products $\omega_p\,\omega_q$ over the ordered pairs $(p,q)$ with $p,q\ge\rho$ and $p+q=2\rho+j$. It depends on $k$ through the tilt. In the last-car recursion for the threshold $c$ at the size $c+\rho$ ($1\le\rho\le c-1$), the terms in which both pieces have sizes between $\rho$ and $c-1$ add up to a multiple of $Q_\rho(c-\rho-1)$ (`Parking.FirstLayer.direct_generic`, `Parking.FirstLayer.Sdir`). When the threshold $c$ runs through $k-1,k,k+1$ and $\rho$ is fixed, the length $j=c-\rho-1$ runs through three consecutive values $n,n+1,n+2$ with $\rho+n+2=k$, and the largest index that occurs is $k$. These three pair sums are the subject of `Parking.FirstLayer.pairT_TK`, `Parking.FirstLayer.pairT_mid_le` and `Parking.FirstLayer.pairT_D_le`.

The definition is made through `Parking.FirstLayer.conv` so that `Parking.FirstLayer.conv_TK` applies to it directly. The Lean name is `pairT k ρ j`.

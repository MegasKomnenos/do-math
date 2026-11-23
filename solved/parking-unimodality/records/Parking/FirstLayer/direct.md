---
weight: unit
short: direct part of the last-car recursion in the first layer
---
## Description

The direct part $D(c,P)=\sum_{a=0}^{c-P}\min(P+a+1,c)\,\omega_{P+a}\,\omega_{c-a}$ of the last-car recursion at the size $c+P+1$ and the threshold $c$: the terms in which both pieces have size at most $c$.

## Statement

Let $k$, $c$, $P$ be natural numbers with $P\le c$, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $\omega_n=c_nx_k^{\,n}$, where $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). The direct part is
$$D(c,P)=\sum_{a=0}^{c-P}\min(P+a+1,\,c)\;\omega_{P+a}\;\omega_{c-a}.$$

## Explanation

The tilted last-car recursion for the threshold $c$ (`Parking.zrT_succ`) expresses the tilted mass of the size $c+P+1$ as $x_k$ times the sum over $j=0,\dots,c+P$ of $\min(j+1,c)$ times the product of the tilted masses of the sizes $j$ and $c+P-j$. The size $c+P+1$ lies in the first layer of the threshold $c$, that is, between $c+1$ and $2c+1$; then at most one of the two pieces $j$, $c+P-j$ is larger than $c$. $D(c,P)$ collects the terms $j=P+a$, $P\le j\le c$, in which neither is: both masses are then free, that is, equal to the tilted Cayley masses $\omega_j$ and $\omega_{c+P-j}=\omega_{c-a}$, and the direct part is an explicit expression in $\omega$ that contains no mass of the first layer. The remaining terms form the chain part; `Parking.FirstLayer.zrT_split` states the recursion in this sorted form, and `Parking.FirstLayer.direct_generic` evaluates $D(c,P)$ for $P\le c-2$.

The name of the symbol $D(c,P)$ is local to these records. The Lean definition `direct k c P` sums over `Finset.range (c + 1 - P)` with truncated subtraction, so it is defined, as an empty or shorter sum, also when $P>c$; it is used only for $P\le c$. The index $k$ enters only through the tilt $x_k$.

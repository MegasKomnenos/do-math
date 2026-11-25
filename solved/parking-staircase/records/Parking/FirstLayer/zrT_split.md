---
weight: unit
short: the last-car recursion in the first layer, chain part and direct part
---
## Description

For a threshold $c\ge 1$ and $P\le c$, at the tilt $x_k$: $(c+P+1)\,u^{(c)}_{c+P+1}=x_k\big(\sum_{i<P}(c+i+1)\,\omega_i\,u^{(c)}_{c+P-i}+D(c,P)\big)$, where $u^{(c)}$ is the tilted environment of the threshold $c$, $\omega$ the tilted Cayley masses and $D(c,P)$ the direct part.

## Statement

Let $k$, $c$, $P$ be natural numbers with $c\ge 1$ and $P\le c$. Let $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), $\omega_n=c_nx_k^{\,n}$ with $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT`), and $u^{(c)}_N=z^{(c)}_N\,x_k^{\,N}$, where $z^{(c)}_N=A(N,c-1)/N!$ and $A(N,c-1)$ is the number of parking functions of length $N$ all of whose displacements are smaller than $c$ (`Parking.zrT c (xcrit k) N`). Then
$$(c+P+1)\;u^{(c)}_{c+P+1}\;=\;x_k\Big(\sum_{i=0}^{P-1}(c+i+1)\,\omega_i\,u^{(c)}_{c+P-i}\;+\;D(c,P)\Big),$$
where $D(c,P)=\sum_{a=0}^{c-P}\min(P+a+1,c)\,\omega_{P+a}\,\omega_{c-a}$ is the direct part (`Parking.FirstLayer.direct`).

## Explanation

The sizes $c+1,\dots,2c+1$ are the first layer of the threshold $c$: a parking function of such a length whose last car splits it into two pieces has at most one piece longer than $c$. The statement is the tilted last-car recursion sorted accordingly. In the first sum, the *chain part*, one piece has a size $i<P$ and is free (its mass is $\omega_i$), and the other has the size $c+P-i$, which is again in the first layer, with a smaller excess over the threshold. The weight $c+i+1$ is the sum of the two weights $i+1$ and $c$ that the recursion gives to the two orders of the pieces. The *direct part* $D(c,P)$ contains no mass of the first layer.

This is the form in which the recursion supports an induction on the excess: the mass of the excess $P+1$ is a combination of the masses of the excesses $1,\dots,P$ with coefficients $x_k(c+i+1)\omega_i/(c+P+1)$, plus an explicit term. `Parking.FirstLayer.kernel_TK` runs this induction for the three thresholds $c=k-1,k,k+1$ at once.

The identity holds for any tilt in place of $x_k$; it is stated at $x_k$ because the direct part is defined there. The Lean statement writes the index of the chain mass as `c + (P - i)`.

## Proof

`Parking.zrT_succ`, for the threshold $c\ge 1$, the tilt $x_k$ and $N=c+P$, reads
$$(c+P+1)\,u^{(c)}_{c+P+1}=x_k\sum_{j=0}^{c+P}\min(j+1,c)\,u^{(c)}_j\,u^{(c)}_{c+P-j}.$$
Split the range of $j$ into $0\le j<P$, $P\le j\le c$ and $c<j\le c+P$, and in the third range write $j=c+P-i$ with $0\le i<P$.

In the first range, $j=i<P\le c$: the weight is $\min(i+1,c)=i+1$ and $u^{(c)}_i=\omega_i$, because a mass of a size at most the threshold is free (`Parking.zrT_eq_ccT`). In the third range, the weight is $\min(c+P-i+1,c)=c$ and the second factor is $u^{(c)}_i=\omega_i$. The two ranges together give $\sum_{i<P}\big((i+1)+c\big)\,\omega_i\,u^{(c)}_{c+P-i}$.

In the middle range write $j=P+a$, $0\le a\le c-P$. Both $P+a$ and $c+P-j=c-a$ are at most $c$, so both masses are free by `Parking.zrT_eq_ccT`, and the terms are those of $D(c,P)$.

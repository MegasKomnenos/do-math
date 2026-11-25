---
weight: unit
short: diagonal convexity of the tilted masses in the first layer
---
## Description

For $k\ge 7$ and $k\le N\le 2k-2$, at the critical tilt $x_k$: $u^{(k+1)}_{N+1}-2u^{(k)}_N+u^{(k-1)}_{N-1}\ge 0$, where $u^{(y)}_M=z^{(y)}_Mx_k^{\,M}$ is the tilted environment of the threshold $y$.

## Statement

Let $k\ge 7$ and $N$ be natural numbers with $k\le N\le 2k-2$. Let $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $u^{(y)}_M=z^{(y)}_M\,x_k^{\,M}$, where $z^{(y)}_M=A(M,y-1)/M!$ and $A(M,y-1)$ is the number of parking functions of length $M$ with all displacements smaller than $y$ (`Parking.zrT y (xcrit k) M`). Then
$$u^{(k+1)}_{N+1}-2\,u^{(k)}_N+u^{(k-1)}_{N-1}\ \ge\ 0 .$$

## Explanation

The left side is the second difference of the tilted masses along a diagonal: threshold and size are raised together. In terms of the counts, after division by $x_k^{\,N-1}$, it reads
$$x_k^{2}\,\frac{A(N+1,k)}{(N+1)!}-2x_k\,\frac{A(N,k-1)}{N!}+\frac{A(N-1,k-2)}{(N-1)!}\ \ge 0 .$$
The range $k\le N\le 2k-2$ is the part of the first layer in which the excess $\rho=N-k$ is at most $k-2$.

The inequality is used for the rows $n\ge 2k$ of the columns $k\ge 82$, in the proof of `Parking.step_pos_large`. There the tilted steps of column $k$, weighted by $\Psi'(n)=\max(n,2k-1)$, are summed by parts, and the terms that appear are weighted second differences along the diagonal (`Parking.DeltaPsi_nonneg`, `Parking.weighted_debt`). On the sizes $k\le N\le 2k-2$ the weight $\Psi'$ is constant, so there the weighted second difference is $2k-1$ times the present one: this is the place where plain convexity, and not a weighted form of it, is needed.

It is not proved by itself: it is the case $\mu=0$ of property K of the diagonal triple, `Parking.FirstLayer.kernel_TK`, and the record of `Parking.FirstLayer.TK` explains why the stronger statement is the one that can be proved by induction.

The Lean statement is written with $N=M+1$: its hypotheses are $k\le M+1$ and $M+1\le 2k-2$, and the three sizes are $M+2$, $M+1$, $M$.

## Proof

Put $\rho=N-k$, so $0\le\rho\le k-2$. By `Parking.FirstLayer.kernel_TK` the triple $\big(u^{(k-1)}_{k-1+\rho},u^{(k)}_{k+\rho},u^{(k+1)}_{k+1+\rho}\big)=\big(u^{(k-1)}_{N-1},u^{(k)}_N,u^{(k+1)}_{N+1}\big)$ has property K at $k$, and `Parking.FirstLayer.TK.convex` gives $2u^{(k)}_N\le u^{(k+1)}_{N+1}+u^{(k-1)}_{N-1}$.

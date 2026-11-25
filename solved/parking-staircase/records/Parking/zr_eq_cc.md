---
weight: unit
short: the free range of a threshold
---
## Description

In the free range $n\le y$ of a threshold $y\ge1$ the normalised cumulative count equals the Cayley number: $z^{(y)}_n=A(n,y-1)/n!=c_n=(n+1)^{n-1}/n!$.

## Statement

Let $y\ge1$ and $n\le y$ be natural numbers. Then $z^{(y)}_n=c_n$, where $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`) and $c_n=(n+1)^{n-1}/n!$ (`Parking.cc`).

## Explanation

In a parking function of length $n$ no displacement exceeds $n-1$, so for $n\le y$ the condition that all displacements are smaller than $y$ is no restriction, and $A(n,y-1)$ is the number $(n+1)^{n-1}$ of all parking functions of length $n$. The rows $n\le y$ are therefore called the *free range* of the threshold $y$. The library does not prove the statement in this way, and it nowhere counts the parking functions directly. It obtains the statement from the recursion: for $j+1\le y$ the weight $\min(j+1,y)$ is $j+1$, so up to the index $y$ the sequence $z^{(y)}$ is determined by the same recursion as $c$. In integers the statement is `Parking.A_eq_pow`.

The free range is where every induction over the rows starts, and it is the reason for the truncations in the column equations: $b(n,k)/n!$ vanishes for $n\le k$ (`Parking.bq_eq_zero`), the step of the column $k$ vanishes for $n<k$ (`Parking.dq_eq_zero`), and the tree curvature vanishes below $k$ (`Parking.xi_eq_zero`).

## Proof

By `Parking.zr_isWSol`, $z^{(y)}$ solves the weighted last-car recursion `Parking.IsWSol` with the weight $\min(t,y)$, and $\min(t,y)=t$ for $1\le t\le y$. The sequence $c$ solves the recursion with the weight $t$ (`Parking.cc_rec` with $c_0=1$). Two solutions whose weights agree for $1\le t\le y$ agree up to the index $y$: by strong induction on the index, since the recursion determines the value at $m+1$ from the weights at $1,\dots,m+1$ and the values at $0,\dots,m$. (This comparison is a private lemma of the module; it is also Step 1 of the proof of `Parking.IsWSol.ez`.) Hence $z^{(y)}_n=c_n$ for $n\le y$.

---
weight: unit
short: spots taken by the cars
---
## Description

The spots taken by the $n$ cars of a preference sequence $\alpha$ when they arrive in order at an empty street with the spots $0,\dots,n-1$; undefined if some car cannot park.

## Statement

Let $n$ be a natural number and let $\alpha$ be a function from $\{0,\dots,n-1\}$ to itself. Then
$$\operatorname{pos}(\alpha)=\operatorname{park}_n(\emptyset;\alpha(0),\dots,\alpha(n-1)),$$
where $\operatorname{park}_n$ is the parking process (`Parking.parkFrom`) and $(\alpha(0),\dots,\alpha(n-1))$ is the preference sequence of $\alpha$ (`Parking.prefList`). Explicitly: the cars $0,1,\dots,n-1$ arrive in this order at the empty street with the spots $0,\dots,n-1$, and the car $i$ takes the least spot $s\ge\alpha(i)$, $s<n$, that no earlier car has taken. If every car finds such a spot, $\operatorname{pos}(\alpha)=(p_0,\dots,p_{n-1})$ is the sequence of the spots taken, $p_i$ being the spot of the car $i$. If some car finds none, $\operatorname{pos}(\alpha)$ is undefined.

## Explanation

This is the parking process of the root proposition. There the cars and the spots are numbered $1,\dots,n$ and the spot of car $i$ is written $\mathrm{pos}_i(\alpha)$; with $a_i=\alpha(i-1)+1$ one has $\mathrm{pos}_i=p_{i-1}+1$, so the displacements $\mathrm{pos}_i-a_i=p_{i-1}-\alpha(i-1)$ are the same in both numberings.

`Parking.positions α` has the type `Option (List ℕ)`: `some ps` with the list `ps` of the spots when every car parks, and `none` otherwise. Whether it is `some` is the definition of a parking function (`Parking.IsParkingFunction`), and the list is what the displacements are computed from (`Parking.dispList`, `Parking.maxDisp`).

When every car parks, the $n$ spots taken are pairwise distinct spots of the street, so they are all the spots $0,\dots,n-1$: the cars fill the street. The library proves this inside the proof of `Parking.A_succ`. For $n=0$ there is one function $\alpha$, the empty one, and $\operatorname{pos}(\alpha)$ is the empty sequence.

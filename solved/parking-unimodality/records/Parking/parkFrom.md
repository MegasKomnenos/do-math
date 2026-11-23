---
weight: unit
short: the parking process
---
## Description

The parking process: cars with given preferences arrive one after another at a street with the spots $0,\dots,n-1$, some of them already occupied, and each takes the first free spot at or after its preference. The result is the sequence of the spots taken, and it is undefined if some car cannot park.

## Statement

Let $n$ be a natural number, $U$ a finite set of natural numbers, and $(a_1,\dots,a_m)$ a finite sequence of natural numbers, $m\ge0$. Put $U_0=U$. For $i=1,\dots,m$ in turn, let $s_i=\operatorname{first}_n(U_{i-1},a_i)$ be the least spot $s$ with $a_i\le s<n$ and $s\notin U_{i-1}$ (`Parking.firstFree`), and put $U_i=U_{i-1}\cup\{s_i\}$. If every $s_i$ is defined, then $\operatorname{park}_n(U;a_1,\dots,a_m)=(s_1,\dots,s_m)$. If for some $i$ there is no such spot, then $\operatorname{park}_n(U;a_1,\dots,a_m)$ is undefined. For the empty sequence the result is the empty sequence.

The Lean definition is the equivalent recursion on the first car: $\operatorname{park}_n(U;\,)=()$, and for $m\ge1$, $\operatorname{park}_n(U;a_1,\dots,a_m)$ is defined exactly when $s_1=\operatorname{first}_n(U,a_1)$ and $(s_2,\dots,s_m)=\operatorname{park}_n(U\cup\{s_1\};a_2,\dots,a_m)$ are defined, and it is then $(s_1,s_2,\dots,s_m)$.

## Explanation

**What it models.** The $i$-th car arrives when the spots of $U_{i-1}$ are occupied: those that were occupied at the start and those taken by the cars $1,\dots,i-1$. It takes the first free spot at or after its preference $a_i$, and that spot is occupied from then on. The process stops without a result at the first car that finds the spots $a_i,\dots,n-1$ all occupied. With $U=\emptyset$ and $m=n$ this is the process of the root proposition, in which $n$ cars arrive at an empty street of $n$ spots (`Parking.positions`).

**The Lean form.** `Parking.parkFrom n occ prefs` has the type `Option (List ℕ)`. It is `none` if some car cannot park and `some ps` otherwise, where `ps` is the list of the spots taken, in the order of arrival. The definition is by recursion on the list `prefs`, and it matches on the two `Option` values involved: the spot of the first car and the result for the remaining cars after that spot has been inserted into the set of occupied spots.

**Why occupied spots are a parameter.** The root proposition only needs the empty street. The set $U$ is there because the recursion on the first car changes the street: after the first car has parked, the remaining cars meet a street with one more occupied spot. The proof of the last-car recursion `Parking.A_succ` also needs the opposite decomposition, by the last car, which it derives from this definition: a sequence $(a_1,\dots,a_m,a)$ parks exactly when $(a_1,\dots,a_m)$ parks and a car with preference $a$ finds a spot when the spots taken by the first $m$ cars are occupied.

**Numbering.** Spots and preferences are numbered from $0$; the root proposition numbers them from $1$. See `Parking.firstFree`.

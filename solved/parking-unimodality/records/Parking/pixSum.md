---
weight: unit
short: partial sums of the weights
---
## Description

The partial sums $\Pi_i=\sum_{n=k}^{i}\pi_n$ of the weights $\pi_n=x^na_n/n$ of the column $k$, starting at the index $k$.

## Statement

For natural numbers $k$ and $i$,
$$\Pi_i=\Pi_i(k)=\sum_{n=k}^{i}\pi_n,$$
where $\pi_n=x^na_n/n$ are the weights `Parking.pix` of the column $k$ ($x$ is the diagonal tilt `Parking.xk`, $a_n=n^{n-1}/n!$ is `Parking.cay`). For $i<k$ the sum is empty and $\Pi_i=0$.

## Explanation

The partial sums appear when the tilted column equation of the column $k-1$ is summed over the rows $k,\dots,N$ and the left side $\sum_{n=k}^{N}\pi_nF_{n-1}$ is summed by parts ($F_n$ is the proportion of parking functions of length $n$ with maximum displacement at most $k-1$; see `Parking.pix`): one obtains $F_{N-1}\Pi_N$ plus a sum of terms $\Pi_i(F_{i-1}-F_i)$. This is Step 4 of the proof of `Parking.cross_criterion`.

Two facts about $\Pi_i$ are used. The weights are positive and nondecreasing from the index $k$ on, so $\Pi_i\le(i-k+1)\,\pi_i$ for $i\ge k$: the sum of $i-k+1$ terms is at most that many times the largest. And the ratio $\Pi_{j+1}/\pi_{j+1}$, which would equal the number of terms $j-k+2$ if the weights were constant, is written as $(j-k+2)-\mathsf e_j$; this defines the correction $\mathsf e_j$ (`Parking.ecor`).

In Lean, `pixSum k i = ∑ n ∈ Icc k i, pix k n`.

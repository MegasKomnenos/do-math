---
weight: unit
short: the first column: b(n,0) ≤ b(n,1) for n ≥ 3
---
## Description

For every $n\ge 3$: $b(n,0)\le b(n,1)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $n\ge 3$ be a natural number. Then $b(n,0)\le b(n,1)$.

## Explanation

This is the column $k=1$ of the left half (`Parking.left_half`), which the general arguments for the columns $k\ge 2$ do not cover. With $A(n,\ell)$ the number of parking functions of length $n$ with maximum displacement at most $\ell$, $b(n,0)=A(n,0)$ and $b(n,1)=A(n,1)-A(n,0)$, so the statement is $2A(n,0)\le A(n,1)$. For $n=2$ it fails ($A(2,0)=2$, $A(2,1)=3$), and at $n=3$ it reads $12\le 13$. From there on it is inherited from row to row by the last-car recursion, in which the level $1$ gives the weight $2$ to every term with index $j\ge 1$ and the level $0$ gives the weight $1$.

## Proof

**Reduction.** `Parking.b_zero` gives $b(n,0)=A(n,0)$ and `Parking.b_succ_add_A` gives $b(n,1)+A(n,0)=A(n,1)$. So it suffices to show $2A(n,0)\le A(n,1)$ for $n\ge 3$, by induction on $n$.

**Base $n=3$.** The inequality $2A(3,0)\le A(3,1)$ is checked by computation: the kernel evaluates the Boolean $2\cdot\mathrm{hd}(0,3)\le\mathrm{hd}(1,3)$, where $\mathrm{hd}(\ell,n)$ is the head of the list of natural numbers that the last-car recursion computes for the level $\ell$ up to the row $n$ (`Parking.Tab.hd`), in natural-number arithmetic; `Parking.Tab.hd_eq` states $\mathrm{hd}(\ell,n)=A(n,\ell)$ and turns the Boolean into the inequality.

**Step.** `Parking.A_succ` gives $A(n+1,\ell)=\sum_{j=0}^{n}\min(j+1,\ell+1)\binom nj A(j,\ell)\,A(n-j,\ell)$. For $\ell=0$ all weights are $1$; for $\ell=1$ the weight is $1$ at $j=0$ and $2$ at $j\ge 1$. Compare $2A(n+1,0)$ with $A(n+1,1)$ term by term. For $j\ge 1$: $2\binom njA(j,0)A(n-j,0)\le 2\binom njA(j,1)A(n-j,1)$, because $A(m,0)\le A(m,1)$ (`Parking.A_mono`). For $j=0$, with $A(0,\ell)=1$ (`Parking.A_zero`): the two terms are $2A(n,0)$ and $A(n,1)$, and $2A(n,0)\le A(n,1)$ is the induction hypothesis.

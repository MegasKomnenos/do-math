---
weight: unit
short: parking functions with maximum displacement at most k
---
## Description

$A(n,k)$ is the number of parking functions of length $n$ whose maximum displacement is at most $k$, that is, in which every car parks at most $k$ spots after the spot it prefers.

## Statement

For natural numbers $n$ and $k$,
$$A(n,k)=\#\{\alpha:\{0,\dots,n-1\}\to\{0,\dots,n-1\}\ :\ \alpha \text{ is a parking function and } M(\alpha)\le k\},$$
where $M(\alpha)$ is the maximum displacement of $\alpha$ (`Parking.maxDisp`), which is defined exactly when $\alpha$ is a parking function.

## Explanation

**The object.** $A(n,k)$ is the cumulative count belonging to the numbers $b(n,\ell)$ of the root proposition (`Parking.b`): $A(n,k)=\sum_{\ell\le k}b(n,\ell)$. In the library this relation appears in the form $b(n,0)=A(n,0)$ and $b(n,\ell+1)+A(n,\ell)=A(n,\ell+1)$ (`Parking.b_zero`, `Parking.b_succ_add_A`). The root proposition does not mention $A$; the whole proof is carried out with it.

**Why the proof works with $A$ and not with $b$.** The condition $M(\alpha)\le k$ is a condition on each car separately: every displacement is at most $k$. Such a condition is inherited by the two groups of cars into which the last car splits a parking function, and this gives the last-car recursion
$$A(n+1,k)=\sum_{j=0}^{n}\min(j+1,k+1)\binom nj A(j,k)\,A(n-j,k)$$
(`Parking.A_succ`). The condition $M(\alpha)=\ell$ is not of this kind, and the library has no recursion for $b$ itself. All later arguments use the parking process only through this recursion, the value $A(0,k)=1$ (`Parking.A_zero`), the monotonicity of $A(n,k)$ in $k$ (`Parking.A_mono`), and the two relations to $b$.

**Special values.** $A(0,k)=1$: the empty function is a parking function with $M=0$. For $n\le k+1$, $A(n,k)=(n+1)^{n-1}$ (`Parking.A_eq_pow`, which the library derives from the recursion). This is the number of all parking functions of length $n$, since for $n\le k+1$ the bound is no restriction: no displacement exceeds $n-1$. $A(n,0)=b(n,0)$ (`Parking.b_zero`); this number is $n!$, as is noted with the root proposition, because $M(\alpha)=0$ means that every car parks in the spot it prefers, so that $\alpha$ is a permutation. The library does not need this value and does not prove it.

**The Lean form.** `Parking.A n k` is the cardinality of the set of functions `α : Fin n → Fin n` for which there is $m\le k$ with `maxDisp α = some m`. As for `Parking.b`, the equation `maxDisp α = some m` contains the condition that $\alpha$ is a parking function. Later modules use $A$ with the index shifted by one: the threshold $y=k+1$ stands for "all displacements are smaller than $y$", and $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`).

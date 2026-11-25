---
weight: unit
short: parking functions with maximum displacement exactly l
---
## Description

$b(n,\ell)$ is the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$.

## Statement

For natural numbers $n$ and $\ell$,
$$b(n,\ell)=\#\{\alpha:\{0,\dots,n-1\}\to\{0,\dots,n-1\}\ :\ \alpha \text{ is a parking function and } M(\alpha)=\ell\},$$
where $M(\alpha)$ is the maximum displacement of $\alpha$ (`Parking.maxDisp`), which is defined exactly when $\alpha$ is a parking function, that is, when every car parks (`Parking.positions`).

## Explanation

**The object.** These are the numbers $b_{n,\ell}$ of the root proposition, which asserts that for every $n\ge1$ the sequence $b(n,0),\dots,b(n,n-1)$ is unimodal (`Parking.unimodal_via_staircase`). The root proposition counts sequences $(a_1,\dots,a_n)\in\{1,\dots,n\}^n$; the bijection $a_i=\alpha(i-1)+1$ carries parking functions to parking functions and preserves every displacement, so the two counts agree. The first rows are

| $n$ | $b(n,0),\dots,b(n,n-1)$ |
|---|---|
| 1 | 1 |
| 2 | 2, 1 |
| 3 | 6, 7, 3 |
| 4 | 24, 51, 34, 16 |
| 5 | 120, 421, 377, 253, 125 |

(the check values given with the root proposition).

**The Lean form.** `Parking.b n ℓ` is the cardinality of the set of all functions `α : Fin n → Fin n` with `maxDisp α = some ℓ`. The condition has two parts in one: `maxDisp α` is `none` when some car cannot park, so `maxDisp α = some ℓ` holds exactly for the parking functions with $M(\alpha)=\ell$. This is why $b$ is defined through `maxDisp` and no set of parking functions is formed first.

**Values outside the range of the root proposition.** The definition makes sense for all natural numbers $n$ and $\ell$, and the library uses that. For $n\ge1$ a parking function has $M(\alpha)\le n-1$, so $b(n,\ell)=0$ for $\ell\ge n$. The library has the vanishing as `Parking.bq_eq_zero` (for $\ell\ge1$ and $n\le\ell$); it obtains it from the last-car recursion and does not prove the bound $M(\alpha)\le n-1$ as a statement of its own. For $n=0$ the empty function is a parking function with $M=0$, so $b(0,0)=1$. Because of the first fact the step $b(k,k)-b(k,k-1)=-b(k,k-1)$ is negative, which is where every column of the table $b(n,k)$ starts (`Parking.dq_base`).

**How the library works with $b$.** No argument counts the parking functions with $M(\alpha)=\ell$ directly. The library passes to the cumulative numbers $A(n,k)$ (`Parking.A`), for which the last-car recursion `Parking.A_succ` holds, through $b(n,0)=A(n,0)$ and $b(n,\ell+1)=A(n,\ell+1)-A(n,\ell)$ (`Parking.b_zero`, `Parking.b_succ_add_A`). The quantity that the proof of the root proposition studies is the step $d_{n,k}=b(n,k)-b(n,k-1)$ of the column $k$ in the row $n$; for $k\ge2$ it is the second difference $A(n,k)-2A(n,k-1)+A(n,k-2)$ (`Parking.d_eq_A`).

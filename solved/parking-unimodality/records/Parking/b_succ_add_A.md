---
weight: step
short: b as a difference of A
---
## Description

$b(n,\ell+1)+A(n,\ell)=A(n,\ell+1)$: the parking functions with maximum displacement at most $\ell+1$ are those with maximum displacement exactly $\ell+1$ together with those with maximum displacement at most $\ell$.

## Statement

For all natural numbers $n$ and $\ell$, $b(n,\ell+1)+A(n,\ell)=A(n,\ell+1)$, where $b(n,\ell)$ (`Parking.b`) is the number of parking functions of length $n$ with maximum displacement exactly $\ell$ and $A(n,k)$ (`Parking.A`) the number of those with maximum displacement at most $k$.

## Explanation

The identity is written as a sum so that no subtraction of natural numbers occurs; it says $b(n,\ell+1)=A(n,\ell+1)-A(n,\ell)$. With `Parking.b_zero` it reduces every statement about the numbers $b$ to the cumulative counts $A$, for which the last-car recursion `Parking.A_succ` holds. Its normalised form is `Parking.bq_eq`, and the step of a column becomes a second difference of $A$ (`Parking.d_eq_A`).

## Proof

Among the functions $\alpha$ from $\{1,\dots,n\}$ to the spots, consider the set $S_1$ of those whose maximum displacement is exactly $\ell+1$ and the set $S_2$ of those whose maximum displacement is some $m\le\ell$. The two sets are disjoint, because the maximum displacement of a parking function is one number. Their union is the set of those $\alpha$ whose maximum displacement is some $m\le\ell+1$: such an $m$ is either at most $\ell$ or equal to $\ell+1$. Hence $|S_1|+|S_2|=b(n,\ell+1)+A(n,\ell)$ is the number $A(n,\ell+1)$ of elements of the union.

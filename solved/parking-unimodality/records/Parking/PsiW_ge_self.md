---
weight: step
short: the weight Ψ′ is at least the row number
---
## Description

$N\le\Psi'(N)$, where $\Psi'(N)=\max(N,2k-1)$.

## Statement

For natural numbers $k$ and $N$, $N\le\Psi'(N)$, where $\Psi'(N)=\max(N,2k-1)$ is the weight of `Parking.PsiW`.

## Explanation

Used in the row step of `Parking.big_columns` in the form $n-2\le\Psi'(n-2)$.

## Proof

A maximum is at least each of its arguments.

---
weight: step
short: the weight Ψ′ is nondecreasing
---
## Description

$\Psi'(N)\le\Psi'(N')$ for $N\le N'$, where $\Psi'(N)=\max(N,2k-1)$.

## Statement

Let $k$, $N$, $N'$ be natural numbers with $N\le N'$. Then $\Psi'(N)\le\Psi'(N')$, where $\Psi'(N)=\max(N,2k-1)$ is the weight of `Parking.PsiW`.

## Explanation

Used in the row step of `Parking.big_columns` in the form $\Psi'(n-2)\le\Psi'(n-1)$.

## Proof

The maximum with a fixed number is monotone in the other argument.

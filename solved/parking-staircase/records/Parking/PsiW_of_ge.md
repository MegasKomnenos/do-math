---
weight: step
short: the weight Ψ′ on the rows from 2k−1 on
---
## Description

$\Psi'(N)=N$ for $N\ge 2k-1$, where $\Psi'(N)=\max(N,2k-1)$.

## Statement

Let $k$ and $N$ be natural numbers with $2k-1\le N$. Then $\Psi'(N)=N$, where $\Psi'(N)=\max(N,2k-1)$ is the weight of `Parking.PsiW`.

## Explanation

On these rows the weight is the row number. In the Lean statement $2k-1$ is a truncated subtraction, so for $k=0$ the hypothesis reads $0\le N$ instead of $-1\le N$; both always hold, and the conclusion is the same.

## Proof

The maximum of $N$ and $2k-1$ is $N$.

---
weight: step
short: the weight Ψ′ on the rows up to 2k−1
---
## Description

$\Psi'(N)=2k-1$ for $N\le 2k-1$ and $k\ge 1$, where $\Psi'(N)=\max(N,2k-1)$.

## Statement

Let $k\ge 1$ and $N$ be natural numbers with $N\le 2k-1$. Then $\Psi'(N)=2k-1$, where $\Psi'(N)=\max(N,2k-1)$ is the weight of `Parking.PsiW`.

## Explanation

On the rows up to $2k-1$ the weight is constant. These rows contain the whole first layer and, for a column $k\ge 82$, all rows before the crossing row. The hypothesis $k\ge 1$ makes the natural-number subtraction $2k-1$ of the Lean definition agree with the real number $2k-1$ on the right.

## Proof

The maximum of $N$ and $2k-1$ is $2k-1$.

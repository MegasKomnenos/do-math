---
weight: step
short: the weight Ψ′ is at least the row number
---
## Description

$N\le\Psi'(N)$, where $\Psi'(N)=\max(N,2k-1)$.

## Statement

For natural numbers $k$ and $N$, $N\le\Psi'(N)$, where $\Psi'(N)=\max(N,2k-1)$ is the weight of `Parking.PsiW`.

## Explanation

Used in the proof of `Parking.step_pos_large`, in the step that passes from the rows before a row $n\ge 2k$ to the row $n$, in the form $n-2\le\Psi'(n-2)$.

## Proof

A maximum is at least each of its arguments.

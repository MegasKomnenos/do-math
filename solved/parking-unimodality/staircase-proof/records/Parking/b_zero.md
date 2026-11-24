---
weight: step
short: b at displacement zero
---
## Description

$b(n,0)=A(n,0)$: maximum displacement exactly $0$ and maximum displacement at most $0$ are the same condition.

## Statement

For every natural number $n$, $b(n,0)=A(n,0)$, where $b(n,\ell)$ (`Parking.b`) is the number of parking functions of length $n$ with maximum displacement exactly $\ell$ and $A(n,k)$ (`Parking.A`) the number of those with maximum displacement at most $k$.

## Explanation

Together with `Parking.b_succ_add_A` this expresses every $b(n,\ell)$ through the cumulative counts: $b(n,0)=A(n,0)$ and $b(n,\ell+1)=A(n,\ell+1)-A(n,\ell)$. The counts $b$ enter the later arguments only in this way. The identity is used directly for the column $k=1$, whose step is $b(n,1)-b(n,0)$ (in the proof of `Parking.step_pos_beyond`).

## Proof

The two numbers count the same functions $\alpha$: the condition "the maximum displacement of $\alpha$ is some $m\le 0$" is the condition "the maximum displacement of $\alpha$ is $0$".

---
weight: step
short: a column as a difference of environments
---
## Description

For $k\ge1$ the normalised count of the column $k$ is the difference of the environments of the thresholds $k+1$ and $k$: $\beta^{(k)}_n=z^{(k+1)}_n-z^{(k)}_n$.

## Statement

For all natural numbers $k\ge1$ and $n$, $\beta^{(k)}_n=z^{(k+1)}_n-z^{(k)}_n$, where $\beta^{(k)}_n=b(n,k)/n!$ (`Parking.bq`) and $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`).

## Explanation

A parking function has maximum displacement exactly $k$ when all its displacements are smaller than $k+1$ but not all are smaller than $k$. This identity is how every statement about a column is reduced to the environments, for which the recursion `Parking.zr_isWSol` holds. The hypothesis $k\ge1$ is needed because for $k=0$ the Lean definition gives $z^{(0)}=z^{(1)}$, while $\beta^{(0)}_n=z^{(1)}_n$ (`Parking.b_zero`).

## Proof

`Parking.b_succ_add_A` with $\ell=k-1$ gives $b(n,k)+A(n,k-1)=A(n,k)$. Dividing by $n!$ gives $\beta^{(k)}_n+z^{(k)}_n=z^{(k+1)}_n$, since $A(n,k)/n!=z^{(k+1)}_n$ and $A(n,k-1)/n!=z^{(k)}_n$.

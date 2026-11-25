---
weight: step
short: vanishing of the step above the column index
---
## Description

For $k\ge2$ the normalised step of the column $k$ vanishes in the rows $n<k$: $\delta^{(k)}_n=0$.

## Statement

For all natural numbers $k\ge2$ and $n<k$, $\delta^{(k)}_n=0$, where $\delta^{(k)}_n=\beta^{(k)}_n-\beta^{(k-1)}_n=(b(n,k)-b(n,k-1))/n!$ (`Parking.dq`).

## Explanation

In a row $n<k$ neither maximum displacement $k$ nor $k-1$ occurs, so both counts are $0$. The first row in which the step of the column $k$ is not zero is $n=k$, where it is negative (`Parking.dq_base`). The statement truncates the feedback sum of the column equation `Parking.dq_col` and of the column inequality on all rows (`Parking.col_eq_all`). The hypothesis $k\ge2$ makes $k-1\ge1$, which `Parking.bq_eq_zero` needs; for $k=1$ and $n=0$ the step is $b(0,1)-b(0,0)=-1$.

## Proof

By `Parking.bq_eq_zero`, $\beta^{(k)}_n=0$ because $k\ge1$ and $n\le k$, and $\beta^{(k-1)}_n=0$ because $k-1\ge1$ and $n\le k-1$. Their difference is $0$.

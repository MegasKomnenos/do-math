---
weight: step
short: vanishing of a column in the free range
---
## Description

For $k\ge1$ and $n\le k$ there is no parking function of length $n$ with maximum displacement exactly $k$: $\beta^{(k)}_n=b(n,k)/n!=0$.

## Statement

For all natural numbers $k\ge1$ and $n\le k$, $\beta^{(k)}_n=0$, where $\beta^{(k)}_n=b(n,k)/n!$ (`Parking.bq`).

## Explanation

A parking function of length $n$ has no displacement larger than $n-1$, so a maximum displacement $k\ge n$ does not occur, except for $n=k=0$, which the hypothesis $k\ge1$ excludes ($b(0,0)=1$). The column $k$ therefore begins in the row $n=k+1$. This is what truncates the sums of the column equations `Parking.bq_L0` and `Parking.dq_col`. The proof goes through the free range of the two thresholds and not through this remark about displacements.

## Proof

By `Parking.bq_eq`, $\beta^{(k)}_n=z^{(k+1)}_n-z^{(k)}_n$. Since $n\le k\le k+1$, the index $n$ lies in the free range of both thresholds, and `Parking.zr_eq_cc` gives $z^{(k+1)}_n=c_n=z^{(k)}_n$. The difference is $0$.

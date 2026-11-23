---
weight: unit
short: the step as a second difference of A
---
## Description

For $k\ge2$ the step $b(n,k)-b(n,k-1)$ of the column $k$ in the row $n$ is the second difference $A(n,k)-2A(n,k-1)+A(n,k-2)$ of the cumulative counts in the bound $k$.

## Statement

For all natural numbers $k\ge2$ and $n$,
$$b(n,k)-b(n,k-1)=A(n,k)-2A(n,k-1)+A(n,k-2)$$
as an identity of integers. Here $b(n,\ell)$ (`Parking.b`) is the number of parking functions of length $n$ with maximum displacement exactly $\ell$ and $A(n,k)$ (`Parking.A`) the number of those with maximum displacement at most $k$.

## Explanation

The main theorem is a statement about the signs of the steps $d_{n,k}=b(n,k)-b(n,k-1)$. Since $b(n,\ell)$ is a first difference of $A(n,\cdot)$, the step is a second difference, so it involves the three consecutive bounds $k$, $k-1$, $k-2$, that is, the three thresholds $k+1$, $k$, $k-1$ in the notation $z^{(y)}_n=A(n,y-1)/n!$ of `Parking.zr`. This is why three thresholds appear together in everything that concerns one column: in the normalised step `Parking.dq`, in the column equation `Parking.dq_col`, and in the tree curvature `Parking.xi`. The hypothesis $k\ge2$ is what makes $k-2$ a bound; for $k=1$ the step is $b(n,1)-b(n,0)=A(n,1)-2A(n,0)$, which is treated separately (`Parking.column_one`).

The identity is stated in the integers because the left-hand side can be negative. Two of the three computed tables use the step in this form. The table of the columns $2\le k\le81$ (`Parking.Tab.small_table`) computes the numbers $A(n,k)$ exactly and reads the sign of $d_{n,k}$ from this second difference. The table of two signs (`Parking.Tab.two_signs`) computes the numbers $U(y,n)=(n+1)^{n-1}-A(n,y-1)$ and reads the sign from $2U(k,n)-U(k+1,n)-U(k-1,n)$, which is the same second difference.

## Proof

Write $k=j+2$. By `Parking.b_succ_add_A`, $b(n,j+2)+A(n,j+1)=A(n,j+2)$ and $b(n,j+1)+A(n,j)=A(n,j+1)$. Subtracting the second identity from the first, in the integers, gives $b(n,j+2)-b(n,j+1)=A(n,j+2)-2A(n,j+1)+A(n,j)$.

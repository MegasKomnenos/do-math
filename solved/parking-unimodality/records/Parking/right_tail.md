---
weight: unit
short: nonpositive steps to the right of the middle
---
## Description

To the right of the middle of a row, a nonpositive step is followed only by nonpositive steps: if $i\ge9$, $n\le2i-1$ and $b(n,i)\le b(n,i-1)$, then $b(m,j)\le b(m,j-1)$ for every column $j\ge i$ and every row $m$ with $j+1\le m\le n$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $n$ and $i$ be natural numbers with $i\ge9$ and $n\le2i-1$, and suppose that $b(n,i)\le b(n,i-1)$. Then for every $j\ge i$ and every $m$ with $j+1\le m\le n$,
$$b(m,j)\le b(m,j-1).$$

## Explanation

Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The statement says: if $d_{n,i}\le0$ at a position with $n\le 2i-1$, then $d_{m,j}\le0$ on the whole triangle of positions $(m,j)$ with $j\ge i$ and $j+1\le m\le n$. The case $m=n$ is what the main theorem needs: in the row $n$, all steps $d_{n,j}$ with $i\le j\le n-1$ are nonpositive, so no strict ascent follows.

The statement is proved for the whole triangle, and not only for the row $n$, because the argument moves from a column to the next one and needs, for the column $j$, the sign in all the rows $j+1,\dots,m$ and not only in the row $m$. The two inputs are of different kinds. Inside the column $i$, the sign is carried back from the row $n$ to the earlier rows: in the chain range $i+1\le m\le 2i-1$ a column that is positive in some row stays positive (`Parking.chain_column_iter`), so a column that is nonpositive in the row $n$ is nonpositive in all earlier rows. From a column to the next, `Parking.mono` says that a column $j+1$ cannot be positive in a row up to which the column $j$ has stayed nonpositive.

The hypothesis $n\le 2i-1$ places the row $n$ in the chain range of the column $i$; it is used only for that column. The hypothesis $i\ge9$ is the range of `Parking.mono`. In Lean the hypothesis $n\le 2i-1$ is written `n + 1 ≤ 2 * i`, and `b m (j - 1)` uses the subtraction of natural numbers, exact since $j\ge9$.

## Proof

By induction on $j\ge i$.

*The column $j=i$.* Let $i+1\le m\le n$ and suppose, for a contradiction, that $b(m,i-1)<b(m,i)$. `Parking.chain_column_iter` says that a column $k\ge2$ which is positive in a row $m\ge k+1$ is positive in every row $m'$ with $m\le m'\le 2k-1$. With $k=i$ and $m'=n\le 2i-1$ it gives $b(n,i-1)<b(n,i)$, against the hypothesis $b(n,i)\le b(n,i-1)$.

*From $j$ to $j+1$.* Suppose that $b(l,j)\le b(l,j-1)$ for all $l$ with $j+1\le l\le n$, and let $j+2\le m\le n$. `Parking.mono` says: for $k\ge9$ and $m\ge k+2$, if $b(l,k)\le b(l,k-1)$ for all $l$ with $k+1\le l\le m$, then $b(m,k+1)\le b(m,k)$. With $k=j\ge i\ge9$ its hypothesis is the induction hypothesis restricted to the rows $l\le m$, and its conclusion is the claim for the column $j+1$ in the row $m$.

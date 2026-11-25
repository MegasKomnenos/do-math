---
weight: unit
short: normalised last-car recursion
---
## Description

For a threshold $y\ge1$ the sequence $z^{(y)}_n=A(n,y-1)/n!$ solves the weighted last-car recursion with the weight $\omega(t)=\min(t,y)$: $z^{(y)}_0=1$ and $(n+1)z^{(y)}_{n+1}=\sum_{j=0}^{n}\min(j+1,y)\,z^{(y)}_jz^{(y)}_{n-j}$.

## Statement

Let $y\ge1$ be a natural number and $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`). Then $z^{(y)}$ is a solution of the weighted last-car recursion with the weight $\omega(t)=\min(t,y)$ in the sense of `Parking.IsWSol`; that is, $z^{(y)}_0=1$ and, for every $n\ge0$,
$$(n+1)\,z^{(y)}_{n+1}=\sum_{j=0}^{n}\min(j+1,y)\;z^{(y)}_j\,z^{(y)}_{n-j}.$$

## Explanation

This is the last-car recursion `Parking.A_succ` for the bound $k=y-1$, divided by $n!$. It is the form in which every later part uses the recursion: through the single-chain formula (`Parking.IsWSol.ez`, `Parking.IsWSol.fwd`) in the column equations, in the table of two signs and for the frozen polynomial; as the differential equation of the series of a threshold (`Parking.deriv_Zs`); and multiplied by $x^{n+1}$ as the tilted recursion (`Parking.zrT_succ`). The hypothesis $y\ge1$ is needed to write the factor $\min(j+1,k+1)$ of `Parking.A_succ` as $\min(j+1,y)$ with $k=y-1$.

## Proof

The initial value is $z^{(y)}_0=A(0,y-1)/0!=1$ by `Parking.A_zero`. For the recursion, `Parking.A_succ` with $k=y-1$, so that $k+1=y$, gives
$$A(n+1,y-1)=\sum_{j=0}^{n}\min(j+1,y)\binom nj A(j,y-1)\,A(n-j,y-1).$$
Divide by $n!$. On the left, $A(n+1,y-1)/n!=(n+1)\,z^{(y)}_{n+1}$, because $(n+1)!=(n+1)\,n!$. On the right, $\binom nj\,j!\,(n-j)!=n!$ for $j\le n$, so $\binom nj A(j,y-1)A(n-j,y-1)/n!=z^{(y)}_j\,z^{(y)}_{n-j}$. This is a routine calculation with factorials.

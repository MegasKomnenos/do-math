---
weight: step
short: the tree curvature beyond the column index
---
## Description

For $k\ge2$ and $n\ge k$ the tree curvature of the column $k$ satisfies $(n+1)\,\xi_{n+1}=(k+1)\,\delta_n+2\,\beta^{(k-1)}_n$.

## Statement

For all natural numbers $k\ge2$ and $n\ge k$,
$$(n+1)\,\xi_{n+1}=(k+1)\,\delta_n+2\,\beta^{(k-1)}_n,$$
where $\xi=\xi^{(k)}$ is the tree curvature of the column $k$ (`Parking.xi`), $\delta_n=\delta^{(k)}_n=(b(n,k)-b(n,k-1))/n!$ (`Parking.dq`) and $\beta^{(k-1)}_n=b(n,k-1)/n!$ (`Parking.bq`).

## Explanation

Beyond the column index the three minima in the definition of $\xi$ are the thresholds themselves, and the tree curvature becomes the combination of the step and of the neighbouring column that stands on the right of the column equation: `Parking.dq_col` reads $n\,\delta_n-n\sum_{m=1}^{n-k}\varepsilon_m\delta_{n-m}=(k+1)\delta_{n-1}+2\beta^{(k-1)}_{n-1}=n\,\xi_n$ for $k+1\le n\le2k-1$. The same combination is the left-hand side of the column inequality on all rows (`Parking.col_eq_all`), whose proof uses the present identity, as does the proof of the propagation theorem `Parking.propagate`.

## Proof

By `Parking.xi_succ`, and since $n+1\ge k+1$ makes the three minima equal to $k+1$, $k$ and $k-1$,
$$(n+1)\,\xi_{n+1}=(k+1)\,z^{(k+1)}_n-2k\,z^{(k)}_n+(k-1)\,z^{(k-1)}_n,$$
with $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`). By `Parking.bq_eq`, applied to the columns $k$ and $k-1$ (both at least $1$), $\beta^{(k)}_n=z^{(k+1)}_n-z^{(k)}_n$ and $\beta^{(k-1)}_n=z^{(k)}_n-z^{(k-1)}_n$, so $\delta_n=z^{(k+1)}_n-2z^{(k)}_n+z^{(k-1)}_n$. Then
$$(k+1)\,\delta_n+2\,\beta^{(k-1)}_n=(k+1)z^{(k+1)}_n-2(k+1)z^{(k)}_n+(k+1)z^{(k-1)}_n+2z^{(k)}_n-2z^{(k-1)}_n,$$
which is the right-hand side above.

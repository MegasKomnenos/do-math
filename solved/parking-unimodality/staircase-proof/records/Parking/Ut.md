---
weight: unit
short: tilted cell of a column
---
## Description

The tilted cell $U_N = z^{(k)}_N x^N - z^{(k-1)}_N x^N$ of a column $k$ at a tilt $x$: the difference of the tilted environments of the thresholds $k$ and $k-1$, equal to $b(N,k-1)\,x^N/N!$ for $k \ge 2$.

## Statement

For a natural number $k$, a real number $x$ and a natural number $N$,
$$U_N \;=\; z^{(k)}_N\, x^N - z^{(k-1)}_N\, x^N ,$$
where $z^{(y)}_N x^N$ is the tilted environment of the threshold $y$ (`Parking.zrT`; $z^{(y)}_N = A(N,y-1)/N!$).

## Explanation

For $k \ge 2$ the difference of the two environments is the normalised count of the parking functions whose maximum displacement is exactly $k-1$: $U_N = \beta^{(k-1)}_N x^N$ with $\beta^{(k-1)}_N = b(N,k-1)/N!$ (`Parking.Ut_eq_bq`, `Parking.bq`; $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$). The word cell refers to the entry $b(N,k-1)$ of the triangle. Note the shift of the index: the cell written with the thresholds $k$ and $k-1$ is the entry of the level $k-1$, and the cell of the level $k$ is `Ut (k+1)`, written $U^+_N$ in the argument for the rows $n\ge2k$ of the columns $k\ge82$ (`Parking.step_pos_large`). The tilted step of the column $k$ is the difference $U^+_N - U_N = \delta_N x^N$, where $\delta_N = (b(N,k) - b(N,k-1))/N!$ (`Parking.dq`).

The object is defined through the environments, and not directly from $b$, because the argument for the rows $n\ge2k$ works with the three tilted environments of the thresholds $k+1$, $k$, $k-1$ and their recursions; there the tilted cell appears in the diagonal lower bound at the critical tilt (`Parking.Ut_diag_lower`) and in the boundary terms of the weighted debt (`Parking.weighted_debt`).

In Lean this is `Ut k x N = zrT k x N - zrT (k - 1) x N`. For $k \le 1$ the natural-number conventions make the two environments equal and the value is $0$; the object is used for $k \ge 2$.

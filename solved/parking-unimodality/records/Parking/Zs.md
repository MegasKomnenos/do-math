---
weight: unit
short: series of a threshold
---
## Description

The formal power series $Z_y = \sum_{n \ge 0} z^{(y)}_n X^n$ of a threshold $y$, where $z^{(y)}_n = A(n,y-1)/n!$ is the number of parking functions of length $n$ all of whose displacements are smaller than $y$, divided by $n!$.

## Statement

For a natural number $y$, the series of the threshold $y$ is the formal power series with real coefficients
$$Z_y \;=\; \sum_{n \ge 0} z^{(y)}_n X^n, \qquad z^{(y)}_n = \frac{A(n,y-1)}{n!},$$
where $A(n,k)$ is the number of parking functions of length $n$ whose maximum displacement is at most $k$ (`Parking.A`) and $z^{(y)}_n$ is the sequence `zr y n`. For $y \ge 1$ this is the exponential generating series of the parking functions all of whose displacements are smaller than $y$.

## Explanation

The word threshold is used for the strict bound: the threshold $y$ admits the displacements $0, \dots, y-1$. A column $k$ of the triangle $b(n,\ell)$ involves three thresholds at once, $k+1$, $k$ and $k-1$. Since $b(n,k) = A(n,k) - A(n,k-1)$, the difference $Z_{k+1} - Z_k$ has the coefficients $\beta^{(k)}_n = b(n,k)/n!$ (`Parking.bq`; the identity is `Parking.bq_eq`, for $k \ge 1$), and the second difference $Z_{k+1} - 2 Z_k + Z_{k-1}$ has the coefficients $\delta_n = (b(n,k) - b(n,k-1))/n!$ (`Parking.dq`), the normalised step of the column $k$. Statements about a column therefore become statements about these three series.

$Z_y$ is a formal power series; no question of convergence arises, and every identity between series in this part is an identity of coefficients. Its constant term is $1$ (`Parking.zr_zero`), so it has an inverse, from which the prime kernel series $K_y = 1 - 1/Z_y$ (`Parking.Ks`) is formed. Up to the degree $y$ its coefficients are the numbers $c_n = (n+1)^{n-1}/n!$ of all parking functions of length $n$ divided by $n!$ (`Parking.zr_eq_cc`), because a parking function of length $n \le y$ has all displacements smaller than $y$. The last-car recursion of the counts $A(n,k)$ is one differential equation for $Z_y$ (`Parking.deriv_Zs`), and that equation is the only fact about parking functions that this part of the library uses.

In Lean, `Zs y` is `PowerSeries.mk (zr y)`. For $y = 0$ the natural-number subtraction in `Parking.zr` gives $A(n,0)$, so `Zs 0` coincides with `Zs 1`; the results about $Z_y$ are stated for $y \ge 1$.

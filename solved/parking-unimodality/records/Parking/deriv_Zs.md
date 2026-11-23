---
weight: unit
short: the last-car recursion as a differential equation
---
## Description

For a threshold $y \ge 1$ the series $Z_y$ of the threshold satisfies $Z_y' = \Gamma_y' Z_y$, where $\Gamma_y'$ has the coefficients $\min(j+1,y)\, z^{(y)}_j$. This is the last-car recursion written for power series.

## Statement

For every natural number $y \ge 1$,
$$Z_y' \;=\; \Gamma_y'\, Z_y$$
as formal power series, where $Z_y = \sum_{n\ge0} z^{(y)}_n X^n$ is the series of the threshold $y$ (`Parking.Zs`; $z^{(y)}_n = A(n,y-1)/n!$) and $\Gamma_y'$ is the series `Parking.Gp`, the formal derivative of $\Gamma_y = \sum_{t\ge1} \frac{\min(t,y)}{t} z^{(y)}_{t-1} X^t$, whose coefficients are $[X^j]\,\Gamma_y' = \min(j+1,y)\, z^{(y)}_j$ (`Parking.coeff_Gp`).

## Explanation

The equation is the last-car recursion `Parking.A_succ`, $A(n+1,k) = \sum_{j \le n} \min(j+1,k+1) \binom{n}{j} A(j,k)\, A(n-j,k)$, for $k = y-1$: the last car parks in some spot, the cars to its left and to its right form two parking functions, and the last car has $\min(j+1,y)$ admissible preferences when $j$ cars stand to its left. Division by $n!$ turns the binomial convolution into the product of power series.

This is the one statement through which the parking process enters this part of the library. The prime kernel (`Parking.deriv_Ks`, `Parking.kq_rec`), the tilted recursion (`Parking.zrT_succ`), the monotonicity of the tilted environment (`Parking.zrT_anti_crit`) and the three inequalities on all rows (`Parking.col_eq_all`, `Parking.one_tree_bound`, `Parking.bq_diag_lower`) are derived from it by algebra and by comparisons of coefficients.

## Proof

By `Parking.zr_isWSol`, for $y \ge 1$ the sequence $W = z^{(y)}$ solves the weighted last-car recursion with the weight $\omega(t) = \min(t,y)$: $W_0 = 1$ and $(n+1)\, W_{n+1} = \sum_{j=0}^{n} \omega(j+1)\, W_j\, W_{n-j}$. For such a solution `Parking.SingleChain.deriv_mk` gives $W' = G' W$ for the series $W = \sum W_n X^n$ and $G = \sum_{t \ge 1} (\omega(t)/t)\, W_{t-1} X^t$: the coefficient of $X^n$ on the left is $(n+1) W_{n+1}$, and on the right it is $\sum_{j=0}^{n} [X^j] G' \cdot W_{n-j}$ with $[X^j] G' = \omega(j+1) W_j$, which is the recursion. With the present $\omega$ and $W$, the series $\sum W_n X^n$ is $Z_y$ and $G'$ is $\Gamma_y'$ by definition.

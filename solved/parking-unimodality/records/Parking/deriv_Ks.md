---
weight: unit
short: differential equation of the prime kernel series
---
## Description

For a threshold $y \ge 1$ the prime kernel series $K_y = 1 - 1/Z_y$ satisfies $K_y' = (1 - K_y)\,\Gamma_y'$, where $\Gamma_y' = Z_y'/Z_y$.

## Statement

For every natural number $y \ge 1$,
$$K_y' \;=\; (1 - K_y)\,\Gamma_y'$$
as formal power series, where $K_y = 1 - Z_y^{-1}$ is the prime kernel series of the threshold $y$ (`Parking.Ks`, with $Z_y$ the series `Parking.Zs`) and $\Gamma_y'$ is the series `Parking.Gp` with coefficients $\min(j+1,y)\, z^{(y)}_j$, $z^{(y)}_j = A(j,y-1)/j!$ (`Parking.zr`).

## Explanation

The equation is the differential equation $Z_y' = \Gamma_y' Z_y$ of the last-car recursion (`Parking.deriv_Zs`) carried over to the inverse: $(1/Z_y)' = -Z_y'/Z_y^2 = -\Gamma_y'/Z_y$. It is the form in which the last-car recursion acts on every quotient by $Z_y$. Two uses follow from it. With $\Gamma_y' = y Z_y - H_y$, where $H_y$ is a polynomial of degree at most $y-2$, it becomes $K_y' = y - (1-K_y) H_y$, a linear equation with polynomial coefficients, whose coefficients are the recursion `Parking.kq_rec`. And for two adjacent thresholds it gives the derivatives of the quotients $Z_{k+1}/Z_k = Z_{k+1}(1-K_k)$ and $Z_{k-1}/Z_k$ in terms of $\Gamma_{k+1}' - \Gamma_k'$ and $\Gamma_k' - \Gamma_{k-1}'$, which have nonnegative coefficients; the inequalities on all rows rest on this (see the record of `Parking.col_eq_all`).

## Proof

Differentiate the identity $Z_y\,(1-K_y) = 1$ (`Parking.Zs_mul_one_sub_Ks`) by the product rule: $Z_y'\,(1-K_y) - Z_y\,K_y' = 0$. Replace $Z_y'$ by $\Gamma_y' Z_y$ (`Parking.deriv_Zs`) and multiply by $1 - K_y$:
$$\Gamma_y'\,(1-K_y)\cdot Z_y(1-K_y) \;=\; K_y' \cdot Z_y (1-K_y).$$
Since $Z_y(1-K_y) = 1$, this is $\Gamma_y'\,(1-K_y) = K_y'$.

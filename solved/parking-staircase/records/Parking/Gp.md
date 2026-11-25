---
weight: unit
short: logarithmic derivative of the series of a threshold
---
## Description

The series $\Gamma_y'$ of a threshold $y$: the formal derivative of $\Gamma_y = \sum_{t \ge 1} \frac{\min(t,y)}{t}\, z^{(y)}_{t-1} X^t$, with coefficients $[X^j]\,\Gamma_y' = \min(j+1,y)\, z^{(y)}_j$. It satisfies $Z_y' = \Gamma_y' Z_y$.

## Statement

For a natural number $y$ let $z^{(y)}_n = A(n,y-1)/n!$ (`Parking.zr`) and
$$\Gamma_y \;=\; \sum_{t \ge 1} \frac{\min(t,y)}{t}\; z^{(y)}_{t-1}\, X^t .$$
The series `Gp y` is the formal derivative $\Gamma_y'$ of this power series.

## Explanation

The last-car recursion of the counts, divided by $n!$, reads $(n+1)\, z^{(y)}_{n+1} = \sum_{j=0}^{n} \min(j+1,y)\, z^{(y)}_j\, z^{(y)}_{n-j}$ for $y \ge 1$ (`Parking.zr_isWSol`). The left-hand side is the coefficient of $X^n$ in $Z_y'$, where $Z_y$ is the series of the threshold (`Parking.Zs`), and the right-hand side is the coefficient of $X^n$ in a product of $Z_y$ with the series whose $j$-th coefficient is $\min(j+1,y)\, z^{(y)}_j$. That series is $\Gamma_y'$ (`Parking.coeff_Gp`), and the recursion becomes $Z_y' = \Gamma_y' Z_y$ (`Parking.deriv_Zs`). So $\Gamma_y'$ is the logarithmic derivative $Z_y'/Z_y$ of the series of the threshold.

The series is defined as a derivative, and not directly by its coefficients, because the general construction of the library does so: for a weight $\omega$ and a solution $W$ of the weighted last-car recursion, `Parking.SingleChain.Gser` is the series $G = \sum_{t\ge1} (\omega(t)/t)\, W_{t-1} X^t$, and the recursion is $W' = G' W$ (`Parking.SingleChain.deriv_mk`). Here $\omega(t) = \min(t,y)$ and $W = z^{(y)}$. The antiderivative $\Gamma_y$ with $\Gamma_y(0) = 0$ is itself used: formally $Z_y = \exp \Gamma_y$, so $\Gamma_y$ is the logarithm of $Z_y$, and in the language of forests it is the series of one tree while $Z_y$ is the series of forests. The library never forms the exponential; it works with the differential equation. In the proofs of the inequalities on all rows (`Parking.col_eq_all`, `Parking.one_tree_bound`, `Parking.bq_diag_lower`) the differences $\Gamma_{k+1} - \Gamma_k$ and $\Gamma_k - \Gamma_{k-1}$ of adjacent thresholds appear, and the coefficients of $\Gamma_{k+1} - 2\Gamma_k + \Gamma_{k-1}$ are the tree curvatures $\xi_t$ (`Parking.xi`).

Two properties of $\Gamma_y'$ carry the later proofs. First, raising the threshold by one changes it by a series with nonnegative coefficients: for $y \ge 2$, $\Gamma_y' - \Gamma_{y-1}' = y\,(Z_y - Z_{y-1}) + \sum_{j \ge y-1} z^{(y-1)}_j X^j$ (proved in the record of `Parking.col_eq_all`). Second, since $\min(j+1,y) = y$ except for $j \le y-2$, where $z^{(y)}_j = c_j = (j+1)^{j-1}/j!$ (`Parking.zr_eq_cc`, `Parking.cc`), one has $\Gamma_y' = y Z_y - H_y$ with the polynomial $H_y = \sum_{j \le y-2} (y-1-j)\, c_j X^j$; this gives the recursion of the prime kernel (`Parking.kq_rec`).

---
weight: unit
short: prime kernel of a threshold
---
## Description

The prime kernel $\kappa^{(y)}_m$ of a threshold $y$: the coefficient of $X^m$ in the prime kernel series $K_y = 1 - 1/Z_y$.

## Statement

For natural numbers $y$ and $m$,
$$\kappa^{(y)}_m \;=\; [X^m]\,K_y, \qquad K_y = 1 - Z_y^{-1},$$
where $Z_y = \sum_{n \ge 0} z^{(y)}_n X^n$ is the series of the threshold $y$ (`Parking.Zs`; $z^{(y)}_n = A(n,y-1)/n!$ is the sequence `Parking.zr`) and $K_y$ is its prime kernel series (`Parking.Ks`).

## Explanation

For $y \ge 1$ the sequence $\kappa^{(y)}$ is determined by $\kappa^{(y)}_0 = 0$ (`Parking.kq_zero`) and the renewal equation
$$z^{(y)}_n \;=\; \sum_{m=1}^{n} \kappa^{(y)}_m\, z^{(y)}_{n-m} \qquad (n \ge 1),$$
which is the identity $Z_y (1 - K_y) = 1$ (`Parking.Zs_mul_one_sub_Ks`) read at the coefficient of $X^n$. More generally, for any power series $F$ the coefficient of $X^n$ in $F\,(1 - K_y)$ is $F_n - \sum_{m=1}^{n} \kappa^{(y)}_m F_{n-m}$ (by `Parking.coeff_one_sub_Ks_zero` and `Parking.coeff_one_sub_Ks_of_pos`), and in this form the kernel appears in the column inequality `Parking.col_eq_all`.

What is known about the kernel is the following. In the free range $1 \le m \le y$ it equals $\varepsilon_m = (m-1)^{m-1}/m!$, the kernel of the unrestricted problem (`Parking.kq_eq_eps`). For $N \ge y \ge 2$ it satisfies the recursion $N \kappa^{(y)}_N = \sum_{\gamma=1}^{y-1} (y-\gamma)\, a_\gamma\, \kappa^{(y)}_{N-\gamma}$ with $a_\gamma = \gamma^{\gamma-1}/\gamma!$ (`Parking.kq_rec`), whose coefficients are nonnegative; hence, for $y \ge 2$, $\kappa^{(y)}_m \ge 0$ for all $m$ (`Parking.kqT_nonneg` with the tilt $1$). Beyond the threshold the kernel is smaller than $\varepsilon$: for $y = 2$ the recursion gives $\kappa^{(2)}_m = 1/m!$ for $m \ge 1$, while $\varepsilon_3 = 2/3$.

The combinatorial meaning of $m!\,\kappa^{(y)}_m$ (the number of prime parking functions of length $m$ with all displacements smaller than $y$) is explained in the record of `Parking.Ks`; the library uses only the definition as a coefficient. The superscript $(y)$ is written here because results about a column $k$ use the kernel of the threshold $k$ next to the series of the thresholds $k \pm 1$. In Lean the sequence is `kq y m`.

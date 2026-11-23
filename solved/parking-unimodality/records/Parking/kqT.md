---
weight: unit
short: tilted prime kernel of a threshold
---
## Description

The tilted prime kernel $\kappa^{(y)}_m x^m$ of a threshold $y$ at a tilt $x$, where $\kappa^{(y)}_m$ is the coefficient of $X^m$ in $1 - 1/Z_y$.

## Statement

For a natural number $y$, a real number $x$ and a natural number $m$, the tilted prime kernel of the threshold $y$ at the tilt $x$ is
$$\kappa^{(y)}_m\, x^m ,$$
where $\kappa^{(y)}_m = [X^m](1 - 1/Z_y)$ is the prime kernel of the threshold $y$ (`Parking.kq`; $Z_y$ is the series `Parking.Zs`).

## Explanation

Tilting (see the record of `Parking.zrT`) is compatible with the renewal equation between the environment and the kernel: $z^{(y)}_n x^n = \sum_{m=1}^{n} \kappa^{(y)}_m x^m \cdot z^{(y)}_{n-m} x^{n-m}$. In the same way, when the column inequality `Parking.col_eq_all` is multiplied by $x^n$, the kernel appears in it in tilted form, as the weights with which the tilted steps of the earlier rows feed back into the row $n$. The left half of the argument needs these weights to be small and ordered, and for that the tilt matters: the untilted kernel is not monotone (already $\varepsilon_2 = 1/2 < \varepsilon_3 = 2/3$ in the free range), whereas at the critical tilt $x_k$ (`Parking.xcrit`), for $k \ge 2$, the tilted prime kernel of the threshold $k$ is nonincreasing in $m \ge 1$, and $m\,\kappa^{(k)}_m x_k^m$ is nonincreasing in $m \ge k$.

The properties established in general are these, where $a_\gamma = \gamma^{\gamma-1}/\gamma!$ (`Parking.cay`) and $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`). For $y \ge 1$ and $1 \le m \le y$ the tilted kernel is the tilted free prime kernel $\varepsilon_m x^m$ (`Parking.kqT_eq_epsT`). For $N \ge y \ge 2$ it satisfies the recursion $N \kappa^{(y)}_N x^N = \sum_{\gamma=1}^{y-1} (y-\gamma)\, a_\gamma x^\gamma \cdot \kappa^{(y)}_{N-\gamma} x^{N-\gamma}$ (`Parking.kqT_rec`). For $y \ge 2$ and $x \ge 0$ it is nonnegative (`Parking.kqT_nonneg`). If, moreover, $\varepsilon_m x^m$ does not increase on $1 \le m \le y$, then $\kappa^{(y)}_m x^m$ does not increase on $m \ge 1$ (`Parking.kqT_succ_le`) and $m\, \kappa^{(y)}_m x^m$ does not increase on $m \ge y$ (`Parking.kqT_harmonic`).

In Lean this is `kqT y x m = kq y m * x ^ m`.

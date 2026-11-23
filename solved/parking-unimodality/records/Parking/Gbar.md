---
weight: step
short: second comparison term of the flow side
---
## Description

The closed form $\bar G=\frac{R^2-1}{2}-(k-1)(R-1)+k(k-1)\log\frac{k+R}{k+1}$; it bounds the sum $\sum_{\rho=1}^{R-1}\frac{\rho(\rho+1)}{k+\rho}$, through which the tilt enters the right side of the crossing criterion.

## Statement

For natural numbers $k$ and $R$,
$$\bar G=\bar G(k,R)=\frac{R^{2}-1}{2}-(k-1)(R-1)+k\,(k-1)\,\log\frac{k+R}{k+1}.$$

## Explanation

The right side of the crossing criterion `Parking.cross_criterion` contains the factor $\mathsf e_{N-1}+\Sigma_\omega$, $N=k+R$ (`Parking.ecor`, `Parking.Somg`), and for $k\ge2$, $R\ge2$ it is at most $\bar H+\frac5k\bar G$, with $\bar H$ the closed form `Parking.Hbar`; this is part (iv) of the proof of `Parking.cross_of_bounds`. The term with $\bar G$ collects everything that comes from the tilt. With $x$ the diagonal tilt (`Parking.xk`) and $\gamma_i$ as in `Parking.gam`, the bound $\log(x\gamma_i)\le\frac{5(i-k)}{2ki}$ for $i\ge k$ gives
$$(i-k+1)\,\log(x\gamma_i)\le\frac{5}{2k}\cdot\frac{(i-k)(i-k+1)}{i},$$
and these terms occur twice: summed over $k<i\le N-1$ they bound $\mathsf e_{N-1}$, and summed over the same range they bound the tilt part of $\Sigma_\omega$. Each time the sum $\sum_{\rho=1}^{R-1}\frac{\rho(\rho+1)}{k+\rho}$ is at most $\bar G$, which explains the coefficient $\frac{5}{2k}+\frac{5}{2k}=\frac5k$.

$\bar G$ is the value at $n=N-1$ of the function $G(n)=\frac{(n-k)(n-k+1)}{2}+(\frac32-k)(n-k)+k(k-1)\log\frac{n+1}{k+1}$, which vanishes at $n=k$ and whose increments dominate the summands. Equivalently, $\bar G=\int_1^R\frac{t(t+1)}{k+t}\,dt$.

$\bar G$ is about $R^3/(3k)$, so $\frac5k\bar G$ is of order $R^3/k^2$. When $R$ is of order $k^{2/3}$, as in `Parking.crossing_strip`, this stays bounded while $\bar H$ grows like $k^{1/3}$. For the smallest column of that application the two are nevertheless of the same size (numerically, for $k=265$ and $R=70$: $\bar H\approx8.09$ and $\frac5k\bar G\approx6.96$), so the tilt part is not a negligible correction there.

In Lean, `Gbar k R = ((R : ℝ) ^ 2 - 1) / 2 - ((k : ℝ) - 1) * ((R : ℝ) - 1) + (k : ℝ) * ((k : ℝ) - 1) * Real.log (((k : ℝ) + R) / ((k : ℝ) + 1))`.

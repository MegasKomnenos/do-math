---
weight: step
short: first comparison term of the flow side
---
## Description

The closed form $\bar H=(R-1)-k\log\frac{k+R+1}{k+2}$; it bounds the sum $\sum_{\rho=1}^{R-1}\frac{\rho+1}{k+\rho+1}$, the tilt-free part of the weighted sum $\Sigma_\omega$ of the flow factors of the column $k$.

## Statement

For natural numbers $k$ and $R$,
$$\bar H=\bar H(k,R)=(R-1)-k\,\log\frac{k+R+1}{k+2}.$$

## Explanation

The right side of the crossing criterion `Parking.cross_criterion` contains the factor $\mathsf e_{N-1}+\Sigma_\omega$, $N=k+R$ (`Parking.ecor`, `Parking.Somg`). For $k\ge2$ and $R\ge2$,
$$0\le\mathsf e_{N-1}+\Sigma_\omega\le\bar H+\frac5k\,\bar G,$$
with $\bar G$ the closed form `Parking.Gbar`; this is part (iv) of the proof of `Parking.cross_of_bounds`. The term $\bar H$ accounts for the part of the flow factors that does not come from the tilt: $\omega_i\le\frac{1}{i+1}+\log(x\gamma_i)$ for $i\ge k$ (`Parking.omg`; $x$ is the diagonal tilt `Parking.xk` and $\gamma_i$ is `Parking.gam`), and the first parts add up to $\sum_{i=k+1}^{N-1}\frac{i-k+1}{i+1}=\sum_{\rho=1}^{R-1}\frac{\rho+1}{k+\rho+1}$.

$\bar H$ is the value at $n=N-1$ of the function $H(n)=(n-k)-k\log\frac{n+2}{k+2}$, which vanishes at $n=k$ and whose increments dominate the summands: $H(i)-H(i-1)=1-k\log\frac{i+2}{i+1}\ge1-\frac{k}{i+1}=\frac{i-k+1}{i+1}$. Equivalently, $\bar H=\int_1^R\frac{t+1}{k+t+1}\,dt$, the integral of the increasing summand.

In the application in `Parking.crossing_strip`, with $R$ of order $k^{2/3}$, $\bar H$ is about $R^2/(2k)$, of order $k^{1/3}$, and for large $k$ it is the dominant part of the bound for $\mathsf e_{N-1}+\Sigma_\omega$; the record of `Parking.Gbar` gives the sizes of the two parts at the smallest column.

In Lean, `Hbar k R = ((R : ℝ) - 1) - k * Real.log (((k : ℝ) + R + 1) / ((k : ℝ) + 2))`.

---
weight: step
short: closed-form bound for the accumulated tilt correction
---
## Description

The closed form $\bar{\mathsf E}=5(R-2)(R-1)R(R+1)/(24k^3)$; it bounds the accumulated tilt correction $\mathsf E=\sum_{j=k}^{k+R-2}\mathsf e_j/(j+1)$ of the column $k$ from above.

## Statement

For natural numbers $k$ and $R$,
$$\bar{\mathsf E}=\bar{\mathsf E}(k,R)=\frac{5\,(R-2)(R-1)\,R\,(R+1)}{24\,k^{3}}.$$

## Explanation

For $k\ge2$ and $R\ge2$ one has $\mathsf E\le\bar{\mathsf E}$, where $\mathsf E$ is the sum `Parking.ecorSum`; this is part (iii) of the proof of `Parking.cross_of_bounds`. The form of $\bar{\mathsf E}$ reflects that proof. Each correction satisfies $\mathsf e_j\le\frac{5}{6k^2}\rho(\rho+1)(\rho+2)$ with $\rho=j-k$ (see `Parking.ecor`), the denominators $j+1$ are replaced by $k$, and $\sum_{\rho=0}^{R-2}\rho(\rho+1)(\rho+2)=\frac14(R-2)(R-1)R(R+1)$.

The bound is of order $R^4/k^3$. In the application in `Parking.crossing_strip`, where $R$ is of order $k^{2/3}$, this is of order $k^{-1/3}$, so $\bar{\mathsf E}$ is a small correction to the main term $R(R+1)/(k+R)$ of the criterion, which is of order $k^{1/3}$.

In Lean, `Ebar k R` is the real number `5 * ((R : ℝ) - 2) * ((R : ℝ) - 1) * R * ((R : ℝ) + 1) / (24 * (k : ℝ) ^ 3)`, with real subtraction.

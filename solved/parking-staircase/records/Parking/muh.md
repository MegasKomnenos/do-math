---
weight: unit
short: mean number of cuts under the homogeneous law
---
## Description

$\mu_r(h)$ is the mean number of cuts of a composition of $r$ under the homogeneous law with parameter $h$, in which a composition with $q$ parts has probability proportional to its Cayley weight times $h^{q-1}$.

## Statement

For a natural number $r$ and a real number $h$,

$$\mu_r(h) = \frac{\sum_{q=1}^{r} (q-1)\, T_{r,q}\, h^{q-1}}{\tau_r(h)},$$

where $T_{r,q}$ is the total Cayley weight of the compositions of $r$ with $q$ parts (`Parking.Tq`) and $\tau_r(h) = \sum_{q=1}^{r} T_{r,q} h^{q-1}$ (`Parking.tau`).

## Explanation

Under the homogeneous law with parameter $h \ge 0$ the number of parts $Q$ of a composition of $r$ takes the value $q$ with probability $T_{r,q} h^{q-1}/\tau_r(h)$, and a composition with $Q$ parts has $Q - 1$ cuts. So $\mu_r(h)$ is the expectation of $Q - 1$. It is also the logarithmic derivative $h\,\tau_r'(h)/\tau_r(h)$.

The mean number of cuts is the quantity through which the homogeneous law enters the comparison of two positions on a diagonal. `Parking.Lam_gain` compares the total weights of the compositions of $q$ for two threshold profiles (`Parking.thr`), with the cut weights $(k-1)/(k+q-s)$ and $k/(k+q+1-s)$ at the cut point $s$: the second total is at least $(1+x)^{\bar e}$ times the first, with $x = q/((k-1)(k+q))$. Here a cut at $s$ contributes $(q+1-s)/q$ to the exponent, and $\bar e$ is the mean, under the first profile, of the sum of the contributions of the cuts of a composition. Under the homogeneous law with parameter $h$ the mean of that sum is $\frac{q+2}{2q}\,\mu_q(h)$, and for $h = (k-1)/(k-1+q)$, the smallest value of the first profile on the cut points, the mean under the first profile is at least as large. So a larger mean number of cuts helps, and `Parking.mu0_le_muh` bounds $\mu_r(h)$ from below by the explicit function `Parking.mu0`.

In Lean the definition is `muh r h`, written with a division. For $r \ge 1$ and $h \ge 0$ the denominator is positive (`Parking.tau_pos`), and `Parking.muh_mul_tau` is the same identity without the division. Where the denominator vanishes, as for $r = 0$, the Lean value is $0$ by the convention for division by zero; the definition is used only for $r \ge 1$ and $h \ge 0$.

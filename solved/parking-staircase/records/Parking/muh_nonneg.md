---
weight: step
short: nonnegativity of the mean number of cuts
---
## Description

The mean number of cuts $\mu_r(h)$ of the compositions of $r \ge 1$ with constant cut weight $h \ge 0$ is nonnegative.

## Statement

For every natural number $r \ge 1$ and every real number $h \ge 0$, $\mu_r(h) \ge 0$, where

$$\mu_r(h) \;=\; \frac{\sum_{q=1}^{r}(q-1)\,T_{r,q}\,h^{q-1}}{\tau_r(h)}$$

is the mean number of cuts under the homogeneous law with parameter $h$ (`Parking.muh`; $T_{r,q}$ is `Parking.Tq` and $\tau_r(h)$ is `Parking.tau`).

## Explanation

A number of cuts is nonnegative, and so is its mean. The sign is needed in the last step of `Parking.mu0_le_muh`: there an inequality between the squares of two expressions is turned into an inequality between the expressions themselves, and the sign of $\mu_r(h)$ shows that the expression which contains it is nonnegative.

## Proof

The numerator is a sum of nonnegative terms: $q - 1 \ge 0$ for $q \ge 1$, $T_{r,q} \ge 0$ by `Parking.Tq_nonneg`, and $h^{q-1} \ge 0$. The denominator is positive by `Parking.tau_pos`.

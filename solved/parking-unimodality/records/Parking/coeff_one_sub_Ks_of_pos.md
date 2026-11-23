---
weight: step
short: higher coefficients of one minus the prime kernel series
---
## Description

For $m \ge 1$, the coefficient of $X^m$ in $1 - K_y$ is $-\kappa^{(y)}_m$, the negative of the prime kernel of the threshold $y$.

## Statement

For every natural number $y$ and every $m \ge 1$, $[X^m]\,(1 - K_y) = -\kappa^{(y)}_m$, where $K_y$ is the prime kernel series of the threshold $y$ (`Parking.Ks`) and $\kappa^{(y)}_m = [X^m] K_y$ (`Parking.kq`).

## Explanation

See `Parking.coeff_one_sub_Ks_zero` for the constant coefficient and for the use of the two statements together. No hypothesis on $y$ is needed here.

## Proof

The coefficient of $X^m$ in the series $1$ is $0$ for $m \ge 1$, and the coefficient of $X^m$ in $K_y$ is $\kappa^{(y)}_m$ by definition.

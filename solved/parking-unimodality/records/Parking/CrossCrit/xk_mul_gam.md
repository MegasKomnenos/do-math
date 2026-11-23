---
weight: step
short: normalisation of the diagonal tilt
---
## Description

The diagonal tilt $x=1/\gamma_k$ satisfies $x\,\gamma_k=1$, for every natural number $k$.

## Statement

For every natural number $k$, $x\,\gamma_k=1$, where $x$ is the diagonal tilt of the column $k$ (`Parking.xk`) and $\gamma_k$ is `Parking.gam`.

## Explanation

This is the property for which the tilt is chosen. It removes the factor $\gamma_k$ from the diagonal lower bound `Parking.bq_diag_lower`: from $\gamma_k\beta^{(k-1)}_{n-1}\le\beta^{(k)}_n$ one gets $x^{n-1}\beta^{(k-1)}_{n-1}=x^n\gamma_k\beta^{(k-1)}_{n-1}\le x^n\beta^{(k)}_n$. The record of `Parking.xk` says what follows from this.

## Proof

$x$ is by definition the inverse of $\gamma_k$, and $\gamma_k\ne0$ because $\gamma_k>0$ (`Parking.gam_pos`).

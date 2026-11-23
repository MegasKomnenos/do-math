---
weight: step
short: positivity of the factor of the diagonal bound
---
## Description

$\gamma_k=(1+1/k)^{k-2}$ is positive.

## Statement

For every natural number $k$, $0<\gamma_k$, where $\gamma_k=(1+1/k)^{k-2}$ for $k\ge2$ (`Parking.gam`); the statement includes the values $\gamma_0=\gamma_1=1$ of the Lean definition.

## Explanation

Positivity is what allows the diagonal tilt $1/\gamma_k$ (`Parking.xk`) to be formed and inequalities to be multiplied or divided by $\gamma_k$.

## Proof

$\gamma_k$ is a power, with a natural number as exponent, of the positive real number $1+1/k$ (for $k=0$, where Lean reads $1/0$ as $0$, of the number $1$).

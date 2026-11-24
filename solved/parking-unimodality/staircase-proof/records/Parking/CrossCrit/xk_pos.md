---
weight: step
short: positivity of the diagonal tilt
---
## Description

The diagonal tilt $x=1/\gamma_k$ is positive, for every natural number $k$.

## Statement

For every natural number $k$, $x>0$, where $x=1/\gamma_k$ is the diagonal tilt of the column $k$ (`Parking.xk`).

## Explanation

Positivity is what allows an inequality between normalised counts to be multiplied by a power $x^n$ without changing its direction, and it makes the tilted step $x^n\delta_n$ (`Parking.stepD`) have the sign of the step. It is used in the proof of the persistence of the sign in the chain range (`Parking.persist`), in both of its regimes `Parking.caseA` and `Parking.caseFar`.

## Proof

$\gamma_k>0$ by `Parking.gam_pos`, and the inverse of a positive number is positive.

---
weight: step
short: value of the threshold profile
---
## Description

The threshold profile with parameters $y$ and $N$ takes the value $y/(N-s)$ at $s$; this is its definition, stated as an equation.

## Statement

For all real numbers $y$ and $N$ and every natural number $s$, $\lambda^{y,N}(s) = y/(N-s)$, where $\lambda^{y,N}$ is the threshold profile of `Parking.thr`.

## Explanation

The statement unfolds the definition `Parking.thr`. It exists so that proofs in other modules (`Parking.Lam_gain`, `Parking.curvSum_step`, `Parking.curv_ge_pair`) can pass from the profile to the fraction without unfolding the definition.

## Proof

Both sides are equal by the definition of the threshold profile.

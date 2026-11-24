---
weight: step
short: upper Stirling bound with the constant c_0
---
## Description

The upper Stirling bound of the Poisson mass written with $c_0 = 1/\sqrt{2\pi}$: $e^{-i} i^i/i! \le c_0/\sqrt{i}$ for every $i \ge 1$.

## Statement

For every natural number $i \ge 1$,

$$e^{-i}\,\frac{i^i}{i!} \le \frac{c_0}{\sqrt{i}},$$

where the left-hand side is the Poisson mass of `Parking.poissonMass` and $c_0 = 1/\sqrt{2\pi}$ (`Parking.c0`).

## Explanation

This is `Parking.poissonMass_le` with $1/\sqrt{2\pi i}$ written as $c_0/\sqrt{i}$. The proofs of the closed-form bounds `Parking.kap_diag_le`, `Parking.Asum_le`, `Parking.Gsum_le` and `Parking.Wsum_ge` bound sums in whose terms the Poisson mass occurs; they replace it by this bound, and in this form the constant factors out of the sums.

## Proof

By `Parking.poissonMass_le`, the Poisson mass is at most $1/\sqrt{2\pi i}$. Since $\sqrt{2\pi i} = \sqrt{2\pi}\,\sqrt{i}$, this is $c_0/\sqrt{i}$.

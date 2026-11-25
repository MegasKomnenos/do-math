---
weight: step
short: the Poisson mass is positive
---
## Description

The Poisson mass $e^{-n} n^n/n!$ is positive for every $n \ge 0$.

## Statement

For every natural number $n$, $e^{-n} n^n/n! > 0$, where $0^0 = 1$ (`Parking.poissonMass`).

## Explanation

Used wherever an inequality is divided by a Poisson mass.

## Proof

The Poisson mass is the product of $e^{-n} > 0$ and $n^n/n! > 0$ (`Parking.ren_pos`).

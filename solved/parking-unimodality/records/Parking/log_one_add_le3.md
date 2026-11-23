---
weight: step
short: cubic upper bound for log(1+u)
---
## Description

$\log(1+u)\le u-u^2/2+u^3/3$ for every real $u\ge0$.

## Statement

For every real number $u\ge0$, $\ \log(1+u)\le u-\dfrac{u^2}{2}+\dfrac{u^3}{3}$.

## Explanation

This is the case $n=3$ of the alternating Taylor bounds `Parking.log_one_add_taylor`. It is used in the bounds for the crossing criterion (module `Parking.Crossing.Bounds`), in the numerics of the persistence argument (`Parking.ChainColumn.Numerics`) and in the criterion for the next column (`Parking.NextColumn.Criterion`).

## Proof

`Parking.log_one_add_taylor` with $n=3$ states $0\le-\bigl(\log(1+u)-(u-u^2/2+u^3/3)\bigr)$.

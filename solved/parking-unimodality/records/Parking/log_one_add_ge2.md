---
weight: step
short: quadratic lower bound for log(1+u)
---
## Description

$u-u^2/2\le\log(1+u)$ for every real $u\ge0$.

## Statement

For every real number $u\ge0$, $\ u-\dfrac{u^2}{2}\le\log(1+u)$.

## Explanation

This is the case $n=2$ of the alternating Taylor bounds `Parking.log_one_add_taylor`, written out so that it can be used as it stands. It is used in the bounds for the crossing criterion (module `Parking.Crossing.Bounds`), in the numerics of the persistence argument (`Parking.ChainColumn.Numerics`) and in the criterion for the next column (`Parking.NextColumn.Criterion`).

## Proof

`Parking.log_one_add_taylor` with $n=2$ states $0\le\log(1+u)-(u-u^2/2)$.

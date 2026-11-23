---
weight: step
short: quintic upper bound for log(1+u)
---
## Description

$\log(1+u)\le u-u^2/2+u^3/3-u^4/4+u^5/5$ for every real $u\ge0$.

## Statement

For every real number $u\ge0$, $\ \log(1+u)\le u-\dfrac{u^2}{2}+\dfrac{u^3}{3}-\dfrac{u^4}{4}+\dfrac{u^5}{5}$.

## Explanation

This is the case $n=5$ of the alternating Taylor bounds `Parking.log_one_add_taylor`. It is used in the numerics of the crossing strip (module `Parking.Crossing.StripNumerics`).

## Proof

`Parking.log_one_add_taylor` with $n=5$ states $0\le-\bigl(\log(1+u)-(u-u^2/2+u^3/3-u^4/4+u^5/5)\bigr)$.

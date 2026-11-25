---
weight: step
short: quartic lower bound for log(1+u)
---
## Description

$u-u^2/2+u^3/3-u^4/4\le\log(1+u)$ for every real $u\ge0$.

## Statement

For every real number $u\ge0$, $\ u-\dfrac{u^2}{2}+\dfrac{u^3}{3}-\dfrac{u^4}{4}\le\log(1+u)$.

## Explanation

This is the case $n=4$ of the alternating Taylor bounds `Parking.log_one_add_taylor`. It is used in the proofs of `Parking.log_gam_sub_le` and `Parking.sbirth_ge`.

## Proof

`Parking.log_one_add_taylor` with $n=4$ states $0\le\log(1+u)-(u-u^2/2+u^3/3-u^4/4)$.

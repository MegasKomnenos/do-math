---
weight: step
short: quadratic lower bound for log(1+u)
---
## Description

$u-u^2/2\le\log(1+u)$ for every real $u\ge0$.

## Statement

For every real number $u\ge0$, $\ u-\dfrac{u^2}{2}\le\log(1+u)$.

## Explanation

This is the case $n=2$ of the alternating Taylor bounds `Parking.log_one_add_taylor`, written out so that it can be used as it stands. It is used in the proofs of `Parking.xk_bounds`, `Parking.Fk_anti`, `Parking.eps_succ_le_gam`, `Parking.theta_f_le`, `Parking.sbirth_ge` and `Parking.ledger`.

## Proof

`Parking.log_one_add_taylor` with $n=2$ states $0\le\log(1+u)-(u-u^2/2)$.

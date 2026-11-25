---
weight: step
short: the Cayley ratio in terms of the diagonal factor
---
## Description

For $m\ge2$: $(1+1/m)^{m-1}=\gamma_m\,(1+1/m)$, where $\gamma_m=(1+1/m)^{m-2}$.

## Statement

For every natural number $m\ge2$,
$$\Bigl(1+\frac1m\Bigr)^{m-1}=\gamma_m\Bigl(1+\frac1m\Bigr),$$
where $\gamma_m=(1+1/m)^{m-2}$ (`Parking.gam`).

## Explanation

The left-hand side is the ratio $a_{m+1}/a_m$ of consecutive Cayley numbers $a_j=j^{j-1}/j!$ (`Parking.cay_ratio`), and it is the reciprocal of the critical tilt (`Parking.xcrit_mul_psi`). The identity lets a statement about that ratio be rewritten with $\gamma_m$; it is used for the monotonicity `Parking.gam_mono` and where the diagonal lower bound is combined with the Cayley numbers. The hypothesis $m\ge2$ makes the exponent $m-2$ an ordinary difference.

## Proof

$(1+1/m)^{m-1}=(1+1/m)^{m-2}\,(1+1/m)$, because $m-1=(m-2)+1$ for $m\ge2$.

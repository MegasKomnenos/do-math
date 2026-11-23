---
weight: step
short: positivity of the second factorial moment of the number of parts
---
## Description

For $m \ge 2$ the sum $\sum_{q=1}^{m} q(q-1)\,T_{m,q}$ over the weights of the compositions of $m$ with $q$ parts is positive.

## Statement

For every natural number $m \ge 2$,

$$\sum_{q=1}^{m} q(q-1)\;T_{m,q} \;>\; 0,$$

where $T_{m,q}$ is the total weight of the compositions of $m$ with exactly $q$ parts, each part of size $p$ weighted by $a_p = p^{p-1}/p!$ (`Parking.Tq`).

## Explanation

The sum is the second factorial moment of the number of parts, before normalisation, and it is the factor that multiplies $D_m$ in `Parking.Dbirth_spec`. Its positivity allows an inequality that has been multiplied by it to be divided again: this is the last step in the comparison of factorial moments in the proof of `Parking.curv_ratio`, and in `Parking.Dbirth_nonneg` and `Parking.Dbirth_mono`. For $m = 1$ the sum is $0$, since the only composition has one part.

## Proof

By `Parking.Tq_eq` and `Parking.Pb_sum3`, as in the proof of `Parking.Dbirth_spec`, the sum equals $a_m \cdot 2m\,(m - s_m)$, where $s_m$ is the mean of the birthday law (`Parking.sbirth`). Here $a_m > 0$ by `Parking.cay_pos`, $m > 0$, and $m - s_m > 0$ by `Parking.sbirth_lt`.

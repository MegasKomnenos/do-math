---
weight: step
short: positivity of the resolvent sequence
---
## Description

The resolvent sequence of the frozen kernel is positive: $G_s > 0$ for every $s \ge 0$.

## Statement

For every natural number $s$, $G_s > 0$, where $G$ is the sequence of `Parking.Gres`.

## Explanation

Positivity is used wherever an inequality is multiplied or divided by a value of $G$: in the proof of `Parking.Gres_sum_le` and in the far rows of `Parking.caseFar`, where the final inequality is stated after multiplication by $G_\rho$.

## Proof

$G$ is the renewal sequence of the frozen kernel $f$ (`Parking.Gres_isRenewal`), and $f_i > 0$ for $i \ge 1$ (`Parking.fker_pos`). By `Parking.renewal_pos`, the renewal sequence of a kernel that is positive on the indices $i \ge 1$ is positive.

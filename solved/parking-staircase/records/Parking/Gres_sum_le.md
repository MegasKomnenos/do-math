---
weight: unit
short: total mass of the resolvent sequence
---
## Description

Every partial sum of the resolvent sequence of the frozen kernel is at most $2e$: $\sum_{s<N}G_s \le 2e$.

## Statement

For every natural number $N$,

$$\sum_{s=0}^{N-1} G_s \le 2e,$$

where $G$ is the sequence of `Parking.Gres`, the renewal sequence of the frozen kernel $f$ of `Parking.fker`.

## Explanation

The bound is the reciprocal of the defect of the kernel: the partial sums of $f$ stay below $1 - \frac1{2e}$, so a unit of mass entering the renewal process is multiplied by at most $1/(1 - (1 - \frac1{2e})) = 2e$ in total. In generating-function terms, $\sum_s G_s = 1/(1 - \sum_i f_i)$. The proof avoids infinite sums of $G$ by applying the resolvent identity to the constant sequence $1$.

In `Parking.caseFar` the far feedback of a row $k + \rho + 1$ is bounded by a constant times $\sum_{i\le\rho-\lfloor3k/5\rfloor}G_i$. For most columns the bound $2e$ is inserted there. For the columns $82 \le k \le 109$ in the last regime it is too weak by a small margin, and it is sharpened by subtracting a lower bound of the tail $\sum_{i\ge a}G_i$ obtained from `Parking.Gres_lower`; this, too, starts from the present statement, applied to a longer range.

## Proof

*The mass of the kernel.* For every $N$, $\sum_{i=1}^{N}f_i \le 1 - \frac12e^{-1}$. Indeed $f_i = e^{-i}\varepsilon_i$ plus $\frac12e^{-1}$ at $i = 1$; the terms $e^{-i}\varepsilon_i$ are nonnegative and their infinite sum is $1 - e^{-1}$ by `Parking.hasSum_eps`, so each partial sum is at most $1 - e^{-1}$, and the correction contributes at most $\frac12e^{-1}$.

*The constant sequence.* For $N = 0$ the sum is empty. Let $N \ge 1$ and write $N = N' + 1$. The constant sequence $v_s = 1$ satisfies $v_s = \iota_s + \sum_{i=1}^{s}f_iv_{s-i}$ with $\iota_s = 1 - \sum_{i=1}^{s}f_i$. By `Parking.resolvent`, applied with the renewal sequence $G$ of $f$ (`Parking.Gres_isRenewal`), a sequence with this property is the convolution of $G$ with $\iota$:

$$1 = \sum_{c=0}^{N'} G_{N'-c}\,\iota_c.$$

By the first step $\iota_c \ge \frac12e^{-1}$, and $G_{N'-c} > 0$ by `Parking.Gres_pos`. Hence $1 \ge \frac12e^{-1}\sum_{c=0}^{N'}G_{N'-c} = \frac12e^{-1}\sum_{s<N}G_s$, which is the claim.

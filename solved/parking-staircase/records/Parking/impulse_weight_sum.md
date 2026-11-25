---
weight: unit
short: sum of the impulse weights
---
## Description

For every natural number $R$: $\sum_{0<s<R} P(R-s)\,(R-1-s)\,\kappa_2(s) = \tfrac{R-3}{3}\,\kappa_3(R)$, where $P$ is the Poisson mass and $\kappa_2$, $\kappa_3$ are its twofold and threefold convolutions.

## Statement

For every natural number $R$,

$$\sum_{0 < s < R} P(R-s)\;(R-1-s)\;\kappa_2(s) \;=\; \frac{R-3}{3}\;\kappa_3(R),$$

where $P(n) = e^{-n} n^n/n!$ (`Parking.poissonMass`), $\kappa_2$ is the twofold convolution of `Parking.kc2` and $\kappa_3$ the threefold convolution of `Parking.kc3`.

## Explanation

The numbers $w_s = P(R-s)\,(R-1-s)\,\kappa_2(s)$, $0 < s < R$, are the weights of a sum that occurs in the upper bound of the boundary term of the pair–impulse criterion, `Parking.impulse_le`; the estimates call that term the impulse. There the first violating point identity `Parking.Lam_defect` produces a sum over a cut point $s$ of a chain of length $R$: the factor $R - 1 - s$ comes from the defect $1 - (K+1)/(K+R-s) = (R-1-s)/(K+R-s)$ of the cut factor at $s$, where $K$ is the threshold at which the boundary term is bounded, the factor $P(R-s)$ from the part of the chain after $s$, and the factor $\kappa_2(s)$ from one further cut point before $s$. The sum has the form $\sum_s w_s\, h(s)$ with a concave, decreasing function $h$, and it is bounded from above by the total weight $\sum_s w_s$ times the value of $h$ at a point that does not exceed the mean position of the weights. The present statement gives the total weight, and `Parking.impulse_weight_mean` bounds the mean position from below.

The weights are nonnegative for $0 < s < R$, and the total vanishes for $R \le 3$: for $R \le 2$ because $\kappa_3(R) = 0$, and for $R = 3$ because of the factor $R - 3$. In Lean the summand is `poissonMass (R - s) * ((R : ℝ) - 1 - s) * kc2 s` and the right side is `((R : ℝ) - 3) / 3 * kc3 R`.

## Proof

Write $R - 1 - s = (R-1) - s$. Then

$$\sum_{0<s<R} P(R-s)\,(R-1-s)\,\kappa_2(s) = (R-1) \sum_{0<s<R} \kappa_2(s)\,P(R-s) \;-\; \sum_{0<s<R} s\,\kappa_2(s)\,P(R-s).$$

The first sum is $\kappa_3(R)$ by the definition of `Parking.kc3`, and the second is $\tfrac{2R}{3}\,\kappa_3(R)$ by `Parking.kc3_mom_left`. The difference is $\bigl(R - 1 - \tfrac{2R}{3}\bigr)\kappa_3(R) = \tfrac{R-3}{3}\,\kappa_3(R)$.

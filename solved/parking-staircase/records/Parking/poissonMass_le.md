---
weight: unit
short: upper Stirling bound of the Poisson mass
---
## Description

The Poisson mass is at most its Stirling approximation: $e^{-n} n^n/n! \le 1/\sqrt{2\pi n}$ for every $n \ge 1$.

## Statement

For every natural number $n \ge 1$,

$$e^{-n}\,\frac{n^n}{n!} \le \frac{1}{\sqrt{2\pi n}},$$

where the left-hand side is the Poisson mass of `Parking.poissonMass`.

## Explanation

Stirling's formula says that the Poisson mass is asymptotic to $1/\sqrt{2\pi n}$. The statement is the classical fact that the approximation is an upper bound for every $n \ge 1$, with no correction factor; it is equivalent to $n! \ge \sqrt{2\pi n}\,(n/e)^n$. The matching lower bound, with the factor $1 - \frac{1}{12n}$, is `Parking.poissonMass_ge`.

The bound is the source of the upper estimates of the kernel $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`) and of the normalised parking numbers (`Parking.cc`) at tilts near $e^{-1}$ in the later parts (the Cayley sum at the critical tilt, the decay of the tilted prime kernel, the numerics of the chain range), and it enters the bound for the mean of the birthday law (`Parking.sbirth_le`). The form with the constant $c_0 = 1/\sqrt{2\pi}$ is `Parking.poissonMass_le_c0`.

The hypothesis $n \ge 1$ excludes $n = 0$, where the left-hand side is $1$ and the right-hand side is not defined (in Lean it is $1/0 = 0$, and the inequality would be false).

## Proof

By `Parking.poissonMass_eq`, the Poisson mass is $(n/e)^n/n!$. Mathlib's lower bound of Stirling's formula states $\sqrt{2\pi n}\,(n/e)^n \le n!$ for every $n$. Dividing by the positive numbers $n!$ and $\sqrt{2\pi n}$ gives $(n/e)^n/n! \le 1/\sqrt{2\pi n}$.

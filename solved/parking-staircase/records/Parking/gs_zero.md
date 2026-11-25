---
weight: step
short: first step ratio of the prime kernel
---
## Description

The first step ratio of the prime kernel is $g_1 = \frac12$.

## Statement

$g_1 = \frac12$, where $g_m$ is the step ratio of `Parking.gs`. In Lean, whose function `gs` counts from zero, this reads `gs 0 = 1/2`.

## Explanation

For $m \ge 2$ the ratio is given by the formula $g_m = \frac{m}{m+1}\bigl(1+\frac1{m-1}\bigr)^{m-1}$, which has no meaning at $m = 1$. The Lean formula `gs i` $= \frac{i+1}{i+2}(1+1/i)^i$ is evaluated at $i = 0$ with the convention $1/0 = 0$, and this statement records the resulting value. It is the value that makes $\varepsilon_2 = g_1\varepsilon_1$ true ($\varepsilon_2 = \frac12$, $\varepsilon_1 = 1$), and it is the base case in the proofs of `Parking.eps_step`, `Parking.eps_succ_le_gam` and `Parking.Fk_anti`.

## Proof

By evaluation of the formula: $\frac{0+1}{0+2}\cdot(1+0)^0 = \frac12$.

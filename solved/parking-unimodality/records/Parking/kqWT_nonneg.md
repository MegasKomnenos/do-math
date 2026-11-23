---
weight: step
short: nonnegativity of the tilted recursion weights
---
## Description

For a tilt $x \ge 0$ the tilted weights $(y-\gamma)^+ a_\gamma x^\gamma$ of the prime-kernel recursion are nonnegative.

## Statement

For every natural number $y$, every real number $x \ge 0$ and every natural number $\gamma$, $(y-\gamma)^+\, a_\gamma x^\gamma \ge 0$, where the left-hand side is the tilted weight `kqWT y x γ` and $a_\gamma = \gamma^{\gamma-1}/\gamma!$ (`Parking.cay`).

## Explanation

Because the weights of the recursion `Parking.kqT_rec` are nonnegative, inequalities between values of the tilted prime kernel can be passed through the recursion term by term. The nonnegativity of the kernel (`Parking.kqT_nonneg`) and its decay (`Parking.kqT_harmonic`, `Parking.kqT_succ_le`) are obtained in this way.

## Proof

The factor $(y-\gamma)^+$ is the cast of a natural number, $a_\gamma \ge 0$ by `Parking.cay_nonneg`, and $x^\gamma \ge 0$ for $x \ge 0$.

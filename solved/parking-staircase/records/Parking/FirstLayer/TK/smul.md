---
weight: step
short: property K of a nonnegative multiple
---
## Description

If a triple has property K at $k$, so does its multiple by a nonnegative real number.

## Statement

Let $k$ be a real number, let $(a,b,c)$ have property K at $k$ (`Parking.FirstLayer.TK`), and let $r\ge 0$. Then $(ra,\,rb,\,rc)$ has property K at $k$.

## Explanation

The multiplier is the same for the three components. In the last-car recursion such multipliers are the constants $x_k\,\omega_i$ that do not depend on the threshold (`Parking.FirstLayer.kernel_TK`). A multiplier that depends on the threshold is a different matter; see `Parking.FirstLayer.TK.mul_ratio`.

## Proof

For each $\mu\ge 0$, multiply the defining inequality $2e^{\mu/k}b\le e^{\mu}c+e^{-\mu}a$ by $r\ge 0$.

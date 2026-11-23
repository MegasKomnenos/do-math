---
weight: step
short: positivity of the prime kernel
---
## Description

The numbers $\varepsilon_m = (m-1)^{m-1}/m!$ are positive for every $m \ge 1$.

## Statement

For every natural number $m \ge 1$ we have $\varepsilon_m > 0$. Here $\varepsilon$ is the sequence of `Parking.eps`: $\varepsilon_m = (m-1)^{m-1}/m!$ for $m \ge 1$, so that $\varepsilon_1 = 1$, and $\varepsilon_0 = 0$.

## Explanation

The hypothesis $m \ge 1$ is needed because `Parking.eps` sets $\varepsilon_0 = 0$. At $m = 1$ the formula reads $0^0/1! = 1$. The record of `Parking.eps_nonneg` gives only $\varepsilon_m \ge 0$. The strict sign is what the arguments about the kernel need: it is the positivity hypothesis under which log-convexity is turned into the cross form (`Parking.eps_cross`), it gives the positivity of the tilted kernel (`Parking.kapx_pos`) and of the frozen kernel (`Parking.fker_pos`), and it is the hypothesis on the kernel in `Parking.persistence_inequality`.

## Proof

Write $m = i + 1$. By `Parking.eps_succ`, $\varepsilon_{i+1} = i^i/(i+1)!$. For $i = 0$ this is $1$. For $i \ge 1$ the numerator and the denominator are positive.

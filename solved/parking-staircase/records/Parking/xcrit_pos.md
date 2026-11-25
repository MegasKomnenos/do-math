---
weight: step
short: positivity of the critical tilt
---
## Description

The critical tilt $x_k = (k/(k+1))^{k-1}$ is positive for every natural number $k$.

## Statement

For every natural number $k$, $x_k > 0$, where $x_k = (k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`).

## Explanation

Positivity of the tilt is what makes tilting harmless for signs: an inequality multiplied by $x_k^n$ keeps its direction. Almost every statement at the critical tilt uses it. The case $k = 0$ is included because in Lean the exponent $k-1$ is then $0$ and the value is $1$.

## Proof

For $k = 0$ the value is $(0/1)^0 = 1$. For $k \ge 1$ the base $k/(k+1)$ is positive, and so is its power.

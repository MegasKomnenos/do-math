---
weight: step
short: the critical tilt is at most one
---
## Description

The critical tilt $x_k = (k/(k+1))^{k-1}$ is at most $1$ for every natural number $k$.

## Statement

For every natural number $k$, $x_k \le 1$, where $x_k = (k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`).

## Explanation

The bound is used in the proof of `Parking.order_pos`, in a comparison of two values of the tilted prime kernel on the free range, where a higher power of $x_k$ is bounded by a lower one.

## Proof

The base $k/(k+1)$ lies in $[0,1]$, so every power of it with a natural exponent is at most $1$.

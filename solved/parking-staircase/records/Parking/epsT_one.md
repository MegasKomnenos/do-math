---
weight: step
short: the tilted free prime kernel at index one
---
## Description

The tilted free prime kernel at the index $1$ is the tilt: $\varepsilon_1 x = x$.

## Statement

For every real number $x$, $\varepsilon_1\, x^1 = x$, where $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`) and $\varepsilon_m x^m$ is the tilted free prime kernel (`Parking.epsT`).

## Explanation

Since the tilted prime kernel of a threshold $k \ge 1$ agrees with the tilted free kernel at $m = 1$, this is also its first value. It is used in the argument for the rows $n\ge2k$, in the proof of `Parking.order_pos`, in a comparison of two values of the tilted prime kernel on the free range, where the indices $1$ and $2$ are treated by their explicit values.

## Proof

$\varepsilon_1 = 1$ (`Parking.eps_one`).

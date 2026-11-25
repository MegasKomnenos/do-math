---
weight: step
short: ratio of consecutive tilted Cayley masses
---
## Description

$c_{j+1} x^{j+1} = x\,(1 + 1/(j+1))^{j}\, c_j x^j$: the ratio of consecutive tilted Cayley masses.

## Statement

For every real number $x$ and every natural number $j$,
$$c_{j+1}\, x^{j+1} \;=\; x \Bigl(1 + \frac{1}{j+1}\Bigr)^{j}\; c_j\, x^j ,$$
where $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`) and $c_n x^n$ is the tilted Cayley mass (`Parking.ccT`).

## Explanation

The factor $(1+1/(j+1))^j$ is of the form $(1+1/i)^{i-1}$ with $i = j+1$, and this expression increases with $i$ (`Parking.psi_mono`). So for a fixed tilt the ratio of consecutive masses increases with the index: the masses decrease as long as the ratio is below $1$ and increase afterwards. The monotonicity statements at the critical tilt, `Parking.ccT_succ_le` and `Parking.ccT_le_succ`, are read off from this formula.

## Proof

`Parking.cay_ratio` at the index $j+1$ gives $a_{j+2} = (1 + 1/(j+1))^{j}\, a_{j+1}$ for the tree numbers $a_n = n^{n-1}/n!$, and $c_n = a_{n+1}$ by definition. Hence $c_{j+1} = (1+1/(j+1))^{j} c_j$; multiply by $x^{j+1} = x \cdot x^j$.

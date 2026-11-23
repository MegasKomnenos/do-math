---
weight: unit
short: the tilted last-car recursion
---
## Description

For a threshold $y \ge 1$ and a tilt $x$, the tilted environment $u_N = z^{(y)}_N x^N$ satisfies $(N+1)\,u_{N+1} = x \sum_{i=0}^{N} \min(i+1,y)\, u_i\, u_{N-i}$.

## Statement

Let $y \ge 1$ be a natural number, $x$ a real number, and $u_N = z^{(y)}_N x^N$ the tilted environment of the threshold $y$ (`Parking.zrT`; $z^{(y)}_N = A(N,y-1)/N!$). Then for every natural number $N$,
$$(N+1)\, u_{N+1} \;=\; x \sum_{i=0}^{N} \min(i+1,y)\; u_i\, u_{N-i} .$$

## Explanation

This is the last-car recursion of the counts $A(n,y-1)$ (`Parking.A_succ`), divided by $N!$ (`Parking.zr_isWSol`) and multiplied by $x^{N+1}$. The indices of the two factors in each term add up to $N$, one less than the index on the left, so the tilt leaves the form of the recursion unchanged and contributes the single factor $x$ in front of the sum. Together with $u_0 = 1$ (`Parking.zrT_zero`) the recursion determines the tilted environment.

The weight $\min(i+1,y)$ is where the threshold acts. For $i+1 \le y$ it is the weight $i+1$ of the unrestricted recursion, and from $i + 1 = y$ on it stays at $y$. The monotonicity of the tilted environment at the critical tilt (`Parking.zrT_anti_crit`) is proved from this recursion by taking the difference of two consecutive instances, and the first-layer analysis of the left half sorts the terms of the same recursion according to whether the two pieces lie in the free range.

## Proof

By `Parking.zr_isWSol`, whose content is the second condition in the definition of a solution of the weighted recursion (`Parking.IsWSol`), for $y \ge 1$,
$$(N+1)\, z^{(y)}_{N+1} \;=\; \sum_{i=0}^{N} \min(i+1,y)\; z^{(y)}_i\, z^{(y)}_{N-i} .$$
Multiply by $x^{N+1}$ and write $x^{N+1} = x \cdot x^{i} \cdot x^{N-i}$ in the term of index $i$.

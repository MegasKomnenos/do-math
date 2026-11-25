---
weight: step
short: monotonicity of the environment in the threshold
---
## Description

The normalised cumulative count $z^{(y)}_n=A(n,y-1)/n!$ is nondecreasing in the threshold $y$.

## Statement

For all natural numbers $y\le y'$ and $n$, $z^{(y)}_n\le z^{(y')}_n$, where $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`). The statement includes $y=0$, for which the Lean definition gives $z^{(0)}_n=z^{(1)}_n$.

## Explanation

Raising the threshold admits more parking functions. This is the normalised form of `Parking.A_mono`. It is one of the two comparisons of factors in the proof of the stochastic monotonicity `Parking.zr_diag_mono`, and it gives the monotonicity of the tilted environment in the threshold (`Parking.zrT_le_zrT`).

## Proof

Since $y\le y'$ implies $y-1\le y'-1$ for the truncated subtraction, `Parking.A_mono` gives $A(n,y-1)\le A(n,y'-1)$. Dividing by $n!>0$ gives the claim.

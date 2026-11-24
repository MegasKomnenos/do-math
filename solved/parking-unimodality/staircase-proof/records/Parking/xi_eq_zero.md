---
weight: step
short: vanishing of the tree curvature below the column index
---
## Description

For $k\ge2$ the tree curvature of the column $k$ vanishes below the column index: $\xi_t=0$ for $t<k$.

## Statement

For all natural numbers $k\ge2$ and $t<k$, $\xi_t=0$, where $\xi=\xi^{(k)}$ is the tree curvature of the column $k$ (`Parking.xi`).

## Explanation

For $t<k$ the three thresholds $k+1$, $k$, $k-1$ are all at least $t$, so the three minima in the definition equal $t$, and the index $t-1$ lies in the free range of each threshold, where the three environments coincide with $c_{t-1}$. The second difference of a quantity that does not depend on the threshold is zero. Sums over the tree curvature therefore start at $t=k$ (`Parking.step_bound`).

## Proof

For $t=0$, $\xi_0=0$ by definition. For $t=s+1$ with $s+1<k$, `Parking.xi_succ` gives
$$(s+1)\,\xi_{s+1}=\min(s+1,k+1)\,z^{(k+1)}_s-2\min(s+1,k)\,z^{(k)}_s+\min(s+1,k-1)\,z^{(k-1)}_s .$$
Since $s+1\le k-1$, the three minima are $s+1$. Since $s\le k-1$ and $k-1\ge1$, `Parking.zr_eq_cc` gives $z^{(k+1)}_s=z^{(k)}_s=z^{(k-1)}_s=c_s$. The right-hand side is $(s+1)c_s(1-2+1)=0$.

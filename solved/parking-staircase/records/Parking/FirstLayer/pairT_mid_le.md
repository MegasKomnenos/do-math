---
weight: step
short: upper bound of the middle pair sum
---
## Description

For $k\ge 3$ and $\rho+n+2=k$: $Q_\rho(n+1)\le(n+2)\,\omega_\rho\,\omega_k$, where $Q_\rho$ is the pair sum of the tilted Cayley masses $\omega$ at the critical tilt $x_k$.

## Statement

Let $k\ge 3$, $\rho$, $n$ be natural numbers with $\rho+n+2=k$, $\omega_m=c_mx_k^{\,m}$ the tilted Cayley masses at the critical tilt $x_k$ (`Parking.ccT`, `Parking.xcrit`) and $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\omega_{\rho+j-a}$ (`Parking.FirstLayer.pairT`). Then
$$Q_\rho(n+1)\le(n+2)\,\omega_\rho\,\omega_k .$$

## Explanation

$Q_\rho(n+1)$ has $n+2$ terms $\omega_p\omega_q$ with $p+q=\rho+(k-1)$, and by log-convexity the largest is the one with the extreme indices, $\omega_\rho\,\omega_{k-1}=\omega_\rho\,\omega_k$. The number of terms is $n+2=k-\rho$. The bound is used in `Parking.FirstLayer.Sdir_TK` for large tilts, where a defect proportional to the middle pair sum has to be compared with a multiple of $\omega_\rho\omega_k$.

## Proof

By `Parking.FirstLayer.ccT_logconvex` with $m=n+1$, each term satisfies $\omega_{\rho+a}\,\omega_{\rho+n+1-a}\le\omega_\rho\,\omega_{\rho+n+1}$ for $0\le a\le n+1$. Here $\rho+n+1=k-1$, and $\omega_{k-1}=\omega_k$ by `Parking.FirstLayer.ccT_top`. Summing over the $n+2$ values of $a$ gives the claim.

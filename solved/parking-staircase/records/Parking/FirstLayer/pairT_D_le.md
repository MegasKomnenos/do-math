---
weight: step
short: tilted difference of the outer pair sums
---
## Description

For $k\ge 3$, $\rho+n+2=k$ and real $\mu\le 1/(k(k+2))$: $e^{\mu}Q_\rho(n+2)-e^{-\mu}Q_\rho(n)\le 2e^{\mu}\,\omega_\rho\,\omega_k$, where $Q_\rho$ is the pair sum of the tilted Cayley masses $\omega$ at the critical tilt $x_k$.

## Statement

Let $k\ge 3$, $\rho$, $n$ be natural numbers with $\rho+n+2=k$, $\omega_m=c_mx_k^{\,m}$ the tilted Cayley masses at the critical tilt $x_k$ (`Parking.ccT`, `Parking.xcrit`) and $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\omega_{\rho+j-a}$ (`Parking.FirstLayer.pairT`). For every real $\mu\le\dfrac{1}{k(k+2)}$,
$$e^{\mu}\,Q_\rho(n+2)-e^{-\mu}\,Q_\rho(n)\ \le\ 2\,e^{\mu}\,\omega_\rho\,\omega_k .$$

## Explanation

$Q_\rho(n+2)$ has two more terms than $Q_\rho(n)$. The statement says that, for small tilts, the tilted difference of the two is at most the two end terms of the longer sum, each of which is $\omega_\rho\omega_k$: every inner term of $Q_\rho(n+2)$, multiplied by $e^{\mu}$, is dominated by the term of $Q_\rho(n)$ with both indices lowered by one, multiplied by $e^{-\mu}$. It is used in `Parking.FirstLayer.Sdir_TK` for the tilts $0\le\mu\le 1/(k(k+2))$. The restriction on $\mu$ comes from `Parking.FirstLayer.ccT_step_down`, and it is the reason why `Parking.FirstLayer.Sdir_TK` treats larger tilts differently.

## Proof

Split off from $Q_\rho(n+2)=\sum_{a=0}^{n+2}\omega_{\rho+a}\omega_{\rho+n+2-a}$ the terms $a=0$ and $a=n+2$. Since $\rho+n+2=k$, each of them equals $\omega_\rho\,\omega_k$. The remaining terms are $\omega_{\rho+b+1}\,\omega_{\rho+(n-b)+1}$ for $0\le b\le n$.

For such $b$, `Parking.FirstLayer.ccT_step_down` applies at the indices $\rho+b$ and $\rho+(n-b)$, since both are at most $k-2$: $e^{\mu}\omega_{\rho+b+1}\le\omega_{\rho+b}$ and $e^{\mu}\omega_{\rho+(n-b)+1}\le\omega_{\rho+(n-b)}$. Multiplying the two (all quantities are nonnegative) and then multiplying by $e^{-\mu}$,
$$e^{\mu}\,\omega_{\rho+b+1}\,\omega_{\rho+(n-b)+1}\ \le\ e^{-\mu}\,\omega_{\rho+b}\,\omega_{\rho+(n-b)} .$$
The right side is $e^{-\mu}$ times the $b$-th term of $Q_\rho(n)$. Summing over $b=0,\dots,n$: $e^{\mu}\big(Q_\rho(n+2)-2\omega_\rho\omega_k\big)\le e^{-\mu}Q_\rho(n)$.

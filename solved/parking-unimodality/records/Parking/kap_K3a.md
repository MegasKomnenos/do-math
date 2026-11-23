---
weight: step
short: harmonic decay of the tilted prime kernel beyond the free range
---
## Description

For $k\ge 2$ and $L\ge k$: $L\,\kappa_L\le k\,\kappa_k$, where $\kappa_m$ is the prime kernel of the threshold $k$ tilted by the critical tilt $x_k$.

## Statement

Let $k\ge 2$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), and $\kappa_m=x_k^{\,m}\,[X^m]K_k$ the tilted prime kernel of the threshold $k$ (`Parking.kqT k (xcrit k) m`), where $K_k=1-1/Z_k$ and $Z_k=\sum_n z^{(k)}_nX^n$ is the series of the threshold $k$. Then for every natural number $L\ge k$,
$$L\,\kappa_L\le k\,\kappa_k .$$

## Explanation

Beyond the free range $1\le m\le k$, where $\kappa_m=\varepsilon_mx_k^{\,m}$ is explicit, the kernel is known only through its recursion. The statement says that there it decays at least like $1/L$. It is one of the estimates that bound the kernel weight $\kappa_{n-q+1}$ of the crossing row in `Parking.big_columns` and that order the kernel weights in `Parking.order_pos`. A faster decay for $L\ge 2k-1$ is `Parking.kap_K3b`.

## Proof

`Parking.kqT_harmonic` states, for a threshold $y\ge 2$ and a tilt $x\ge 0$ at which $\varepsilon_mx^m$, $\varepsilon_m=(m-1)^{m-1}/m!$, does not increase on $1\le m\le y$, that $(m+1)\,x^{m+1}[X^{m+1}]K_y\le m\,x^{m}[X^m]K_y$ for every $m\ge y$. At the critical tilt the hypothesis holds by `Parking.epsT_succ_le`. So $(m+1)\kappa_{m+1}\le m\kappa_m$ for $m\ge k$, and induction on $L$ from $k$ gives the claim.

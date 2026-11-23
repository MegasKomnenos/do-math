---
weight: step
short: log-convexity of the tilted Cayley masses
---
## Description

The tilted Cayley masses $\omega_n=c_nx_k^{\,n}$ are log-convex: $\omega_{\rho+a}\,\omega_{\rho+m-a}\le\omega_\rho\,\omega_{\rho+m}$ for $a\le m$.

## Statement

Let $k$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $\omega_n=c_nx_k^{\,n}$, $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). For natural numbers $\rho$, $m$, $a$ with $a\le m$,
$$\omega_{\rho+a}\,\omega_{\rho+m-a}\;\le\;\omega_\rho\,\omega_{\rho+m}.$$

## Explanation

Among the products $\omega_p\omega_q$ with $p,q\ge\rho$ and $p+q=2\rho+m$, the product of the two extreme indices is the largest. The inequality does not depend on the tilt, since both sides carry the same power $x_k^{\,2\rho+m}$; it is the log-convexity of the numbers $a_j=j^{j-1}/j!$, of which $c_n=a_{n+1}$. It is used in `Parking.FirstLayer.pairT_mid_le` to bound a pair sum by its number of terms times its largest term.

## Proof

`Parking.cay_logconvex` states $a_{u+c}\,a_v\le a_u\,a_{v+c}$ for natural numbers $1\le u\le v$ and $c$. Take $u=\rho+1$, $v=\rho+m-a+1$ and $c=a$; then $u\le v$ because $a\le m$, and the inequality reads $c_{\rho+a}\,c_{\rho+m-a}\le c_\rho\,c_{\rho+m}$. Multiply by $x_k^{\,\rho+a}x_k^{\,\rho+m-a}=x_k^{\,\rho}x_k^{\,\rho+m}\ge 0$.

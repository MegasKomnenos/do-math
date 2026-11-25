---
weight: step
short: surplus of the tilted convexity at the top, bound for small tilts
---
## Description

At the critical tilt of a column $k\ge 3$, for every real $\mu$: $e^{\mu}\omega_{k+1}+e^{-\mu}\omega_{k-1}-2e^{\mu/k}\omega_k\ \ge\ \omega_k\Big(\dfrac{3}{2(k+1)(k+2)}-2\big(e^{\mu/k}-1\big)\Big)$, where $\omega_n=c_nx_k^{\,n}$.

## Statement

Let $k\ge 3$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $\omega_n=c_nx_k^{\,n}$, $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). For every real $\mu$,
$$\omega_k\Big(\frac{3}{2(k+1)(k+2)}-2\big(e^{\mu/k}-1\big)\Big)\ \le\ e^{\mu}\,\omega_{k+1}+e^{-\mu}\,\omega_{k-1}-2\,e^{\mu/k}\,\omega_k .$$

## Explanation

A second lower bound for the surplus at the top, the quantity bounded in `Parking.FirstLayer.ccT_tilt_top`. It is useful only when $\mu/k$ is small, where its right side is close to $\omega_k\cdot\frac{3}{2(k+1)(k+2)}$; this is about three times the value $\omega_k\cdot\frac{k^2-2k-1}{2k^2(k+1)(k+2)}$ that `Parking.FirstLayer.ccT_tilt_top` gives at $\mu=0$. `Parking.FirstLayer.Sdir_TK` needs this larger constant for the tilts $0\le\mu\le 1/(k(k+2))$: there the surplus, divided by $\omega_k$, has to exceed $e^{\mu}/((k+\rho)(k+\rho+1))$ for an excess $\rho\ge 1$, which can be as large as about $1/((k+1)(k+2))$. For large $\mu$ the right side is negative and the statement says nothing.

## Proof

As in the record of `Parking.FirstLayer.ccT_tilt_top`, with $\varphi(y)=(y-1)\log(1+1/y)$ and $\zeta=\varphi(k+1)-\varphi(k)$, the right side of the claim equals $\omega_k\big(e^{\mu+\zeta}+e^{-\mu}-2e^{\mu/k}\big)$. By $e^{t}\ge 1+t$, used for $t=\mu+\zeta$ and $t=-\mu$, $e^{\mu+\zeta}+e^{-\mu}\ge 2+\zeta$. Fact (a) of the record of `Parking.FirstLayer.ccT_tilt_mid`, at $y=k+1$, is $\zeta\ge\dfrac{3}{2(k+1)(k+2)}$. Hence
$$e^{\mu+\zeta}+e^{-\mu}-2e^{\mu/k}\ \ge\ \frac{3}{2(k+1)(k+2)}-2\big(e^{\mu/k}-1\big),$$
and multiplication by $\omega_k>0$ gives the claim.

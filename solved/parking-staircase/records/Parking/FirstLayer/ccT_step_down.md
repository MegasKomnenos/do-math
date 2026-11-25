---
weight: step
short: quantitative decrease of the Cayley masses below the top
---
## Description

At the critical tilt of a column $k\ge 3$: $e^{\mu}\,\omega_{j+1}\le\omega_j$ for every $j$ with $j+2\le k$ and every real $\mu\le 1/(k(k+2))$, where $\omega_n=c_nx_k^{\,n}$.

## Statement

Let $k\ge 3$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $\omega_n=c_nx_k^{\,n}$, $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). For every natural number $j$ with $j+2\le k$ and every real $\mu\le\dfrac{1}{k(k+2)}$,
$$e^{\mu}\,\omega_{j+1}\le\omega_j .$$

## Explanation

Below the top the sequence $\omega$ decreases at each step by a factor of at least $\exp\!\big(1/(k(k+2))\big)$; the step from $k-1$ to $k$, where $\omega_{k-1}=\omega_k$, is excluded by $j+2\le k$. The bound is used in `Parking.FirstLayer.pairT_D_le` to compare the pair sums of two different lengths term by term, and the threshold $1/(k(k+2))$ is the place where `Parking.FirstLayer.Sdir_TK` divides the tilts into small and large.

## Proof

With $\varphi(y)=(y-1)\log(1+1/y)$, the record of `Parking.FirstLayer.ccT_tilt_mid` shows $\omega_{j+1}=\omega_j\,e^{\varphi(j+1)-\varphi(k)}$, that is, $\omega_j=\omega_{j+1}\,e^{\varphi(k)-\varphi(j+1)}$. So it suffices that $\mu\le\varphi(k)-\varphi(j+1)$.

Since $(1+1/i)^{i-1}$ is nondecreasing in the integer $i\ge 1$ (`Parking.psi_mono`), $\varphi$ is nondecreasing on the positive integers, and $j+1\le k-1$ gives $\varphi(j+1)\le\varphi(k-1)$. Fact (a) of the record of `Parking.FirstLayer.ccT_tilt_mid`, at $y=k$, is $\varphi(k)-\varphi(k-1)\ge\dfrac{3}{2k(k+1)}$. Finally $\dfrac{1}{k(k+2)}\le\dfrac{3}{2k(k+1)}$, because $2(k+1)\le 3(k+2)$. Hence $\mu\le\varphi(k)-\varphi(k-1)\le\varphi(k)-\varphi(j+1)$.

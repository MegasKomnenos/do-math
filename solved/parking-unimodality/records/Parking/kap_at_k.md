---
weight: step
short: size of the tilted prime kernel at the index k
---
## Description

For $k\ge 82$: $\kappa_k\le\dfrac{0.662}{k\sqrt k}$, where $\kappa_m$ is the prime kernel of the threshold $k$ tilted by the critical tilt $x_k$.

## Statement

Let $k\ge 82$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), and $\kappa_m=x_k^{\,m}\,[X^m]K_k$ the tilted prime kernel of the threshold $k$ (`Parking.kqT k (xcrit k) m`). Then
$$\kappa_k\le\frac{0.662}{k\sqrt{k}} .$$

## Explanation

The index $k$ is the last one of the free range $1\le m\le k$, in which $\kappa_m=\varepsilon_mx_k^{\,m}$ with $\varepsilon_m=(m-1)^{m-1}/m!$. By Stirling's formula $\varepsilon_m$ is about $e^{m-1}/(m\sqrt{2\pi m})$, and $e\,x_k\le e^{3/(2k)}$ is only slightly larger than $1$, so $\kappa_k$ is about $e^{1/2}/(k\sqrt{2\pi k})\approx 0.658/(k\sqrt k)$. The decay estimates `Parking.kap_K3a` and `Parking.kap_K3b` are relative to $\kappa_k$; this statement supplies the absolute size. The constant is fitted to the arithmetic of the row step in `Parking.big_columns`; the inequality used in the proof holds from $k=79$ on.

## Proof

**The free kernel in closed form.** For $2\le L\le k$,
$$\kappa_L=p_{L-1}\,\frac{(e\,x_k)^{L}}{e\,L},\qquad p_n=e^{-n}\frac{n^n}{n!}$$
(`Parking.poissonMass`). Indeed $\kappa_L=\varepsilon_Lx_k^{\,L}$ by `Parking.kqT_eq_epsT`, and $L\,\varepsilon_L=(L-1)^{L-1}/(L-1)!=p_{L-1}e^{L-1}$ by `Parking.mul_eps`.

**An upper bound in the free range.** For $2\le L\le k$,
$$\kappa_L\le\frac{\exp\!\big(\frac{3L}{2k}-1\big)}{L\,\sqrt{2\pi(L-1)}} ,$$
by $p_{L-1}\le 1/\sqrt{2\pi(L-1)}$ (`Parking.poissonMass_le`) and $e\,x_k\le e^{3/(2k)}$ (`Parking.exp_one_mul_xcrit_le`).

**At $L=k$.** The bound is $e^{1/2}/\big(k\sqrt{2\pi(k-1)}\big)$, and it remains to see $e^{1/2}\sqrt{k}\le 0.662\sqrt{2\pi(k-1)}$, that is, after squaring, $e\,k\le 0.662^2\cdot 2\pi\,(k-1)$. With $e<2.7182818286$ and $\pi>3.1415$ this is a linear inequality in $k$ that holds for $k\ge 82$.

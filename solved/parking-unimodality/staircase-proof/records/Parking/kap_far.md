---
weight: step
short: size of the tilted prime kernel at the indices beyond 0.73k
---
## Description

For $k\ge 82$ and $L-1\ge 0.73\,k$: $\kappa_L\le\dfrac{0.73}{k\sqrt k}$, where $\kappa_m$ is the prime kernel of the threshold $k$ tilted by the critical tilt $x_k$.

## Statement

Let $k\ge 82$ and $L$ be natural numbers with $100\,(L-1)\ge 73\,k$, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), and $\kappa_m=x_k^{\,m}\,[X^m]K_k$ the tilted prime kernel of the threshold $k$ (`Parking.kqT k (xcrit k) m`). Then
$$\kappa_L\le\frac{0.73}{k\sqrt{k}} .$$

## Explanation

In the row step of the proof of `Parking.step_pos_large`, at a row $n\ge 2k$ of a column whose step is first positive in the row $q\le k+\frac{27}{100}k$, the kernel weight that multiplies the weighted debt is $\kappa_L$ with $L=n-q+1$, and $L-1=n-q\ge 0.73k$. When $L\le k$ the index is in the free range and this statement gives the size of the weight; for larger $L$ the decay estimates `Parking.kap_K3a` and `Parking.kap_K3b` together with `Parking.kap_at_k` are used. The constant $0.73$ is fitted to the arithmetic of that step. Since the kernel does not increase, the statement holds for all $L$ with $L-1\ge 0.73k$, not only for $L\le k$.

## Proof

Let $t=\lceil 73k/100\rceil$, so $73k\le 100t\le 73k+99$. Then $t+1\le L$, and $t+1\le k$ because $k\ge 82$. The kernel does not increase on the indices $m\ge 1$ (`Parking.kqT_succ_le`; its hypothesis on the free kernel holds at the critical tilt by `Parking.epsT_succ_le`), so $\kappa_L\le\kappa_{t+1}$. The index $t+1$ lies in the free range, where, as shown in the record of `Parking.kap_at_k`,
$$\kappa_{t+1}\le\frac{e^{y}}{(t+1)\sqrt{2\pi t}},\qquad y=\frac{3(t+1)}{2k}-1 .$$
From the bounds on $t$, $0\le y\le 1.7$, so $e^{y}\le 1+y+y^2$ (`Parking.exp_le_quadratic`). With $yk=\frac32(t+1)-k$, the inequality $(1+y+y^2)\,k\le 1.563368\,(t+1)$ is the polynomial inequality $k^2+(yk)k+(yk)^2\le 1.563368\,(t+1)\,k$, which holds for $k\ge 82$ and $0.73k\le t\le 0.73k+0.99$; this is a routine verification. Finally $\sqrt{2\pi t}\ge 2.1416\sqrt{k}$, because $2\pi\cdot 0.73\ge 2.1416^2$ with $\pi>3.1415$. Together,
$$\kappa_{t+1}\le\frac{1.563368\,(t+1)}{k}\cdot\frac{1}{(t+1)\cdot 2.1416\sqrt{k}}\le\frac{0.73}{k\sqrt{k}} .$$

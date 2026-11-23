---
weight: step
short: quadratic decay of the tilted prime kernel from the index 2k−1 on
---
## Description

For $k\ge 2$ and $L\ge 2k-1$: $(L-1)\,L\,\kappa_L\le 2k(k-1)\,\kappa_k$, where $\kappa_m$ is the prime kernel of the threshold $k$ tilted by the critical tilt $x_k$.

## Statement

Let $k\ge 2$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), and $\kappa_m=x_k^{\,m}\,[X^m]K_k$ the tilted prime kernel of the threshold $k$ (`Parking.kqT k (xcrit k) m`; $K_k=1-1/Z_k$, $Z_k=\sum_nz^{(k)}_nX^n$). Then for every natural number $L\ge 2k-1$,
$$(L-1)\,L\,\kappa_L\le 2k(k-1)\,\kappa_k .$$

## Explanation

From the index $2k-1$ on the kernel decays at least like $1/L^2$. More generally the proof shows a decay of rate $j$, $(m+1)\kappa_{m+1}\le(m+1-j)\kappa_m$, once $m\ge k+(j-1)(k-1)$: each further block of $k-1$ indices gains one unit in the rate. Only the rates $1$ (`Parking.kap_K3a`) and $2$ (the present statement) are stated; the general rate is used once more, inside the proof of `Parking.order_pos`. The statement bounds the kernel weight of the crossing row in `Parking.big_columns` for the rows $n$ that are far from the crossing.

## Proof

Three facts about $\kappa$ are used. (i) The recursion `Parking.kqT_rec`: for $N\ge k$, $N\kappa_N=\sum_{\gamma=1}^{k-1}h_\gamma\,\kappa_{N-\gamma}$ with $h_\gamma=(k-\gamma)\,a_\gamma\,x_k^{\,\gamma}\ge 0$, $a_\gamma=\gamma^{\gamma-1}/\gamma!$ (`Parking.kqWT_nonneg`; the weights vanish for $\gamma\ge k$). (ii) $(m+1)\kappa_{m+1}\le m\kappa_m$ for $m\ge k$ (`Parking.kqT_harmonic`, whose hypothesis on the free kernel holds at the critical tilt by `Parking.epsT_succ_le`). (iii) $\kappa$ does not increase on the indices $m\ge 1$ (`Parking.kqT_succ_le`, with the same hypothesis).

**One step of the recursion.** Let $m\ge k$ and $\rho$ real. If $\kappa_{i+1}\le\rho\,\kappa_i$ for all $i$ with $m-k+1\le i\le m-1$, then $(m+1)\kappa_{m+1}\le\rho\,m\,\kappa_m$. Indeed, by (i) at $m+1$ and at $m$, $(m+1)\kappa_{m+1}=\sum_{\gamma=1}^{k-1}h_\gamma\kappa_{m+1-\gamma}\le\rho\sum_{\gamma=1}^{k-1}h_\gamma\kappa_{m-\gamma}=\rho\,m\,\kappa_m$, the indices $i=m-\gamma$ being those of the window.

**Rate $j$.** For every $j\ge 1$ and $m\ge k+(j-1)(k-1)$: $(m+1)\kappa_{m+1}\le(m+1-j)\kappa_m$. Induction on $j$. For $j=1$ this is (ii). Assume the claim for $j$ and let $m\ge k+j(k-1)$. Every $i$ in the window $[m-k+1,m-1]$ satisfies $i\ge k+(j-1)(k-1)$, so $(i+1)\kappa_{i+1}\le(i+1-j)\kappa_i$; with (iii), $m\,\kappa_{i+1}=(i+1)\kappa_{i+1}+(m-i-1)\kappa_{i+1}\le(m-j)\kappa_i$. The one-step statement with $\rho=(m-j)/m$ gives $(m+1)\kappa_{m+1}\le(m-j)\kappa_m$.

**The statement.** Induction on $L\ge 2k-1$. For $L=2k-1$, `Parking.kap_K3a` gives $(2k-1)\kappa_{2k-1}\le k\kappa_k$; multiply by $2k-2$. For the step, the rate $2$ applies to $m=L\ge 2k-1=k+(k-1)$: $(L+1)\kappa_{L+1}\le(L-1)\kappa_L$; multiply by $L$ and use the induction hypothesis.

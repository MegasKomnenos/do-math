---
weight: unit
short: property K of the pair sums
---
## Description

For $k\ge 3$ and $\rho+n+2=k$, the pair sums $Q_\rho(n)$, $Q_\rho(n+1)$, $Q_\rho(n+2)$ of tilted Cayley masses at the critical tilt $x_k$ form a triple with property K at $k$.

## Statement

Let $k\ge 3$, $\rho$, $n$ be natural numbers with $\rho+n+2=k$. Let $\omega_m=c_mx_k^{\,m}$ be the tilted Cayley masses at the critical tilt $x_k=(k/(k+1))^{k-1}$ (`Parking.ccT`, `Parking.xcrit`) and $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\omega_{\rho+j-a}$ the pair sums (`Parking.FirstLayer.pairT`). Then the triple $\big(Q_\rho(n),\,Q_\rho(n+1),\,Q_\rho(n+2)\big)$ has property K at $k$ (`Parking.FirstLayer.TK`): for every $\mu\ge 0$,
$$2e^{\mu/k}\,Q_\rho(n+1)\le e^{\mu}\,Q_\rho(n+2)+e^{-\mu}\,Q_\rho(n).$$

## Explanation

The three pair sums are those that occur in the last-car recursion at the thresholds $k-1$, $k$, $k+1$ and the same excess $\rho$: $Q_\rho(c-\rho-1)$ for $c=k-1,k,k+1$ (see `Parking.FirstLayer.Sdir`). The condition $\rho+n+2=k$ says that the largest index occurring in $Q_\rho(n+2)$ is exactly $k$, so that all indices lie in the range $0,\dots,k$ where the shape of $\omega$ is known. The statement is one of the two inputs of `Parking.FirstLayer.Sdir_TK`.

## Proof

Apply `Parking.FirstLayer.conv_TK` to the sequence $f(a)=\omega_{\rho+a}$ and the number $n$; note $n+2\le k$. Its four hypotheses hold:

1. $f(a)>0$, since all $\omega_m$ are positive (`Parking.ccT_pos`, `Parking.xcrit_pos`).
2. $f(n+1)\le f(a)$ for $a\le n$: the indices satisfy $\rho+a\le\rho+n+1=k-1\le k$, and $\omega$ does not increase up to the index $k$ (`Parking.FirstLayer.ccT_anti`).
3. $f(n+2)=f(n+1)$: this is $\omega_k=\omega_{k-1}$ (`Parking.FirstLayer.ccT_top`).
4. For $\mu\ge 0$ and $j\le n$, $2e^{\mu/k}f(j+1)\le e^{\mu}f(j+2)+e^{-\mu}f(j)$: this is `Parking.FirstLayer.ccT_tilt_mid` at the index $\rho+j$, which is admissible because $\rho+j+2\le k$.

The conclusion of `Parking.FirstLayer.conv_TK` is the claim, because the self-convolution of $f$ at the length $j$ is $Q_\rho(j)$ by definition.

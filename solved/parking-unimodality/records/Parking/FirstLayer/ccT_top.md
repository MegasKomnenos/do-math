---
weight: step
short: equal Cayley masses at the indices k−1 and k
---
## Description

At the critical tilt $x_k$ of a column $k\ge 1$, the tilted Cayley masses at the indices $k-1$ and $k$ are equal: $c_kx_k^{\,k}=c_{k-1}x_k^{\,k-1}$.

## Statement

Let $k\ge 1$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $\omega_n=c_nx_k^{\,n}$, $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). Then $\omega_k=\omega_{k-1}$.

## Explanation

This is the property that defines the critical tilt: $c_k/c_{k-1}=(1+1/k)^{k-1}$, and $x_k$ is the reciprocal of this number. Together with `Parking.FirstLayer.ccT_anti` it says that $\omega$ reaches its minimum over the indices $0,\dots,k$ at $k-1$ and $k$. The flat top $f(n+2)=f(n+1)$ required by `Parking.FirstLayer.conv_TK` is this equality.

## Proof

`Parking.ccT_succ_mul_xcrit` states $c_{n+1}x^{n+1}\cdot x_{n+1}=x\cdot c_nx^{n}$ for every real $x$ and every $n$. Take $x=x_k$ and $n=k-1$: $\omega_k\,x_k=x_k\,\omega_{k-1}$, and $x_k>0$. (The Lean proof passes through the exponential form $\omega_{n+1}=\omega_n e^{\varphi(n+1)-\varphi(k)}$ of the same identity, given in the record of `Parking.FirstLayer.ccT_tilt_mid`, at $n+1=k$.)

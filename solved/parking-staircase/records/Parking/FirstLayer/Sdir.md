---
weight: step
short: direct term of the first-layer recursion
---
## Description

The direct term $S_\rho(c)=x_k\,\omega_{\rho-1}\,\omega_c+\frac{x_k}{2}\cdot\frac{c+\rho+1}{c+\rho}\,Q_\rho(c-\rho-1)$: the direct part of the last-car recursion at the size $c+\rho$ and the threshold $c$, multiplied by $x_k$ and divided by the size.

## Statement

Let $k$, $\rho$, $c$ be natural numbers with $1\le\rho\le c-1$, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), $\omega_n=c_nx_k^{\,n}$, $c_n=(n+1)^{n-1}/n!$, the tilted Cayley masses (`Parking.ccT`) and $Q_\rho(j)=\sum_{a=0}^{j}\omega_{\rho+a}\omega_{\rho+j-a}$ the pair sums (`Parking.FirstLayer.pairT`). The direct term is
$$S_\rho(c)=x_k\,\omega_{\rho-1}\,\omega_c+\frac{x_k}{2}\cdot\frac{c+\rho+1}{c+\rho}\cdot Q_\rho(c-\rho-1).$$

## Explanation

With $u^{(c)}_N=z^{(c)}_Nx_k^{\,N}$ the tilted environment of the threshold $c$ (`Parking.zrT`), the last-car recursion at the size $c+\rho$, divided by the size, is
$$u^{(c)}_{c+\rho}=\sum_{i=0}^{\rho-2}x_k\,\omega_i\,\frac{c+i+1}{c+\rho}\,u^{(c)}_{c+\rho-1-i}\;+\;S_\rho(c)\qquad(1\le\rho\le c-1).$$
This follows from `Parking.FirstLayer.zrT_split` with $P=\rho-1$ and from `Parking.FirstLayer.direct_generic`: the direct part is $(c+\rho)\,\omega_{\rho-1}\omega_c+\frac{c+\rho+1}{2}Q_\rho(c-\rho-1)$, and division by $c+\rho$ gives $S_\rho(c)/x_k$. The recursion in this form is a private lemma of the module of `Parking.FirstLayer.kernel_TK` and is derived in that record.

$S_\rho(c)$ is the part of the mass $u^{(c)}_{c+\rho}$ that comes from splittings into two free pieces. It is an explicit function of the threshold $c$, and `Parking.FirstLayer.Sdir_TK` shows that its values at $c=k-1,k,k+1$ have property K at $k$. The difficulty of that statement sits in the factor $\nu(c)=\frac{c+\rho+1}{c+\rho}$ of the pair sum: it is the ratio of the mean weight $\frac{c+\rho+1}{2}$ of an inner pair to half the size $c+\rho$, and it decreases as the threshold $c$ grows.

In the Lean definition `Sdir k ρ c` the subtractions $\rho-1$ and $c-\rho-1$ are truncated, so the expression is defined for all natural numbers; it has the meaning above only for $1\le\rho\le c-1$.

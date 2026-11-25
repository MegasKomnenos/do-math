---
weight: unit
short: weighted diagonal convexity in the first layer, for every weight c ≥ k
---
## Description

For $k\ge 7$, $k\le N\le 2k-2$ and every real $c\ge k$, at the critical tilt $x_k$: $(c+1)\,u^{(k+1)}_{N+1}-2c\,u^{(k)}_N+(c-1)\,u^{(k-1)}_{N-1}\ge 0$, where $u^{(y)}_M=z^{(y)}_Mx_k^{\,M}$ is the tilted environment of the threshold $y$.

## Statement

Let $k\ge 7$ and $N$ be natural numbers with $k\le N\le 2k-2$, and let $c\ge k$ be a real number. Let $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $u^{(y)}_M=z^{(y)}_M\,x_k^{\,M}$ with $z^{(y)}_M=A(M,y-1)/M!$ (`Parking.zrT y (xcrit k) M`). Then
$$(c+1)\,u^{(k+1)}_{N+1}-2c\,u^{(k)}_N+(c-1)\,u^{(k-1)}_{N-1}\ \ge\ 0 .$$

## Explanation

With $\mathrm{DC}(N)=u^{(k+1)}_{N+1}-2u^{(k)}_N+u^{(k-1)}_{N-1}$ and $e_N=u^{(k+1)}_{N+1}-u^{(k-1)}_{N-1}$, the left side is $c\cdot\mathrm{DC}(N)+e_N$: the diagonal second difference in which the three masses carry the weights $c-1$, $c$, $c+1$ that increase along the diagonal by one per step.

The statement is the input from the first layer to `Parking.DeltaId_nonneg`, the weighted convexity $(N+1)u^{(k+1)}_{N+1}-2Nu^{(k)}_N+(N-1)u^{(k-1)}_{N-1}\ge 0$ on the sizes $N\ge 2k-1$. When the three last-car recursions are subtracted there, a term in which one piece is free of size $\ell\le k-2$ leaves exactly a combination of this form at the smaller size $N-1-\ell$, with the weight $c=\ell+k+1$; so weights between $k$ and $2k-1$ occur, and the case $c=N$ alone would not be enough.

It follows from property K of the diagonal triple by the closure of property K under the factor $z\mapsto z+\beta$, which is the case $b=0$ of the factor $(z+a)(z+b)/z$ of `Parking.FirstLayer.TK.mul_prod`. The masses do not decrease along the diagonal from the size $k-1$ on, so $e_N\ge 0$ for these sizes (this is shown in the proof of `Parking.DeltaId_nonneg`). The present statement is therefore also a consequence of $\mathrm{DC}(N)\ge 0$ (`Parking.FirstLayer.zrT_diag_convex`) and $e_N\ge 0$. The Lean proof does not take that route; it obtains the weighted inequality directly from property K.

The Lean statement is written with $N=M+1$ (hypotheses $k\le M+1\le 2k-2$, sizes $M+2$, $M+1$, $M$).

## Proof

Put $\rho=N-k$, $0\le\rho\le k-2$, and $\beta=c-k\ge 0$. By `Parking.FirstLayer.kernel_TK` the triple $\big(u^{(k-1)}_{N-1},u^{(k)}_N,u^{(k+1)}_{N+1}\big)$ has property K at $k$, and its middle value is nonnegative (`Parking.zrT_nonneg`). Apply `Parking.FirstLayer.TK.mul_prod` with $a=\beta$ and $b=0$; the hypothesis $ab\le k^2-1$ is $0\le k^2-1$. The three factors are $\frac{(k-1+\beta)(k-1)}{k-1}=c-1$, $\frac{(k+\beta)k}{k}=c$ and $\frac{(k+1+\beta)(k+1)}{k+1}=c+1$. So $\big((c-1)u^{(k-1)}_{N-1},\,c\,u^{(k)}_N,\,(c+1)u^{(k+1)}_{N+1}\big)$ has property K at $k$, and `Parking.FirstLayer.TK.convex` gives $2c\,u^{(k)}_N\le(c+1)u^{(k+1)}_{N+1}+(c-1)u^{(k-1)}_{N-1}$.

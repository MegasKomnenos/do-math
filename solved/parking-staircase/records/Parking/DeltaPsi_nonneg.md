---
weight: unit
short: weighted diagonal convexity with the weight Ψ′ on all sizes
---
## Description

For $k\ge 7$ and every size $N\ge k$, at the critical tilt $x_k$: $\Psi'(N+1)\,u^{(k+1)}_{N+1}-2\Psi'(N)\,u^{(k)}_N+\Psi'(N-1)\,u^{(k-1)}_{N-1}\ge 0$, where $\Psi'(M)=\max(M,2k-1)$ and $u^{(y)}_M=z^{(y)}_Mx_k^{\,M}$ is the tilted environment of the threshold $y$.

## Statement

Let $k\ge 7$ and $N\ge k$ be natural numbers. Let $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), $u^{(y)}_M=z^{(y)}_M\,x_k^{\,M}$ with $z^{(y)}_M=A(M,y-1)/M!$ (`Parking.zrT y (xcrit k) M`), and $\Psi'(M)=\max(M,2k-1)$ (`Parking.PsiW`). Then
$$\Delta_{\Psi'}(N):=\Psi'(N+1)\,u^{(k+1)}_{N+1}-2\,\Psi'(N)\,u^{(k)}_N+\Psi'(N-1)\,u^{(k-1)}_{N-1}\ \ge\ 0 .$$

## Explanation

This is the second difference along the diagonal of the weighted masses $\Psi'(M)\,u^{(y)}_M$, the threshold and the size being raised together. It joins the two convexity results of the library into one statement valid for all sizes from $k$ on: in the first layer, where the weight is constant, it is the plain convexity `Parking.FirstLayer.zrT_diag_convex`, and beyond it is the convexity with the weight $N$, `Parking.DeltaId_nonneg`. The record of `Parking.PsiW` explains why the weight has this form.

The statement is the summand in the summation by parts of `Parking.weighted_debt`: the difference of two consecutive partial sums of the weighted tilted steps of column $k$, corrected by boundary terms, is exactly $\Delta_{\Psi'}(N)$.

The Lean statement is written with $N=M+1$ (hypothesis $k\le M+1$; sizes $M+2$, $M+1$, $M$).

## Proof

Three cases according to the position of $N$ relative to $2k-1$.

*$k\le N\le 2k-2$.* The three sizes $N-1,N,N+1$ are at most $2k-1$, so the three weights equal $2k-1$ (`Parking.PsiW_low`), and $\Delta_{\Psi'}(N)=(2k-1)\big(u^{(k+1)}_{N+1}-2u^{(k)}_N+u^{(k-1)}_{N-1}\big)\ge 0$ by `Parking.FirstLayer.zrT_diag_convex`.

*$N=2k-1$.* The weights are $\Psi'(N+1)=N+1$, $\Psi'(N)=N$ (`Parking.PsiW_of_ge`) and $\Psi'(N-1)=2k-1=N$ (`Parking.PsiW_low`). Hence $\Delta_{\Psi'}(N)=\Delta_{\mathrm{id}}(N)+u^{(k-1)}_{N-1}$, where $\Delta_{\mathrm{id}}(N)=(N+1)u^{(k+1)}_{N+1}-2Nu^{(k)}_N+(N-1)u^{(k-1)}_{N-1}\ge 0$ by `Parking.DeltaId_nonneg` and $u^{(k-1)}_{N-1}\ge 0$ by `Parking.zrT_nonneg`.

*$N\ge 2k$.* The three weights are $N+1$, $N$, $N-1$ (`Parking.PsiW_of_ge`), and $\Delta_{\Psi'}(N)=\Delta_{\mathrm{id}}(N)\ge 0$ by `Parking.DeltaId_nonneg`.

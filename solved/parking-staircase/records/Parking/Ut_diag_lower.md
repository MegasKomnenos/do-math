---
weight: unit
short: diagonal lower bound at the critical tilt
---
## Description

For $k\ge 2$ and $n\ge 1$, at the critical tilt $x_k$: $k\,U_{n-1}\le(k+1)\,U^{+}_n$, where $U_N=x_k^{\,N}\,b(N,k-1)/N!$ and $U^{+}_N=x_k^{\,N}\,b(N,k)/N!$ are the tilted masses of the levels $k-1$ and $k$.

## Statement

Let $k\ge 2$ and $n\ge 1$ be natural numbers, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), and let $u^{(y)}_N=z^{(y)}_Nx_k^{\,N}$ with $z^{(y)}_N=A(N,y-1)/N!$ be the tilted environment of the threshold $y$ (`Parking.zrT y (xcrit k) N`). Put
$$U_N=u^{(k)}_N-u^{(k-1)}_N,\qquad U^{+}_N=u^{(k+1)}_N-u^{(k)}_N$$
(`Parking.Ut k (xcrit k) N` and `Parking.Ut (k+1) (xcrit k) N`). Then
$$k\;U_{n-1}\ \le\ (k+1)\;U^{+}_n .$$

## Explanation

Since $A(N,\ell)-A(N,\ell-1)=b(N,\ell)$ is the number of parking functions of length $N$ with maximum displacement exactly $\ell$, $U_N=\beta^{(k-1)}_Nx_k^{\,N}$ and $U^{+}_N=\beta^{(k)}_Nx_k^{\,N}$ with $\beta^{(\ell)}_N=b(N,\ell)/N!$ (`Parking.Ut_eq_bq`). Both are tilted with the same number $x_k$. The statement compares the mass of the level $k-1$ at the size $n-1$ with the mass of the level $k$ at the size $n$, one step along the diagonal.

It is `Parking.bq_diag_lower`, $\gamma_k\,\beta^{(k-1)}_{n-1}\le\beta^{(k)}_n$ with $\gamma_k=(1+1/k)^{k-2}$, read at the critical tilt, where the constant becomes rational: $(k+1)\,x_k\,\gamma_k=k$. It is used twice for the columns $k\ge 82$: inside the proof of `Parking.DeltaId_nonneg`, to bound the middle part of the subtracted recursions, and in the proof of `Parking.step_pos_large`, in the step that passes from the rows before a row $n\ge 2k$ to the row $n$, where with $U^{+}_{n-1}=U_{n-1}+\eta_{n-1}$ it bounds $U_{n-2}$ by $U_{n-1}$ and the tilted step $\eta_{n-1}$ of the column.

## Proof

Write $n=m+1$. `Parking.bq_diag_lower` gives $\gamma_k\,\beta^{(k-1)}_m\le\beta^{(k)}_{m+1}$. `Parking.xcrit_mul_psi` states $x_k(1+1/k)^{k-1}=1$, and $(1+1/k)^{k-1}=\gamma_k(1+1/k)$ for $k\ge 2$ (`Parking.psi_eq_gam`); hence $(k+1)\,x_k\,\gamma_k=k$. Therefore
$$k\,\beta^{(k-1)}_m\,x_k^{\,m}=(k+1)\,x_k^{\,m+1}\,\gamma_k\,\beta^{(k-1)}_m\ \le\ (k+1)\,x_k^{\,m+1}\,\beta^{(k)}_{m+1},$$
and by `Parking.Ut_eq_bq` the two ends are $k\,U_m$ and $(k+1)\,U^{+}_{m+1}$.

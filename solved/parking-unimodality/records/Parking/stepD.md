---
weight: unit
short: tilted step at the diagonal tilt
---
## Description

The tilted step $\eta_n=x^n\,\delta_n$ of the column $k$: the normalised step $\delta_n=(b(n,k)-b(n,k-1))/n!$ multiplied by the powers of the diagonal tilt $x=1/\gamma_k$.

## Statement

For natural numbers $k$ and $n$,
$$\eta_n=\eta_n(k)=x^n\,\delta_n,$$
where $x$ is the diagonal tilt of the column $k$ (`Parking.xk`) and $\delta_n=\beta^{(k)}_n-\beta^{(k-1)}_n=d_{n,k}/n!$ is the normalised step of the column $k$ in the row $n$ (`Parking.dq`), with $d_{n,k}=b(n,k)-b(n,k-1)$.

## Explanation

Since $x>0$ (`Parking.CrossCrit.xk_pos`), $\eta_n$ has the sign of $d_{n,k}$: the column $k$ is positive in the row $n$, that is $b(n,k)>b(n,k-1)$, exactly when $\eta_n>0$. The tilt is introduced because the tilted step satisfies a column equation whose coefficients are the tilted kernel masses $\kappa_m=x^m\varepsilon_m$ (`Parking.kapx`) and whose source is the tilted profile $u_n=x^n\beta^{(k-1)}_n$ (`Parking.profD`). For $k\ge2$ and $k+1\le n\le2k-1$, multiplying `Parking.dq_col` by $x^n$ gives
$$\eta_n=\frac{2x}{n}\,u_{n-1}+\frac{(k+1)x}{n}\,\eta_{n-1}+\sum_{m=1}^{n-k}\kappa_m\,\eta_{n-m},$$
and by `Parking.dq_base` the starting value is $\eta_k=-\pi_k=-u_k$, with $\pi_k=x^ka_k/k$ (`Parking.pix`). The column therefore starts negative on the diagonal row $n=k$ and is pushed upward by the nonnegative source $u$.

Two arguments use $\eta$. In the crossing criterion `Parking.cross_criterion` the equation is summed over the rows $k+1,\dots,N$ while $\eta\le0$; this bounds the total source, and with it the proportion of parking functions with maximum displacement exactly $k-1$ (the "budget" of Step 6 of that proof). In the chain range, the argument for the rows near the diagonal (`Parking.caseA`) applies the two-point persistence `Parking.two_point` to the sequences $\eta$, $u$ and $\kappa$.

In Lean, `stepD k n = xk k ^ n * dq k n`, where `dq k n = bq k n - bq (k - 1) n` with a subtraction of natural numbers in the index. The left half of the argument tilts the same step by the critical tilt `Parking.xcrit` and writes the product inline as `dq k n * x ^ n`; there is no separate definition for it there.

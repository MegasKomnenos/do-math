---
weight: unit
short: tilted profile at the diagonal tilt
---
## Description

The tilted profile $u_j=x^j\,\beta^{(k-1)}_j$ of the column $k$: the normalised counts $b(j,k-1)/j!$ of the column $k-1$, multiplied by the powers of the diagonal tilt $x=1/\gamma_k$ of the column $k$.

## Statement

For natural numbers $k\ge1$ and $j$,
$$u_j=u_j(k)=x^j\,\beta^{(k-1)}_j,$$
where $x$ is the diagonal tilt of the column $k$ (`Parking.xk`) and $\beta^{(k-1)}_j=b(j,k-1)/j!$ (`Parking.bq`) is the number of parking functions of length $j$ with maximum displacement exactly $k-1$, divided by $j!$.

## Explanation

**Why the column $k-1$ with the tilt of the column $k$.** The step of the column $k$ is $\delta_n=\beta^{(k)}_n-\beta^{(k-1)}_n$ (`Parking.dq`), and its column equation `Parking.dq_col` is driven by the column $k-1$: the source term is $(2/n)\beta^{(k-1)}_{n-1}$. So the sign of the column $k$ is decided by the shape of the column $k-1$ in the rows $n\ge k$ that follow the diagonal row $n=k$, and this is what is called the profile of the column $k$. The tilt is the one that makes the diagonal lower bound `Parking.bq_diag_lower`, $\gamma_k\beta^{(k-1)}_{n-1}\le\beta^{(k)}_n$ with $\gamma_k=(1+1/k)^{k-2}$ (`Parking.gam`), free of its factor (see `Parking.xk`).

**Properties used.** Let $k\ge2$.

- $u_j\ge0$, and $u_j=0$ for $j\le k-1$ (`Parking.bq_eq_zero`); $u_k=\pi_k$ with $\pi_k=x^ka_k/k$ (`Parking.pix`).
- If $\delta_{n+1}\le0$ for some $n\ge k$, then $u_n\le u_{n+1}$: indeed $u_n=x^{n+1}\gamma_k\beta^{(k-1)}_n\le x^{n+1}\beta^{(k)}_{n+1}\le x^{n+1}\beta^{(k-1)}_{n+1}$. In general $u_{n}-u_{n+1}\le x^{n+1}\delta_{n+1}$.
- In the rows $k\le n\le2k-1$ the profile satisfies the column equation `Parking.bq_L0` multiplied by $x^n$:
$$u_n=\frac{x^n z^{(k)}_{n-1}}{n}+\frac{(k-1)x}{n}\,u_{n-1}+\sum_{m=1}^{n-k}\kappa_m\,u_{n-m},$$
with $\kappa_m=x^m\varepsilon_m$ (`Parking.kapx`) and $z^{(k)}_n=A(n,k-1)/n!$ (`Parking.zr`).

These are proved inside the proofs that use them: the crossing criterion `Parking.cross_criterion`, which bounds the ratio of $u_N$ to the source term of the row $N$ from both sides, and the argument for the rows near the diagonal in the chain range (`Parking.caseA`), where $u$ is the source of the tilted column equation of the step $\eta_n=x^n\delta_n$ (`Parking.stepD`).

**The Lean form.** `profD k j = xk k ^ j * bq (k - 1) j`. The index $k-1$ is a subtraction of natural numbers, the ordinary one for $k\ge1$. For $k\ge2$ the same number is `Ut k (xk k) j`, the tilted cell `Parking.Ut` at the diagonal tilt (by `Parking.Ut_eq_bq`), with the power written first.

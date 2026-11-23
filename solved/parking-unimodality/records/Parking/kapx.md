---
weight: unit
short: tilted kernel masses
---
## Description

The tilted kernel masses $\kappa_m=x^m\varepsilon_m$ of the column $k$, where $x=1/\gamma_k$ is the diagonal tilt of the column and $\varepsilon_m=(m-1)^{m-1}/m!$.

## Statement

For natural numbers $k$ and $m$,
$$\kappa_m=\kappa_m(k)=x^m\,\varepsilon_m,$$
where $x$ is the diagonal tilt of the column $k$ (`Parking.xk`) and $\varepsilon_m$ is `Parking.eps`: $\varepsilon_m=(m-1)^{m-1}/m!$ for $m\ge1$ (so $\varepsilon_1=1$) and $\varepsilon_0=0$. In particular $\kappa_0=0$ and $\kappa_1=x$.

## Explanation

**Where the masses come from.** The numbers $\varepsilon_m$ are the kernel of the column equations. For the normalised counts $\beta^{(k-1)}_n$ of the column $k-1$ the equation `Parking.bq_L0` reads, in the rows $k\le n\le2k-1$,
$$\beta^{(k-1)}_n=\frac{z^{(k)}_{n-1}}{n}+\frac{k-1}{n}\,\beta^{(k-1)}_{n-1}+\sum_{m=1}^{n-k}\varepsilon_m\,\beta^{(k-1)}_{n-m},$$
where $\beta^{(k-1)}_n=b(n,k-1)/n!$ is `Parking.bq` and $z^{(k)}_n=A(n,k-1)/n!$ is `Parking.zr`. The equation `Parking.dq_col` of the normalised step $\delta_n=d_{n,k}/n!$ of the column $k$ (`Parking.dq`) has the same convolution term $\sum_{m=1}^{n-k}\varepsilon_m\delta_{n-m}$. Multiplying the equation of the row $n$ by $x^n$ and writing $x^n=x^m\cdot x^{n-m}$ in each term of the convolution gives $\sum_m\kappa_m\,(x^{n-m}\beta^{(k-1)}_{n-m})$. So the tilted sequences $u_n=x^n\beta^{(k-1)}_n$ (`Parking.profD`) and $\eta_n=x^n\delta_n$ (`Parking.stepD`) satisfy the same equations with $\varepsilon_m$ replaced by $\kappa_m$. The $\kappa_m$ are nonnegative, and positive for $m\ge1$ (`Parking.kapx_pos`).

**Two sums of the masses that matter.** The total mass, compared with $1$, gives the kernel deficit $\bar\kappa_M=1-x-\sum_{m\le M}\kappa_m$ (`Parking.kbar`). The first moment has a closed form for each term: by `Parking.mul_eps`, $m\,\varepsilon_m=(m-1)^{m-1}/(m-1)!$, hence
$$m\,\kappa_m=x\cdot\frac{((m-1)x)^{m-1}}{(m-1)!},\qquad\sum_{m=1}^{R}m\,\kappa_m=x\,S_R,$$
with $S_R$ the sum `Parking.SR`.

**Where they are used.** In the crossing criterion `Parking.cross_criterion` and its closed-form version `Parking.cross_of_bounds`, and in the chain range, where `Parking.kapx_succ_le`, `Parking.kapx_cross` and `Parking.Fk_anti` state that the masses are nonincreasing on an initial range, log-convex, and satisfy the two-point condition.

**The Lean form.** `kapx k m = xk k ^ m * eps m`. Mathematically this is the tilted free prime kernel `Parking.epsT` evaluated at the diagonal tilt, `epsT (xk k) m`, with the factors in the other order; the library keeps the separate spelling for the diagonal tilt.

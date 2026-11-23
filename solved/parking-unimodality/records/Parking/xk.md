---
weight: unit
short: diagonal tilt of a column
---
## Description

The diagonal tilt $x=1/\gamma_k$ of the column $k$, where $\gamma_k=(1+1/k)^{k-2}$; for $k\ge2$ it is $x=(k/(k+1))^{k-2}$.

## Statement

For a natural number $k$, the *diagonal tilt* of the column $k$ is the real number
$$x=x(k)=\frac1{\gamma_k},$$
where $\gamma_k$ is `Parking.gam`. For $k\ge2$ one has $\gamma_k=(1+1/k)^{k-2}$, and therefore $x=(k/(k+1))^{k-2}$.

## Explanation

**What the tilt is for.** To tilt a sequence $(f_n)$ by $x$ is to pass to the sequence $(x^nf_n)$. The arguments about the column $k$ in the rows $k\le n\le 2k-1$ do not work with the normalised counts $\beta^{(k-1)}_n=b(n,k-1)/n!$ (`Parking.bq`) and the normalised step $\delta_n=d_{n,k}/n!$ (`Parking.dq`) themselves but with their tilts $u_n=x^n\beta^{(k-1)}_n$ (`Parking.profD`) and $\eta_n=x^n\delta_n$ (`Parking.stepD`). A tilt by a positive number changes no sign, and it turns the column equations `Parking.bq_L0` and `Parking.dq_col` into equations of the same shape with the kernel $\varepsilon_m=(m-1)^{m-1}/m!$ (`Parking.eps`) replaced by $\kappa_m=x^m\varepsilon_m$ (`Parking.kapx`).

**Why this value.** The value is fixed by one requirement: $x\gamma_k=1$ (`Parking.CrossCrit.xk_mul_gam`). The diagonal lower bound `Parking.bq_diag_lower` says $\gamma_k\,\beta^{(k-1)}_{n-1}\le\beta^{(k)}_n$: passing from the position (row $n-1$, column $k-1$) to its diagonal neighbour (row $n$, column $k$) multiplies the normalised count by at least $\gamma_k$. After the tilt by $x=1/\gamma_k$ the factor disappears: $x^{n-1}\beta^{(k-1)}_{n-1}\le x^n\beta^{(k)}_n$. Hence in every row $n$ in which the step of the column $k$ is not positive, that is $\beta^{(k)}_n\le\beta^{(k-1)}_n$, one gets $u_{n-1}\le u_n$: the tilted profile does not decrease as long as the column has not turned positive. This monotonicity is the starting point of the crossing criterion `Parking.cross_criterion`, and the same tilted inequality is the diagonal bound used by the two-point argument for the rows near the diagonal in the chain range (`Parking.caseA`). The name "diagonal" refers to this origin.

**Its size.** The tilt lies just above $e^{-1}$: $e^{-1}\le x\le e^{-1}e^{5/(2k)}$ for $k\ge2$ (`Parking.xk_bounds`). The number $e^{-1}$ is the radius of convergence of the tree series $\sum_ja_jX^j$, $a_j=j^{j-1}/j!$, and the value at which the kernel masses add up exactly: $e^{-1}+\sum_{m\ge1}e^{-m}\varepsilon_m=1$ (`Parking.hasSum_eps`). That $x$ exceeds $e^{-1}$ by a factor $1+O(1/k)$ is what makes the kernel deficit `Parking.kbar` a delicate quantity. Since $\gamma$ is nondecreasing, $x\gamma_i\ge1$ for $i\ge k$ (`Parking.CrossCrit.one_le_xk_mul_gam`).

**Relation to the other tilt of the library.** The left half of the argument (rows $n\ge2k$) uses the critical tilt $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`). The two differ by the factor $k/(k+1)$: the critical tilt is $k/(k+1)$ times the diagonal tilt. They serve different inequalities and no statement relates the tilted sequences at the two tilts.

**The Lean form.** `xk k` is the inverse of `gam k` for every natural number $k$. The exponent $k-2$ in `gam` is a subtraction of natural numbers, so `gam k = 1` and `xk k = 1` for $k\le1$; every result that uses the tilt assumes $k\ge2$, where the formula above is the ordinary one.

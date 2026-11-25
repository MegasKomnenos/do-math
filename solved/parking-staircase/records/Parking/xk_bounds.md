---
weight: step
short: bounds for the diagonal tilt
---
## Description

For $k\ge2$ the diagonal tilt $x=1/\gamma_k$ satisfies $e^{-1}\le x\le e^{-1}e^{5/(2k)}$.

## Statement

Let $k\ge2$ be a natural number, $x$ the diagonal tilt of the column $k$ (`Parking.xk`) and $\bar a=5/(2k)$ (`Parking.abar`). Then
$$e^{-1}\le x\le e^{-1}\,e^{\bar a}.$$

## Explanation

The statement locates the tilt just above $e^{-1}$, the value of the tilt $x$ at which the kernel masses $x^m\varepsilon_m$ add up to exactly $1-x$ (`Parking.hasSum_eps`); see `Parking.xk`. In the chain range the upper bound is used in the form $e^{1-5/(2k)}\le\gamma_k$, which enters the comparison $\varepsilon_{m+1}\le\gamma_k\varepsilon_m$ (`Parking.eps_succ_le_gam`) and the other numerical estimates of the kernel masses there.

The proof establishes the sharper two-sided bound $\underline a\le1+\log x\le\bar a$ with $\underline a=\frac{5}{2k}-\frac{4}{3k^2}$ (`Parking.alow`). This bound is not a public statement.

## Proof

Put $\alpha=1+\log x$, so that $x=e^{\alpha-1}$ ($x>0$ by `Parking.CrossCrit.xk_pos`). Since $x=1/\gamma_k$ and $\gamma_k=(1+1/k)^{k-2}$,
$$\alpha=1-(k-2)\,\log\Bigl(1+\frac1k\Bigr).$$
For $u\ge0$, $u-\frac{u^2}{2}\le\log(1+u)\le u-\frac{u^2}{2}+\frac{u^3}{3}$ (`Parking.log_one_add_ge2`, `Parking.log_one_add_le3`). With $u=1/k$ and the factor $k-2\ge0$ these give
$$\alpha\le1-(k-2)\Bigl(\frac1k-\frac1{2k^2}\Bigr)=\frac{5}{2k}-\frac{1}{k^2}\le\bar a,$$
$$\alpha\ge1-(k-2)\Bigl(\frac1k-\frac1{2k^2}+\frac1{3k^3}\Bigr)=\frac{5}{2k}-\frac{4}{3k^2}+\frac{2}{3k^3}\ge\underline a .$$
Moreover $\underline a=(15k-8)/(6k^2)\ge0$. Hence $0\le\alpha\le\bar a$, and since the exponential is increasing, $e^{-1}\le e^{\alpha-1}=x\le e^{\bar a-1}$.

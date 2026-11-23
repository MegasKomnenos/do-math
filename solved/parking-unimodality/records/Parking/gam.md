---
weight: unit
short: the factor of the diagonal lower bound
---
## Description

The factor $\gamma_k=(1+1/k)^{k-2}$ of the diagonal lower bound $\gamma_k\,\beta^{(k-1)}_{n-1}\le\beta^{(k)}_n$.

## Statement

For a natural number $k\ge2$,
$$\gamma_k=\Bigl(1+\frac1k\Bigr)^{k-2},$$
a real number. The Lean definition `gam k` is also defined for $k=0$ and $k=1$, where the exponent $k-2$ is the truncated difference $0$ (and $1/0=0$), so that $\gamma_0=\gamma_1=1$ there; for $k=1$ this differs from the ordinary reading $(1+1)^{-1}$.

## Explanation

$\gamma_k$ is the constant of the diagonal lower bound `Parking.bq_diag_lower`: for $k\ge2$ and $n\ge1$, $\gamma_k\,\beta^{(k-1)}_{n-1}\le\beta^{(k)}_n$, where $\beta^{(k)}_n=b(n,k)/n!$ (`Parking.bq`). The bound compares an entry of the column $k$ with the entry one step up the diagonal, in the column $k-1$ and the row $n-1$.

The value of the constant is the one for which the bound is an equality in the first row in which it says something. By `Parking.dq_base` and `Parking.bq_eq_zero`, $\beta^{(k-1)}_k=a_k/k$ and $\beta^{(k)}_{k+1}=a_{k+1}/(k+1)$ with $a_j=j^{j-1}/j!$ (`Parking.cay`), and by `Parking.cay_ratio`, $a_{k+1}/a_k=(1+1/k)^{k-1}$; hence
$$\frac{\beta^{(k)}_{k+1}}{\beta^{(k-1)}_k}=\frac{k}{k+1}\Bigl(1+\frac1k\Bigr)^{k-1}=\Bigl(1+\frac1k\Bigr)^{k-2}=\gamma_k.$$
The relation to the ratio of consecutive Cayley numbers is recorded as `Parking.psi_eq_gam`. The sequence $\gamma_k$ is nondecreasing for $k\ge2$ (`Parking.gam_mono`) and starts at $\gamma_2=1$. Its inverse $1/\gamma_k$ is the diagonal tilt (`Parking.xk`) with which the column equations are weighted in the crossing criterion and in the chain range.

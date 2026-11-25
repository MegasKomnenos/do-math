---
weight: unit
short: ratio of consecutive Cayley coefficients
---
## Description

Consecutive Cayley coefficients $a_j = j^{j-1}/j!$ have the ratio $a_{j+1}/a_j = (1 + 1/j)^{j-1}$ for $j \ge 1$.

## Statement

For every natural number $j \ge 1$,

$$a_{j+1} = \Bigl(1 + \frac{1}{j}\Bigr)^{j-1} a_j,$$

where $a$ denotes the Cayley coefficients (`Parking.cay`).

## Explanation

The ratio $\psi(j) = (1+1/j)^{j-1}$ is $1$ at $j = 1$, does not decrease in $j$ (`Parking.psi_mono`), and stays below $e$. Two things follow. The Cayley coefficients are log-convex (`Parking.cay_logconvex`), since a sequence with nondecreasing ratios is log-convex. And $a_j$ grows like $e^{j}$ up to a factor that is a power of $j$, which is why the library multiplies such sequences by $x^j$ with $x$ near $e^{-1}$ (a tilt): the tilted sequence varies only like a power of $j$.

The ratio is the form in which the Cayley coefficients enter most estimates of the library. In the shifted indexing $c_n = a_{n+1}$ (`Parking.cc`) it reads $c_{n+1} = (1 + 1/(n+1))^{n}\, c_n$. The critical tilt $x_k = (k/(k+1))^{k-1}$ is the reciprocal of $\psi(k)$ (`Parking.xcrit_mul_psi`), and the factor $\gamma_k = (1+1/k)^{k-2}$ of the diagonal bounds is $\psi(k)/(1+1/k)$ (`Parking.psi_eq_gam`).

The hypothesis $j \ge 1$ is needed: at $j = 0$ the right-hand side contains $a_0 = 0$, while $a_1 = 1$.

## Proof

Write $j = i + 1$. By `Parking.cay_succ`, $a_{i+2} = (i+2)^{i+1}/(i+2)!$ and $a_{i+1} = (i+1)^i/(i+1)!$. Since $(i+2)! = (i+2)\,(i+1)!$, the first is $(i+2)^i/(i+1)!$, and therefore

$$\frac{a_{i+2}}{a_{i+1}} = \frac{(i+2)^i}{(i+1)^i} = \Bigl(1 + \frac{1}{i+1}\Bigr)^{i},$$

which is the claim, because $j - 1 = i$. The calculation is routine.

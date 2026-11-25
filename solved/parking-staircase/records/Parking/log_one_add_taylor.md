---
weight: unit
short: alternating Taylor bounds for log(1+u)
---
## Description

For $u\ge0$ the Taylor polynomials of $\log(1+u)$ bound it alternately: the polynomial of even degree from below and the polynomial of odd degree from above.

## Statement

For every natural number $n$ and every real number $u\ge0$,
$$0\ \le\ (-1)^n\Bigl(\log(1+u)-\sum_{i=0}^{n-1}(-1)^i\frac{u^{i+1}}{i+1}\Bigr).$$
That is, with $T_n(u)=u-\frac{u^2}{2}+\dots+(-1)^{n-1}\frac{u^n}{n}$: $T_n(u)\le\log(1+u)$ for even $n$ and $\log(1+u)\le T_n(u)$ for odd $n$.

## Explanation

The series $\log(1+u)=u-u^2/2+u^3/3-\dots$ converges only for $u\le1$, but the alternating bounds by its partial sums hold for every $u\ge0$, and no bound on $u$ is assumed. The reason is that the error of the $n$-th partial sum has the derivative $(-1)^nu^n/(1+u)$, of constant sign.

The library needs explicit two-sided bounds for logarithms wherever a power $(1+1/k)^{k}$ or a tilt such as $(k/(k+1))^{k-1}$ has to be compared with an exponential. It uses the three cases $n=2,3,4$ (`Parking.log_one_add_ge2`, `Parking.log_one_add_le3`, `Parking.log_one_add_ge4`): in the bounds for the diagonal tilt and for the factors $\gamma_k=(1+1/k)^{k-2}$ (`Parking.xk_bounds`, `Parking.log_gam_sub_le`), in the numerics of the persistence argument, and in the numerical estimates of `Parking.ledger`, `Parking.pair_numeric` and `Parking.sbirth_ge`.

In Lean the sum runs over `range n`, the coefficient $1/(i+1)$ is written with the real number `(i : ℝ) + 1`, and for $n=0$ the statement reads $0\le\log(1+u)$.

## Proof

Fix $n$ and put $f(w)=(-1)^n\bigl(\log(1+w)-\sum_{i<n}(-1)^iw^{i+1}/(i+1)\bigr)$ for $w\ge0$. Then $f(0)=0$. At every $v\ge0$ the function $f$ is differentiable, and since the derivative of $(-1)^iw^{i+1}/(i+1)$ is $(-w)^i$,
$$f'(v)=(-1)^n\Bigl(\frac1{1+v}-\sum_{i<n}(-v)^i\Bigr).$$
The geometric sum satisfies $\bigl(\sum_{i<n}(-v)^i\bigr)(1+v)=1-(-v)^n$, hence
$$f'(v)=(-1)^n\,\frac{(-v)^n}{1+v}=\frac{v^n}{1+v}\ \ge0.$$
A function that vanishes at $0$ and has a nonnegative derivative at every point of $[0,\infty)$ is nondecreasing on $[0,\infty)$, by the mean value theorem, and so is nonnegative there. Hence $f(u)\ge0$.

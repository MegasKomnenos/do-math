---
weight: unit
short: tilted convexity of the Cayley masses below the top
---
## Description

At the critical tilt of a column $k\ge 3$, the tilted Cayley masses $\omega_n=c_nx_k^n$ satisfy $2e^{\mu/k}\omega_{j+1}\le e^{\mu}\omega_{j+2}+e^{-\mu}\omega_j$ for every $j$ with $j+2\le k$ and every real $\mu$.

## Statement

Let $k\ge 3$ be a natural number, $x_k=(k/(k+1))^{k-1}$ the critical tilt (`Parking.xcrit`), and $\omega_n=c_n\,x_k^{\,n}$ with $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). For every natural number $j$ with $j+2\le k$ and every real number $\mu$,
$$2\,e^{\mu/k}\,\omega_{j+1}\;\le\;e^{\mu}\,\omega_{j+2}+e^{-\mu}\,\omega_j .$$

## Explanation

The inequality is that of property K at $k$ (`Parking.FirstLayer.TK`) for three consecutive values of the one sequence $\omega$, and here it holds for negative $\mu$ as well. It is the base on which the first-layer convexity rests: `Parking.FirstLayer.conv_TK` turns it into property K of the pair sums (`Parking.FirstLayer.pairT_TK`). The triple at the top, $(\omega_{k-1},\omega_k,\omega_{k+1})$, is not covered ($j+2\le k$ excludes $j=k-1$) and is treated in `Parking.FirstLayer.TK_ccT_top`.

Why it holds. Put $\varphi(y)=(y-1)\log(1+1/y)$ for real $y>0$. Then $x_k=e^{-\varphi(k)}$ and
$$\omega_{n+1}=\omega_n\,e^{\varphi(n+1)-\varphi(k)}\qquad(n\ge 0),\tag{R}$$
and $\varphi$ is nondecreasing on the positive integers (`Parking.psi_mono`). So $\omega$ is a log-convex sequence whose ratio $\omega_{n+1}/\omega_n$ equals $1$ at $n+1=k$: it does not increase up to the index $k-1$, $\omega_{k-1}=\omega_k$, and it does not decrease afterwards. The critical tilt is the tilt that puts the minimum of the tilted Cayley masses at the indices $k-1$ and $k$. After division by $\omega_{j+1}$ the claim becomes $e^{\mu+p}+e^{-\mu+q}\ge 2e^{\mu/k}$ with $p=\varphi(j+2)-\varphi(k)\le 0$ and $q=\varphi(k)-\varphi(j+1)\ge 0$. By the weighted inequality between the arithmetic and the geometric mean, with the weights $(k+1)/(2k)$ and $(k-1)/(2k)$ that the exponent $\mu/k$ dictates, this holds for all $\mu$ as soon as
$$(k+1)\,p+(k-1)\,q\ \ge\ \varkappa(k):=(k+1)\log\frac{k+1}{k}+(k-1)\log\frac{k-1}{k},$$
and $\varkappa(k)$ is the second difference of $z\log z$ at $k-1,k,k+1$. So the statement is a comparison between increments of $\varphi$, and it is tight near the top: at $j+1=k-1$ the two sides of the exponent inequality differ by $(k-3)\big(k\log(1+\tfrac1k)-(k-1)\log(1+\tfrac1{k-1})\big)$, which vanishes for $k=3$.

The Lean statement writes the three indices as $j$, $j+1$, $j+2$ and casts $k$ to a real number in $\mu/k$.

## Proof

Throughout, $\varphi(y)=(y-1)\big(\log(y+1)-\log y\big)$.

**The ratio formula (R).** For a natural number $n\ge 1$, $e^{\varphi(n)}=(1+1/n)^{n-1}$. `Parking.xcrit_mul_psi` states $x_n(1+1/n)^{n-1}=1$, so $x_n=e^{-\varphi(n)}$ for $n\ge 1$. `Parking.ccT_succ_mul_xcrit` states $c_{n+1}x^{n+1}\cdot x_{n+1}=x\cdot c_nx^n$ for every real $x$; at $x=x_k$ this is $\omega_{n+1}=\omega_n\,x_k/x_{n+1}=\omega_n e^{\varphi(n+1)-\varphi(k)}$.

**One calculus lemma.** Let $a_1,a_2,a_3>0$ and $c_1,c_2,c_3,\alpha,\beta$ be real. If $\alpha+\beta t\le\sum_i c_i/(a_i+t)$ for all $t\in[0,1]$, then $\alpha+\beta/2\le\sum_i c_i\big(\log(a_i+1)-\log a_i\big)$. Indeed the function $t\mapsto\sum_i c_i\log(a_i+t)-\alpha t-\beta t^2/2$ has a nonnegative derivative on $[0,1]$, so by the mean value theorem its value at $1$ is at least its value at $0$. This is the only use of calculus; the next two facts are instances.

**(a) $\varphi(y)-\varphi(y-1)\ge\dfrac{3}{2y(y+1)}$ for real $y\ge 2$.** The left side is $(y-1)(\log(y+1)-\log y)-(y-2)(\log y-\log(y-1))$. Apply the lemma with $(c_1,a_1)=(y-1,y)$, $(c_2,a_2)=(-(y-2),y-1)$, $c_3=0$, $\alpha=\beta=1/(y(y+1))$: the hypothesis is $\frac{1+t}{y(y+1)}\le\frac{y-1}{y+t}-\frac{y-2}{y-1+t}=\frac{1+t}{(y+t)(y-1+t)}$, true because $(y+t)(y-1+t)\le y(y+1)$ on $[0,1]$.

**(b) $(y+2)\big(\varphi(y+1)-\varphi(y)\big)\le y\big(\varphi(y)-\varphi(y-1)\big)$ for real $y\ge 2$.** Written out, the difference of the right and left sides is $-y(y-2)\,\ell(y-1)+2(y^2-1)\,\ell(y)-y(y+2)\,\ell(y+1)$ with $\ell(a)=\log(a+1)-\log a$. Apply the lemma with these three coefficients, $a_i=y-1,y,y+1$ and $\alpha=\beta=0$: the sum $\sum_ic_i/(a_i+t)$ equals $\dfrac{2(1-t^2)}{(y-1+t)(y+t)(y+1+t)}\ge 0$ on $[0,1]$.

**The exponent inequality.** For natural numbers $k\ge 3$ and $1\le n\le k-1$,
$$(k+1)\big(\varphi(n+1)-\varphi(k)\big)+(k-1)\big(\varphi(k)-\varphi(n)\big)\ \ge\ \varkappa(k).\tag{E}$$
Let $G(m)=(k+1)\varphi(m+1)-(k-1)\varphi(m)$; the left side of (E) is $G(n)-2\varphi(k)$. For $1\le m\le k-2$, $G(m+1)\le G(m)$: by (b) at $y=m+1$, $(m+3)(\varphi(m+2)-\varphi(m+1))\le(m+1)(\varphi(m+1)-\varphi(m))$; by (a), $\varphi(m+1)-\varphi(m)\ge 0$; and $(k+1)(m+1)\le(k-1)(m+3)$ because $m+2\le k$. Hence $G(n)\ge G(k-1)$. A direct rearrangement gives
$$G(k-1)-2\varphi(k)-\varkappa(k)=(k-3)\Big(k\log\big(1+\tfrac1k\big)-(k-1)\log\big(1+\tfrac1{k-1}\big)\Big),$$
which is nonnegative because $k\ge 3$ and because $(1+1/i)^i$ is nondecreasing in $i$ (`Parking.chi_mono`).

**Weighted AM–GM in tilt form.** Let $k>1$ be real and $p,q,\xi$ real with $(k+1)p+(k-1)q\ge\varkappa(k)+\xi$. Then for every real $\mu$,
$$e^{\mu+p}+e^{-\mu+q}\ \ge\ 2\,e^{\mu/k}\,e^{\xi/(2k)}.$$
Write $e^{\mu+p}=\frac{k+1}{k}e^{u}$ and $e^{-\mu+q}=\frac{k-1}{k}e^{v}$ with $u=\mu+p-\log\frac{k+1}{k}$, $v=-\mu+q+\log\frac{k}{k-1}$. The two coefficients add up to $2$. Put $E=\mu/k+\xi/(2k)$. The tangent line of the exponential at $E$ gives $e^{w}\ge e^{E}(1+w-E)$ for all $w$, and $\frac{k+1}{k}(u-E)+\frac{k-1}{k}(v-E)=\frac1k\big((k+1)p+(k-1)q-\varkappa(k)-\xi\big)\ge 0$. Adding the two tangent inequalities with the coefficients $\frac{k+1}{k}$, $\frac{k-1}{k}$ gives the sum $\ge 2e^{E}$.

**Conclusion.** Let $j+2\le k$ and $n=j+1$, so $1\le n\le k-1$. By (R), $\omega_{j+2}=\omega_{j+1}e^{p}$ and $\omega_j=\omega_{j+1}e^{q}$ with $p=\varphi(j+2)-\varphi(k)$, $q=\varphi(k)-\varphi(j+1)$. By (E), $(k+1)p+(k-1)q\ge\varkappa(k)$, so the AM–GM statement with $\xi=0$ gives $e^{\mu+p}+e^{-\mu+q}\ge 2e^{\mu/k}$. Multiply by $\omega_{j+1}>0$.

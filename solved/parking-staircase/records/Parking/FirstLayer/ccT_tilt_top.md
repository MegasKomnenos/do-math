---
weight: step
short: surplus of the tilted convexity at the top, relative bound
---
## Description

At the critical tilt of a column $k\ge 3$, for every real $\mu$: $e^{\mu}\omega_{k+1}+e^{-\mu}\omega_{k-1}-2e^{\mu/k}\omega_k\ \ge\ \omega_k\,e^{\mu/k}\,\dfrac{k^2-2k-1}{2k^2(k+1)(k+2)}$, where $\omega_n=c_nx_k^{\,n}$.

## Statement

Let $k\ge 3$ be a natural number, $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $\omega_n=c_nx_k^{\,n}$, $c_n=(n+1)^{n-1}/n!$ (`Parking.ccT` at the tilt $x_k$). For every real $\mu$,
$$\omega_k\,e^{\mu/k}\cdot\frac{1}{k}\cdot\frac{k^2-2k-1}{2k(k+1)(k+2)}\ \le\ e^{\mu}\,\omega_{k+1}+e^{-\mu}\,\omega_{k-1}-2\,e^{\mu/k}\,\omega_k .$$

## Explanation

The right side is the amount by which the triple $(\omega_{k-1},\omega_k,\omega_{k+1})$ exceeds what property K at $k$ requires (`Parking.FirstLayer.TK`); it is called the surplus at the top. The statement bounds the surplus from below by a positive multiple of $\omega_k e^{\mu/k}$, that is, in proportion to the middle term of the inequality. `Parking.FirstLayer.TK_ccT_top` keeps only its sign. `Parking.FirstLayer.Sdir_TK` uses the size: for tilts $\mu\ge 1/(k(k+2))$ this surplus pays for the defect that the decreasing factor $(c+\rho+1)/(c+\rho)$ causes in the pair-sum term of the direct term. For small tilts the companion bound `Parking.FirstLayer.ccT_tilt_top'` is used instead.

The surplus is positive because, at the top, $\omega_{k-1}=\omega_k$ and $\omega_{k+1}=\omega_ke^{\zeta}$ with $\zeta=\varphi(k+1)-\varphi(k)>0$, $\varphi(y)=(y-1)\log(1+1/y)$: the ratio to the lower neighbour is $1$ and the ratio to the upper neighbour is larger than the weighted mean inequality needs. The excess is $\Lambda_k=(k+1)\zeta-\varkappa(k)$ with $\varkappa(k)=(k+1)\log\frac{k+1}{k}+(k-1)\log\frac{k-1}{k}$, and $\Lambda_k\ge\frac{k^2-2k-1}{2k(k+1)(k+2)}$, a lower bound of the order $1/(2k)$.

## Proof

Notation and two facts are taken from the record of `Parking.FirstLayer.ccT_tilt_mid`: the ratio formula $\omega_{n+1}=\omega_ne^{\varphi(n+1)-\varphi(k)}$; the calculus lemma (if $\alpha+\beta t\le\sum_ic_i/(a_i+t)$ on $[0,1]$ with $a_i>0$, then $\alpha+\beta/2\le\sum_ic_i(\log(a_i+1)-\log a_i)$); and the weighted AM–GM inequality in tilt form (if $(k+1)p+(k-1)q\ge\varkappa(k)+\xi$, then $e^{\mu+p}+e^{-\mu+q}\ge 2e^{\mu/k}e^{\xi/(2k)}$ for all real $\mu$).

**The surplus.** By the ratio formula and `Parking.FirstLayer.ccT_top` ($\omega_{k-1}=\omega_k$),
$$e^{\mu}\omega_{k+1}+e^{-\mu}\omega_{k-1}-2e^{\mu/k}\omega_k=\omega_k\big(e^{\mu+\zeta}+e^{-\mu}-2e^{\mu/k}\big),\qquad\zeta=\varphi(k+1)-\varphi(k).$$

**A lower bound for $\Lambda_y=(y+1)(\varphi(y+1)-\varphi(y))-\varkappa(y)$, real $y\ge 3$:** $\Lambda_y\ge\dfrac{y^2-2y-1}{2y(y+1)(y+2)}$. With $\ell(a)=\log(a+1)-\log a$, $\Lambda_y=(y-1)\ell(y-1)-y(y+1)\ell(y)+y(y+1)\ell(y+1)$. Apply the calculus lemma with these coefficients, $a_i=y-1,y,y+1$, $\alpha=0$ and $\beta=\frac{y^2-2y-1}{y(y+1)(y+2)}$. The sum $\sum_ic_i/(a_i+t)$ equals $\dfrac{t\,(y^2-2y-1+(y-1)t)}{(y-1+t)(y+t)(y+1+t)}$, and this is at least $\beta t$ on $[0,1]$ because the denominator is at most $y(y+1)(y+2)$ and $y^2-2y-1\ge 0$, $(y-1)t\ge 0$.

**Conclusion.** Apply the AM–GM statement with $p=\zeta$, $q=0$ and $\xi=\Lambda_k$; its hypothesis holds with equality. It gives $e^{\mu+\zeta}+e^{-\mu}\ge 2e^{\mu/k}e^{\Lambda_k/(2k)}\ge 2e^{\mu/k}\big(1+\Lambda_k/(2k)\big)$, hence
$$e^{\mu+\zeta}+e^{-\mu}-2e^{\mu/k}\ \ge\ e^{\mu/k}\,\frac{\Lambda_k}{k}\ \ge\ e^{\mu/k}\cdot\frac1k\cdot\frac{k^2-2k-1}{2k(k+1)(k+2)}.$$
Multiply by $\omega_k>0$.

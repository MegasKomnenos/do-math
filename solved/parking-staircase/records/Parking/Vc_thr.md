---
weight: step
short: homogeneity of the composition weights in the threshold
---
## Description

For the threshold profile $s \mapsto y/(N-s)$ the weight of the compositions of $m$ with $q$ parts is $y^{q-1}$ times its value at $y = 1$.

## Statement

For all real numbers $y$ and $N$ and all natural numbers $q$ and $m$,

$$V_q(m;\lambda^{y,N}) = y^{q-1}\, V_q(m;\lambda^{1,N}),$$

where $V_q(m;f)$ is the total weight of the compositions of $m$ with $q$ parts for the cut profile $f$ (`Parking.Vc`) and $\lambda^{y,N}(s) = y/(N-s)$ is the threshold profile (`Parking.thr`). For $q = 0$ both sides are $0$.

## Explanation

A composition with $q$ parts has $q - 1$ cuts, and each cut carries the factor $y$ once. The statement separates the dependence on the threshold $y$ from the dependence on the top size $N$. It makes the chain sum $\Lambda_m(y;N)$ a polynomial in $y$ with the coefficients $V_q(m;\lambda^{1,N})$ (`Parking.Lam_thr`), and in the proof of `Parking.curvSum_pos` it expresses the curvature sum through the weights $V_q(m;\lambda^{y,N})$ of the profile with the threshold $y$ itself. The exponent $q - 1$ is a natural-number subtraction in Lean, which gives $y^0$ for $q = 0$; this is harmless because $V_0 = 0$.

## Proof

The statement is a case of the homogeneity of $V_q(m;f)$ in the profile: for every profile $f$ and every real $y$, $V_q(m; y f) = y^{q-1} V_q(m;f)$. This is proved by induction on $q$. For $q = 0$ both sides vanish, and for $q = 1$ both sides are $a_m$ by `Parking.Vc_one`. For $q + 2$ parts, `Parking.Vc_succ_succ` gives

$$V_{q+2}(m; yf) = \sum_{0<s<m} V_{q+1}(s; yf)\cdot y f(s)\cdot a_{m-s} = y^{q+1} \sum_{0<s<m} V_{q+1}(s;f)\, f(s)\, a_{m-s},$$

where the induction hypothesis supplies the factor $y^q$ of $V_{q+1}(s;yf)$. Since $\lambda^{y,N} = y \cdot \lambda^{1,N}$, the statement follows.

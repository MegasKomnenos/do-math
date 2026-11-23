---
weight: unit
short: truncated first moment of the kernel
---
## Description

The sum $S_R=\sum_{i=0}^{R-1}(ix)^i/i!$ for the diagonal tilt $x=1/\gamma_k$ of the column $k$; $x\,S_R$ is the first moment $\sum_{m=1}^{R}m\,\kappa_m$ of the tilted kernel masses up to $R$.

## Statement

For natural numbers $k$ and $R$,
$$S_R=S_R(k)=\sum_{i=0}^{R-1}\frac{(i\,x)^i}{i!},$$
where $x$ is the diagonal tilt of the column $k$ (`Parking.xk`) and the term with $i=0$ is $1$.

## Explanation

**What it is.** With the tilted kernel masses $\kappa_m=x^m\varepsilon_m$ (`Parking.kapx`), $\varepsilon_m=(m-1)^{m-1}/m!$, the identity $m\,\varepsilon_m=(m-1)^{m-1}/(m-1)!$ (`Parking.mul_eps`) gives $m\,\kappa_m=x\,((m-1)x)^{m-1}/(m-1)!$, so that
$$x\,S_R=\sum_{m=1}^{R}m\,\kappa_m .$$
Equivalently, in terms of the kernel deficits $\bar\kappa_M=1-x-\sum_{m\le M}\kappa_m$ (`Parking.kbar`), $x\,S_R=\sum_{M=0}^{R}(\bar\kappa_M-\bar\kappa_R)$. This second form is how $S_R$ arises in the proof of `Parking.cross_criterion`: the coefficients of the summed column equation contain the deficits $\bar\kappa_M$, $M\le R$, and their sum is $(R+1)\bar\kappa_R+x\,S_R$.

**Its role and its size.** On the left side of the crossing criterion the main term $R(R+1)/N$, $N=k+R$, has to exceed $1+S_R$ (and two smaller corrections). Writing $x=e^{\alpha-1}$, each term is $(ix)^i/i!=p_i\,e^{\alpha i}$ with $p_i=e^{-i}i^i/i!$ (`Parking.poissonMass`), and $p_i\le c_0/\sqrt i$ with $c_0=1/\sqrt{2\pi}$ by Stirling's formula (`Parking.poissonMass_le_c0`). So $S_R$ grows like $2c_0\sqrt R=\sqrt{2R/\pi}$, up to the factor coming from $e^{\alpha i}$, while the main term grows like $R^2/k$. The criterion can therefore hold once $R^{3/2}$ is a sufficiently large multiple of $k$, that is, for $R$ of order $k^{2/3}$. The explicit bound is $S_R\le\bar S$ with the closed form `Parking.Sbar`; it holds for $k\ge2$, $R\ge2$ and $\frac{5}{2k}R\le0.6679$, and is proved inside the proof of `Parking.cross_of_bounds`.

**The Lean form.** `SR k R = ∑ i ∈ range R, ((i : ℝ) * xk k) ^ i / (i.factorial : ℝ)`; the term $i=0$ is $0^0/0!=1$ by the convention $0^0=1$.

---
weight: unit
short: kernel deficit
---
## Description

The kernel deficit $\bar\kappa_M=1-x-\sum_{m=1}^{M}\kappa_m$ of the column $k$, where $x=1/\gamma_k$ is the diagonal tilt and $\kappa_m=x^m\varepsilon_m$ are the tilted kernel masses.

## Statement

For natural numbers $k$ and $M$,
$$\bar\kappa_M=\bar\kappa_M(k)=1-x-\sum_{m=1}^{M}\kappa_m,$$
where $x$ is the diagonal tilt of the column $k$ (`Parking.xk`) and $\kappa_m=x^m\varepsilon_m$ (`Parking.kapx`), with $\varepsilon_m=(m-1)^{m-1}/m!$ (`Parking.eps`). In particular $\bar\kappa_0=1-x$ and $\bar\kappa_1=1-2x$.

## Explanation

**What it measures.** Write $u_n=x^n\beta^{(k-1)}_n$ for the tilted profile (`Parking.profD`; $\beta^{(k-1)}_n=b(n,k-1)/n!$ is `Parking.bq`). Multiplied by $x^N$, the column equation `Parking.bq_L0` of the column $k-1$ in a row $N=k+R$ with $1\le R\le k-1$ reads
$$u_N=\frac{x^N z^{(k)}_{N-1}}{N}+\frac{(k-1)x}{N}\,u_{N-1}+\sum_{m=1}^{R}\kappa_m\,u_{N-m},$$
where $z^{(k)}_n=A(n,k-1)/n!$ is `Parking.zr`. If the profile is nondecreasing up to the row $N$, every value of $u$ on the right is at most $u_N$, and the equation gives
$$u_N\Bigl(1-\frac{(k-1)x}{N}-\sum_{m=1}^{R}\kappa_m\Bigr)\le\frac{x^N z^{(k)}_{N-1}}{N},\qquad 1-\frac{(k-1)x}{N}-\sum_{m=1}^{R}\kappa_m=\bar\kappa_R+\frac{x(R+1)}{N}.$$
The deficit is what remains of the weight $1$ of $u_N$ after the kernel masses up to $R$ and one further mass $x$ have been taken away. This is how $\bar\kappa_R$ enters the crossing criterion `Parking.cross_criterion`, whose first hypothesis is $\bar\kappa_R\ge0$.

**Why its sign is delicate.** Since $\kappa_m\ge0$, the deficit is nonincreasing in $M$. At the tilt $e^{-1}$ the masses add up exactly, $e^{-1}+\sum_{m\ge1}e^{-m}\varepsilon_m=1$ (`Parking.hasSum_eps`), so there the deficit would be the positive tail $\sum_{m>M}e^{-m}\varepsilon_m$, of size about $2e^{-1}c_0/\sqrt M$ with $c_0=1/\sqrt{2\pi}$. The diagonal tilt is $x=e^{\alpha-1}$ with $0\le\alpha\le5/(2k)$ (`Parking.xk_bounds`), which multiplies the mass $\kappa_m$ by $e^{\alpha m}$. Thus
$$\bar\kappa_M=\sum_{m>M}e^{-m}\varepsilon_m-e^{-1}(e^{\alpha}-1)-\sum_{m=1}^{M}(e^{\alpha m}-1)\,e^{-m}\varepsilon_m,$$
a decreasing tail minus an excess that grows with $M$. For a fixed column the deficit is therefore nonnegative only for $M$ up to some bound, and near that bound it is a small difference of two larger terms. The closed forms `Parking.tlow` and `Parking.tup` bound $\bar\kappa_R$ from below and from above along these lines, for $k\ge2$ and $R\ge2$ (the lower bound under the additional condition $\frac{5}{2k}R\le0.6679$); the proof is in the record of `Parking.cross_of_bounds`.

**Two facts used in the proof of the criterion.** If $\bar\kappa_R\ge0$ for some $R\ge1$, then $1-2x=\bar\kappa_1\ge\bar\kappa_R\ge0$, so $x\le\frac12$; for the diagonal tilt this happens exactly for $k\ge8$, so the criterion says nothing about smaller columns. And the deficits sum to
$$\sum_{M=0}^{R}\bar\kappa_M=(R+1)\,\bar\kappa_R+x\,S_R,$$
with $S_R$ the sum `Parking.SR`, because $\sum_{M=0}^{R}(\bar\kappa_M-\bar\kappa_R)=\sum_{m=1}^{R}m\,\kappa_m=x\,S_R$.

**The Lean form.** `kbar k M = 1 - xk k - ∑ m ∈ Icc 1 M, kapx k m`, a real number defined for all natural $k$ and $M$.

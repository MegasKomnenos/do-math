---
weight: unit
short: tilt correction of a row
---
## Description

The correction $\mathsf e_j=(j-k+2)-\Pi_{j+1}/\pi_{j+1}$ of the column $k$: the amount by which the sum $\Pi_{j+1}=\pi_k+\dots+\pi_{j+1}$ of the weights, divided by its last term, falls short of its number of terms.

## Statement

For natural numbers $k$ and $j$,
$$\mathsf e_j=\mathsf e_j(k)=(j-k+2)-\frac{\Pi_{j+1}}{\pi_{j+1}},$$
where $\pi_n=x^na_n/n$ are the weights `Parking.pix` of the column $k$ and $\Pi_i=\sum_{n=k}^{i}\pi_n$ their partial sums `Parking.pixSum`. For $j\ge k$ this is
$$\mathsf e_j=\sum_{n=k}^{j+1}\Bigl(1-\frac{\pi_n}{\pi_{j+1}}\Bigr).$$

## Explanation

**What it measures.** For $j\ge k\ge2$ the weights $\pi_k\le\pi_{k+1}\le\dots$ are nondecreasing (see `Parking.pix`), so every term of the second formula is nonnegative and $\mathsf e_j\ge0$ (`Parking.CrossCrit.ecor_nonneg`). If the weights were constant, $\mathsf e_j$ would be $0$. They are not constant because the diagonal tilt $x=1/\gamma_k$ (`Parking.xk`; $\gamma_n=(1+1/n)^{n-2}$ is `Parking.gam`) is adapted to the column $k$ alone: the ratio $\pi_{n+1}/\pi_n=x\gamma_n$ is $1$ at $n=k$ and larger than $1$ beyond. The correction is the price of that choice of tilt, and it is small: $\mathsf e_k=0$, and $\mathsf e_j\le\frac{5}{6k^2}\rho(\rho+1)(\rho+2)$ with $\rho=j-k$.

**Where it enters.** In the crossing criterion `Parking.cross_criterion` (with $N=k+R$) the correction occurs twice. The identity $\Pi_N=\pi_N\,(R+1-\mathsf e_{N-1})$ puts $\mathsf e_{N-1}$ on the right side of the criterion. And for $k\le j\le N-2$ the identity
$$\Pi_{j+1}\,P_j=u_j\cdot\frac{x\,(j-k+2-\mathsf e_j)}{j+1}$$
is used, in which $u_j=x^j\beta^{(k-1)}_j$ is the tilted profile (`Parking.profD`), $P_j=\beta^{(k-1)}_j/c_j$ is the proportion of parking functions of length $j$ with maximum displacement exactly $k-1$, and $c_j=(j+1)^{j-1}/j!$ (`Parking.cc`). It adds $x\,\mathsf e_j/(j+1)$ to the coefficient of $u_j$ in the summed column equation, and these contributions add up to $x\,\mathsf E$ with $\mathsf E$ the sum `Parking.ecorSum`.

**Recursion and bounds.** For $j\ge k$, with $r=x\gamma_{j+1}\ge1$,
$$\mathsf e_{j+1}=(j-k+2)\Bigl(1-\frac1r\Bigr)+\frac{\mathsf e_j}{r},\qquad\text{hence}\qquad\mathsf e_{j+1}\le(j-k+2)\log(x\gamma_{j+1})+\mathsf e_j .$$
The recursion, the bound $\log(x\gamma_i)\le5(i-k)/(2ki)$ and the resulting bounds for $\mathsf e_j$ are proved inside the proof of `Parking.cross_of_bounds`; they are stated here because they describe the object.

**The Lean form.** `ecor k j = ((j : ℝ) - k + 2) - pixSum k (j + 1) / pix k (j + 1)`, with real subtraction and division; it is defined for all $k$ and $j$ and used only for $j\ge k\ge2$.

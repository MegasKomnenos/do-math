---
weight: unit
short: flow factor
---
## Description

The factor $\omega_i=1-i/((i+1)\,x\gamma_i)$ of the column $k$, where $x=1/\gamma_k$ is the diagonal tilt and $\gamma_i=(1+1/i)^{i-2}$; it bounds the diagonal increase of the cumulative proportion in the row $i$.

## Statement

For natural numbers $k$ and $i$,
$$\omega_i=\omega_i(k)=1-\frac{i}{(i+1)\,x\,\gamma_i},$$
where $x$ is the diagonal tilt of the column $k$ (`Parking.xk`) and $\gamma_i$ is `Parking.gam`.

## Explanation

**Another form.** With $c_n=(n+1)^{n-1}/n!$ (`Parking.cc`) one has $c_i=\gamma_i\,(1+1/i)\,c_{i-1}$ for $i\ge2$ (from `Parking.cay_ratio`), and $1/x=\gamma_k$. Hence
$$\omega_i=1-\frac{\gamma_k\,c_{i-1}}{c_i}\qquad(i\ge2).$$
For $i\ge k\ge2$, $x\gamma_i\ge1$ (`Parking.CrossCrit.one_le_xk_mul_gam`), so $0\le\omega_i<1$.

**What it bounds.** Let $F_n=z^{(k)}_n/c_n$ and $F^-_n=z^{(k-1)}_n/c_n$ be the proportions of parking functions of length $n$ with maximum displacement at most $k-1$ and at most $k-2$ ($z^{(y)}_n$ is `Parking.zr`). The flow $J_i=F_i-F^-_{i-1}$ is the increase of the cumulative proportion when the length and the bound on the displacement are both raised by one; it is nonnegative by `Parking.zr_diag_mono`. The diagonal lower bound `Parking.bq_diag_lower`, summed over the columns $k,k+1,\dots,i-1$, gives $\gamma_k\,(c_{i-1}-z^{(k-1)}_{i-1})\le c_i-z^{(k)}_i$, and dividing by $c_i$ turns this into
$$J_i\le\omega_i\,(1-F^-_{i-1})\qquad(i\ge k).$$
This is Step 5 of the proof of `Parking.cross_criterion`. In that proof the flow is the part of the decrease $F_{i-1}-F_i$ that the column $k-1$ does not account for: $F_{i-1}-F_i=P_{i-1}-J_i$, where $P_n=F_n-F^-_n$ is the proportion of parking functions of length $n$ with maximum displacement exactly $k-1$. The factor $\omega_i$ is what controls this remainder.

**Its size.** For $i\ge k\ge2$, $\omega_i\le\frac1{i+1}+\log(x\gamma_i)\le\frac1{i+1}+\frac{5(i-k)}{2ki}$; this is proved inside the proof of `Parking.cross_of_bounds`. The first part comes from the factor $i/(i+1)$ and the second from the tilt.

**The Lean form.** `omg k i = 1 - (i : ℝ) / (((i : ℝ) + 1) * (xk k * gam i))`, defined for all $k$ and $i$ and used for $i>k\ge2$.

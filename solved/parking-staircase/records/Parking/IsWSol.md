---
weight: unit
short: solution of the weighted last-car recursion
---
## Description

The predicate "$W$ solves the weighted last-car recursion with weight $\omega$": $W_0=1$ and $(n+1)W_{n+1}=\sum_{j=0}^{n}\omega(j+1)\,W_j\,W_{n-j}$ for all $n\ge0$, for real sequences $\omega$ and $W$.

## Statement

Let $\omega$ and $W$ be sequences of real numbers indexed by the natural numbers. $W$ is a *solution of the weighted last-car recursion with weight $\omega$* if

- $W_0=1$, and
- for every $n\ge0$, $\;(n+1)\,W_{n+1}=\sum_{j=0}^{n}\omega(j+1)\,W_j\,W_{n-j}$.

## Explanation

**Where the recursion comes from.** Divide the last-car recursion `Parking.A_succ` for the bound $k=y-1$ by $n!$. Since $\binom nj/n!=1/(j!\,(n-j)!)$, the numbers $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`) satisfy $(n+1)z^{(y)}_{n+1}=\sum_{j\le n}\min(j+1,y)\,z^{(y)}_j z^{(y)}_{n-j}$, which is the recursion above with the weight $\omega(t)=\min(t,y)$ (`Parking.zr_isWSol`). The argument $t=j+1$ of the weight is the number of spots up to and including the spot of the last car, and $\omega(t)$ is the number of preferences open to the last car. Without a bound on the displacement the weight is $\omega(t)=t$, and the solution is $c_n=(n+1)^{n-1}/n!$ (`Parking.cc`, by `Parking.cc_rec`). The notion is introduced for a general weight so that the comparison of a solution with $c$, the single-chain formula `Parking.IsWSol.ez`, `Parking.IsWSol.fwd`, is proved once, using of the weight only that $\omega(t)=t$ for $t\le k$. In the library the weights that occur are $\omega(t)=t$ and the threshold weights $\omega(t)=\min(t,y)$.

**Elementary properties.** Only the values $\omega(t)$ with $t\ge1$ enter. The recursion determines $W_{n+1}$ from $W_0,\dots,W_n$ and $\omega(1),\dots,\omega(n+1)$, so a weight has at most one solution, and more precisely two solutions whose weights agree on $1\le t\le n$ agree up to the index $n$. The library uses this comparison (a private lemma, proved by strong induction) to identify a solution with $c$ on an initial range; see `Parking.zr_eq_cc`. In terms of the generating series $\mathbf W=\sum_n W_nX^n$ the recursion is the differential equation $\mathbf W'=G'\,\mathbf W$ with $G=\sum_{t\ge1}\frac{\omega(t)}{t}W_{t-1}X^t$ (`Parking.SingleChain.Gser`, `Parking.SingleChain.deriv_mk`).

**The Lean form.** `IsWSol ω W` is a structure with two fields, `zero` for the initial value and `succ` for the recursion; the sum runs over `range (n + 1)` and `W (n - j)` uses the subtraction of natural numbers, which is exact there. The factor $n+1$ is written as the real number `(n : ℝ) + 1`.

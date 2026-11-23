---
weight: step
short: the weighted recursion as a differential equation
---
## Description

If $W$ solves the weighted last-car recursion with weight $\omega$, then its generating series satisfies $\mathbf W'=G'\,\mathbf W$, where $G=\sum_{t\ge1}\frac{\omega(t)}{t}W_{t-1}X^t$.

## Statement

Let $\omega$ and $W$ be real sequences such that $W$ is a solution of the weighted last-car recursion with weight $\omega$ (`Parking.IsWSol`). Let $\mathbf W=\sum_{n\ge0}W_nX^n$ and let $G$ be the series `Parking.SingleChain.Gser` of $\omega$ and $W$. Then, as formal power series over the real numbers,
$$\mathbf W'=G'\,\mathbf W .$$

## Explanation

This is the recursion read coefficient by coefficient; the derivative on the left produces the factor $n+1$, and the product on the right produces the convolution. In this form the recursion can be combined with other series identities: with $E'=-E\,T'$ for $E=1/P$ in the proof of the single-chain formula (`Parking.IsWSol.ez`), and, for the threshold weight, as the differential equation of the series of a threshold (`Parking.deriv_Zs`). Only the recursion of `Parking.IsWSol` is used, not the initial value.

## Proof

Compare the coefficients of $X^n$. On the left it is $(n+1)W_{n+1}$. On the right, by the formula for the coefficients of a product (`Parking.TreeSeries.coeff_mul_range`), it is $\sum_{j=0}^{n}[X^j]G'\cdot W_{n-j}$, and $[X^j]G'=(j+1)\cdot\frac{\omega(j+1)}{j+1}W_j=\omega(j+1)W_j$. So the right-hand coefficient is $\sum_{j=0}^{n}\omega(j+1)W_jW_{n-j}$, which equals $(n+1)W_{n+1}$ by the recursion.

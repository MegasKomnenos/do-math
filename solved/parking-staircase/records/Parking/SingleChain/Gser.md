---
weight: step
short: the series G of a weighted recursion
---
## Description

The formal power series $G=\sum_{t\ge1}\frac{\omega(t)}{t}\,W_{t-1}\,X^t$ attached to a weight $\omega$ and a sequence $W$; a solution $W$ of the weighted last-car recursion satisfies $\mathbf W'=G'\mathbf W$.

## Statement

For real sequences $\omega$ and $W$, $G=G_{\omega,W}$ is the formal power series over the real numbers with constant coefficient $0$ and, for $t\ge1$, coefficient $\frac{\omega(t)}{t}\,W_{t-1}$ of $X^t$.

## Explanation

The series is made so that its derivative has the coefficients $[X^j]\,G'=\omega(j+1)\,W_j$, the factors of the weighted last-car recursion (`Parking.IsWSol`). The recursion then reads $\mathbf W'=G'\,\mathbf W$ for $\mathbf W=\sum_nW_nX^n$ (`Parking.SingleChain.deriv_mk`), so $G$ is the formal logarithm of $\mathbf W$. For the weight $\omega(t)=t$ and its solution $c$ the series $G$ is the tree series $T=\sum_ja_jX^j$ (`Parking.TreeSeries.Tser`), since $c_{t-1}=a_t$. The proof of the single-chain formula (`Parking.IsWSol.ez`) compares $G$ with $T$ through the difference $D=T-G$. For the threshold weight $\omega(t)=\min(t,y)$ the derivative $G'$ is the series `Parking.Gp` of the later part on the series of a threshold.

In the Lean definition the coefficient is given by a case distinction on $t=0$, and `W (t - 1)` is only read for $t\ge1$.

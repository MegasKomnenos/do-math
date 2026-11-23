---
weight: unit
short: property K of a triple
---
## Description

Property K at $k$ of a triple of real numbers $(a,b,c)$: the inequality $2e^{\mu/k}b\le e^{\mu}c+e^{-\mu}a$ holds for every real $\mu\ge 0$.

## Statement

Let $k$, $a$, $b$, $c$ be real numbers. The triple $(a,b,c)$ *has property K at $k$* when
$$2\,e^{\mu/k}\,b\;\le\;e^{\mu}\,c+e^{-\mu}\,a\qquad\text{for every real }\mu\ge 0 .$$

## Explanation

**What the three numbers are.** In every use, $a$, $b$, $c$ are the values at the three consecutive thresholds $k-1$, $k$, $k+1$ of one quantity that depends on the threshold: $a=W(k-1)$, $b=W(k)$, $c=W(k+1)$. The order of the triple is the order of the thresholds, so the lower value $a$ carries the factor $e^{-\mu}$ and the upper value $c$ the factor $e^{\mu}$. The number $\mu$ is called the tilt of the triple.

**What the property says.** At $\mu=0$ it is the convexity $2b\le a+c$ of the three values (`Parking.FirstLayer.TK.convex`). For $\mu>0$ it says that the triple stays convex after the lower value has been multiplied by $e^{-\mu}$ and the upper value by $e^{\mu}$, and that it does so with the room $e^{\mu/k}$ on the middle value.

**Why a family of inequalities and not convexity alone.** The convexity that the library needs is that of the tilted masses along a diagonal in the first layer (`Parking.FirstLayer.zrT_diag_convex`). It is proved by an induction along the last-car recursion (`Parking.FirstLayer.kernel_TK`), and the recursion builds the triple of one size from triples of smaller sizes by four operations: sums, multiplication by a nonnegative constant that is the same for the three thresholds, multiplication by a factor that depends on the threshold, such as $(c+i+1)/(c+\rho)$ taken at $c=k-1,k,k+1$, and a truncated self-convolution. Convexity survives the first two and does not survive the third. The triple $(2,1,0)$ is convex; multiplied by positive factors $f_-<f_0<f_+$ it becomes $(2f_-,f_0,0)$, and $2f_0>2f_-$. A factor that increases with the threshold moves weight from the lower value to the upper one, and a triple that is only just convex does not withstand that.

Property K is the form of convexity that withstands it. The identity behind this is `Parking.FirstLayer.TK.shift`: multiplying $c$ by $e^{L}$ and $a$ by $e^{M}$ has the same effect on the inequality as moving the tilt from $\mu$ to $\mu+(L-M)/2$ and multiplying the middle value by $\exp\!\big(((k+1)L+(k-1)M)/(2k)\big)$. If the factor does not decrease from the lower to the upper threshold, then $L\ge M$, the tilt moves upward, and the inequality at the new tilt is again one of the family. This is the reason the property is required for all $\mu\ge 0$: an induction hypothesis that held only at $\mu=0$ could not be used after a single increasing factor.

**Why the room $e^{\mu/k}$.** The multiplier that the shift puts on the middle value is at least $1$ exactly when $(k+1)\log(f_+/f_0)+(k-1)\log(f_-/f_0)\ge 0$, where $f_-,f_0,f_+$ are the values of the factor at $k-1,k,k+1$. This number is the second difference at $k-1,k,k+1$ of the function $z\mapsto z\log f(z)$. The weights $k+1$ and $k-1$ come from the exponent $\mu/k$: without it the condition would be $\log f_++\log f_-\ge 2\log f_0$, the log-convexity of $f$ in the threshold, and the factors of the recursion, which have the form $(z+\alpha)/(z+\beta)$ with $0\le\alpha\le\beta$, are log-concave. With it the condition is the convexity of $z\log f(z)$, which these factors satisfy (`Parking.FirstLayer.TK.mul_ratio`), as do the factors $(z+a)(z+b)/z$ (`Parking.FirstLayer.TK.mul_prod`). So the exponent $\mu/k$ on the middle value is what makes the factors of the recursion admissible. The price is that the base triples must be shown to have the property with the room $e^{\mu/k}$ (`Parking.FirstLayer.ccT_tilt_mid`, `Parking.FirstLayer.TK_ccT_top`) and that the self-convolution must be shown to preserve it (`Parking.FirstLayer.conv_TK`).

**The Lean form.** `TK k a b c` is a proposition about four real numbers. Lean's division gives $\mu/k=0$ when $k=0$; in every use $k$ is a natural number at least $3$, cast to the reals.

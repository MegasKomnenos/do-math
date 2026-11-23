---
weight: step
short: tilt shift for property K
---
## Description

For a triple $(a,b,c)$ with property K at $k>0$: multiplying $c$ by $e^{L}$ and $a$ by $e^{M}$ shifts the tilt by $(L-M)/2$ and multiplies the middle value by $\exp(((k+1)L+(k-1)M)/(2k))$.

## Statement

Let $k>0$ be real and let $(a,b,c)$ have property K at $k$ (`Parking.FirstLayer.TK`). Let $L$, $M$, $\mu$ be real numbers with $\mu+(L-M)/2\ge 0$. Then
$$2\,e^{\mu/k}\,\exp\!\Big(\frac{(k+1)L+(k-1)M}{2k}\Big)\,b\;\le\;e^{\mu}\,(e^{L}c)+e^{-\mu}\,(e^{M}a).$$

## Explanation

The statement is the defining inequality of property K, used at the tilt $\mu'=\mu+(L-M)/2$ in place of $\mu$ and rewritten. It is the one computation from which all closure properties of property K under threshold-dependent factors follow. Two cases occur.

If $L\ge M$, that is, if the factor on the upper value is at least the factor on the lower value, every $\mu\ge 0$ is admissible, and when in addition $(k+1)L+(k-1)M\ge 0$ the exponential on the left is at least $1$ and can be dropped. This gives the closure under increasing factors (`Parking.FirstLayer.TK.mul_ratio`, `Parking.FirstLayer.TK.mul_prod`).

If $L<M$, the tilt moves downward, and only the tilts $\mu\ge (M-L)/2$ are admissible, because property K says nothing at negative tilts. This case occurs once, in `Parking.FirstLayer.Sdir_TK`, for the decreasing factor $(c+\rho+1)/(c+\rho)$; there the statement is used for large $\mu$ and the remaining small tilts are treated by another argument. $\mu$ itself is not required to be nonnegative in the statement.

## Proof

Put $\mu'=\mu+(L-M)/2\ge 0$. Property K at the tilt $\mu'$ gives $2e^{\mu'/k}b\le e^{\mu'}c+e^{-\mu'}a$. Multiply by $e^{(L+M)/2}>0$. The three exponents become
$$\frac{L+M}{2}+\mu'=\mu+L,\qquad \frac{L+M}{2}-\mu'=-\mu+M,\qquad \frac{L+M}{2}+\frac{\mu'}{k}=\frac{\mu}{k}+\frac{(k+1)L+(k-1)M}{2k},$$
the last one because $\frac{L+M}{2}+\frac{L-M}{2k}=\frac{(k+1)L+(k-1)M}{2k}$; here $k\ne 0$ is used. This is the claim.

---
weight: step
short: bound exp(y) at most 1+y+y^2 on [0, 1.7]
---
## Description

$e^y\le1+y+y^2$ for real $y$ with $0\le y\le1.7$.

## Statement

For every real number $y$ with $0\le y\le1.7$, $\ e^y\le1+y+y^2$.

## Explanation

A polynomial upper bound for the exponential on an interval that reaches beyond $1$. It is used in two estimates at the critical tilt $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`). In the estimate of the sum $x_k\sum_{j=1}^{k}c_jx_k^j$, where $c_j=(j+1)^{j-1}/j!$ (`Parking.cc`, `Parking.cayleySum_le_one`), each power $(e\,x_k)^n$ is first bounded by $e^{y}$ with $y\le1.625$ and then by $1+y+y^2$, which leaves sums of powers of $\sqrt n$ that are compared with integrals. The numerical bounds for the prime kernel at the critical tilt (module `Parking.LeftHalf.KernelDecay`) use it in the same way for an exponent $y\le1.7$.

## Proof

Put $z=y/2\in[0,0.85]$. The exponential series with the standard estimate of its remainder (Mathlib's `Real.exp_bound'` with four terms) gives, for $0\le z\le1$,
$$e^z\le1+z+\frac{z^2}{2}+\frac{z^3}{6}+\frac{5z^4}{96}.$$
On $[0,0.85]$ one has $\frac z6+\frac{5z^2}{96}\le0.2$, hence $e^z\le1+z+0.7z^2$. Squaring, $e^y=(e^z)^2\le(1+z+0.7z^2)^2=1+2z+2.4z^2+1.4z^3+0.49z^4$, and this is at most $1+2z+4z^2=1+y+y^2$ because $1.4z+0.49z^2\le1.6$ for $0\le z\le0.85$. The two polynomial inequalities on $[0,0.85]$ are routine.

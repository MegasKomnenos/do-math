---
weight: step
short: product of two Poisson masses
---
## Description

For natural numbers $g \le m$: $P(g)\,P(m-g) = e^{-m}\,\operatorname{ren}(g)\,\operatorname{ren}(m-g)$, where $P(n) = e^{-n} n^n/n!$ and $\operatorname{ren}(n) = n^n/n!$.

## Statement

For all natural numbers $g$ and $m$ with $g \le m$,

$$P(g)\; P(m-g) \;=\; e^{-m}\;\operatorname{ren}(g)\;\operatorname{ren}(m-g),$$

where $P(n) = e^{-n}\operatorname{ren}(n)$ is the Poisson mass (`Parking.poissonMass`) and $\operatorname{ren}(n) = n^n/n!$ (`Parking.ren`).

## Explanation

In a product of Poisson masses whose arguments add up to $m$, the exponential factors combine to $e^{-m}$, whatever the splitting. This is what lets a sum of products of the numbers $\operatorname{ren}$ over the splittings of $m$, which is the form in which sums over compositions appear, be written as a convolution of Poisson masses. It is used in the closed forms `Parking.kc2_eq` and `Parking.kc3_eq`, and in the same way in the proofs of `Parking.pairSum_ge` and `Parking.impulse_le`. The hypothesis $g \le m$ makes the subtraction $m - g$ of natural numbers exact.

## Proof

By definition $P(g)\,P(m-g) = e^{-g}\operatorname{ren}(g)\cdot e^{-(m-g)}\operatorname{ren}(m-g)$, and $e^{-g}\, e^{-(m-g)} = e^{-m}$.

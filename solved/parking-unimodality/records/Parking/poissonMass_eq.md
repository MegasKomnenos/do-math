---
weight: step
short: Poisson mass as (n/e)^n/n!
---
## Description

The Poisson mass $e^{-n} n^n/n!$ equals $(n/e)^n/n!$.

## Statement

For every natural number $n$,

$$e^{-n}\,\frac{n^n}{n!} = \frac{(n/e)^n}{n!},$$

where the left-hand side is the Poisson mass of `Parking.poissonMass`.

## Explanation

Stirling's formula compares $n!$ with $\sqrt{2\pi n}\,(n/e)^n$. The statement puts the Poisson mass in the form in which that comparison applies directly; it is the first step of `Parking.poissonMass_le` and `Parking.poissonMass_ge`.

## Proof

$(n/e)^n = n^n/e^n$ and $e^n = 1/e^{-n}$; the rest is a rearrangement.

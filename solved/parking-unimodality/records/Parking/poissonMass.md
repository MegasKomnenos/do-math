---
weight: unit
short: Poisson mass e^{-n} n^n/n!
---
## Description

The number $e^{-n} n^n/n!$ for $n \ge 0$: the probability that a Poisson variable with mean $n$ takes the value $n$. Its value at $n = 0$ is $1$.

## Statement

For a natural number $n$, the Poisson mass at $n$ is

$$e^{-n}\,\frac{n^n}{n!} = e^{-n} \operatorname{ren}(n),$$

where $\operatorname{ren}(n) = n^n/n!$ with $0^0 = 1$ (`Parking.ren`).

## Explanation

A Poisson variable with mean $\lambda$ takes the value $n$ with probability $e^{-\lambda}\lambda^n/n!$; the number defined here is that probability for $\lambda = n$. By Stirling's formula it is close to $1/\sqrt{2\pi n}$, and the library has this with explicit bounds on both sides: `Parking.poissonMass_le` and `Parking.poissonMass_ge`.

The Poisson mass is the form in which the sequence $n^n/n!$ and the kernel $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`) are estimated at the scale $e^{-1}$, which is the scale of the tilts the library uses. From $m\,\varepsilon_m = \operatorname{ren}(m-1)$ (`Parking.mul_eps`) one gets $e^{-(i+1)}\varepsilon_{i+1} = e^{-1}\cdot e^{-i}\operatorname{ren}(i)/(i+1)$, so the tilted kernel masses are of order $i^{-3/2}$. The Poisson masses are also the renewal sequence of the Borel weights $e^{-j} a_j$, $a_j = j^{j-1}/j!$: this is `Parking.ren_conv` multiplied by $e^{-n}$, and it is the starting point of the proof of `Parking.hasSum_borel`.

The records of this part write the Poisson mass out as $e^{-n} n^n/n!$ and introduce no symbol for it. In Lean it is `Parking.poissonMass n = Real.exp (-n) * ren n`.

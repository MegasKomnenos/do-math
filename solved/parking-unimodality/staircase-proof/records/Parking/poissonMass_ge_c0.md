---
weight: step
short: lower Stirling bound with the constant c_0
---
## Description

The lower Stirling bound of the Poisson mass written with $c_0 = 1/\sqrt{2\pi}$: $c_0\,(1 - \frac{1}{12i})/\sqrt{i} \le e^{-i} i^i/i!$ for every $i \ge 1$.

## Statement

For every natural number $i \ge 1$,

$$\frac{c_0\,\bigl(1 - \frac{1}{12i}\bigr)}{\sqrt{i}} \le e^{-i}\,\frac{i^i}{i!},$$

where the right-hand side is the Poisson mass of `Parking.poissonMass` and $c_0 = 1/\sqrt{2\pi}$ (`Parking.c0`).

## Explanation

This is `Parking.poissonMass_ge` with $1/\sqrt{2\pi i}$ written as $c_0/\sqrt{i}$, the form in which the proof of `Parking.kap_diag_le` uses it: there it bounds the terms $e^{-n}\,n^n/(n\cdot n!)$, $n \ge a$, of a series from below, and their sum is then bounded below by a multiple of $c_0/\sqrt{a}$.

## Proof

By `Parking.poissonMass_ge`, the Poisson mass is at least $(1 - \frac{1}{12i})/\sqrt{2\pi i}$. Since $\sqrt{2\pi i} = \sqrt{2\pi}\,\sqrt{i}$, this is $c_0\,(1 - \frac{1}{12i})/\sqrt{i}$.

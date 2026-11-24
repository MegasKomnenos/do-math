---
weight: unit
short: lower Stirling bound of the Poisson mass
---
## Description

The Poisson mass is at least its Stirling approximation times $1 - \frac{1}{12n}$: $(1 - \frac{1}{12n})/\sqrt{2\pi n} \le e^{-n} n^n/n!$ for every $n \ge 1$.

## Statement

For every natural number $n \ge 1$,

$$\Bigl(1 - \frac{1}{12n}\Bigr)\frac{1}{\sqrt{2\pi n}} \le e^{-n}\,\frac{n^n}{n!},$$

where the right-hand side is the Poisson mass of `Parking.poissonMass`.

## Explanation

Together with `Parking.poissonMass_le` this encloses the Poisson mass between $(1 - \frac{1}{12n})/\sqrt{2\pi n}$ and $1/\sqrt{2\pi n}$: Stirling's approximation with a relative error of at most $\frac{1}{12n}$. The lower bound is Robbins' upper bound for the factorial (`Parking.factorial_lt_robbins`), with $e^{-1/(12n)}$ replaced by the smaller and more convenient $1 - \frac{1}{12n}$.

It is used where a lower bound of order $n^{-1/2}$ for the Poisson masses is needed: for the divergence of their sum in the proof of `Parking.hasSum_borel`, for the lower bound of the resolvent sequence (`Parking.Gres_lower`), and in the estimates of the tilted prime kernel that the proof of `Parking.step_pos_large` uses (`Parking.order_pos`). The form with the constant $c_0 = 1/\sqrt{2\pi}$ is `Parking.poissonMass_ge_c0`.

## Proof

By `Parking.poissonMass_eq`, the Poisson mass is $(n/e)^n/n!$, so after multiplying by the positive numbers $n!$ and $\sqrt{2\pi n}$ the claim reads

$$\Bigl(1 - \frac{1}{12n}\Bigr)\, n! \le \Bigl(\frac{n}{e}\Bigr)^{n} \sqrt{2\pi n}.$$

From $1 + t \le e^{t}$ at $t = -\frac{1}{12n}$ we have $1 - \frac{1}{12n} \le e^{-1/(12n)}$. By `Parking.factorial_lt_robbins`, $n! < \sqrt{2\pi n}\,(n/e)^n e^{1/(12n)}$, and in particular $n! \le \sqrt{2\pi n}\,(n/e)^n e^{1/(12n)}$. Hence

$$\Bigl(1 - \frac{1}{12n}\Bigr)\, n! \le e^{-1/(12n)}\, n! \le e^{-1/(12n)} \sqrt{2\pi n}\,\Bigl(\frac{n}{e}\Bigr)^{n} e^{1/(12n)} = \sqrt{2\pi n}\,\Bigl(\frac{n}{e}\Bigr)^{n}.$$

---
weight: step
short: upper bound 0.39894229 for 1/√(2π)
---
## Description

The constant $c_0 = 1/\sqrt{2\pi}$ is at most $0.39894229$.

## Statement

$$c_0 \le 0.39894229,$$

where $c_0 = 1/\sqrt{2\pi}$ (`Parking.c0`).

## Explanation

The value of the constant is $c_0 = 0.3989422804\ldots$, so the bound exceeds it by less than $10^{-8}$.

The constant enters the curve increase through Stirling's bound $e^{-m} m^m/m! \le c_0/\sqrt{m}$ for the Poisson mass. The numerical statements of the curve increase do not mention $c_0$: each of `Parking.Wsum_numeric`, `Parking.Asum_numeric`, `Parking.Gsum_numeric` and `Parking.impulse_numeric` is about a real number $a$ with $a \le 0.39894229$. The present statement is what allows $a = c_0$ there; it is used for this in the proofs of `Parking.Wsum_ge`, `Parking.Gsum_le`, `Parking.Asum_le` and `Parking.curve_step_pos`.

A bound to five places would not do. The proof of `Parking.impulse_numeric` uses the inequality $1.253314 \cdot a \le 1/2$, where $1.253314$ is $\sqrt{\pi/2} = 1/(2c_0) = 1.2533141\ldots$ rounded down. For $a = 0.39894229$ the product is $0.49999995\ldots$; for $a = 0.39895$ it would be $0.50000962\ldots$, which is larger than $1/2$.

## Proof

Mathlib provides the bound $3.14159265358979323846 < \pi$. The inequality

$$\Bigl(\frac{1}{0.39894229}\Bigr)^2 \le 2 \cdot 3.14159265358979323846$$

is an inequality between two rational numbers and is verified by exact arithmetic; the left side is $6.2831850048\ldots$ and the right side is $6.2831853071\ldots$. Hence $(1/0.39894229)^2 \le 2\pi$, and since the square root is monotone, $1/0.39894229 \le \sqrt{2\pi}$. Multiplying by $0.39894229$ gives $1 \le 0.39894229 \cdot \sqrt{2\pi}$, and dividing by $\sqrt{2\pi} > 0$ gives $c_0 = 1/\sqrt{2\pi} \le 0.39894229$.

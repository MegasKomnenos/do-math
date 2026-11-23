---
weight: step
short: decimal enclosure of 1/√(2π)
---
## Description

The constant $c_0 = 1/\sqrt{2\pi}$ satisfies $0.39894 \le c_0 \le 0.39895$.

## Statement

$$\frac{19947}{50000} \le c_0 \le \frac{7979}{20000},$$

where $c_0 = 1/\sqrt{2\pi}$ (`Parking.c0`). In decimals, $0.39894 \le c_0 \le 0.39895$.

## Explanation

The enclosure is what the explicit numerical inequalities of the later parts use in place of the irrational constant: the bookkeeping of the crossing strip (in the proof of `Parking.crossing_strip`) and the lower bound of the resolvent sequence in the far rows (in the proof of `Parking.caseFar`). The true value is $0.398942\ldots$, so both bounds are correct to five decimal places.

## Proof

Mathlib provides $3.141592 < \pi < 3.141593$. The claim is equivalent to

$$\frac{20000}{7979} \le \sqrt{2\pi} \le \frac{50000}{19947}.$$

For the upper bound, $2\pi \le 2 \cdot 3.141593 \le (50000/19947)^2$, and the square root is monotone. For the lower bound, $(20000/7979)^2 \le 2 \cdot 3.141592 \le 2\pi$. The two inequalities between rational numbers, $2 \cdot \frac{3141593}{1000000} \le \bigl(\frac{50000}{19947}\bigr)^2$ and $\bigl(\frac{20000}{7979}\bigr)^2 \le 2 \cdot \frac{3141592}{1000000}$, are verified by exact rational arithmetic. Taking reciprocals of the positive numbers gives the enclosure of $c_0$.

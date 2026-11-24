---
weight: step
short: decimal enclosure of exp(−0.35)
---
## Description

The number $e^{-0.35}$ lies between $0.704688$ and $0.704689$.

## Statement

$$0.704688 \le e^{-0.35} \le 0.704689.$$

## Explanation

The value is $e^{-0.35} = 0.70468808\ldots$, so the two bounds are the value rounded down and up at the sixth decimal place.

The number $0.35$ is the value of the free parameter $c'$ at which the upper bound of the impulse, `Parking.impulse_le`, is applied in the proof of `Parking.curve_step_pos`. That bound contains the factor $e^{-c'}$ in front of a difference of two nonnegative terms. The numerical statement `Parking.impulse_numeric`, which finishes the comparison, treats the factor as a real number $\eta$ with $0.704688 \le \eta \le 0.704689$ and uses the lower bound on the term that is subtracted and the upper bound on the term that is added; this is why both bounds are stated. The present statement supplies the two hypotheses on $\eta$ for $\eta = e^{-0.35}$.

In the Lean statement the exponent is a real variable $c$ with the hypothesis $c = 0.35$, and the conclusion is about $e^{-c}$. This says the same as the statement above. The proof keeps the exponent as the symbol $c$ and puts in the value $0.35$ only where a rational number has to be evaluated.

## Proof

The proof rests on two bounds of the exponential function by its Taylor polynomials at $0$, both taken from Mathlib and written out for the orders used here.

- *Upper bound, order 12.* For $0 \le x \le 1$,
  $$e^x \le \sum_{j=0}^{11} \frac{x^j}{j!} + \frac{13\,x^{12}}{12 \cdot 12!}.$$
  This is the Taylor polynomial of degree $11$ plus a bound of the remainder; it is the case $n = 12$ of Mathlib's bound $e^x \le \sum_{j<n} x^j/j! + x^n (n+1)/(n! \cdot n)$ for $0 \le x \le 1$.
- *Lower bound, order 8.* For $x \ge 0$,
  $$\sum_{j=0}^{7} \frac{x^j}{j!} \le e^x,$$
  because every term of the exponential series is nonnegative.

At $x = 0.35$ both polynomials are rational numbers, and exact arithmetic gives

$$1.4190675 \le \sum_{j=0}^{7} \frac{0.35^j}{j!} \qquad\text{and}\qquad \sum_{j=0}^{11} \frac{0.35^j}{j!} + \frac{13 \cdot 0.35^{12}}{12 \cdot 12!} \le 1.4190676,$$

so $1.4190675 \le e^{0.35} \le 1.4190676$.

Now $e^{-0.35}$ is positive and $e^{-0.35} \cdot e^{0.35} = 1$. From $e^{0.35} \le 1.4190676$ it follows that $1 \le 1.4190676 \cdot e^{-0.35}$, and since $0.704688 \cdot 1.4190676 = 0.9999999089088 \le 1$, this gives $0.704688 \le e^{-0.35}$. From $1.4190675 \le e^{0.35}$ it follows that $1.4190675 \cdot e^{-0.35} \le 1$, and since $0.704689 \cdot 1.4190675 = 1.0000012575075 \ge 1$, this gives $e^{-0.35} \le 0.704689$.

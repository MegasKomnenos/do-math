---
weight: step
short: the closed bound for the kernel deficit is nonnegative
---
## Description

For $2a \le k$ the closed form $\mathsf T(k,a)$ that bounds the relative growth of the kernel deficit on a diagonal step is nonnegative.

## Statement

Let $k$ and $a$ be natural numbers with $2a \le k$. Then $\mathsf T(k,a) \ge 0$, where $\mathsf T(0,a) = 0$ and, for $k \ge 1$, with $\xi = a/k$,

$$\mathsf T(k,a) = \frac{\frac32\,\xi\,\bigl(1+\frac{2}{3(k+2)}\bigr)\bigl(1+\frac32\xi+\frac38\xi^2\bigr)}{\frac{23}{24}-\frac32\,\xi\,\bigl(1+\frac\xi4\bigr)}$$

(`Parking.kapStepBound`).

## Explanation

The numerator of $\mathsf T(k,a)$ is nonnegative for all $k$ and $a$; the statement is that the denominator is positive when $\xi = a/k \le \frac12$. It is used in `Parking.scalar_step`, where $\log(1 + \mathsf T/k) \le \mathsf T/k$ is applied and needs $1 + \mathsf T/k > 0$.

The Lean statement has the single hypothesis `2 * a ≤ k` and therefore includes $k = a = 0$; there Lean's value of $\mathsf T$ is $0$, by its convention that a quotient by zero is zero, and the statement is trivial.

## Proof

If $k = 0$, the hypothesis gives $a = 0$, and $\mathsf T(0,0) = 0$. Let $k \ge 1$ and $\xi = a/k$. From $2a \le k$ we get $0 \le \xi \le \frac12$, hence $\xi^2 \le \frac12\xi$ and

$$\frac32\,\xi\,\Bigl(1+\frac\xi4\Bigr) = \frac32\,\xi + \frac38\,\xi^2 \;\le\; \frac34 + \frac{3}{32} = \frac{27}{32} \;<\; \frac{23}{24}.$$

So the denominator of $\mathsf T(k,a)$ is positive. The numerator is a product of nonnegative factors. A quotient of a nonnegative number by a positive one is nonnegative.

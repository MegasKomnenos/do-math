---
weight: unit
short: Robbins' upper bound for the factorial
---
## Description

Robbins' upper bound for the factorial: $n! \le \sqrt{2\pi n}\,(n/e)^n\, e^{1/(12n)}$ for every $n \ge 1$.

## Statement

For every natural number $n \ge 1$,

$$n! \le \sqrt{2\pi n}\,\Bigl(\frac{n}{e}\Bigr)^{n} e^{1/(12n)}.$$

## Explanation

This is the classical upper half of Robbins' form of Stirling's formula, which encloses $n!$ between $\sqrt{2\pi n}\,(n/e)^n e^{1/(12n+1)}$ and $\sqrt{2\pi n}\,(n/e)^n e^{1/(12n)}$. The library needs the upper bound in the form stated and, from below, only the weaker bound $\sqrt{2\pi n}\,(n/e)^n \le n!$, which Mathlib provides.

The version of Mathlib that the library is built on does not state the upper bound, but it contains what its proof consists of: the sequence $s_n = n!/(\sqrt{2n}\,(n/e)^n)$, its limit $\sqrt{\pi}$, and the bound $\log s_k - \log s_{k+1} \le \frac{1}{12k(k+1)}$ for one step. The right-hand side of that bound is the difference $\frac{1}{12k} - \frac{1}{12(k+1)}$, so the steps telescope, and the sum of all steps from $n$ on is at most $\frac{1}{12n}$. That is the whole argument.

The bound is used twice: for the lower bound of the Poisson mass $e^{-n}n^n/n!$ (`Parking.poissonMass_ge`), and for the upper bound of the mean of the birthday law (`Parking.sbirth_le`).

## Proof

Let $s_n = n!/(\sqrt{2n}\,(n/e)^n)$ for $n \ge 1$; this is Mathlib's Stirling sequence, and $s_n > 0$. Three facts about it are taken from Mathlib: the one-step bound

$$\log s_k - \log s_{k+1} \le \frac{1}{12\,k\,(k+1)} \qquad (k \ge 1),$$

the limit $s_m \to \sqrt{\pi}$ as $m \to \infty$, and the positivity of $s_n$.

*Telescoping.* For $1 \le n \le m$,

$$\log s_n + \frac{1}{12m} \le \log s_m + \frac{1}{12n}.$$

This is proved by induction on $m$. For $m = n$ it is an equality. If it holds for $m = k$, then, since $\frac{1}{12k(k+1)} = \frac{1}{12k} - \frac{1}{12(k+1)}$, the one-step bound gives $\log s_k + \frac{1}{12(k+1)} \le \log s_{k+1} + \frac{1}{12k}$, and adding the two inequalities gives the claim for $m = k+1$.

*Passage to the limit.* Dropping the nonnegative term $\frac{1}{12m}$, we have $\log s_n - \frac{1}{12n} \le \log s_m$ for every $m \ge n$. The logarithm is continuous at $\sqrt{\pi} > 0$, so $\log s_m \to \log\sqrt{\pi}$, and therefore $\log s_n - \frac{1}{12n} \le \log\sqrt{\pi}$. Applying the exponential function,

$$s_n \le \sqrt{\pi}\; e^{1/(12n)} \qquad (n \ge 1).$$

*Conclusion.* Multiplying by the positive number $\sqrt{2n}\,(n/e)^n$ gives $n! \le \sqrt{\pi}\,\sqrt{2n}\,(n/e)^n e^{1/(12n)}$, and $\sqrt{\pi}\,\sqrt{2n} = \sqrt{2\pi n}$.

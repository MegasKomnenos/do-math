---
weight: unit
short: Robbins' lower bound for the factorial
---
## Description

Robbins' lower bound for the factorial: $\sqrt{2\pi n}\,(n/e)^n\, e^{1/(12n+1)} < n!$ for every $n \ge 1$.

## Statement

For every natural number $n \ge 1$,

$$\sqrt{2\pi n}\,\Bigl(\frac{n}{e}\Bigr)^{n} e^{1/(12n+1)} < n!.$$

## Explanation

This is the lower half of Robbins' form of Stirling's formula, which encloses $n!$ strictly between $\sqrt{2\pi n}\,(n/e)^n e^{1/(12n+1)}$ and $\sqrt{2\pi n}\,(n/e)^n e^{1/(12n)}$ for every $n \ge 1$ [robbins1955, p. 26, (1) and (2)]. The upper half is `Parking.factorial_lt_robbins`.

No other declaration of the library uses this bound. The estimates of the library need from below only the weaker bound $\sqrt{2\pi n}\,(n/e)^n \le n!$, which Mathlib provides and which `Parking.poissonMass_le` uses. The bound is stated so that the library proves Robbins' inequality as it stands in the literature, with both halves and with strict inequality in each.

The version of Mathlib that the library is built on does not state the bound. It contains the sequence $s_n = n!/(\sqrt{2n}\,(n/e)^n)$, its limit $\sqrt{\pi}$, and the expansion of one step of its logarithm into a series,

$$\log s_n - \log s_{n+1} = \sum_{k \ge 1} \frac{1}{2k+1}\Bigl(\frac{1}{2n+1}\Bigr)^{2k} \qquad (n \ge 1).$$

All terms of the series are positive, so its sum is at least its first term $\frac{1}{3(2n+1)^2}$. This first term exceeds the difference $\frac{1}{12n+1} - \frac{1}{12(n+1)+1}$ for every $n \ge 1$. The sequence $\log s_n - \frac{1}{12n+1}$ therefore decreases strictly, and a strictly decreasing sequence stays strictly above its limit. The proof of the upper half has the same three parts, with the series bounded from above by a geometric series.

## Proof

Let $s_n = n!/(\sqrt{2n}\,(n/e)^n)$ for $n \ge 1$; this is Mathlib's Stirling sequence, and $s_n > 0$ because it is a quotient of positive numbers. Two facts about it are taken from Mathlib: the series for one step that is displayed in the explanation, and the limit $s_n \to \sqrt{\pi}$ as $n \to \infty$.

*One step.* Let $n \ge 1$. Every term of the series is nonnegative, so the sum of the series is at least its first term:

$$\log s_n - \log s_{n+1} \ge \frac13\Bigl(\frac{1}{2n+1}\Bigr)^{2}.$$

Bringing the three fractions to a common denominator gives

$$\frac13\Bigl(\frac{1}{2n+1}\Bigr)^{2} - \Bigl(\frac{1}{12n+1} - \frac{1}{12(n+1)+1}\Bigr) = \frac{24n - 23}{3\,(2n+1)^2\,(12n+1)\,(12(n+1)+1)},$$

because $(12n+1)(12n+13) - 36(2n+1)^2 = 24n - 23$. For $n \ge 1$ the numerator and the denominator are positive. Therefore

$$\frac{1}{12n+1} - \frac{1}{12(n+1)+1} < \log s_n - \log s_{n+1} \qquad (n \ge 1).$$

*The limit.* The logarithm is continuous at $\sqrt{\pi} > 0$, so $\log s_n \to \log\sqrt{\pi}$. Since $12n + 1 \to \infty$, we have $\frac{1}{12n+1} \to 0$, and therefore $\log s_n - \frac{1}{12n+1} \to \log\sqrt{\pi}$.

*The bound for $\log s_n$.* Put $v_n = \log s_n - \frac{1}{12n+1}$. By the first part $v_{n+1} < v_n$ for every $n \ge 1$; in particular the sequence $(v_n)$ does not increase. A sequence that does not increase and converges is bounded below by its limit, so $\log\sqrt{\pi} \le v_{n+1}$. Hence $\log\sqrt{\pi} \le v_{n+1} < v_n$, that is,

$$\frac{1}{12n+1} < \log s_n - \log\sqrt{\pi} \qquad (n \ge 1).$$

*Conclusion.* By the definition of $s_n$ and because $\sqrt{\pi}\,\sqrt{2n} = \sqrt{2\pi n}$ and $e^{\log s_n - \log\sqrt{\pi}} = s_n/\sqrt{\pi}$,

$$n! = s_n\,\sqrt{2n}\,\Bigl(\frac{n}{e}\Bigr)^{n} = \sqrt{2\pi n}\,\Bigl(\frac{n}{e}\Bigr)^{n} e^{\log s_n - \log\sqrt{\pi}}.$$

The exponential function increases strictly, so $e^{1/(12n+1)} < e^{\log s_n - \log\sqrt{\pi}}$, and multiplying by the positive number $\sqrt{2\pi n}\,(n/e)^n$ gives the claim.

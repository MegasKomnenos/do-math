---
weight: unit
short: Robbins' upper bound for the factorial
---
## Description

Robbins' upper bound for the factorial: $n! < \sqrt{2\pi n}\,(n/e)^n\, e^{1/(12n)}$ for every $n \ge 1$.

## Statement

For every natural number $n \ge 1$,

$$n! < \sqrt{2\pi n}\,\Bigl(\frac{n}{e}\Bigr)^{n} e^{1/(12n)}.$$

## Explanation

This is the upper half of Robbins' form of Stirling's formula, which encloses $n!$ strictly between $\sqrt{2\pi n}\,(n/e)^n e^{1/(12n+1)}$ and $\sqrt{2\pi n}\,(n/e)^n e^{1/(12n)}$ for every $n \ge 1$ [robbins1955, p. 26, (1) and (2)].

The bound is used twice: for the lower bound of the Poisson mass $e^{-n}n^n/n!$ (`Parking.poissonMass_ge`), and for the upper bound of the mean of the birthday law (`Parking.sbirth_le`). Both uses need it only with $\le$ in place of $<$. From below, the estimates of the library need only the weaker bound $\sqrt{2\pi n}\,(n/e)^n \le n!$, which Mathlib provides and which `Parking.poissonMass_le` uses.

The version of Mathlib that the library is built on does not state the bound, but it contains what the proof starts from: the sequence $s_n = n!/(\sqrt{2n}\,(n/e)^n)$, its limit $\sqrt{\pi}$, and the expansion of one step of its logarithm into a series,

$$\log s_n - \log s_{n+1} = \sum_{k \ge 1} \frac{1}{2k+1}\Bigl(\frac{1}{2n+1}\Bigr)^{2k} \qquad (n \ge 1).$$

Mathlib also derives from this series the bound $\log s_n - \log s_{n+1} \le \frac{1}{12n(n+1)}$, with $\le$. The statement here has $<$, so the proof goes back to the series and compares it term by term with a geometric series, with strict inequality in one term. The right-hand side $\frac{1}{12n(n+1)}$ of the resulting bound is the difference $\frac{1}{12n} - \frac{1}{12(n+1)}$. The sequence $\log s_n - \frac{1}{12n}$ therefore increases strictly, and a strictly increasing sequence stays strictly below its limit.

## Proof

Let $s_n = n!/(\sqrt{2n}\,(n/e)^n)$ for $n \ge 1$; this is Mathlib's Stirling sequence, and $s_n > 0$ because it is a quotient of positive numbers. Two facts about it are taken from Mathlib: the series for one step that is displayed in the explanation, and the limit $s_n \to \sqrt{\pi}$ as $n \to \infty$.

*One step.* Let $n \ge 1$ and $r = 1/(2n+1)^2$, so that $0 < r < 1$. In terms of $r$ the series reads $\log s_n - \log s_{n+1} = \sum_{k \ge 1} \frac{r^k}{2k+1}$. We compare it term by term with the geometric series $\sum_{k \ge 1} \frac{r^k}{3}$. For every $k \ge 1$ we have $2k+1 \ge 3$ and $r^k \ge 0$, hence $\frac{r^k}{2k+1} \le \frac{r^k}{3}$; for $k = 2$ the inequality is strict, $\frac{r^2}{5} < \frac{r^2}{3}$, because $r^2 > 0$. If each term of one convergent series is at most the corresponding term of another, and one term is strictly smaller, then its sum is strictly smaller. The geometric series has the sum $\frac13 \cdot \frac{r}{1-r}$, and $1 - r = 4n(n+1)\,r$ because $(2n+1)^2 - 1 = 4n(n+1)$; so its sum is $\frac{1}{12n(n+1)} = \frac{1}{12n} - \frac{1}{12(n+1)}$. Therefore

$$\log s_n - \log s_{n+1} < \frac{1}{12n} - \frac{1}{12(n+1)} \qquad (n \ge 1).$$

*The limit.* The logarithm is continuous at $\sqrt{\pi} > 0$, so $\log s_n \to \log\sqrt{\pi}$. Since $12n \to \infty$, we have $\frac{1}{12n} \to 0$, and therefore $\log s_n - \frac{1}{12n} \to \log\sqrt{\pi}$.

*The bound for $\log s_n$.* Put $u_n = \log s_n - \frac{1}{12n}$. By the first part $u_n < u_{n+1}$ for every $n \ge 1$; in particular the sequence $(u_n)$ does not decrease. A sequence that does not decrease and converges is bounded above by its limit, so $u_{n+1} \le \log\sqrt{\pi}$. Hence $u_n < u_{n+1} \le \log\sqrt{\pi}$, that is,

$$\log s_n - \log\sqrt{\pi} < \frac{1}{12n} \qquad (n \ge 1).$$

*Conclusion.* By the definition of $s_n$ and because $\sqrt{\pi}\,\sqrt{2n} = \sqrt{2\pi n}$ and $e^{\log s_n - \log\sqrt{\pi}} = s_n/\sqrt{\pi}$,

$$n! = s_n\,\sqrt{2n}\,\Bigl(\frac{n}{e}\Bigr)^{n} = \sqrt{2\pi n}\,\Bigl(\frac{n}{e}\Bigr)^{n} e^{\log s_n - \log\sqrt{\pi}}.$$

The exponential function increases strictly, so $e^{\log s_n - \log\sqrt{\pi}} < e^{1/(12n)}$, and multiplying by the positive number $\sqrt{2\pi n}\,(n/e)^n$ gives the claim.

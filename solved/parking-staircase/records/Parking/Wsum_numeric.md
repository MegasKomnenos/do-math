---
weight: step
short: arithmetic of the lower bound of the weight sum
---
## Description

For real $s \ge 6.48$, $R = s^2$, $0 \le a \le 0.39894229$, $S_1 \le 2s + \frac{1}{2s} - 2.44948$ and $S_2 \le 1.63300$: $\frac R2 - 1.06385\,s + 0.7184 \le \frac{R-1}{2} - \frac43 a S_1 - \frac{a}{15} S_2$.

## Statement

Let $s$, $a$, $R$, $S_1$ and $S_2$ be real numbers with $s \ge 6.48$, $R = s^2$, $0 \le a \le 0.39894229$,

$$S_1 \le 2s + \frac{1}{2s} - 2.44948 \qquad\text{and}\qquad S_2 \le 1.63300.$$

Then

$$\frac R2 - 1.06385\,s + 0.7184 \le \frac{R-1}{2} - \frac43\,a\,S_1 - \frac{a}{15}\,S_2.$$

## Explanation

The statement is the arithmetic behind `Parking.Wsum_ge`, the lower bound of the weight sum $W_\Sigma(R) = \sum_{b=1}^{R}\kappa_2(b)$ (`Parking.Wsum`), where $\kappa_2$ is the convolution `Parking.kc2`. There $R \ge 42$ is a natural number, $s = \sqrt{R}$, $a = c_0 = 1/\sqrt{2\pi}$, and

$$S_1 = \sum_{b=2}^{R} b^{-1/2}, \qquad S_2 = \sum_{b=2}^{R} b^{-3/2}.$$

The right side is what one obtains by summing over $2 \le b \le R$ the lower bound $\kappa_2(b) \ge \frac12 - \frac43 c_0 b^{-1/2} - \frac{c_0}{15} b^{-3/2}$, and the hypotheses on $S_1$ and $S_2$ are the bounds `Parking.sum_Icc_two_inv_sqrt_le` and `Parking.sum_Icc_two_inv_sqrt_cube_le` of the two power sums. The hypothesis on $a$ is `Parking.c0_le`.

The left side is the polynomial

$$W_0(s) = \frac{s^2}{2} - 1.06385\,s + 0.7184,$$

which from here on stands for the weight sum: it is the lower bound assumed in `Parking.pair_numeric`, and it appears on the right side of `Parking.impulse_numeric`. Its two decimal constants are what the hypotheses give after rounding. The coefficient of $s$ is $\frac83 \cdot 0.39894229 = 1.0638461\ldots$, rounded up to $1.06385$. The constant term is $-\frac12 + \frac43 \cdot 0.39894229 \cdot \bigl(2.44948 - \frac{25}{324}\bigr) - \frac{0.39894229}{15} \cdot 1.633 = 0.71845991\ldots$, rounded down to $0.7184$; the number $\frac{25}{324} = \frac{1}{2 \cdot 6.48}$ bounds the term $\frac{1}{2s}$.

Unlike the other statements of this kind (`Parking.Asum_numeric`, `Parking.Gsum_numeric`), this one needs no polynomial certificate: after the hypotheses are inserted the inequality is linear in $s$ and $\frac{1}{2s}$.

## Proof

Substitute $R = s^2$ and write $q = \frac{1}{2s}$. Then $q > 0$, and $q \le \frac{25}{324}$ because $s \ge 6.48 = \frac{162}{25}$.

Since $a \ge 0$, the hypotheses give $a S_1 \le a\,(2s + q - 2.44948)$ and $a S_2 \le 1.633\,a \le 1.633 \cdot 0.39894229$. The number $2s + q - 2.44948$ is nonnegative, so $a \le 0.39894229$ gives $a\,(2s + q - 2.44948) \le 0.39894229\,(2s + q - 2.44948)$. Therefore

$$\frac{s^2-1}{2} - \frac43 a S_1 - \frac{a}{15} S_2 \ge \frac{s^2}{2} - \frac12 - \frac43 \cdot 0.39894229\,(2s + q - 2.44948) - \frac{0.39894229}{15} \cdot 1.633.$$

The right side is $\frac{s^2}{2}$ plus an expression that is linear in $s$ and $q$. In it the coefficient of $s$ is $-1.0638461\ldots \ge -1.06385$, and $s \ge 0$; the coefficient of $q$ is negative, and $q \le \frac{25}{324}$; and with $q$ replaced by $\frac{25}{324}$ the constant term is $0.71845991\ldots \ge 0.7184$. Hence the right side is at least $\frac{s^2}{2} - 1.06385\,s + 0.7184$. These comparisons are between rational numbers and are routine.

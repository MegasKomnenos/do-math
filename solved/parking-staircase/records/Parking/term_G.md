---
weight: step
short: one term of the sum G
---
## Description

For real $p > 0$, $B = p^2 \ge 1$, $r \le a/p$ and $\kappa \ge \frac12 - \frac43\frac{a}{p} - \frac{a}{15}\frac{1}{Bp}$: $3(B-1)r - \frac52\kappa \le a\bigl(3p + \frac{1}{3p} + \frac{1}{6Bp}\bigr) - \frac54$.

## Statement

Let $a$, $p$, $B$, $r$ and $\kappa$ be real numbers with $p > 0$, $B = p^2$ and $B \ge 1$. If

$$r \le \frac{a}{p} \qquad\text{and}\qquad \frac12 - \frac43 \cdot \frac{a}{p} - \frac{a}{15} \cdot \frac{1}{Bp} \le \kappa,$$

then

$$3(B-1)\,r - \frac52\,\kappa \le a\Bigl(3p + \frac13 \cdot \frac1p + \frac16 \cdot \frac{1}{Bp}\Bigr) - \frac54.$$

## Explanation

Here $\kappa$ and $r$ are arbitrary real numbers. The statement is applied in the proof of `Parking.Gsum_le`, once for each natural number $b$ with $2 \le b \le R$, with $B = b$, $p = \sqrt{b}$, $a = c_0 = 1/\sqrt{2\pi}$, $r = P(b) = e^{-b}b^b/b!$ the Poisson mass and $\kappa = \kappa_2(b)$ (`Parking.kc2`). The two hypotheses are then Stirling's bound $P(b) \le c_0/\sqrt{b}$ and the lower bound $\kappa_2(b) \ge \frac12 - \bigl(\frac43 + \frac{1}{15b}\bigr)P(b)$ of `Parking.kc2_lower` combined with Stirling's bound.

The left side is the $b$-th term of the main part of the sum $G(k,R)$ (`Parking.Gsum`): by the closed form $\kappa_3(b) = (b-1)P(b) - 2\kappa_2(b)$ of `Parking.kc3_eq` for the convolution $\kappa_3$ (`Parking.kc3`), the three contributions $\frac72\kappa_2(b) + 2\kappa_3(b) + \kappa_3(b)$ add up to $3(b-1)P(b) - \frac52\kappa_2(b)$. The convolution $\kappa_2$ enters with a negative coefficient, and this is why a lower bound of $\kappa_2$ is needed. The right side is a combination of the powers $b^{1/2}$, $b^{-1/2}$, $b^{-3/2}$ and a constant, so that the sum over $b$ becomes $c_0\bigl(3S_3 + \frac13 S_1 + \frac16 S_2\bigr) - \frac54(R-1)$ with $S_3 = \sum b^{1/2}$, $S_1 = \sum b^{-1/2}$, $S_2 = \sum b^{-3/2}$, the expression that `Parking.Gsum_numeric` bounds.

The Lean statement writes the reciprocals as $1/p$ and $1/(B \cdot p)$ and has no hypothesis on the sign of $a$; none is needed, because the conclusion is a combination of the two hypotheses with nonnegative coefficients.

## Proof

Substitute $B = p^2$, so that $Bp = p^3$. Since $B \ge 1$, the coefficient $3(B-1)$ is nonnegative, and the first hypothesis gives

$$3(B-1)\,r \le 3(p^2-1)\frac{a}{p} = 3a\Bigl(p - \frac1p\Bigr).$$

The second hypothesis, multiplied by $-\frac52$, gives

$$-\frac52\,\kappa \le -\frac54 + \frac{10}{3} \cdot \frac{a}{p} + \frac{a}{6} \cdot \frac{1}{p^3}.$$

Adding the two,

$$3(B-1)\,r - \frac52\,\kappa \le a\Bigl(3p - \frac3p + \frac{10}{3p} + \frac{1}{6p^3}\Bigr) - \frac54 = a\Bigl(3p + \frac{1}{3p} + \frac{1}{6Bp}\Bigr) - \frac54.$$

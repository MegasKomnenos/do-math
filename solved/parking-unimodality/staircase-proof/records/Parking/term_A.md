---
weight: step
short: one term of the sum 𝒜
---
## Description

For real $p > 0$, $1 \le B = p^2 \le R$, $r \le a/p$ and $\kappa \ge \frac12 - \frac43\frac{a}{p} - \frac{a}{15}\frac{1}{Bp}$: $(3R-2B)(B-1)r - (\frac52 R - B)\kappa \le a\bigl(-2Bp + (3R+\frac23)p + (\frac R3 - \frac1{15})\frac1p + \frac R6\frac{1}{Bp}\bigr) - \frac12(\frac52 R - B)$.

## Statement

Let $a$, $p$, $B$, $R$, $r$ and $\kappa$ be real numbers with $p > 0$, $B = p^2$ and $1 \le B \le R$. If

$$r \le \frac{a}{p} \qquad\text{and}\qquad \frac12 - \frac43 \cdot \frac{a}{p} - \frac{a}{15} \cdot \frac{1}{Bp} \le \kappa,$$

then

$$(3R-2B)(B-1)\,r - \Bigl(\frac52 R - B\Bigr)\kappa \le a\Bigl(-2Bp + \Bigl(3R+\frac23\Bigr)p + \Bigl(\frac R3 - \frac{1}{15}\Bigr)\frac1p + \frac R6 \cdot \frac{1}{Bp}\Bigr) - \frac12\Bigl(\frac52 R - B\Bigr).$$

## Explanation

This is the counterpart of `Parking.term_G` for the sum $\mathcal{A}(k,R)$ (`Parking.Asum`), with the same two hypotheses and with weights that depend on $R$. Here $\kappa$, $r$ and $R$ are arbitrary real numbers. The statement is applied in the proof of `Parking.Asum_le`, once for each natural number $b$ with $2 \le b \le R$, with $B = b$, $p = \sqrt{b}$, $a = c_0 = 1/\sqrt{2\pi}$, $r = P(b) = e^{-b}b^b/b!$ the Poisson mass and $\kappa = \kappa_2(b)$ (`Parking.kc2`). The hypotheses are then Stirling's bound $P(b) \le c_0/\sqrt{b}$ and the lower bound of $\kappa_2(b)$ that `Parking.kc2_lower` and Stirling's bound give together.

The left side is the $b$-th term of the main part of $\mathcal{A}$. That term is $\bigl(R - \frac b2\bigr)\bigl(\kappa_2(b) + 2\kappa_3(b)\bigr) + \frac52(R-b)\kappa_2(b) + (R-b)\kappa_3(b)$, and with the closed form $\kappa_3(b) = (b-1)P(b) - 2\kappa_2(b)$ of `Parking.kc3_eq` for the convolution $\kappa_3$ (`Parking.kc3`) it equals $(3R-2b)(b-1)P(b) - \bigl(\frac52 R - b\bigr)\kappa_2(b)$. As in `Parking.term_G`, $\kappa_2$ enters with a negative coefficient. The right side is a combination of $b^{3/2}$, $b^{1/2}$, $b^{-1/2}$, $b^{-3/2}$ and a term linear in $b$. Summed over $2 \le b \le R$ it becomes

$$c_0\Bigl(-2S_4 + \Bigl(3R+\frac23\Bigr)S_3 + \Bigl(\frac R3 - \frac1{15}\Bigr)S_1 + \frac R6 S_2\Bigr) - \Bigl(R^2 - \frac32 R + \frac12\Bigr),$$

with $S_4 = \sum b^{3/2}$, $S_3 = \sum b^{1/2}$, $S_1 = \sum b^{-1/2}$, $S_2 = \sum b^{-3/2}$; this is the main part of the left side of `Parking.Asum_numeric`.

The Lean statement writes the reciprocals as $1/p$ and $1/(B \cdot p)$ and has no hypothesis on the sign of $a$.

## Proof

Substitute $B = p^2$, so that $Bp = p^3$ and $p^2 \cdot \frac1p = p$.

Since $1 \le B \le R$, the three numbers $3R - 2B$, $B - 1$ and $\frac52 R - B$ are nonnegative. The first hypothesis, multiplied by $(3R-2B)(B-1) \ge 0$, gives

$$(3R-2B)(B-1)\,r \le (3R-2p^2)(p^2-1)\frac{a}{p} = a\,(3R-2p^2)\Bigl(p - \frac1p\Bigr),$$

and the second, multiplied by $\frac52 R - B \ge 0$, gives

$$-\Bigl(\frac52 R - B\Bigr)\kappa \le -\frac12\Bigl(\frac52 R - p^2\Bigr) + a\Bigl(\frac52 R - p^2\Bigr)\Bigl(\frac{4}{3p} + \frac{1}{15p^3}\Bigr).$$

It remains to add the two right sides. Expanding,

$$(3R-2p^2)\Bigl(p - \frac1p\Bigr) = -2p^3 + (3R+2)p - \frac{3R}{p}, \qquad \Bigl(\frac52 R - p^2\Bigr)\Bigl(\frac{4}{3p} + \frac{1}{15p^3}\Bigr) = -\frac43 p + \Bigl(\frac{10R}{3} - \frac{1}{15}\Bigr)\frac1p + \frac{R}{6p^3},$$

and the sum of these is $-2p^3 + \bigl(3R + \frac23\bigr)p + \bigl(\frac R3 - \frac1{15}\bigr)\frac1p + \frac{R}{6p^3}$, which is the bracket of the claim with $Bp = p^3$. This is a routine identity.

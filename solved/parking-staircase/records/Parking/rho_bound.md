---
weight: step
short: bound of the correction ϱ in s
---
## Description

For real $s \ge 6.48$, $k$ with $s^3 \le 1.07593\,k$, $0 \le c \le s^2$ and $d \ge k$: $\frac{c}{2d} + \frac{c^2}{8d^2} \le 0.560302 \cdot \frac{c}{s^3}$.

## Statement

Let $s$, $k$, $c$ and $d$ be real numbers with $s \ge 6.48$, $s^3 \le 1.07593\,k$, $0 \le c \le s^2$ and $d \ge k$. Then

$$\frac{c}{2d} + \frac{c^2}{8d^2} \le 0.560302 \cdot \frac{c}{s^3}.$$

## Explanation

The left side, with $d = N - c$, is the correction $\varrho_c = \frac{c}{2(N-c)} + \frac{c^2}{8(N-c)^2}$ (`Parking.rhoC`), which occurs through the factors $1 + \varrho_c$ in the two sums $G(k,R)$ and $\mathcal{A}(k,R)$ (`Parking.Gsum`, `Parking.Asum`) of the lower bound `Parking.pairSum_ge` of the pair sum, with $N = k + R$ and $c$ a cut point, $0 < c < R$. In the proofs of `Parking.Gsum_le` and `Parking.Asum_le` the statement is applied with $s = \sqrt{R}$ for a natural number $R \ge 42$, with the natural number $c \le R = s^2$, and with $d = k + R - c \ge k$. It gives $\varrho_c \le 0.560302\,c/R^{3/2}$. Together with the bound $\kappa_3(c) \le c_0\sqrt{c}$ of the convolution $\kappa_3$ (`Parking.kc3`), where $c_0 = 1/\sqrt{2\pi}$, this turns the correction sums $\sum_c \kappa_3(c)\varrho_c$ and $\sum_c (R-c)\kappa_3(c)\varrho_c$ into $\frac{0.560302\,c_0}{s^3}$ times sums of $c^{3/2}$ and of $c^{3/2}(R-c)$, which are the last terms on the left sides of `Parking.Gsum_numeric` and `Parking.Asum_numeric`.

The hypothesis $s^3 \le 1.07593\,k$ is the upper inequality of `Parking.k_window`. The constant is $\frac{1.07593}{2} + \frac{1.07593^2}{8 \cdot 6.48} = 0.5602957\ldots$ rounded up: the first summand bounds the linear term $c/(2d)$, and the second, which is about four per cent of the first, bounds the quadratic term.

## Proof

From $s \ge 6.48$ we have $s^3 > 0$, hence $k > 0$ and $d \ge k > 0$. Put $w = c/d \ge 0$. The left side is $\frac{w}{2} + \frac{w^2}{8}$, and since $s^3 > 0$ the claim is equivalent to

$$s^3\Bigl(\frac{w}{2} + \frac{w^2}{8}\Bigr) \le 0.560302\,c.$$

Three bounds are used.

1. $s^3/d \le 1.07593$, because $s^3 \le 1.07593\,k \le 1.07593\,d$.
2. $w s^3 = c \cdot (s^3/d) \le 1.07593\,c$, by 1 and $c \ge 0$.
3. $6.48\,w \le 1.07593$: from $c \le s^2$ we get $w s = c s/d \le s^3/d \le 1.07593$, and $6.48\,w \le w s$ because $w \ge 0$ and $s \ge 6.48$.

Then

$$s^3\Bigl(\frac{w}{2} + \frac{w^2}{8}\Bigr) = \frac{w s^3}{2} + \frac{w \cdot (w s^3)}{8} \le \frac{1.07593\,c}{2} + \frac{w \cdot 1.07593\,c}{8} \le \Bigl(\frac{1.07593}{2} + \frac{1.07593^2}{8 \cdot 6.48}\Bigr) c,$$

where the first inequality uses 2 twice and the second uses 3 in the form $w \le 1.07593/6.48$. The rational number in the last bracket is $0.5602957\ldots \le 0.560302$, and $c \ge 0$.

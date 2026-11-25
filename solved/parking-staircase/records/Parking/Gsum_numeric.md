---
weight: step
short: arithmetic of the upper bound of the sum G
---
## Description

For real $s \ge 6.48$, $R = s^2$ and $0 \le a \le 0.39894229$: if four real numbers $S_1, S_2, S_3, S_G$ satisfy the bounds of the power sums of $b^{-1/2}$, $b^{-3/2}$, $b^{1/2}$ and $c^{3/2}$, then $a\bigl(3S_3 + \frac13 S_1 + \frac16 S_2\bigr) - \frac54(R-1) + \frac{0.560302\,a}{s^3}S_G \le 2\,(0.478731\,s^3 - 0.974453\,s^2 + 0.642741\,s)$.

## Statement

Let $s$, $a$, $R$, $S_1$, $S_2$, $S_3$ and $S_G$ be real numbers with $s \ge 6.48$, $R = s^2$, $0 \le a \le 0.39894229$ and

- $S_1 \le 2s + \dfrac{1}{2s} - 2.44948$,
- $S_2 \le 1.63300$,
- $S_3 \le \dfrac23\,R s + \dfrac12\,s - 1.17851$,
- $S_G \le \dfrac25\,R^2 s$.

Then

$$a\Bigl(3S_3 + \frac13\,S_1 + \frac16\,S_2\Bigr) - \frac54\,(R-1) + \frac{a \cdot 0.560302}{s^3}\,S_G \le 2\,\bigl(0.478731\,s^3 - 0.974453\,s^2 + 0.642741\,s\bigr).$$

## Explanation

The statement is the arithmetic behind `Parking.Gsum_le`, the upper bound of the sum $G(k,R)$ (`Parking.Gsum`), one of the three sums in the lower bound `Parking.pairSum_ge` of the pair sum. There $R \ge 42$ is a natural number, $s = \sqrt{R}$, $a = c_0 = 1/\sqrt{2\pi}$, and the four numbers are

$$S_1 = \sum_{b=2}^{R} b^{-1/2}, \quad S_2 = \sum_{b=2}^{R} b^{-3/2}, \quad S_3 = \sum_{b=2}^{R} b^{1/2}, \quad S_G = \sum_{0<c<R} c^{3/2}.$$

The hypotheses are, in this order, the bounds `Parking.sum_Icc_two_inv_sqrt_le`, `Parking.sum_Icc_two_inv_sqrt_cube_le`, `Parking.sum_Icc_two_sqrt_le` and `Parking.sum_Ioo_sqrt_cube_le`. The left side is the bound of $G$ that the proof of `Parking.Gsum_le` assembles: its first two terms come from summing `Parking.term_G` over $2 \le b \le R$, and its last term bounds the correction $\sum_{0<c<R}\kappa_3(c)\varrho_c$, where $\kappa_3$ is the convolution `Parking.kc3` and $\varrho_c$ the correction `Parking.rhoC` at $N = k + R$, with $\kappa_3(c) \le c_0\sqrt{c}$ and $\varrho_c \le 0.560302\,c/s^3$ from `Parking.rho_bound`.

The right side is the polynomial

$$G_0(s) = 2\,\bigl(0.478731\,s^3 - 0.974453\,s^2 + 0.642741\,s\bigr) = 2s\,q_0(s), \qquad q_0(s) = 0.478731\,s^2 - 0.974453\,s + 0.642741,$$

which from here on stands for $G$: it is the upper bound assumed in `Parking.pair_numeric`. It is built from the same quadratic $q_0$ as the bound $A_0(s) = s^3 q_0(s)$ of `Parking.Asum_numeric`, so that $G_0 = 2A_0/s^2$. This relation is what `Parking.pair_numeric` uses: there the two bounds enter only through $q_0$, and the ratio $A_0/G_0 = s^2/2$ fixes one of the two free parameters.

In this form $G_0$ is not a sharp bound of the left side. The assembled bound is a cubic in $s$ with leading coefficient $2 \cdot 0.39894229 = 0.79788458$, while $G_0$ has leading coefficient $0.957462$. The difference between $G_0$ and the assembled bound is the cubic

$$\frac{7978871}{50000000}\,s^3 - 0.788317\ldots\,s^2 + 0.421107\ldots\,s + 0.367366\ldots,$$

whose leading coefficient is $0.15957742$ and whose value at $s = 6.48$ is about $13.4$, against $G_0(6.48) \approx 187$. This is in contrast with `Parking.Asum_numeric`, where the polynomial $A_0$ agrees with the assembled bound up to rounding in its three leading terms.

The proof uses two polynomial inequalities on the half-line $s \ge 6.48$. Each is shown by writing $s = 6.48 + t$ with $t \ge 0$ and expanding in powers of $t$: every coefficient is positive. Such an expansion is an identity between polynomials with rational coefficients, since $6.48 = \frac{162}{25}$.

## Proof

Substitute $R = s^2$ and write $q = \frac{1}{2s}$. Then $q > 0$, and $q \le \frac{25}{324}$ because $s \ge 6.48 = \frac{162}{25}$.

*Step 1: the bracket.* The hypotheses on $S_1$, $S_2$, $S_3$ and the bound of $q$ give

$$3S_3 + \frac13 S_1 + \frac16 S_2 \le U_G(s), \qquad U_G(s) = 3\Bigl(\frac23 s^3 + \frac12 s - 1.17851\Bigr) + \frac13\Bigl(2s + \frac{25}{324} - 2.44948\Bigr) + \frac16 \cdot 1.63300.$$

Expanded, $U_G(s) = 2s^3 + \frac{13}{6}s - \frac{98515517}{24300000}$, where $\frac{98515517}{24300000} = 4.0541\ldots$.

*Step 2: $U_G(s) \ge 0$ for $s \ge 6.48$.* With $s = 6.48 + t$, $U_G$ becomes the polynomial $\frac{67333045871}{121500000} + \frac{952909}{3750}\,t + \frac{972}{25}\,t^2 + 2t^3$ with positive coefficients; the constant term is about $554.18$. Since $a \ge 0$, Step 1 gives $a\bigl(3S_3 + \frac13 S_1 + \frac16 S_2\bigr) \le a\,U_G(s)$, and since $U_G(s) \ge 0$ and $a \le 0.39894229$, this is at most $0.39894229 \cdot U_G(s)$.

*Step 3: the correction term.* The hypothesis on $S_G$ reads $S_G \le \frac25 s^5$. Multiplying by $\frac{0.560302\,a}{s^3} \ge 0$ and then using $a \le 0.39894229$,

$$\frac{0.560302\,a}{s^3}\,S_G \le a \cdot 0.560302 \cdot \frac25\,s^2 \le 0.39894229 \cdot 0.560302 \cdot \frac25\,s^2.$$

*Step 4: the comparison.* By Steps 2 and 3 the left side of the claim is at most

$$0.39894229 \cdot U_G(s) - \frac54\,(s^2-1) + 0.39894229 \cdot 0.560302 \cdot \frac25\,s^2,$$

a cubic in $s$. The polynomial $G_0(s)$ minus this cubic is the cubic displayed in the explanation. With $s = 6.48 + t$ it becomes a polynomial in $t$ whose four coefficients are positive: the constant term is $\frac{509352544950961979489}{37968750000000000000} \approx 13.415$, the next two are approximately $10.307$ and $2.3139$, and the leading coefficient is $\frac{7978871}{50000000}$. Hence the difference is positive for $t \ge 0$, which proves the claim.

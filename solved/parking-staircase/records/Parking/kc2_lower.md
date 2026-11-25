---
weight: unit
short: lower bound of the twofold convolution of the Poisson mass
---
## Description

For every natural number $m\ge2$: $\kappa_2(m)\ge\frac12-\bigl(\frac43+\frac{1}{15m}\bigr)P(m)$, where $P(m)=e^{-m}m^m/m!$ is the Poisson mass and $\kappa_2(m)=\sum_{0<g<m}P(g)\,P(m-g)$ is its convolution with itself.

## Statement

Let $P(m)=e^{-m}m^m/m!$ be the Poisson mass (`Parking.poissonMass`), and let
$$\kappa_2(m)=\sum_{g=1}^{m-1}P(g)\,P(m-g)$$
be its convolution with itself over the proper splittings of $m$ (`Parking.kc2`). Then for every natural number $m\ge2$,
$$\frac12-\Bigl(\frac43+\frac{1}{15\,m}\Bigr)P(m)\ \le\ \kappa_2(m).$$

## Explanation

**What the statement says.** The number $\kappa_2(m)$ lies a little below $\frac12$, and the statement bounds the distance from above: it is at most $\bigl(\frac43+\frac1{15m}\bigr)P(m)$, which is of the order $m^{-1/2}$ because $P(m)\le c_0/\sqrt m$ with $c_0=1/\sqrt{2\pi}$ by Stirling's formula.

The reason is a statement about the Poisson law. The closed form `Parking.kc2_eq` says $\kappa_2(m)=P(m)\,(s_m-1)$, where $s_m$ is the mean of the birthday law (`Parking.sbirth`), the function that Ramanujan called $Q(m)$. Let $\mathfrak p(m)=e^{-m}\sum_{i=0}^{m}m^i/i!$ be the probability that a Poisson variable of mean $m$ is at most $m$. The mean of the birthday law satisfies $1+s_m=\mathfrak p(m)/P(m)$; this is the identity through which `Parking.sbirth_ge` is proved. Hence
$$\kappa_2(m)=\mathfrak p(m)-2\,P(m),$$
and the statement is the inequality $\mathfrak p(m)\ge\frac12+\bigl(\frac23-\frac1{15m}\bigr)P(m)$ in another form. This inequality is the lower half of Ramanujan's estimate, according to which $\mathfrak p(m)$ exceeds $\frac12$ by a little less than two thirds of $P(m)$. The upper half, $\mathfrak p(m)\le\frac12+\frac23P(m)$, gives in the same way $\kappa_2(m)\le\frac12-\frac43P(m)$; the library proves it on the way to its upper bound of $s_m$, and the proof uses it only through that upper bound of $s_m$, in the diagonal step, and never in the form of an upper bound of $\kappa_2$. Between the two halves the value of $\kappa_2(m)$ is determined up to $P(m)/(15m)$, a quantity of the order $m^{-3/2}$. In floating point, which is not part of any proof, $\kappa_2(42)=0.418042$ and the bound of this statement is $0.417988$.

**What it is used for.** The statement is the one place where Ramanujan's estimate enters the estimates of the curve increase, and it enters on both sides of the comparison that proves `Parking.curve_step_pos`.

- On the pair side it is applied at every $b$ with $2\le b\le R$ and summed. Together with Stirling's bound it gives $\kappa_2(b)\ge\frac12-\frac43c_0\,b^{-1/2}-\frac{c_0}{15}\,b^{-3/2}$, and the three statements `Parking.Wsum_ge`, `Parking.Gsum_le`, `Parking.Asum_le` are sums of this inequality with different weights.
- On the impulse side it is applied at the single point $m=R$, as a hypothesis of `Parking.impulse_numeric`.

In all these places a bound of $\kappa_2$ from below is what is needed, and an upper bound never is. For $W_\Sigma=\sum_b\kappa_2(b)$ this is evident, since a lower bound of $W_\Sigma$ is wanted. In the other places an upper bound is wanted of an expression in which $\kappa_2$ occurs together with the threefold convolution $\kappa_3$ (`Parking.kc3`). The closed form $\kappa_3(m)=(m-1)P(m)-2\kappa_2(m)$ (`Parking.kc3_eq`) removes $\kappa_3$ from such an expression, and the coefficient of $\kappa_2$ that remains is negative each time: $-\frac52$ in the terms of $G$, $-(\frac52R-b)$ in the terms of $\mathcal A$, and a negative number in the bound of the impulse. The records of the three statements named above and of `Parking.curve_step_pos` show this at each place.

**The range.** The hypothesis $m\ge2$ is that of `Parking.sbirth_ge`. For $m=1$ the inequality is true and says nothing: $\kappa_2(1)=0$ and the left side is negative.

**The Lean form.** The statement is `1 / 2 - (4 / 3 + 1 / (15 * (m : ℝ))) * poissonMass m ≤ kc2 m`, with $m$ cast to a real number.

## Proof

Let $m\ge2$ and write $P=P(m)$; it is positive (`Parking.poissonMass_pos`). The lower bound of the mean of the birthday law, `Parking.sbirth_ge`, says
$$\frac{1}{2P}-\frac13-\frac{1}{15\,m}\ \le\ s_m .$$
Multiplying by $P>0$ gives $\frac12-\frac P3-\frac{P}{15m}\le P\,s_m$. By the closed form `Parking.kc2_eq`, which holds for $m\ge1$, $\kappa_2(m)=P\,(s_m-1)=P\,s_m-P$. Therefore
$$\kappa_2(m)\ \ge\ \frac12-\frac P3-\frac{P}{15\,m}-P\ =\ \frac12-\Bigl(\frac43+\frac{1}{15\,m}\Bigr)P .$$

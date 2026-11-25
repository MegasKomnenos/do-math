---
weight: step
short: pair side at the chosen tangent parameters
---
## Description

Let $s \ge 6.48$, $R = s^2$, $k \le s^3 \le 1.07593\,k$, and let $W$, $G$, $A$ satisfy the polynomial bounds in $s$ of the three sums of the pair side. If $C\,e^{-\mu}\bigl((1+\mu)W - (\log(1+\theta) - \frac{\theta}{1+\theta})G - \frac{A}{k(1+\theta)}\bigr) \le \Pi$ for all $\theta \ge 0$ and all $\mu$, with $C \ge 0$, then $C \cdot 0.38385\,(1 + \frac{1}{10s})\,\frac{k}{s^3}\,(\frac R2 - 1.06385\,s + 0.7184) \le \Pi$.

## Statement

Let $s$, $R$, $k$, $W$, $G$, $A$, $C$ and $\Pi$ be real numbers with $s \ge 6.48$, $R = s^2$, $k \le s^3$, $s^3 \le 1.07593\,k$, $C \ge 0$ and

- $\dfrac R2 - 1.06385\,s + 0.7184 \le W$,
- $G \le 2\,\bigl(0.478731\,s^3 - 0.974453\,s^2 + 0.642741\,s\bigr)$,
- $A \le 0.478731\,s^5 - 0.974453\,s^4 + 0.642741\,s^3$.

Suppose that for all real numbers $\theta$ and $\mu$ with $\theta \ge 0$,

$$C \cdot e^{-\mu}\Bigl((1+\mu)\,W - \Bigl(\bigl(\log(1+\theta) - \frac{\theta}{1+\theta}\bigr)\,G + \frac{1}{k(1+\theta)}\,A\Bigr)\Bigr) \le \Pi.$$

Then

$$C \cdot 0.38385 \cdot \Bigl(1 + \frac{1}{10s}\Bigr) \cdot \frac{k}{s^3} \cdot \Bigl(\frac R2 - 1.06385\,s + 0.7184\Bigr) \le \Pi.$$

## Explanation

*What the statement is used for.* It is used once, in the proof of `Parking.curve_step_pos`, with $k$ the column, $R \ge 42$ a natural number, $s = \sqrt{R}$, $C = a_k e^R$ where $a_k = k^{k-1}/k!$, and $\Pi = \mathcal{P}(k,R)$ the pair sum (`Parking.pairSum`). The numbers $W$, $G$, $A$ are the three sums $W_\Sigma(R)$, $G(k,R)$, $\mathcal{A}(k,R)$ (`Parking.Wsum`, `Parking.Gsum`, `Parking.Asum`), and the three hypotheses on them are `Parking.Wsum_ge`, `Parking.Gsum_le`, `Parking.Asum_le`. The hypothesis with the two free parameters is the lower bound `Parking.pairSum_ge` of the pair sum, which holds for every $\theta \ge 0$ and every real $\mu$. The hypotheses $k \le s^3 \le 1.07593\,k$ are the conclusion of `Parking.k_window`. The conclusion is the lower bound of the pair sum in the form in which the proof uses it:

$$\mathcal{P}(k,R) \ge a_k e^R \cdot 0.38385 \cdot \Bigl(1 + \frac{1}{10s}\Bigr) \cdot \frac{k}{s^3} \cdot W_0(s).$$

The pair–impulse criterion `Parking.dq_pos_of_pair` gives a positive step as soon as $k\,a_k\Lambda_R(k+1;\,k+R) < 2\,\mathcal{P}(k,R)$, where $\Lambda_R(k+1;\,k+R)$ is the chain sum of length $R$ with the cut factors $(k+1)/(k+R-c)$ at the cut points $c$ (in Lean `Lam (thr (k + 1) (k + R)) R`). The present statement bounds the right side of that inequality, the pair side, from below, and `Parking.impulse_numeric` shows that the upper bound of the left side, the impulse side, lies strictly below this lower bound.

*Notation.* Throughout,

$$W_0(s) = \frac{s^2}{2} - 1.06385\,s + 0.7184, \qquad q_0(s) = 0.478731\,s^2 - 0.974453\,s + 0.642741,$$

so that the three hypotheses read $W \ge W_0(s)$, $G \le G_0(s) = 2s\,q_0(s)$ and $A \le A_0(s) = s^3 q_0(s)$. Write also $x = s^3/k$; the hypotheses on $k$ say $1 \le x \le 1.07593$.

*The choice of the parameters.* The statement removes the two free parameters of `Parking.pairSum_ge` by choosing

$$\theta = \frac{s^2}{2k}, \qquad \mu = \frac{G_0(s)\,\log(1+\theta)}{W_0(s)}.$$

These are the values at which the bound is largest when $W$, $G$, $A$ are replaced by $W_0$, $G_0$, $A_0$. The derivative in $\theta$ of $-\bigl(\log(1+\theta) - \frac{\theta}{1+\theta}\bigr)G_0 - \frac{A_0}{k(1+\theta)}$ is $\frac{A_0/k - \theta G_0}{(1+\theta)^2}$, which vanishes at $\theta = A_0/(kG_0) = s^2/(2k)$; and for a fixed number $Y$ the function $\mu \mapsto e^{-\mu}\bigl((1+\mu)W_0 - Y\bigr)$ has derivative $e^{-\mu}(Y - \mu W_0)$ and is largest at $\mu = Y/W_0$, where its value is $e^{-\mu}W_0$. The proof does not use that the values are optimal. It uses the two identities $\theta\,G_0 = A_0/k$ and $\mu W_0 = G_0\log(1+\theta)$, by which the bracket of the bound collapses to $W_0$, so that the bound becomes $C\,e^{-\mu}W_0(s)$.

*Where the constants come from.* What is left is to bound the exponent $\mu$ from above. Since $\theta = x/(2s)$ is small and $\log(1+\theta) \le \theta$, $\mu$ is close to $x\,q_0(s)/W_0(s)$, and $q_0(s)/W_0(s)$ tends to $2 \cdot 0.478731 = 0.957462$ as $s$ grows. The proof shows $\mu \le x\,\bigl(0.9575 - \frac{1}{10s}\bigr)$. The factor $e^{-0.9575}$ gives the constant $0.38385$ (the value is $e^{-0.9575} = 0.3838513\ldots$), the correction $\frac{1}{10s}$ in the exponent gives the factor $1 + \frac{1}{10s}$, and the dependence on $x \in [1,\,1.07593]$ is absorbed in the factor $\frac1x = \frac{k}{s^3}$.

The Lean statement writes the three polynomial bounds out in full, the first with $R/2$ for $s^2/2$, as above.

## Proof

Substitute $R = s^2$. We have $s > 0$ and, from $s^3 \le 1.07593\,k$, $k > 0$. For $s \ge 6.48$ both $W_0(s) = s\bigl(\frac s2 - 1.06385\bigr) + 0.7184$ and $q_0(s) = s\,(0.478731\,s - 0.974453) + 0.642741$ are positive, since in each the bracket is nonnegative. Put

$$\theta = \frac{s^2}{2k} > 0, \qquad L = \log(1+\theta) \ge 0, \qquad \mu = \frac{2s\,q_0(s)\,L}{W_0(s)} \ge 0, \qquad x = \frac{s^3}{k},$$

so that $\theta \cdot 2k = s^2$, $\theta \cdot 2s = x$, $\mu W_0 = 2s\,q_0 L$ and $1 \le x \le 1.07593$. The proof has three steps: the bracket of the hypothesis at these parameters is at least $W_0$; the exponent satisfies $\mu \le x c$ with $c = 0.9575 - \frac{1}{10s}$; and $e^{-xc} \ge 0.38385\,\bigl(1 + \frac{1}{10s}\bigr)\frac1x$.

*Step 1: the bracket.* We claim

$$W_0 \le (1+\mu)\,W - \Bigl(\bigl(L - \frac{\theta}{1+\theta}\bigr)\,G + \frac{1}{k(1+\theta)}\,A\Bigr).$$

The three coefficients $1 + \mu$, $L - \frac{\theta}{1+\theta}$ and $\frac{1}{k(1+\theta)}$ are nonnegative; for the second this is the inequality $1 - \frac1y \le \log y$ at $y = 1 + \theta$. So the right side does not increase when $W$ is replaced by $W_0$, $G$ by $2s\,q_0$ and $A$ by $s^3 q_0$, and it is at least

$$(1+\mu)\,W_0 - \bigl(L - \frac{\theta}{1+\theta}\bigr) \cdot 2s\,q_0 - \frac{s^3 q_0}{k(1+\theta)}.$$

Here $\frac{\theta}{1+\theta} \cdot 2s\,q_0 = \frac{s^3 q_0}{k(1+\theta)}$, because $\theta \cdot 2s = s^3/k$; these two terms cancel. And $\mu W_0 = 2s\,q_0 L$; these two cancel as well. What remains is $W_0$.

*Step 2: the exponent.* Let $c = 0.9575 - \frac{1}{10s}$, so that $c\,s^2 = 0.9575\,s^2 - \frac{s}{10}$. We claim $\mu \le x c$.

By `Parking.log_one_add_le3`, $L \le \theta - \frac{\theta^2}{2} + \frac{\theta^3}{3}$. Put $y = \theta s$, so that $2y = x$ and $\frac12 \le y \le 0.537965$. Multiplying the bound of $L$ by $2s\,q_0 \cdot s^2 \ge 0$ and using $\mu W_0 = 2s\,q_0 L$,

$$\mu\,W_0\,s^2 \le 2s^3 q_0\Bigl(\theta - \frac{\theta^2}{2} + \frac{\theta^3}{3}\Bigr) = x\,q_0\Bigl(s^2 - \frac{y s}{2} + \frac{y^2}{3}\Bigr).$$

The bracket is largest at the smallest value of $y$:

$$\Bigl(s^2 - \frac s4 + \frac1{12}\Bigr) - \Bigl(s^2 - \frac{y s}{2} + \frac{y^2}{3}\Bigr) = \Bigl(y - \frac12\Bigr)\Bigl(\frac s2 - \frac{y + \frac12}{3}\Bigr) \ge 0,$$

since $y \ge \frac12$ and $\frac s2 \ge 3.24 > \frac{y + 1/2}{3}$. Therefore $\mu\,W_0\,s^2 \le x\,q_0(s)\bigl(s^2 - \frac s4 + \frac1{12}\bigr)$.

Now a polynomial inequality is needed: for $s \ge 6.48$,

$$q_0(s)\Bigl(s^2 - \frac s4 + \frac1{12}\Bigr) \le W_0(s)\Bigl(0.9575\,s^2 - \frac{s}{10}\Bigr).$$

The right side minus the left side is the quartic

$$\frac{19}{1000000}\,s^4 + \frac{40799}{1600000}\,s^3 - \frac{263991}{2000000}\,s^2 + \frac{510149}{3000000}\,s - \frac{214247}{4000000}.$$

Its leading coefficient is $\frac{0.9575}{2} - 0.478731 = 0.000019$: the constant $0.9575$ is $2 \cdot 0.478731 = 0.957462$ rounded up to four decimal places. Write $s = 6.48 + t$ with $t \ge 0$, where $6.48 = \frac{162}{25}$. The quartic becomes a polynomial in $t$ whose five coefficients are positive; from the constant term upward they are $\frac{3871313377861}{1562500000000} \approx 2.4776$, $\frac{158648839393}{93750000000} \approx 1.6923$, $\frac{921248139}{2500000000} \approx 0.3685$, $\frac{5198371}{200000000} \approx 0.02599$ and $\frac{19}{1000000}$. So the quartic is positive for $s \ge 6.48$.

Together, since $x > 0$,

$$\mu\,W_0\,s^2 \le x\,W_0\Bigl(0.9575\,s^2 - \frac{s}{10}\Bigr) = x c \cdot W_0\,s^2,$$

and dividing by $W_0 s^2 > 0$ gives $\mu \le x c$.

*Step 3: the exponential.* Write $\delta = \frac{1}{10s} \ge 0$, so that $c = 0.9575 - \delta$. We claim

$$0.38385\,(1+\delta)\,\frac1x \le e^{-xc}.$$

Since $-xc = -0.9575 + \delta - (x-1)c$, the right side is the product $e^{-0.9575} \cdot e^{\delta} \cdot e^{-(x-1)c}$, and each factor is bounded from below.

- $e^{-0.9575} \ge 0.38385$. The Taylor bound $e^{u} \le \sum_{j=0}^{11} \frac{u^j}{j!} + \frac{13\,u^{12}}{12 \cdot 12!}$ for $0 \le u \le 1$ (the case $n = 12$ of Mathlib's bound $e^u \le \sum_{j<n} u^j/j! + u^n(n+1)/(n! \cdot n)$) gives at $u = 0.9575$, by exact rational arithmetic, $e^{0.9575} \le 2.60518$. Since $e^{-0.9575}\,e^{0.9575} = 1$ and $0.38385 \cdot 2.60518 = 0.999998343 \le 1$, the bound follows.
- $e^{\delta} \ge 1 + \delta$.
- $e^{-(x-1)c} \ge \frac1x$. This is equivalent to $e^{(x-1)c} \le x$, that is, to $(x-1)\,c \le \log x$. Mathlib's inequality $\frac{2v}{v+2} \le \log(1+v)$ for $v \ge 0$, at $v = x - 1$, gives $\frac{2(x-1)}{x+1} \le \log x$. And $(x-1)\,c \le 0.9575\,(x-1) \le \frac{2(x-1)}{x+1}$, because $c \le 0.9575$, $x \ge 1$ and $0.9575\,(x+1) \le 0.9575 \cdot 2.07593 = 1.9877\ldots \le 2$.

The three factors and their lower bounds are nonnegative, so the product of the lower bounds is a lower bound of the product.

*Conclusion.* By Step 2, $e^{-xc} \le e^{-\mu}$. With Step 3 and $\frac{k}{s^3} = \frac1x$,

$$C \cdot 0.38385\,\Bigl(1 + \frac{1}{10s}\Bigr)\frac{k}{s^3}\,W_0 \le C\,e^{-\mu}\,W_0,$$

because $C \ge 0$ and $W_0 > 0$. By Step 1 and $C\,e^{-\mu} \ge 0$, the right side is at most $C\,e^{-\mu}$ times the bracket of the hypothesis at the parameters $\theta$ and $\mu$, and the hypothesis, applied to these two values with $\theta \ge 0$, says that this is at most $\Pi$.

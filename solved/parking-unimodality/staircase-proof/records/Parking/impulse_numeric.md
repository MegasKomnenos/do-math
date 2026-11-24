---
weight: step
short: final comparison of the impulse side with the pair side
---
## Description

For $s \ge 6.48$ and $R = s^2$: a real number $X$ that satisfies the upper bound of the impulse at the threshold $K = (R-1)(2R-1)/(2s)$ with parameter $0.35$, in which the Poisson mass and the two convolutions are real numbers subject to Stirling's bound, the lower bound of $\kappa_2$ and the closed form of $\kappa_3$, satisfies $X < 2 \cdot 0.38385\,(\frac R2 - 1.06385\,s + 0.7184)(1 + \frac{1}{10s})/s^3$.

## Statement

Let $s$, $R$, $K$, $a$, $\rho$, $\eta$, $c'$, $X$, $y_2$ and $y_3$ be real numbers such that

- $s \ge 6.48$, $R = s^2$ and $c' = 0.35$;
- $K \cdot 2s = (R-1)(2R-1)$;
- $0 < a \le 0.39894229$;
- $0.704688 \le \eta \le 0.704689$;
- $\rho \le \dfrac{a}{s}$;
- $X \le \rho - \eta\,\Bigl((1+c')\,\dfrac{R-2}{2(K+R-1)}\,y_2 - \dfrac{1}{K+1} \cdot \dfrac{R-3}{3}\,y_3 \cdot \dfrac{\frac45 R - 1}{K + \frac35 R}\Bigr)$;
- $\dfrac12 - \Bigl(\dfrac43 + \dfrac{1}{15R}\Bigr)\rho \le y_2$;
- $y_3 = (R-1)\,\rho - 2\,y_2$.

Then

$$X < \frac{2 \cdot 0.38385 \cdot \bigl(\frac R2 - 1.06385\,s + 0.7184\bigr)\bigl(1 + \frac{1}{10s}\bigr)}{s^3}.$$

## Explanation

*What the statement is used for.* It is the last step of the proof of `Parking.curve_step_pos`, where the upper bound of the impulse side is compared with the lower bound of the pair side. There $R \ge 42$ is a natural number, $s = \sqrt{R}$, $k$ is the column, and the letters of the statement stand for the following quantities.

- $X = e^{-R}\Lambda_R(k+1;\,k+R)$, where $\Lambda_R(k+1;\,k+R)$ is the chain sum of length $R$ with the cut factors $(k+1)/(k+R-c)$ at the cut points $c$ (in Lean `Lam (thr (k + 1) (k + R)) R`); and $K$ is the threshold of `Parking.K_facts`.
- $\rho = P(R) = e^{-R}R^R/R!$, the Poisson mass; $a = c_0 = 1/\sqrt{2\pi}$, and $\rho \le a/s$ is Stirling's bound; $a \le 0.39894229$ is `Parking.c0_le`.
- $y_2 = \kappa_2(R)$ and $y_3 = \kappa_3(R)$, the convolutions `Parking.kc2` and `Parking.kc3`. The hypothesis on $y_2$ is `Parking.kc2_lower`, the lower half of Ramanujan's estimate, and the equation for $y_3$ is the closed form `Parking.kc3_eq`.
- $\eta = e^{-0.35}$, with the bounds of `Parking.exp_neg_035_bounds`.
- With these quantities in the places of the letters, the hypothesis on $X$ is the conclusion of `Parking.impulse_le` at the threshold $K$ with $c' = 0.35$.

The right side of the conclusion is $2 \cdot 0.38385 \cdot W_0(s)\bigl(1 + \frac{1}{10s}\bigr)/s^3$ with $W_0(s) = \frac{s^2}{2} - 1.06385\,s + 0.7184$. Multiplied by $k\,a_k e^R$, where $a_k = k^{k-1}/k!$, it is twice the lower bound of the pair sum that `Parking.pair_numeric` gives. So the conclusion, with `Parking.pair_numeric`, is the inequality $k\,a_k\Lambda_R(k+1;\,k+R) < 2\,\mathcal{P}(k,R)$ that the pair–impulse criterion `Parking.dq_pos_of_pair` asks for, where $\mathcal{P}(k,R)$ is the pair sum (`Parking.pairSum`). The left side of that inequality is called the impulse side and the right side the pair side. The strict sign of the conclusion is the strict sign of that criterion.

*How the statement is built.* The hypotheses give an upper bound of $X$ that depends on $\rho$, and the first part of the proof shows that it is nondecreasing in $\rho$, so that $\rho$ may be replaced by $a/s$. After that everything is a rational function of $s$, multiplied by $a/s$: the proof arrives at $X \le \frac as F(s)$ and at the claim $F(s) < V(s)$ for two explicit rational functions, where $a\,V(s)/s$ is at most the right side of the conclusion. Clearing the denominators turns $F < V$ into the positivity of one polynomial $Q$ of degree $15$ on the half-line $s \ge 6.48$. This is shown as in the other statements of this kind (`Parking.Asum_numeric`, `Parking.Gsum_numeric`, `Parking.pair_numeric`): with $s = 6.48 + t$, every coefficient of $Q$ as a polynomial in $t$ is positive.

*How much room there is.* For large $s$ the two sides are far apart: $V(s)$ tends to $1.9243/2 = 0.96215$ and $F(s)$ to about $0.5918$. At the lower end of the range the lower-order terms of $W_0$ and of the two rational functions take almost all of this away. A floating-point evaluation of the polynomial $Q$ finds that it is $1.0$ per cent of its first product (the term that comes from $V$) at $s = 6.48$, $1.6$ per cent at $R = 43$ and $4.9$ per cent at $R = 50$; these figures are numerical evaluations and are not proved. The figure at $s = 6.48$ agrees with the formal proof, in which the value $Q(6.48)$ occurs exactly as the constant term of the polynomial in $t$: it is about $2.886 \cdot 10^{12}$, and an evaluation of the first product at $s = 6.48$ in rational arithmetic, made for this record and not part of the formal proof, gives about $2.818 \cdot 10^{14}$. In terms of the two rational functions, $V(6.48) \approx 0.6896$ and $V(6.48) - F(6.48) \approx 0.0071$. The decimal constants of this statement, of $W_0$ and of the bounds that lead to it therefore cannot be weakened freely. The theorem `Parking.curve_crossing` applies `Parking.curve_step_pos` only with $R \ge 43$.

*The Lean form.* The statement is about real numbers only; $\rho$, $\eta$, $y_2$, $y_3$ are variables, and what they stand for enters through the hypotheses. The parameter is a variable $c'$ with the hypothesis $c' = 0.35$, and the definition of $K$ is given without a division. The number $\eta$ is not tied to $c'$ in the statement; only its two decimal bounds are assumed.

## Proof

Substitute $R = s^2$ and $c' = 0.35$. Then $s > 0$, $s^2 \ge 6.48^2 \ge 41.99$, and $K > 0$ because $K \cdot 2s = (s^2-1)(2s^2-1) > 0$. Introduce

$$c_1 = \frac{s^2-2}{2(K+s^2-1)}, \qquad c_2 = \frac{s^2-3}{3} \cdot \frac{\frac45 s^2 - 1}{K + \frac35 s^2}, \qquad u = \frac{1}{K+1}, \qquad a' = \frac43 + \frac{1}{15s^2}, \qquad \rho_b = \frac as.$$

All five are nonnegative, $u$ and $\rho_b$ are positive, and $a' \le \frac43 + \frac{1}{600} = 1.335$ because $15s^2 \ge 600$. In this notation the hypothesis on $X$ reads

$$X \le \rho - \eta\bigl((1+0.35)\,c_1 y_2 - u\,c_2 y_3\bigr),$$

and the hypotheses on $y_2$ and on $\rho$ read $\frac12 - a'\rho \le y_2$ and $\rho \le \rho_b$. From $y_3 = (s^2-1)\rho - 2y_2$ and the lower bound of $y_2$,

$$y_3 \le \beta\rho - 1, \qquad \beta = s^2 - 1 + 2a' \ge 0.$$

The proof has four steps: $\rho$ is replaced by $\rho_b$; the bound is brought into the form $\rho_b F$; the inequality $F < V$ is proved by the polynomial certificate; and $\rho_b V$ is compared with the right side of the claim.

*Step 1: replacing $\rho$ by $\rho_b$.* Since $c_1 \ge 0$, $c_1 y_2 \ge c_1\bigl(\frac12 - a'\rho\bigr)$; since $c_2 \ge 0$ and $u \ge 0$, $u\,c_2 y_3 \le u\,c_2(\beta\rho - 1)$. With $\eta \ge 0$ the hypothesis on $X$ gives

$$X \le \rho - \eta\Bigl((1+0.35)\,c_1\bigl(\tfrac12 - a'\rho\bigr) - u\,c_2(\beta\rho - 1)\Bigr).$$

The right side is an affine function of $\rho$ with slope $1 + \eta\bigl((1+0.35)\,c_1 a' + u\,c_2\beta\bigr) \ge 0$. Hence it does not decrease when $\rho$ is replaced by the larger number $\rho_b$:

$$X \le \rho_b - \eta\Bigl((1+0.35)\,c_1\bigl(\tfrac12 - a'\rho_b\bigr) - u\,c_2(\beta\rho_b - 1)\Bigr).$$

*Step 2: the form $\rho_b F$.* Put

$$J = 1.253314\,s - a', \qquad H = s^2 - 2.5066\,s + 1.67.$$

Both are nonnegative: $J \ge 1.253314 \cdot 6.48 - 1.335 > 0$, and $H = s\,(s - 2.5066) + 1.67 > 0$. Two inequalities hold, each by $\rho_b s = a$ and the bound $a \le 0.39894229$.

- $\rho_b J \le \frac12 - a'\rho_b$. Indeed $\rho_b J = 1.253314\,a - a'\rho_b$, and $1.253314\,a \le 1.253314 \cdot 0.39894229 = 0.49999995\ldots \le \frac12$.
- $\beta\rho_b - 1 \le \rho_b H$. Indeed $\rho_b H - (\beta\rho_b - 1) = 1 - 2.5066\,a + \rho_b\,(2.67 - 2a')$, where $2.5066\,a \le 2.5066 \cdot 0.39894229 = 0.99998874\ldots \le 1$ and $2a' \le 2.67$.

The constants $1.253314$ and $2.5066$ are $\sqrt{\pi/2} = 1/(2c_0)$ and $\sqrt{2\pi} = 1/c_0$ rounded down, and the two inequalities say that $J$ is a lower bound of $\bigl(\frac12 - a'\rho_b\bigr)/\rho_b$ and $H$ an upper bound of $(\beta\rho_b - 1)/\rho_b$. Inserting them into the bound of Step 1 (the coefficients $c_1$ and $u\,c_2$ are nonnegative) gives $X \le \rho_b - \eta\bigl((1+0.35)\,c_1 J - u\,c_2 H\bigr)\rho_b$. Finally $\eta \ge 0.704688$ is used on the nonnegative term $c_1 J\rho_b$, which is subtracted, and $\eta \le 0.704689$ on the nonnegative term $u\,c_2 H\rho_b$, which is added:

$$X \le \rho_b\,F, \qquad F = 1 - (1+0.35) \cdot 0.704688 \cdot c_1 J + 0.704689 \cdot u\,c_2 \cdot H.$$

*Step 3: the certificate.* Let

$$V = \frac{1.9243 \cdot W_0(s)\,(10s+1)}{10\,s^3}, \qquad W_0(s) = \frac{s^2}{2} - 1.06385\,s + 0.7184.$$

We claim $F < V$. First the quantities in $F$ are written as rational functions of $s$, using $K \cdot 2s = (s^2-1)(2s^2-1)$. Put

$$D_1 = (s^2-1)(2s^2+2s-1), \qquad D_2 = (s^2-1)(2s^2-1) + \tfrac65 s^3, \qquad D_3 = (s^2-1)(2s^2-1) + 2s.$$

Then $2s \cdot 2(K+s^2-1) = 2D_1$, $2s\,(K + \frac35 s^2) = D_2$ and $2s\,(K+1) = D_3$, and all three are positive. Consequently

$$c_1 = \frac{s\,(s^2-2)}{D_1}, \qquad u\,c_2 = \frac{4s^2(s^2-3)\bigl(\frac45 s^2 - 1\bigr)}{3\,D_2 D_3}, \qquad J = \frac{15 \cdot 1.253314\,s^3 - 20s^2 - 1}{15\,s^2},$$

the last because $a' \cdot 15s^2 = 20s^2 + 1$. Multiplying $V - F$ by the positive common denominator $M = 30\,s^3 D_1 D_2 D_3$ gives the identity $(V - F)\,M = Q(s)$ with the polynomial

$$\begin{aligned} Q(s) ={}& 1.9243 \cdot W_0(s)\,(10s+1) \cdot 3\,D_1 D_2 D_3 \;-\; 30\,s^3 D_1 D_2 D_3 \\ &+ (1+0.35) \cdot 0.704688 \cdot s\,(s^2-2)\,\bigl(15 \cdot 1.253314\,s^3 - 20s^2 - 1\bigr) \cdot 2s \cdot D_2 D_3 \\ &- 0.704689 \cdot 4s^2(s^2-3)\bigl(\tfrac45 s^2 - 1\bigr)\,\bigl(s^2 - 2.5066\,s + 1.67\bigr) \cdot 10\,s^3 \cdot D_1. \end{aligned}$$

The four terms are $V M$, $M$, $(1+0.35) \cdot 0.704688 \cdot c_1 J \cdot M$ and $0.704689 \cdot u\,c_2 H \cdot M$. Each has degree $15$ in $s$, and $Q$ has degree $15$ with leading coefficient $\frac{1388961694331}{15625000000} \approx 88.89$. As a polynomial in $s$ it has coefficients of both signs, so its sign on the half-line cannot be read off directly.

It remains to show $Q(s) > 0$ for $s \ge 6.48$. Write $s = 6.48 + t$ with $t \ge 0$, where $6.48 = \frac{162}{25}$. Expanding $Q(6.48 + t)$ in powers of $t$ is an identity between polynomials with rational coefficients, and all sixteen coefficients are positive rational numbers. The constant term, which is $Q(6.48)$, is

$$\frac{167985278733377715569112118845646151677038147}{58207660913467407226562500000000} \approx 2.886 \cdot 10^{12},$$

and the coefficients of $t, t^2, \dots, t^{15}$ are, rounded to four significant digits, $2.735 \cdot 10^{13}$, $5.211 \cdot 10^{13}$, $5.005 \cdot 10^{13}$, $3.024 \cdot 10^{13}$, $1.267 \cdot 10^{13}$, $3.873 \cdot 10^{12}$, $8.898 \cdot 10^{11}$, $1.559 \cdot 10^{11}$, $2.090 \cdot 10^{10}$, $2.134 \cdot 10^{9}$, $1.634 \cdot 10^{8}$, $9.090 \cdot 10^{6}$, $3.473 \cdot 10^{5}$, $8.159 \cdot 10^{3}$ and $88.89$. A polynomial in $t$ with positive coefficients is positive for $t \ge 0$. Hence $Q(s) > 0$, and since $M > 0$, $F < V$.

*Step 4: the conclusion.* Since $\rho_b > 0$, Steps 2 and 3 give $X \le \rho_b F < \rho_b V$. Write $T = W_0(s)\bigl(1 + \frac{1}{10s}\bigr)/s^3 \ge 0$, so that $V = 1.9243\,T\,s$ and, by $\rho_b s = a$, $\rho_b V = 1.9243\,a\,T$. Since $1.9243\,a \le 1.9243 \cdot 0.39894229 = 0.76768\ldots \le 0.7677 = 2 \cdot 0.38385$,

$$X < 1.9243\,a\,T \le 2 \cdot 0.38385 \cdot T,$$

which is the claim. The constant $1.9243$ is $2 \cdot 0.38385/0.39894229 = 1.92433\ldots$ rounded down.

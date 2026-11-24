---
weight: step
short: comparison of the bound of the loss term with a number p
---
## Description

The bound `Parking.near_term_le` of $\frac N2\,\varepsilon_{t+1}x^t$ at the diagonal tilt $x = 1/\gamma_k$, compared with a number $p$: when $t$ lies in $[\sigma k, \sigma k + 1]$ and $N \le ck$, the quantity is at most $p$ as soon as $\lambda^2c^2E_0 \le p^2\cdot 8\cdot 3.14\cdot\sigma^3k$, where $E_0 \ge e^{5\sigma}$ and $\lambda \ge \sigma(k+3)/(\sigma k+1)$.

## Statement

Let $k \ge 15$ and $t \ge 1$ be natural numbers and let $\sigma$, $c$, $E_0$, $\lambda$, $N$, $p$ be real numbers such that

- $\sigma > 0$, $\lambda > 0$ and $\sigma(k+3) \le \lambda(\sigma k+1)$;
- $\sigma k \le t \le \sigma k + 1$;
- $e^{5\sigma} \le E_0$;
- $0 \le N \le c\,k$;
- $p \ge 0$ and $\lambda^2c^2E_0 \le p^2\cdot\bigl(8\cdot\frac{314}{100}\cdot\sigma^3\cdot k\bigr)$.

Then

$$\frac N2\;\varepsilon_{t+1}\,x^{t} \le p,$$

where $\varepsilon_m = (m-1)^{m-1}/m!$ is the sequence of `Parking.eps` and $x = 1/\gamma_k$, $\gamma_k = (1+1/k)^{k-2}$, is the diagonal tilt of `Parking.xk`.

## Explanation

The quantity $\psi = \varepsilon_{t+1}x^t = \varepsilon_{t+1}/\gamma_k^t$ is the loss term of `Parking.persistence_inequality` for the cut $\tau = t+1$: when the column has been nonnegative on the $t$ rows before the row $n$, the inequality has the leading term $(\frac2n - \psi)\,\beta^{(k-1)}_{n-1}$. The source $\frac2n$ wins if $\frac n2\psi < 1$, and this statement is the tool that certifies $\frac n2\psi \le p$ for a chosen $p < 1$, with $N = n$.

Under the first, second and fourth hypothesis, `Parking.near_term_le` with $L = c$ gives

$$\frac N2\,\psi \le \frac{\lambda\,c\,e^{5\sigma/2}}{2\sigma\sqrt{2\pi\sigma k}}.$$

The square of the right-hand side is $\lambda^2c^2e^{5\sigma}/(8\pi\sigma^3k)$, so the right-hand side is at most $p \ge 0$ exactly when $\lambda^2c^2e^{5\sigma} \le p^2\cdot 8\pi\sigma^3k$. The numerical hypothesis of the present statement is this condition with $\pi$ replaced by the smaller number $3.14$ and $e^{5\sigma}$ by a larger number $E_0$. For rational $\sigma$, $c$, $E_0$, $\lambda$ and $p$ it is a linear inequality in $k$ with rational coefficients, which holds from an explicit $k$ on.

The parameters are left free because `Parking.caseFar` applies the statement three times with different $\sigma$ and $c$; the values of $E_0$ are provided by `Parking.exp_41_60`, `Parking.exp_4_3` and `Parking.exp_7_3`.

## Proof

Let $S = \sqrt{2\pi\sigma k}$, which is positive because $\sigma > 0$ and $k > 0$, so that $S^2 = 2\pi\sigma k$ and $2\sigma S > 0$. By `Parking.near_term_le`, applied with $L = c$,

$$\frac N2\;\varepsilon_{t+1}\,x^{t} \le \frac{\lambda\,c\,e^{5\sigma/2}}{2\sigma S}.$$

It remains to show that the right-hand side is at most $p$, that is, $\lambda\,c\,e^{5\sigma/2} \le p\cdot 2\sigma S$. Since $(e^{5\sigma/2})^2 = e^{5\sigma} \le E_0$ and $\pi > 3.14$,

$$\bigl(\lambda\,c\,e^{5\sigma/2}\bigr)^2 = \lambda^2c^2e^{5\sigma} \le \lambda^2c^2E_0 \le p^2\cdot 8\cdot3.14\cdot\sigma^3k \le p^2\cdot8\pi\sigma^3k = (p\cdot2\sigma S)^2 ,$$

where the second inequality is the numerical hypothesis and the last equality uses $S^2 = 2\pi\sigma k$. As $p\cdot 2\sigma S \ge 0$, taking square roots gives $\lambda\,c\,e^{5\sigma/2} \le p\cdot 2\sigma S$, and dividing by $2\sigma S > 0$ yields the claim.

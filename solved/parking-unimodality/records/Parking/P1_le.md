---
weight: step
short: bound of the loss term of a finite run of positive rows
---
## Description

A bound for $\frac N2\,\varepsilon_{t+1}x^t$ at the diagonal tilt $x = 1/\gamma_k$, when $t$ lies in $[\sigma k, \sigma k + 1]$ and $N \le ck$: it is at most $p$ as soon as $\lambda^2c^2E_0 \le p^2\cdot 8\cdot 3.14\cdot\sigma^3k$, where $E_0 \ge e^{5\sigma}$ and $\lambda \ge \sigma(k+3)/(\sigma k+1)$.

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

By Stirling's formula $\psi \approx e^{5t/(2k)}/\bigl((t+1)\sqrt{2\pi t}\bigr)$, so with $t \approx \sigma k$ and $n \le ck$ the quantity $\frac n2\psi$ is about $c\,e^{5\sigma/2}/\bigl(2\sigma\sqrt{2\pi\sigma k}\bigr)$. It decreases like $k^{-1/2}$: a run of positive rows of length proportional to $k$ makes the loss small for large $k$. The numerical hypothesis is this expression squared, with $\pi$ replaced by $3.14$, $e^{5\sigma}$ by $E_0$, and a factor $\lambda$ that accounts for $t$ being an integer near $\sigma k$. The parameters are left free because `Parking.caseFar` applies the statement three times with different $\sigma$ and $c$; the values of $E_0$ are provided by `Parking.exp_41_60`, `Parking.exp_4_3` and `Parking.exp_7_3`.

## Proof

Let $\psi = \varepsilon_{t+1}x^t$ and $S = \sqrt{2\pi t}$.

*Stirling.* By `Parking.mul_eps`, $(t+1)\varepsilon_{t+1} = t^t/t!$, and by `Parking.poissonMass_le`, $e^{-t}t^t/t! \le 1/S$. By `Parking.xk_bounds`, $x \le e^{-1}e^{5/(2k)}$. Hence

$$\psi \le \frac{e^{5t/(2k)}}{(t+1)\,S}.$$

*The exponential factor.* Since $t \le \sigma k + 1$, $e^{5t/(2k)} \le e^{5\sigma/2}\,e^{5/(2k)}$. For $0 \le y \le \frac16$ one has $e^y \le 1 + \frac65y$ (from $e^{-y} \ge 1-y$ and $(1-y)(1+\frac65y) \ge 1$); with $y = \frac5{2k} \le \frac16$, which is where $k \ge 15$ is used, $e^{5/(2k)} \le 1 + \frac3k$. So $\psi\,(t+1)\,S \le e^{5\sigma/2}(1+\frac3k)$.

*The integer part.* $(1+\frac3k)\,\sigma k = \sigma(k+3) \le \lambda(\sigma k+1) \le \lambda(t+1)$, by the hypothesis on $\lambda$ and $\sigma k \le t$. Multiplying the previous bound by $\sigma k$ and cancelling $t+1$ gives $\psi\,S\,\sigma k \le e^{5\sigma/2}\lambda$.

*The row.* Multiply by $N \ge 0$ and use $N \le ck$: $\frac N2\psi\cdot 2S\sigma \le c\,e^{5\sigma/2}\lambda$.

*The numerical condition.* Since $(e^{5\sigma/2})^2 = e^{5\sigma} \le E_0$, $\pi > 3.14$ and $t \ge \sigma k$,

$$\bigl(c\,e^{5\sigma/2}\lambda\bigr)^2 \le \lambda^2c^2E_0 \le p^2\cdot 8\cdot3.14\cdot\sigma^3k \le p^2\cdot4\sigma^2\cdot2\pi t = (p\cdot2S\sigma)^2 .$$

As $p\cdot 2S\sigma \ge 0$, this gives $c\,e^{5\sigma/2}\lambda \le p\cdot 2S\sigma$, and dividing the inequality of the previous step by $2S\sigma > 0$ yields $\frac N2\psi \le p$.

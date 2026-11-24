---
weight: step
short: bound of the loss term of a finite run of positive rows
---
## Description

A bound for $\frac N2\,\varepsilon_{t+1}x^t$ at the diagonal tilt $x = 1/\gamma_k$, when $t$ lies in $[\sigma k, \sigma k + 1]$ and $0 \le N \le Lk$: it is at most $\lambda L\,e^{5\sigma/2}/\bigl(2\sigma\sqrt{2\pi\sigma k}\bigr)$, where $\lambda \ge \sigma(k+3)/(\sigma k+1)$.

## Statement

Let $k \ge 15$ and $t \ge 1$ be natural numbers and let $\sigma$, $\lambda$, $L$, $N$ be real numbers such that

- $\sigma > 0$, $\lambda > 0$ and $\sigma(k+3) \le \lambda(\sigma k+1)$;
- $\sigma k \le t \le \sigma k + 1$;
- $0 \le N \le L\,k$.

Then

$$\frac N2\;\varepsilon_{t+1}\,x^{t} \le \frac{\lambda\,L\,e^{5\sigma/2}}{2\sigma\sqrt{2\pi\sigma k}},$$

where $\varepsilon_m = (m-1)^{m-1}/m!$ is the sequence of `Parking.eps` and $x = 1/\gamma_k$, $\gamma_k = (1+1/k)^{k-2}$, is the diagonal tilt of `Parking.xk`.

## Explanation

The quantity $\psi = \varepsilon_{t+1}x^t = \varepsilon_{t+1}/\gamma_k^t$ is the loss term of `Parking.persistence_inequality` for the cut $\tau = t+1$: when the column has been nonnegative on the $t$ rows before the row $n$, the inequality has the leading term $(\frac2n - \psi)\,\beta^{(k-1)}_{n-1}$. The source $\frac2n$ wins if $\frac n2\psi < 1$. This statement bounds $\frac n2\psi$, with $N = n$, by an explicit expression in $k$.

By Stirling's formula $\psi \approx e^{5t/(2k)}/\bigl((t+1)\sqrt{2\pi t}\bigr)$, so with $t \approx \sigma k$ and $n \le Lk$ the quantity $\frac n2\psi$ is about $L\,e^{5\sigma/2}/\bigl(2\sigma\sqrt{2\pi\sigma k}\bigr)$. It decreases like $k^{-1/2}$: a run of positive rows of length proportional to $k$ makes the loss small for large $k$. The factor $\lambda$ accounts for what the approximation neglects, namely that $t$ is an integer in $[\sigma k, \sigma k+1]$ and that $x$ exceeds $e^{-1}$ by a factor of at most $e^{5/(2k)} \le 1 + \frac3k$: the proof needs $(1+\frac3k)\,\sigma k \le \lambda\,(t+1)$, and the hypothesis $\sigma(k+3) \le \lambda(\sigma k+1)$ provides it. When $3\sigma \le 1$ one may take $\lambda = 1$.

The hypotheses $t \ge 1$ and $\lambda > 0$ follow from the others ($t \ge \sigma k > 0$ and $t$ is an integer; $\lambda\,(\sigma k+1) \ge \sigma(k+3) > 0$). They are stated because the proof uses them in this form.

The statement is used by `Parking.P1_le`, which compares the bound with a number $p$; in this form `Parking.caseFar` applies it three times, with different $\sigma$ and $L$.

## Proof

Let $\psi = \varepsilon_{t+1}x^t$ and $S = \sqrt{2\pi t}$; both are defined and $S > 0$ because $t \ge 1$, and $\psi \ge 0$ because $\varepsilon_{t+1} \ge 0$ (`Parking.eps_nonneg`) and $x > 0$.

*Stirling.* By `Parking.mul_eps`, $(t+1)\varepsilon_{t+1} = t^t/t!$, and by `Parking.poissonMass_le`, $e^{-t}t^t/t! \le 1/S$. By `Parking.xk_bounds`, $x \le e^{-1}e^{5/(2k)}$. Hence

$$\psi \le \frac{e^{5t/(2k)}}{(t+1)\,S}.$$

*The exponential factor.* Since $t \le \sigma k + 1$, $e^{5t/(2k)} \le e^{5\sigma/2}\,e^{5/(2k)}$. For $0 \le y \le \frac16$ one has $e^y \le 1 + \frac65y$ (from $e^{-y} \ge 1-y$ and $(1-y)(1+\frac65y) \ge 1$); with $y = \frac5{2k} \le \frac16$, which is where $k \ge 15$ is used, $e^{5/(2k)} \le 1 + \frac3k$. So $\psi\,(t+1)\,S \le e^{5\sigma/2}(1+\frac3k)$.

*The integer part.* $(1+\frac3k)\,\sigma k = \sigma(k+3) \le \lambda(\sigma k+1) \le \lambda(t+1)$, by the hypothesis on $\lambda$, $\lambda \ge 0$ and $\sigma k \le t$. Multiplying the previous bound by $\sigma k \ge 0$ and cancelling $t+1 > 0$ gives $\psi\,S\,\sigma k \le \lambda\,e^{5\sigma/2}$.

*The row.* Multiply by $N \ge 0$ and use $N \le Lk$ and $\lambda\,e^{5\sigma/2} \ge 0$: $\frac N2\psi\cdot 2\sigma S\cdot k \le \lambda L\,e^{5\sigma/2}\cdot k$. Cancelling $k > 0$,

$$\frac N2\,\psi\cdot 2\sigma S \le \lambda\,L\,e^{5\sigma/2}.$$

*From $t$ to $\sigma k$.* Since $\sigma k \le t$ and the square root is monotone, $\sqrt{2\pi\sigma k} \le S$. As $\frac N2\psi \ge 0$ and $2\sigma > 0$,

$$\frac N2\,\psi\cdot 2\sigma\sqrt{2\pi\sigma k} \le \frac N2\,\psi\cdot 2\sigma S \le \lambda\,L\,e^{5\sigma/2},$$

and dividing by $2\sigma\sqrt{2\pi\sigma k} > 0$ yields the claim.

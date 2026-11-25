---
weight: unit
short: Jensen's inequality for the environment of a threshold
---
## Description

For $k \ge 1$ and $1 \le M \le 2k+1$: $a_M \exp\bigl(-\sum_{k<t<M} \operatorname{ren}(M-t)\, a_t \log(t/k) / a_M\bigr) \le z^{(k)}_{M-1}$, where $z^{(k)}_n = A(n,k-1)/n!$ is the normalised number of parking functions of length $n$ with all displacements less than $k$, $a_p = p^{p-1}/p!$ and $\operatorname{ren}(n) = n^n/n!$.

## Statement

Let $a_p = p^{p-1}/p!$ (`Parking.cay`), $\operatorname{ren}(n) = n^n/n!$ (`Parking.ren`), and let $z^{(k)}_n = A(n,k-1)/n!$ be the environment of the threshold $k$ (`Parking.zr`), where $A(n,k-1)$ is the number of parking functions of length $n$ with maximum displacement at most $k - 1$. For all natural numbers $k \ge 1$ and $M$ with $1 \le M \le 2k+1$,

$$a_M\;\exp\Bigl(-\,\frac{1}{a_M} \sum_{k < t < M} \operatorname{ren}(M-t)\; a_t\; \log\frac{t}{k}\Bigr) \;\le\; z^{(k)}_{M-1}.$$

## Explanation

**What is bounded.** The number $a_M = M^{M-1}/M!$ equals $(n+1)^{n-1}/n!$ for $n = M - 1$, that is, the classical number $(n+1)^{n-1}$ of all parking functions of length $n$, divided by $n!$. So $z^{(k)}_{M-1}/a_M$ is the fraction of the parking functions of length $M - 1$ whose displacements are all less than $k$, and the statement is a lower bound of this fraction by an explicit exponential. For $M \le k + 1$ the sum is empty and the statement reads $a_M \le z^{(k)}_{M-1}$; in that range the two numbers are equal, since a threshold $k$ imposes no restriction on a parking function of length at most $k$.

**Why it holds.** In the rows $n = M - 1 \le 2k$ the environment satisfies a linear equation of Volterra type with the Cayley kernel,

$$z^{(k)}_{M-1} = \kappa_k(M) + \sum_{k<t<M} a_{M-t}\;\frac{k}{t}\; z^{(k)}_{t-1}, \qquad \kappa_k(M) = a_M - \sum_{k<i<M} a_i\, a_{M-i},$$

where $\kappa_k$ is the sequence of `Parking.kap`. The equation is derived in the proof below from the single-chain formula `Parking.IsWSol.fwd`. Its weights are $k/t = e^{-\log(t/k)}$, and without the weights it is solved by $a_M$ itself: the equation $a_M = \kappa_k(M) + \sum_{k<t<M} a_{M-t}\, a_t$ is the definition of $\kappa_k$. So the environment is to $a_M$ what a weighted composition sum is to $\operatorname{ren}(m)$, and `Parking.volterra_tangent` applies. In the reading of that record, $z^{(k)}_{M-1}/a_M$ is the average over chains of sizes $M > t_1 > \dots > t_j > k$ of the product of the factors $k/t_i$, and the exponent in the statement is minus the average of $\sum_i \log(t_i/k)$; the weight of the chains that visit the size $t$ is $\operatorname{ren}(M-t)\, a_t$.

**What it is for.** Each term of the pair sum `Parking.pairSum` contains the environment $z^{(k)}_{N-b-1}$ below the lower marked point, with $N = k + R$. The lower bound of the pair sum, `Parking.pairSum_ge`, applies the present statement with $M = N - b$, next to `Parking.Lam_jensen` for the two composition sums of the term, so that the whole term is bounded from below by one exponential.

**The Lean form.** The right side is `zr k (M - 1)`; the subtraction is exact because $M \ge 1$. The logarithm is `Real.log ((t : ℝ) / k)`, and the sum runs over `Finset.Ioo k M` with the summand `ren (M - t) * (cay t * Real.log ((t : ℝ) / k))`.

## Proof

**The Volterra equation of the environment.** We first show: for $k \ge 1$ and every natural number $n \le 2k + 1$,

$$z^{(k)}_n = \kappa_k(n+1) + \sum_{k<t<n+1} a_{n+1-t}\;\frac{k}{t}\; z^{(k)}_{t-1}. \tag{1}$$

By `Parking.zr_isWSol`, the sequence $z^{(k)}$ solves the weighted last-car recursion with the weight $\omega(t) = \min(t,k)$. This weight satisfies $\omega(t) = t$ for $1 \le t \le k$, so the single-chain formula `Parking.IsWSol.fwd` applies with the parameter $k$ and gives, for $n \le 2k+1$ and with $c_m = (m+1)^{m-1}/m! = a_{m+1}$,

$$c_n - z^{(k)}_n = \sum_{t=k+1}^{n} c_{n-t}\,\Bigl(c_{t-1} - \frac{\omega(t)}{t}\, z^{(k)}_{t-1}\Bigr).$$

For $t \ge k+1$ we have $\omega(t) = k$. Writing $c_n = a_{n+1}$, $c_{n-t} = a_{n+1-t}$ and $c_{t-1} = a_t$, and noting that the range $k + 1 \le t \le n$ is the range $k < t < n+1$, the formula becomes

$$a_{n+1} - z^{(k)}_n = \sum_{k<t<n+1} a_t\, a_{n+1-t} - \sum_{k<t<n+1} a_{n+1-t}\;\frac{k}{t}\; z^{(k)}_{t-1},$$

and the first sum subtracted from $a_{n+1}$ is $\kappa_k(n+1)$ by the definition of `Parking.kap`. This is (1). (In the Lean source this equation is a private lemma of the module of the frozen polynomial, stated for the two thresholds $k$ and $k+1$; its argument is the one just given.)

**The tangent inequality.** Apply `Parking.volterra_tangent` with $t_0 = k$, $B = 2k+1$, $\kappa = \kappa_k$, $r(M) = a_M$, $u(M) = z^{(k)}_{M-1}$ and $x(t) = \log(t/k)$. Its hypotheses hold for $1 \le M \le 2k+1$:

- $\kappa_k(M) > 0$ by `Parking.kap_pos`;
- $a_M = \kappa_k(M) + \sum_{k<t<M} a_{M-t}\, a_t$, by the definition of $\kappa_k$;
- $z^{(k)}_{M-1} = \kappa_k(M) + \sum_{k<t<M} a_{M-t}\, e^{-x(t)}\, z^{(k)}_{t-1}$; this is (1) for $n = M - 1 \le 2k$, because $e^{-\log(t/k)} = k/t$ for $t > k \ge 1$.

Hence, for every real $\mu$,

$$e^{-\mu}\,\bigl((1+\mu)\, a_M - S\bigr) \;\le\; z^{(k)}_{M-1}, \qquad S = \sum_{k<t<M} \operatorname{ren}(M-t)\; a_t\; \log\frac{t}{k}.$$

**The choice of the parameter.** Since $a_M > 0$ (`Parking.cay_pos`), we may take $\mu = S/a_M$. Then $(1 + S/a_M)\, a_M - S = a_M$, and the inequality reads $a_M\, e^{-S/a_M} \le z^{(k)}_{M-1}$, which is the statement.

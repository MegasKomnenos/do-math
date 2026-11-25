---
weight: unit
short: the persistence inequality for abstract sequences
---
## Description

An abstract lower bound for a column $\delta$ at a row $n$. From the column equation at $n$, a diagonal lower bound $\gamma u_{j-1} - u_j \le \delta_j$ on the rows $k,\dots,n-1$, a kernel $\varepsilon$ with $\varepsilon_{m+1} \le \gamma\varepsilon_m$ for $m < \tau$, and $\delta \ge 0$ on the $\tau - 1$ rows before $n$: $\bigl(\frac2n - \varepsilon_\tau/\gamma^{\tau-1}\bigr)u_{n-1} + \sum_{m=\tau}^{n-k-1}(\gamma\varepsilon_m - \varepsilon_{m+1})\,u_{n-1-m} \le \delta_n$.

## Statement

Let $\varepsilon$, $u$, $\delta$ be sequences of real numbers indexed by the natural numbers, $\gamma > 0$ a real number, and $k \ge 1$, $n$, $\tau$ natural numbers with $k + 1 \le n$ and $2 \le \tau \le n - k$. Assume:

1. $\varepsilon_m > 0$ for every $m \ge 1$;
2. $u_{k-1} = 0$;
3. (column equation at the row $n$, as an inequality)
   $\dfrac2n\,u_{n-1} + \dfrac{k+1}{n}\,\delta_{n-1} + \sum_{m=1}^{n-k}\varepsilon_m\,\delta_{n-m} \le \delta_n$;
4. (diagonal lower bound) $\gamma\,u_{j-1} - u_j \le \delta_j$ for every $j$ with $k \le j \le n-1$;
5. (kernel in the diagonal scale) $\varepsilon_{m+1} \le \gamma\,\varepsilon_m$ for every $m$ with $1 \le m < \tau$;
6. (a run of nonnegative rows) $\delta_j \ge 0$ for every $j$ with $n - \tau + 1 \le j \le n-1$.

Then

$$\Bigl(\frac2n - \frac{\varepsilon_\tau}{\gamma^{\tau-1}}\Bigr)\,u_{n-1} + \sum_{m=\tau}^{n-k-1}\bigl(\gamma\,\varepsilon_m - \varepsilon_{m+1}\bigr)\,u_{n-1-m} \;\le\; \delta_n.$$

## Explanation

The statement turns the column equation, which expresses $\delta_n$ through the earlier values of the same column, into a lower bound in terms of the profile $u$ alone. In the application (the proof of `Parking.caseFar`) $\delta_j = d_{j,k}/j!$ is the normalised step of the column $k$, $u_j = b(j,k-1)/j!$ is the profile of the level $k-1$, $\varepsilon$ is the prime kernel and $\gamma = \gamma_k = (1+1/k)^{k-2}$.

The idea is to replace every $\delta_{n-m}$ in the feedback sum by its diagonal lower bound $\gamma u_{n-1-m} - u_{n-m}$. This is legitimate for a row at any distance $m$, whatever its sign, since $\varepsilon_m > 0$; but then consecutive terms nearly cancel, and what is left at the distance $m$ is $(\gamma\varepsilon_m - \varepsilon_{m+1})u_{n-1-m}$, a summation by parts. If this were done for all $m \ge 1$, the term $m = 1$ would consume the source: it leaves $-\varepsilon_1u_{n-1} = -u_{n-1}$ in the normalisation $\varepsilon_1 = 1$ of the prime kernel, against a source $\frac2nu_{n-1}$. On the rows that are known to be nonnegative one can do better: there $\varepsilon_m\delta_{n-m} \ge \psi\gamma^{m-1}\delta_{n-m}$ for the smaller weight $\psi\gamma^{m-1}$ with $\psi = \varepsilon_\tau/\gamma^{\tau-1}$, and for these geometric weights the diagonal bounds telescope exactly. The price of the run being only $\tau - 1$ rows long is the loss $\psi u_{n-1}$, which is small when $\tau$ is large: in the application $\varepsilon_\tau/\gamma^{\tau-1}$ is of the order $\tau^{-3/2}$ (see `Parking.near_term_le`). Hypothesis 5 is what allows the comparison $\psi\gamma^{m-1} \le \varepsilon_m$ on the run.

The result has two parts. The leading term $(\frac2n - \psi)u_{n-1}$ is positive when $\frac n2\psi < 1$ (certified by `Parking.P1_le`). The sum has the coefficients $\gamma\varepsilon_m - \varepsilon_{m+1}$, whose sign is not controlled by the hypotheses for $m \ge \tau$: in the application they are nonnegative for $m + 1 \le \frac35k$ (`Parking.eps_succ_le_gam`) and may be negative beyond, where `Parking.caseFar` bounds them by means of `Parking.extreme_column_le`.

Unlike `Parking.two_point`, the inequality says nothing unless a run of nonnegative rows of some length precedes $n$, and it makes no use of the rows before that run except through the diagonal bound. Hypothesis 2 removes a boundary term; in the application $u_{k-1} = b(k-1,k-1)/(k-1)! = 0$. The Lean statement writes $u_{k-1}$ with the truncated subtraction of natural numbers, which is the ordinary one because $k \ge 1$.

## Proof

Put $\psi = \varepsilon_\tau/\gamma^{\tau-1} > 0$.

*A comparison of weights.* For $1 \le m \le \tau$, $\psi\gamma^{m-1} \le \varepsilon_m$. This holds with equality at $m = \tau$, and descending induction gives the rest: if $\psi\gamma^{m} \le \varepsilon_{m+1}$ with $m < \tau$, then $\gamma\cdot\psi\gamma^{m-1} \le \varepsilon_{m+1} \le \gamma\varepsilon_m$ by hypothesis 5.

*Step 1.* Since $\tau \ge 2$, the row $n-1$ belongs to the run of hypothesis 6, so $\frac{k+1}{n}\delta_{n-1} \ge 0$, and hypothesis 3 gives $\frac2nu_{n-1} + \sum_{m=1}^{n-k}\varepsilon_m\delta_{n-m} \le \delta_n$. The diagonal bound at the row $n - m$, for $1 \le m \le n-k$, reads $\gamma u_{n-1-m} - u_{n-m} \le \delta_{n-m}$. Split the sum at $\tau$.

*Step 2: the rows $1 \le m \le \tau-1$.* Here $\delta_{n-m} \ge 0$, so by the comparison of weights and the diagonal bound

$$\varepsilon_m\delta_{n-m} \ge \psi\gamma^{m-1}\delta_{n-m} \ge \psi\bigl(\gamma^m u_{n-1-m} - \gamma^{m-1}u_{n-m}\bigr).$$

The right sides telescope: their sum over $1 \le m \le \tau-1$ is $\psi\gamma^{\tau-1}u_{n-\tau} - \psi u_{n-1} = \varepsilon_\tau u_{n-\tau} - \psi u_{n-1}$.

*Step 3: the rows $\tau \le m \le n-k$.* Here only $\varepsilon_m > 0$ and the diagonal bound are used: $\varepsilon_m\delta_{n-m} \ge \varepsilon_m(\gamma u_{n-1-m} - u_{n-m})$. Summation by parts gives

$$\sum_{m=\tau}^{n-k}\varepsilon_m\bigl(\gamma u_{n-1-m} - u_{n-m}\bigr) = -\varepsilon_\tau u_{n-\tau} + \sum_{m=\tau}^{n-k-1}\bigl(\gamma\varepsilon_m - \varepsilon_{m+1}\bigr)u_{n-1-m} + \gamma\,\varepsilon_{n-k}\,u_{k-1},$$

and the last term vanishes by hypothesis 2.

*Step 4.* Adding the bounds of Steps 2 and 3 to $\frac2nu_{n-1}$, the terms $\pm\varepsilon_\tau u_{n-\tau}$ cancel, and the claim follows from Step 1.

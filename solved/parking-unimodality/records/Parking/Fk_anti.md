---
weight: unit
short: the two-point condition of the near rows
---
## Description

For $k \ge 42$ the quantity $(k+\rho)\,\kappa_\rho$, with $\kappa_\rho = \varepsilon_\rho/\gamma_k^\rho$ the tilted kernel at the diagonal tilt, is nonincreasing in $\rho$ on the range $1 \le \rho \le 0.47k$.

## Statement

Let $k \ge 42$ and let $a \le b$ be natural numbers with $1 \le a$ and $100\,b \le 47\,k$. Then

$$(k+b)\,\kappa_b \le (k+a)\,\kappa_a,$$

where $\kappa_m = x^m\varepsilon_m$ is the tilted kernel of `Parking.kapx`, $x = 1/\gamma_k$ is the diagonal tilt of `Parking.xk`, $\gamma_k = (1+1/k)^{k-2}$ and $\varepsilon_m = (m-1)^{m-1}/m!$.

## Explanation

Write $F(\rho) = (k+\rho)\kappa_\rho$. In the tilted column equation of the column $k$ at the row $n = k+\rho$, the source has the coefficient $2x/n$ and the row at distance $\rho$, the bottom row $k$, is weighted by $\kappa_\rho$. The two-point argument `Parking.two_point` requires, for the crossing row $q = k + r_q$ and a later row $n = k + r$, that $\kappa_r\cdot\frac{2x}{q} \le \kappa_{r_q}\cdot\frac{2x}{n}$: the kernel must have fallen between the two rows at least as much as the source coefficient has. This is $F(r) \le F(r_q)$, and the present statement delivers it whenever both offsets are at most $0.47k$. That is how `Parking.caseA` uses it.

The number $0.47$ is where the method stops. One step $F(\rho+1) \le F(\rho)$ is the inequality $(1 + \frac{1}{k+\rho})\,g_\rho \le \gamma_k$ for the step ratio $g_\rho$ of `Parking.gs`. With $g_\rho \approx \exp(1 - \frac{3}{2\rho})$ and $\gamma_k \approx \exp(1-\frac5{2k})$ this asks for $\frac1{k+\rho} \le \frac{3}{2\rho} - \frac5{2k}$, which for $\rho = \theta k$ and large $k$ becomes $5\theta^2 + 4\theta - 3 \le 0$, that is $\theta \le (\sqrt{19}-2)/5 = 0.4718\ldots$ So the sufficient condition used in the proof is available only up to that offset. (The research from which the library was formalized records that $F$ does increase beyond it, so that $F$ has the shape of a valley; the library neither proves nor uses this.) Monotonicity of $F$ therefore cannot give the two-point condition for larger offsets. The library ends the two-point regime at $0.47k$ and treats the rows beyond it by a different argument (`Parking.caseFar`). The hypothesis $k \ge 42$ pays for the terms of lower order in the polynomial inequality of the proof when $0.47$ is this close to the root.

## Proof

By induction on $b$ it suffices to prove one step: for $k \ge 42$, $\rho \ge 1$ and $100(\rho+1) \le 47k$,

$$(k+\rho+1)\,\kappa_{\rho+1} \le (k+\rho)\,\kappa_\rho.$$

Here $\kappa_{\rho+1} = x^{\rho+1}g_\rho\,\varepsilon_\rho$, where $g_\rho = \varepsilon_{\rho+1}/\varepsilon_\rho$ is the step ratio of `Parking.gs` (`Parking.eps_step`), and $\kappa_\rho = x^{\rho}\varepsilon_\rho = x^{\rho+1}\gamma_k\,\varepsilon_\rho$ because $x\gamma_k = 1$ (`Parking.CrossCrit.xk_mul_gam`). The step therefore follows from

$$(k+\rho+1)\,g_\rho \le (k+\rho)\,\gamma_k$$

after multiplication by $x^{\rho+1}\varepsilon_\rho \ge 0$.

For $\rho = 1$: $g_1 = \frac12$ (`Parking.gs_zero`) and $\gamma_k \ge 1$, so $(k+2)\cdot\frac12 \le k+1 \le (k+1)\gamma_k$.

For $\rho \ge 2$ the proof uses the two bounds $g_\rho \le \exp\bigl(1-\frac{3}{2(\rho+1)}\bigr)$ and $\gamma_k \ge \exp\bigl(1-\frac5{2k}\bigr)$, which are established in the proof of `Parking.eps_succ_le_gam`. It is then enough to show

$$1 + \frac1{k+\rho} \le \exp\Bigl(\frac{3}{2(\rho+1)} - \frac{5}{2k}\Bigr),$$

and by $1 + y \le e^y$ this follows from $\frac1{k+\rho} \le \frac{3}{2(\rho+1)} - \frac5{2k}$. Bringing the three fractions to a common denominator,

$$\frac{3}{2(\rho+1)} - \frac5{2k} - \frac1{k+\rho} = \frac{3k^2 - 5\rho^2 - (4k+5)\rho - 7k}{2k(\rho+1)(k+\rho)},$$

so what is needed is the polynomial inequality $5\rho^2 + (4k+5)\rho + 7k \le 3k^2$. Its left side increases with $\rho$, and the hypothesis gives $\rho \le 0.47k - 1$. At $\rho = 0.47k - 1$ the left side equals

$$5(0.47k-1)^2 + (4k+5)(0.47k-1) + 7k = 2.9845\,k^2 + 0.65\,k,$$

and $2.9845\,k^2 + 0.65\,k \le 3k^2$ is equivalent to $k \ge 0.65/0.0155 = 41.9\ldots$, which holds for $k \ge 42$. This is the step at which the constant $0.47$ and the threshold $42$ enter: the coefficient $2.9845 = 5\cdot0.47^2 + 4\cdot0.47$ is just below $3$ because $0.47$ is just below the root of $5\theta^2 + 4\theta - 3$.

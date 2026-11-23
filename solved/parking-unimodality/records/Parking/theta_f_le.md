---
weight: step
short: bound of the far weights against the frozen kernel
---
## Description

For $m \ge 49$ with $\frac35k \le m + 1 \le k$: $(g_m - \gamma_k)\,f_m \le 1.05\,c_0\,k^{-5/2}$, where $g_m = \varepsilon_{m+1}/\varepsilon_m$, $\gamma_k = (1+1/k)^{k-2}$, $f$ is the frozen kernel and $c_0 = 1/\sqrt{2\pi}$.

## Statement

Let $k$ and $m \ge 49$ be natural numbers with $m + 1 \le k$ and $3k \le 5(m+1)$. Then

$$(g_m - \gamma_k)\,f_m \;\le\; \frac{105}{100}\cdot\frac{c_0}{k^2\sqrt k},$$

where $g_m$ is the step ratio of `Parking.gs`, $\gamma_k$ the number of `Parking.gam`, $f$ the frozen kernel of `Parking.fker` (here $f_m = e^{-m}\varepsilon_m$) and $c_0 = 1/\sqrt{2\pi}$ the constant of `Parking.c0`. In Lean, with $m = i + 1$: for $48 \le i$, $i + 2 \le k$ and $3k \le 5(i+2)$, `(gs i - gam k) * fker (i + 1) ≤ 105/100 * c0 / (k^2 * √k)`.

## Explanation

In the persistence inequality (`Parking.persistence_inequality`) the row at distance $m$ behind the target row carries the coefficient $\gamma_k\varepsilon_m - \varepsilon_{m+1} = -(g_m - \gamma_k)\varepsilon_m$. For $m + 1 \le \frac35k$ it is nonnegative (`Parking.eps_succ_le_gam`). For larger $m$ it may be negative, and `Parking.caseFar` has to bound the resulting "far feedback". After passing to the Borel scale the size of one far coefficient is $(g_m - \gamma_k)^+ f_m$, and this statement bounds it uniformly in $m$ by a quantity of the order $k^{-5/2}$.

The order $k^{-5/2}$ has two sources. The excess $g_m - \gamma_k$ is at most $e\,\bigl(\frac5{2k} - \frac{3}{2(m+1)}\bigr)$, which is of the order $1/k$ and vanishes at $m + 1 = \frac35k$. The kernel $f_m$ is of the order $m^{-3/2}$ by Stirling's formula. Their product, as a function of $s = m+1$, is at most its value in the limit $s = k$, up to the factor $1.05$ that absorbs the difference between $s$, $s-1$ and $s-2$ for $s \ge 50$.

The hypothesis $m + 1 \le k$ is the natural range (in `Parking.caseFar`, $m \le k-2$); the proof uses it only to know that $k$ is positive. The statement bounds the signed quantity, so it also holds, trivially, where $g_m < \gamma_k$.

## Proof

Write $s = m + 1$, so $s \ge 50$ and $\frac35k \le s$.

*The excess.* The proof of `Parking.eps_succ_le_gam` establishes $g_m \le \exp\bigl(1 - \frac{3}{2s}\bigr)$ for $m \ge 2$ and $\gamma_k \ge \exp\bigl(1 - \frac5{2k}\bigr)$ for $k \ge 2$. Put $D = \frac5{2k} - \frac3{2s}$, which is nonnegative because $3k \le 5s$. Then $\gamma_k \ge \exp(1-\frac3{2s})\,e^{-D} \ge \exp(1-\frac3{2s})(1 - D)$, hence

$$g_m - \gamma_k \le \exp\Bigl(1-\frac3{2s}\Bigr)D \le e\,D.$$

*The kernel.* By `Parking.mul_eps`, $m\,\varepsilon_m = (m-1)^{m-1}/(m-1)!$, and by `Parking.poissonMass_le`, $e^{-n}n^n/n! \le 1/\sqrt{2\pi n}$ for $n \ge 1$. With $n = m - 1$ this gives

$$f_m = e^{-m}\varepsilon_m \le \frac{e^{-1}}{m\sqrt{2\pi(m-1)}}.$$

*The product.* Since $f_m \ge 0$ and $eD \ge 0$,

$$(g_m - \gamma_k)f_m \le \frac{D}{m\sqrt{2\pi(m-1)}} = \frac{5s - 3k}{2ks\,(s-1)\sqrt{s-2}\,\sqrt{2\pi}}.$$

It remains to show that this is at most $1.05\,k^{-5/2}/\sqrt{2\pi}$, that is,

$$(5s - 3k)\,k^{3/2} \le 1.05\cdot 2s\,(s-1)\sqrt{s-2}.$$

Two inequalities give this. With $a = \sqrt s$ and $b = \sqrt k$,

$$2a^5 - (5a^2 - 3b^2)\,b^3 = (a-b)^2\,(2a^3 + 4a^2b + 6ab^2 + 3b^3) \ge 0,$$

so $(5s-3k)k^{3/2} \le 2s^{5/2}$; this is the statement that the function $s \mapsto (5s-3k)/s^{5/2}$ is largest at $s = k$. And $s^{3/2} \le 1.05\,(s-1)\sqrt{s-2}$, which after squaring is $s^3 \le 1.1025\,(s-1)^2(s-2)$ and holds for $s \ge 50$. Multiplying the second by $2s$ and combining with the first gives the claim.

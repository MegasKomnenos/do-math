---
weight: unit
short: the criterion for the next column
---
## Description

At a first-layer position $n = k + r$, $2 \le r \le k - 1$, at which the criterion function satisfies $\mathsf{G}(r,k) \ge 0$: if the step of column $k$ in the row $n$ is nonpositive, then the step of column $k + 1$ in the row $n$ is negative.

## Statement

Let $k \ge 3$ and $2 \le r \le k - 1$ be natural numbers, and put $n = k + r$. Let $\delta^{(j)}_n = \bigl(b(n,j) - b(n,j-1)\bigr)/n!$ be the normalised step of column $j$ in the row $n$ (`Parking.dq`), where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$, and let $\mathsf{G}(r,k)$ be the criterion function of `Parking.Gfun`. If $\mathsf{G}(r,k) \ge 0$ and $\delta^{(k)}_n \le 0$, then $\delta^{(k+1)}_n < 0$.

In terms of the counts: if $\mathsf{G}(r,k) \ge 0$ and $b(n,k) \le b(n,k-1)$, then $b(n,k+1) < b(n,k)$.

## Explanation

This statement is where the passage from parking functions to compositions pays off, and it is the only place where the pieces of that passage meet. Its proof has no combinatorics of its own; it is a chain of five inequalities, each supplied by one earlier result.

Write $N = n + 1$ and let $K = K_{n,k}$ be the frozen polynomial (`Parking.Kpoly`). By `Parking.dq_frozen`,

$$\delta^{(k)}_n = C_- - B_-, \qquad \delta^{(k+1)}_n = C_+ - B_+,$$

where $C_-$ and $C_+$ are the second differences of $K$ at $k$ and at $k + 1$ and

$$B_- = \frac{a_k}{k}\,\Lambda_{r+1}(k-1;N), \qquad B_+ = \frac{a_{k+1}}{k+1}\,\Lambda_r(k+2;N)$$

are multiples of chain sums (`Parking.Lam`). The hypothesis is $C_- \le B_-$ and the conclusion is $C_+ < B_+$. The curvature can grow from column $k$ to column $k + 1$ by at most the factor $e^{D_r/(k-1)}$ (`Parking.curv_ratio`). The boundary term changes in three ways, and each is controlled against the common chain sum $\Lambda = \Lambda_r(k;N)$: the constant in front changes by the Cayley ratio $(1+1/k)^{k-2}$; the length drops from $r + 1$ to $r$ while the threshold rises from $k - 1$ to $k$, which is `Parking.Lam_shorten`; and the threshold rises from $k$ to $k + 2$, which is `Parking.Lam_raise`. What is left is an inequality between real numbers,

$$e^{D_r/(k-1)}\Bigl(1+\frac1r\Bigr)^{r} e^{-\mu_-/(2(k-1))} \ <\ \Bigl(1+\frac1k\Bigr)^{k-2}\Bigl(1+\frac2k\Bigr)^{\mu_{\mathrm{mid}}},$$

in which $\mu_-$ and $\mu_{\mathrm{mid}}$ are mean numbers of cuts under two homogeneous laws. The criterion function is built so that $\mathsf{G}(r,k) \ge 0$ implies it: the logarithm of the right side exceeds the logarithm of the left side by at least $\mathsf{G}(r,k)/k + 1/k^2$. The record of `Parking.Gfun` goes through the terms of $\mathsf{G}$ one by one.

The conclusion is strict although the hypotheses are not; the strictness comes from the term $1/k^2$. The statement is applied in `Parking.mono265` and in `Parking.strip_step`, where `Parking.Gfun_pos` supplies $\mathsf{G}(r,k) > 0$.

On the hypotheses: $k \ge 3$ follows from $2 \le r \le k - 1$ and is listed separately in the Lean statement. The proof uses $r \ge 1$ only; the hypothesis $r \ge 2$ keeps the statement in the range in which $D_r$ is given by its formula (for $r = 1$ the formula is $0/0$, see `Parking.curv_ratio`). In Lean the hypothesis and the conclusion are `dq k (k + r) ≤ 0` and `dq (k + 1) (k + r) < 0`; the form in terms of the counts follows from `Parking.dq_nonpos_iff` and `Parking.dq_neg_iff`.

## Proof

Put $N = k + r + 1$, $\Lambda = \Lambda_r(k;N)$, $A = a_k/k$, and

$$h_- = \frac{k-1}{k+r}, \quad \mu_- = \mu_r(h_-), \qquad h_{\mathrm{mid}} = \frac{k}{k+1+r/2}, \quad \mu_{\mathrm{mid}} = \mu_r(h_{\mathrm{mid}}),$$

with the mean number of cuts $\mu_r(h)$ of `Parking.muh`. We have $\Lambda > 0$ by `Parking.Lam_thr_pos` and $A > 0$ by `Parking.cay_pos`.

**The five inputs.**

1. `Parking.dq_frozen` gives $\delta^{(k)}_n = C_- - A\,\Lambda_{r+1}(k-1;N)$ and $\delta^{(k+1)}_n = C_+ - \frac{a_{k+1}}{k+1}\,\Lambda_r(k+2;N)$. So the hypothesis reads $C_- \le A\,\Lambda_{r+1}(k-1;N)$.
2. `Parking.curv_ratio` gives $C_+ \le e^{D_r/(k-1)}\,C_-$.
3. `Parking.Lam_shorten` gives $\Lambda_{r+1}(k-1;N) \le (1+1/r)^r\,(1 - t)\,\Lambda$ with $t = \mu_-/(2(k-1))$, and $1 - t \le e^{-t}$.
4. `Parking.Lam_raise` gives $(1+2/k)^{\mu_{\mathrm{mid}}}\,\Lambda \le \Lambda_r(k+2;N)$.
5. `Parking.cay_ratio` gives $a_{k+1} = (1+1/k)^{k-1} a_k$, hence $a_{k+1}/(k+1) = (1+1/k)^{k-2}\,A$.

**The chain.** Suppose the scalar inequality

$$e^{D_r/(k-1)}\Bigl(1+\frac1r\Bigr)^{r} e^{-t} \ <\ \Bigl(1+\frac1k\Bigr)^{k-2}\Bigl(1+\frac2k\Bigr)^{\mu_{\mathrm{mid}}} \tag{S}$$

holds. Then, using 2, 1, 3, (S), 4 and 5 in this order, and the positivity of $A$ and $\Lambda$,

$$C_+ \le e^{D_r/(k-1)} C_- \le e^{D_r/(k-1)} A \Bigl(1+\frac1r\Bigr)^{r} e^{-t}\,\Lambda < \Bigl(1+\frac1k\Bigr)^{k-2} A \Bigl(1+\frac2k\Bigr)^{\mu_{\mathrm{mid}}} \Lambda \le \frac{a_{k+1}}{k+1}\,\Lambda_r(k+2;N),$$

which is $\delta^{(k+1)}_n < 0$.

**The scalar inequality.** Taking logarithms, (S) is equivalent to

$$\frac{D_r}{k-1} + r\log\Bigl(1+\frac1r\Bigr) - \frac{\mu_-}{2(k-1)} \ <\ (k-2)\log\Bigl(1+\frac1k\Bigr) + \mu_{\mathrm{mid}}\log\Bigl(1+\frac2k\Bigr).$$

Two lower bounds for the means enter. By `Parking.mu0_le_muh`, applied at $h_-$ and at $h_{\mathrm{mid}}$, both of which lie in $(0,1]$,

$$m_1 := \mu^0_r\Bigl(\frac{r(r+1)}{k-1}\Bigr) \le \mu_-, \qquad m_2 := \mu^0_r\Bigl(\frac{r(r+2)}{2k}\Bigr) \le \mu_{\mathrm{mid}},$$

because $r(1/h_- - 1) = r(r+1)/(k-1)$ and $r(1/h_{\mathrm{mid}} - 1) = r(r+2)/(2k)$; here $\mu^0_r$ is the function of `Parking.mu0`. Moreover $m_1 \ge 0$ (`Parking.mu0_nonneg`) and $\mu_{\mathrm{mid}} \ge 0$ (`Parking.muh_nonneg`).

Put $a = 1/r$, $b = 1/k$ and $d = 1/(k-1)$, so that $0 < b \le d$ and $b \le 1/3$. The Taylor bounds for the logarithm, `Parking.log_one_add_le3`, `Parking.log_one_add_ge4` and `Parking.log_one_add_ge2`, give

$$r\log\Bigl(1+\frac1r\Bigr) \le 1 - \frac a2 + \frac{a^2}{3}, \qquad (k-2)\log\Bigl(1+\frac1k\Bigr) \ge 1 - \frac52 b + b^2, \qquad \log\Bigl(1+\frac2k\Bigr) \ge 2b(1-b).$$

The first is $r$ times $\log(1+a) \le a - a^2/2 + a^3/3$. The third is $\log(1+2b) \ge 2b - (2b)^2/2$. For the second, $(k-2)$ times $b - b^2/2 + b^3/3 - b^4/4$ equals $1 - \frac52 b + \frac43 b^2 - \frac{11}{12} b^3 + \frac12 b^4$ (using $kb = 1$), and this exceeds $1 - \frac52 b + b^2$ by $\frac{1}{12} b^2 (4 - 3b)(1 - 2b) \ge 0$; this is where $k \ge 3$ is used.

The hypothesis $\mathsf{G}(r,k) \ge 0$, multiplied by $b > 0$ and written with $kb = 1$ and $k/(k-1) = k d$, reads

$$0 \le \Bigl(\frac a2 - \frac{a^2}{3}\Bigr) - \frac52 b + \frac12 m_1 b + 2b(1-b)\,m_2 - D_r\,d.$$

Since $m_1 b \le \mu_- d$ (from $0 \le m_1 \le \mu_-$ and $0 < b \le d$) and $2b(1-b)\,m_2 \le 2b(1-b)\,\mu_{\mathrm{mid}}$, it follows that

$$D_r\,d + 1 - \frac a2 + \frac{a^2}{3} - \frac{\mu_- d}{2} \ \le\ 1 - \frac52 b + 2b(1-b)\,\mu_{\mathrm{mid}} \ <\ 1 - \frac52 b + b^2 + 2b(1-b)\,\mu_{\mathrm{mid}}.$$

By the three logarithm bounds, and $\mu_{\mathrm{mid}} \ge 0$ for the third, the left end is at least the left side of the logarithmic form of (S) and the right end is at most its right side. This proves (S), with the margin $b^2 = 1/k^2$.

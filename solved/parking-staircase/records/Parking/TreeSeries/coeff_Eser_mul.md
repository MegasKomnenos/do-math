---
weight: unit
short: coefficients of 1/P and of a quotient by P
---
## Description

For every real power series $f$, the coefficients of $f/P$ are $[X^n](E f) = f_n - \sum_{m=1}^{n} \varepsilon_m f_{n-m}$, where $P = \sum_n c_n X^n$, $c_n = (n+1)^{n-1}/n!$, $E = 1/P$ and $\varepsilon_m = (m-1)^{m-1}/m!$. Equivalently, $1/P = 1 - \sum_{m \ge 1} \varepsilon_m X^m$.

## Statement

Let $E = 1/P$ be the inverse of the series $P = \sum_{n \ge 0} c_n X^n$ (`Parking.TreeSeries.Eser`, `Parking.TreeSeries.Pser`). For every formal power series $f = \sum_j f_j X^j$ with real coefficients and every natural number $n$,

$$[X^n](E f) = f_n - \sum_{m=1}^{n} \varepsilon_m\, f_{n-m},$$

where $\varepsilon_m = (m-1)^{m-1}/m!$ for $m \ge 1$ (`Parking.eps`).

## Explanation

The statement is equivalent to the formula $E = 1 - \sum_{m \ge 1} \varepsilon_m X^m$ for the coefficients of $1/P$: taking $f = 1$ gives $[X^n] E = -\varepsilon_n$ for $n \ge 1$, and conversely the formula for a general $f$ is the coefficient of a product. It is stated for a product because that is how it is applied: to divide a series by $P$ and read off the result as a renewal-type expression with the kernel $\varepsilon$. With $f = P$ it gives the renewal equation $c_n = \sum_{m=1}^{n} \varepsilon_m c_{n-m}$ (`Parking.eps_conv`). With $f$ the series of a solution $W$ of a weighted last-car recursion it gives the left-hand side $W_n - \sum_{m=1}^{n} \varepsilon_m W_{n-m}$ of the single-chain formula (`Parking.IsWSol.ez`), and from there the column equations. It is used once more for the renewal equation of the resolvent sequence (`Parking.Gres_isRenewal`).

That the coefficients of $1/P$ have this closed form is a property of the particular numbers $c_n$. It comes from the differential equation $E' = -E\,T'$ and the fact that $E\,T'$ can be computed: it equals $1 + X T'$, whose coefficients are $n^n/n!$.

## Proof

Write $T = XP$ for the tree series (`Parking.TreeSeries.Tser`), $a_j$ for the Cayley coefficients, which are its coefficients (`Parking.TreeSeries.coeff_Tser`), and $\operatorname{ren}(n) = n^n/n!$ (`Parking.ren`).

*The coefficients of $E$.* We show $[X^{m+1}]\,E = -\varepsilon_{m+1}$ for every $m \ge 0$, in four steps.

(i) $P' = T'P$. This is the recursion `Parking.cc_rec` read coefficient by coefficient; the argument is given in the proof of `Parking.TreeSeries.deriv_Eser`.

(ii) $E\,T' = 1 + X\,T'$. By the product rule, $T' = (XP)' = P + XP'$. Multiply by $E$ and use $EP = 1$ (`Parking.TreeSeries.Eser_mul_Pser`) and (i): $E\,T' = EP + X\,E\,P' = 1 + X\,E\,T'P = 1 + X\,T'$.

(iii) The coefficient of $X^n$ in $1 + XT'$ is $\operatorname{ren}(n)$. For $n = 0$ it is $1 = \operatorname{ren}(0)$. For $n \ge 1$ it is the coefficient of $X^{n-1}$ in $T'$, which is $n\,a_n = n \cdot n^{n-1}/n! = n^n/n!$.

(iv) By `Parking.TreeSeries.deriv_Eser` and (ii), $E' = -E\,T' = -(1 + XT')$. Comparing the coefficients of $X^m$ and using (iii), $(m+1)\,[X^{m+1}]E = -\operatorname{ren}(m)$. By `Parking.mul_eps`, $\operatorname{ren}(m) = (m+1)\,\varepsilon_{m+1}$. Dividing by $m + 1$ gives $[X^{m+1}]E = -\varepsilon_{m+1}$.

*The product.* By `Parking.TreeSeries.coeff_mul_split`, $[X^n](Ef) = E_0 f_n + \sum_{m=1}^{n} E_m f_{n-m}$, where $E_m = [X^m]E$. Here $E_0 = 1$ (`Parking.TreeSeries.coeff_Eser_zero`) and $E_m = -\varepsilon_m$ for $m \ge 1$, which is the claim.

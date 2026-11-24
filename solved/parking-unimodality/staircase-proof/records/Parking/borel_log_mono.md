---
weight: unit
short: the Borel weights times m^{3/2} do not decrease
---
## Description

For natural numbers $1 \le i \le j$: $\log a_i - i + \tfrac32\log i \le \log a_j - j + \tfrac32\log j$, where $a_m = m^{m-1}/m!$. Equivalently, the sequence $e^{-m} a_m\, m^{3/2}$, $m \ge 1$, does not decrease.

## Statement

Let $a_m = m^{m-1}/m!$ for $m \ge 1$ (the Cayley coefficients, `Parking.cay`). For all natural numbers $i$ and $j$ with $1 \le i \le j$,

$$\log a_i - i + \tfrac32\log i \;\le\; \log a_j - j + \tfrac32\log j .$$

## Explanation

The numbers $e^{-m} a_m$, $m \ge 1$, are the probabilities of the Borel distribution with parameter $1$; we call them the Borel weights. By Stirling's formula $e^{-m} a_m$ is asymptotic to $m^{-3/2}/\sqrt{2\pi}$. The statement is an exact, one-sided form of this asymptotic relation. Each side is the logarithm of $e^{-m} a_m\, m^{3/2}$, at $m = i$ and at $m = j$, so the claim is that this product does not decrease as $m \ge 1$ grows. Since all the numbers involved are positive, it can be read as

$$\frac{e^{-i} a_i}{e^{-j} a_j} \;\le\; \Bigl(\frac{j}{i}\Bigr)^{3/2} \qquad (1 \le i \le j):$$

from an index to a larger one the Borel weights fall by at most the factor by which the power $m^{-3/2}$ falls.

The statement is written with logarithms because it is proved one step $m \to m+1$ at a time, where the logarithm turns the ratio $a_{m+1}/a_m = (1+1/m)^{m-1}$ into a sum, and because its direct use is an inequality between logarithms. It has two uses. `Parking.borel_ratio_le` derives from it a polynomial bound for the ratio of two Borel weights; that bound serves both the curve increase and the diagonal step behind the curve, as its record explains. The lower bound of the pair sum, `Parking.pairSum_ge`, uses the present statement directly, with $i = k$ and $j = k + R - b$, where $k$ is the column, $R$ the parameter of the pair sum and $b \le R$ the larger of the two marked cut points: the exponent attached to the pair contains the term $\log\bigl(a_k\, e^{R-b}/a_{k+R-b}\bigr)$, and the statement bounds it by $\tfrac32 \log\bigl((k+R-b)/k\bigr)$.

In Lean the statement is `Real.log (cay i) - i + 3 / 2 * Real.log i ≤ Real.log (cay j) - j + 3 / 2 * Real.log j`, with the natural numbers $i$ and $j$ cast to real numbers.

## Proof

Put $\phi(m) = \log a_m - m + \tfrac32 \log m$ for $m \ge 1$. The claim is $\phi(i) \le \phi(j)$ for $1 \le i \le j$. We argue by induction on $j$, starting at $j = i$, where there is nothing to prove; the induction step is the inequality $\phi(j) \le \phi(j+1)$ for every $j \ge 1$, which we now show.

Fix $j \ge 1$ and put $\ell = \log(1 + 1/j)$. By `Parking.cay_ratio`, $a_{j+1} = (1+1/j)^{j-1}\, a_j$, and $a_j > 0$ by `Parking.cay_pos`, so $\log a_{j+1} = (j-1)\,\ell + \log a_j$. Moreover $\log(j+1) = \log j + \ell$. Hence

$$\phi(j+1) - \phi(j) \;=\; (j-1)\,\ell \;-\; 1 \;+\; \tfrac32\,\ell \;=\; \bigl(j + \tfrac12\bigr)\,\ell - 1 .$$

For every real $x \ge 0$ one has $\log(1+x) \ge 2x/(x+2)$; this is a standard inequality (the two sides agree at $x = 0$, and the derivative of their difference is $x^2/((1+x)(x+2)^2) \ge 0$). At $x = 1/j$ it reads $\ell \ge 2/(2j+1)$, that is, $\bigl(j + \tfrac12\bigr)\,\ell \ge 1$. Therefore $\phi(j+1) - \phi(j) \ge 0$.

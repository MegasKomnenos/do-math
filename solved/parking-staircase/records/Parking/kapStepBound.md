---
weight: unit
short: closed bound for the relative growth of the kernel deficit
---
## Description

The closed form $\mathsf T(k,a) = \dfrac{\frac32\,\xi\,\bigl(1+\frac{2}{3(k+2)}\bigr)\bigl(1+\frac32\xi+\frac38\xi^2\bigr)}{\frac{23}{24}-\frac32\,\xi\,\bigl(1+\frac\xi4\bigr)}$ with $\xi = a/k$; the normalised kernel deficit grows on a diagonal step by at most the factor $1 + \mathsf T(k,a)/k$.

## Statement

For natural numbers $k \ge 1$ and $a$, with $\xi = a/k$,

$$\mathsf T(k,a) \;=\; \frac{\dfrac32\;\xi\;\Bigl(1+\dfrac{2}{3\,(k+2)}\Bigr)\Bigl(1+\dfrac32\,\xi+\dfrac38\,\xi^2\Bigr)}{\dfrac{23}{24}-\dfrac32\;\xi\,\Bigl(1+\dfrac{\xi}{4}\Bigr)} ,$$

a real number, defined when the denominator is not zero; this is the case for $2a \le k$, where the denominator is positive. For $k = 0$ put $\mathsf T(0,a) = 0$.

## Explanation

**What it bounds.** With the Cayley coefficients $a_j = j^{j-1}/j!$ and the kernel deficit $\kappa_k(t) = a_t - \sum_{k<i<t} a_i\,a_{t-i}$ (`Parking.kap`), `Parking.kap_diag_le` states for $k \ge 1$ and $2a \le k$ that

$$\frac{\kappa_{k+1}(k+a+1)}{a_{k+a+1}} \;\le\; \Bigl(1 + \frac{\mathsf T(k,a)}{k}\Bigr)\,\frac{\kappa_k(k+a)}{a_{k+a}} .$$

To first order $\mathsf T(k,a) \approx \frac32\cdot\frac{24}{23}\,\xi$, so the relative growth is of the order $a/k^2$.

**Where the factors come from.** Each factor is the trace of one estimate in the proof of `Parking.kap_diag_le`. The polynomial $1+\frac32\xi+\frac38\xi^2$ bounds the ratio of two Borel weights $e^{-i}a_i$ whose indices differ by a fraction at most $\xi$ (`Parking.borel_ratio_le`). The factor $\frac32\bigl(1+\frac{2}{3(k+2)}\bigr)$ comes from the decrease of a ratio $a_i/a_{i+j}$ when both indices are raised by one, which is at most $\frac{j}{i+j}\bigl(\frac{3}{2i}+\frac{1}{i(i+1)}\bigr)$ in relative terms, at $i \ge k+1$. The denominator is what is left of a lower bound for the normalised deficit itself: the deficit is at least a Borel tail minus $\frac32(1+\frac\xi4)$ times a sum of Poisson masses divided by $k+1$, and $\frac{23}{24}$ times that sum is at most $a$ times the tail.

**The range.** The denominator $\frac{23}{24}-\frac32\xi(1+\frac\xi4)$ decreases in $\xi \ge 0$, equals $\frac{11}{96}$ at $\xi = \frac12$, and vanishes near $\xi = 0.56$. On $0 \le \xi \le \frac12$ the closed form is nonnegative (`Parking.kapStepBound_nonneg`). In the diagonal step it is used for $\xi \le 0.151$ only, where `Parking.ledger` replaces it by the chord $\frac32\,\xi\,(1.047 + 4.45\,\xi)$.

**One closed form for three statements.** The same expression stands in `Parking.kap_diag_le`, in `Parking.scalar_step` and in `Parking.ledger`. The numerical constants of the last one are fitted to this expression, so the definition fixes it once.

**The Lean form.** `Parking.kapStepBound k a` is the expression above with `(a : ℝ) / k` for $\xi$, for all natural numbers $k$ and $a$. Lean's division by zero is $0$, so the definition also has a value for $k = 0$ (where $\xi = 0$ and the value is $0$) and where the denominator vanishes; no statement of the library uses those values except `Parking.kapStepBound_nonneg` at $k = a = 0$.

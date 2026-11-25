---
weight: step
short: Jensen's inequality for an exponential function
---
## Description

Jensen's inequality for $e \mapsto c^e$ with a base $c > 0$: for weights $w_i \ge 0$ with sum $W$ and real exponents $e_i$ with weighted mean $\bar e$, $c^{\bar e}\,W \le \sum_i w_i\,c^{e_i}$.

## Statement

Let $I$ be a finite set, and for each $i \in I$ let $w_i \ge 0$ and $e_i$ be real numbers. Let $c > 0$ be a real number, and let $W$ and $\bar e$ be real numbers with

$$W = \sum_{i \in I} w_i, \qquad \bar e\,W = \sum_{i \in I} w_i\,e_i .$$

Then

$$c^{\bar e}\,W \;\le\; \sum_{i \in I} w_i\,c^{e_i}.$$

## Explanation

The function $e \mapsto c^e = \exp(e \log c)$ is convex for every base $c > 0$, whether $c$ is below or above $1$. The statement is Jensen's inequality for this function and the weights $w_i$, multiplied by the total weight $W$, so that the weights need not be normalised.

The mean $\bar e$ enters through the equation $\bar e\,W = \sum_i w_i e_i$ and not as a quotient. This is the form in which the two uses supply it, and it covers the case $W = 0$, in which every $w_i$ is $0$, the number $\bar e$ is arbitrary, and both sides are $0$.

The statement is used twice in the diagonal step, with bases on the two sides of $1$. In `Parking.Vc_sum_pow_le` the base is a number $\rho \le 1$, the index is the number $Q$ of parts of a composition, and the exponent is the number $Q - 1$ of its cut points. In `Parking.Lam_gain` the base is a number $1 + x \ge 1$, the index is a set of cut points, and the exponent is an additive statistic of that set. In both, the inequality replaces a mean of powers by the power of a mean, which can then be bounded.

In Lean the index set is a `Finset` of an arbitrary type, the weights and exponents are functions on that type, and the hypothesis $w_i \ge 0$ is asked for the members of the finite set only. The power $c^{e}$ is the real power `Real.rpow`.

## Proof

For every $i \in I$,

$$c^{e_i} = c^{\bar e}\,c^{e_i - \bar e} = c^{\bar e}\exp\bigl((e_i - \bar e)\log c\bigr) \;\ge\; c^{\bar e}\bigl(1 + (e_i - \bar e)\log c\bigr),$$

because $\exp t \ge 1 + t$ for every real $t$ and $c^{\bar e} > 0$. This is the tangent of $e \mapsto c^e$ at $\bar e$. Multiply by $w_i \ge 0$ and sum over $i$:

$$\sum_i w_i\,c^{e_i} \;\ge\; c^{\bar e}\Bigl(\sum_i w_i + \log c\,\Bigl(\sum_i w_i e_i - \bar e \sum_i w_i\Bigr)\Bigr) = c^{\bar e}\bigl(W + \log c\,(\bar e\,W - \bar e\,W)\bigr) = c^{\bar e}\,W .$$

The linear parts cancel by the two hypotheses on $W$ and $\bar e$.

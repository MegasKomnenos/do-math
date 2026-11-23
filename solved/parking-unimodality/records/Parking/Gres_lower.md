---
weight: unit
short: lower bound of the resolvent sequence
---
## Description

For $s \ge 6$ the resolvent sequence of the frozen kernel satisfies $G_s \ge e\,\bigl(1-\frac1{12(s+1)}\bigr)\bigl(4-\frac{21}{s+1}\bigr)\big/\bigl((s+1)\sqrt{2\pi(s+1)}\bigr)$.

## Statement

For every natural number $s \ge 6$,

$$G_s \;\ge\; \frac{e}{s+1}\cdot\frac{1-\dfrac1{12(s+1)}}{\sqrt{2\pi(s+1)}}\cdot\Bigl(4-\frac{21}{s+1}\Bigr),$$

where $G$ is the sequence of `Parking.Gres`.

## Explanation

The bound says that $G_s$ decays no faster than $(s+1)^{-3/2}$, with the explicit constant $4e/\sqrt{2\pi}$ up to the two correction factors. It has the shape of the leading term of $G$: by the closed form, $H_s = e^sG_s$ is $c_s$ times a sum that tends to $\sum_{j\ge0}(j+1)2^{-j} = 4$, and $e^{-s}c_s$ is of the order $e\,(s+1)^{-3/2}/\sqrt{2\pi}$ by Stirling's formula. The constant $21$ and the range $s \ge 6$ come from the way the finite sum is bounded below; they are not sharp.

A lower bound of $G$ is needed because the far rows of a column (`Parking.caseFar`) end in an inequality of the form "source times $G_\rho$ exceeds far feedback times $\sum G_i$", in which $G_\rho$ stands on the favourable side. The bound is used there at $s = \rho \ge 49$, and once more to bound a tail sum of $G$ from below.

The definition of $G$ by explicit coefficients (`Parking.Gres`, `Parking.Hres`, `Parking.hcoef`) exists for the sake of this statement: the proof evaluates the coefficients $[X^s]X^jP^{j+1}$ in closed form by Abel's identity.

## Proof

Write $P = \sum_n c_nX^n$ with $c_n = (n+1)^{n-1}/n!$, $h_{j,s} = [X^s]X^jP^{j+1}$ (`Parking.hcoef`), $H_s = \sum_{j=0}^{s}2^{-j}h_{j,s}$ (`Parking.Hres`), so that $G_s = e^{-s}H_s$. Let $w_0(x) = 1$ and $w_n(x) = x(x+n)^{n-1}$ for $n \ge 1$ be the Abel weights of `Parking.abelW`. The proof has five steps: a convolution form of Abel's identity; the coefficients of the powers of $P$; a lower bound of $h_{j,s}$ relative to $h_{0,s} = c_s$; the summation over $j$; and Stirling's bound for $c_s$.

*Step 1: Abel's identity in convolution form.* For every natural number $n \ge 1$ and real $x$, $y$,

$$\sum_{k=0}^{n}\binom nk\,w_k(x)\,w_{n-k}(y) = (x+y)\,(x+y+n)^{n-1}.$$

This follows from `Parking.abel_identity`, which states $\sum_{k=0}^{n}\binom nk w_k(x)(y'-k)^{n-k} = (x+y')^n$ for all $n$, $x$, $y'$. Put $y' = y + n$ and $S = \sum_{k=0}^{n-1}\binom nk w_k(x)(y+n-k)^{n-1-k}$. For $k \le n-1$ one has $w_{n-k}(y) = y\,(y+n-k)^{n-1-k}$, so the left side of the claim is $yS + w_n(x)$. On the other hand, splitting $(y+n-k)^{n-k} = \bigl(y + (n-k)\bigr)(y+n-k)^{n-1-k}$ and using $\binom nk(n-k) = n\binom{n-1}k$, the identity at $n$ becomes

$$yS + n\sum_{k=0}^{n-1}\binom{n-1}k w_k(x)(y+n-k)^{n-1-k} + w_n(x) = (x+y+n)^n,$$

and the middle sum is $(x+y+n)^{n-1}$ by the identity at $n-1$ with the same $y'$. Hence $yS + w_n(x) = (x+y+n)^n - n(x+y+n)^{n-1} = (x+y)(x+y+n)^{n-1}$.

*Step 2: the coefficients of $P^{a+1}$.* For all natural numbers $a$ and $n$,

$$[X^n]\,P^{a+1} = \frac{w_n(a+1)}{n!}.$$

The proof is by induction on $a$. For $a = 0$ this is $c_n = w_n(1)/n!$, which is `Parking.cc_eq_abelW`. For the step, $[X^n]P^{a+2} = \sum_{j=0}^{n}[X^j]P^{a+1}\cdot c_{n-j} = \frac1{n!}\sum_{j}\binom nj w_j(a+1)\,w_{n-j}(1)$, which for $n \ge 1$ equals $(a+2)(a+2+n)^{n-1}/n! = w_n(a+2)/n!$ by Step 1, and for $n = 0$ equals $1$.

Consequently $h_{j,s} = 0$ for $s < j$ and $h_{j,s} = w_{s-j}(j+1)/(s-j)!$ for $j \le s$. In particular $h_{0,s} = c_s$, and comparing the closed forms at $j$ and $j+1$ gives, for $j + 1 \le s$,

$$h_{j+1,s}\,(j+1)(s+1) = h_{j,s}\,(j+2)(s-j).$$

This is a routine calculation with $w_{s-j}(j+1) = (j+1)(s+1)^{s-j-1}$.

*Step 3: a lower bound of the coefficients.* For $0 \le j \le s$,

$$h_{j,s} \ge c_s\,(j+1)\Bigl(1 - \frac{j(j+1)}{2(s+1)}\Bigr).$$

The proof is by induction on $j$, with equality at $j = 0$. By the relation of Step 2, $h_{j+1,s} = h_{j,s}\cdot\frac{j+2}{j+1}\bigl(1 - \frac{j+1}{s+1}\bigr)$, and the factor is nonnegative. Inserting the bound for $h_{j,s}$ and using $(1-a)(1-b) \ge 1 - a - b$ for $a, b \ge 0$, with $a = \frac{j(j+1)}{2(s+1)}$ and $b = \frac{j+1}{s+1}$, so that $a + b = \frac{(j+1)(j+2)}{2(s+1)}$, gives the bound for $h_{j+1,s}$. In effect the product $\prod_{u=1}^{j}(1 - \frac{u}{s+1})$ is bounded below by $1 - \sum_{u\le j}\frac{u}{s+1}$.

*Step 4: summation.* Two finite sums are evaluated by induction on $s$:

$$\sum_{j=0}^{s}\frac{j+1}{2^j} = 4 - \frac{s+3}{2^s}, \qquad \sum_{j=0}^{s}\frac{j(j+1)^2}{2^j} = 40 - \frac{s^3+8s^2+27s+40}{2^s}.$$

Multiplying the bound of Step 3 by $2^{-j}$ and summing over $j \le s$,

$$H_s \ge c_s\Bigl(4 - \frac{s+3}{2^s}\Bigr) - \frac{c_s}{2(s+1)}\Bigl(40 - \frac{s^3+8s^2+27s+40}{2^s}\Bigr).$$

The right side minus $c_s\bigl(4 - \frac{21}{s+1}\bigr)$ equals

$$\frac{c_s}{s+1}\Bigl[\Bigl(1 - \frac{(s+3)(s+1)}{2^s}\Bigr) + \frac{s^3+8s^2+27s+40}{2^{s+1}}\Bigr],$$

and this is nonnegative as soon as $(s+3)(s+1) \le 2^s$, which holds for $s \ge 6$ (at $s = 6$ it reads $63 \le 64$, and the induction step is routine). Hence $H_s \ge c_s\bigl(4 - \frac{21}{s+1}\bigr)$ for $s \ge 6$. This is the only place where $s \ge 6$ is used, apart from the sign in Step 5.

*Step 5: Stirling's bound.* Let $p_n = e^{-n}n^n/n!$ be the Poisson mass of `Parking.poissonMass`. From $c_s = (s+1)^s/(s+1)!$ (`Parking.cc_eq`) one gets $e^{-s}c_s = e\,p_{s+1}/(s+1)$, and `Parking.poissonMass_ge` gives $p_{s+1} \ge \bigl(1 - \frac1{12(s+1)}\bigr)/\sqrt{2\pi(s+1)}$. Since $4 - \frac{21}{s+1} \ge 0$ for $s \ge 6$, multiplying the bound of Step 4 by $e^{-s}$ yields

$$G_s = e^{-s}H_s \ge e^{-s}c_s\Bigl(4 - \frac{21}{s+1}\Bigr) \ge \frac{e}{s+1}\cdot\frac{1-\frac1{12(s+1)}}{\sqrt{2\pi(s+1)}}\Bigl(4 - \frac{21}{s+1}\Bigr).$$

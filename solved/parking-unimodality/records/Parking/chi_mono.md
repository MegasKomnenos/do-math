---
weight: step
short: (1+1/i)^i is nondecreasing
---
## Description

The sequence $(1 + 1/i)^i$ is nondecreasing in $i \ge 1$.

## Statement

For all natural numbers $1 \le i \le j$,

$$\Bigl(1 + \frac{1}{i}\Bigr)^{i} \le \Bigl(1 + \frac{1}{j}\Bigr)^{j}.$$

## Explanation

This is the classical fact that the sequence $(1+1/i)^i$, whose limit is $e$, increases. The library needs only the weak inequality. It is used for the monotonicity of the companion sequence $(1+1/i)^{i-1}$ (`Parking.psi_mono`), which is the ratio of consecutive Cayley coefficients (`Parking.cay_ratio`), and in several comparisons of ratios of the sequences $c_n = (n+1)^{n-1}/n!$ and $\varepsilon_m = (m-1)^{m-1}/m!$ further on, for instance in the monotonicity of the step ratio of $\varepsilon$ (`Parking.gs_mono`).

## Proof

By induction on $j$ it suffices to prove one step: $(1+1/i)^i \le (1+1/(i+1))^{i+1}$ for $i \ge 1$.

The two bases are related by

$$1 + \frac{1}{i+1} = \Bigl(1 + \frac{1}{i}\Bigr)\Bigl(1 - \frac{1}{(i+1)^2}\Bigr),$$

which is checked by clearing denominators. Bernoulli's inequality $(1+u)^{m} \ge 1 + m u$ for $u \ge -1$, applied with $u = -1/(i+1)^2$ and $m = i+1$, gives

$$\Bigl(1 - \frac{1}{(i+1)^2}\Bigr)^{i+1} \ge 1 - \frac{1}{i+1} = \frac{i}{i+1}.$$

Hence

$$\Bigl(1 + \frac{1}{i+1}\Bigr)^{i+1} = \Bigl(1 + \frac{1}{i}\Bigr)^{i+1}\Bigl(1 - \frac{1}{(i+1)^2}\Bigr)^{i+1} \ge \Bigl(1 + \frac{1}{i}\Bigr)^{i} \cdot \Bigl(1 + \frac{1}{i}\Bigr)\frac{i}{i+1} = \Bigl(1 + \frac{1}{i}\Bigr)^{i},$$

because $(1 + 1/i) \cdot i/(i+1) = 1$.

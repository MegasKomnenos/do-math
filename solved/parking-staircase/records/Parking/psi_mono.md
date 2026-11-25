---
weight: step
short: (1+1/i)^(i-1) is nondecreasing
---
## Description

The sequence $(1 + 1/i)^{i-1}$ is nondecreasing in $i \ge 1$.

## Statement

For all natural numbers $1 \le i \le j$,

$$\Bigl(1 + \frac{1}{i}\Bigr)^{i-1} \le \Bigl(1 + \frac{1}{j}\Bigr)^{j-1}.$$

## Explanation

The number $\psi(i) = (1+1/i)^{i-1}$ is the ratio $a_{i+1}/a_i$ of consecutive Cayley coefficients $a_j = j^{j-1}/j!$ (`Parking.cay_ratio`). That this ratio does not decrease is the log-convexity of the Cayley coefficients (`Parking.cay_logconvex`). The same monotonicity gives the behaviour of the tilted sequence $c_n x^n$, $c_n = a_{n+1}$, at the critical tilt $x = 1/\psi(k)$: the ratio of its consecutive terms, $c_{n+1}x^{n+1}/(c_n x^n) = x\,\psi(n+1)$, is at most $1$ for $n + 1 \le k$ and at least $1$ for $n + 1 \ge k$ (`Parking.ccT_succ_le`, `Parking.ccT_le_succ`). It also gives the monotonicity of $\gamma_k = (1+1/k)^{k-2}$ (`Parking.gam_mono`).

Both sequences $(1+1/i)^{i}$ and $(1+1/i)^{i-1}$ increase to $e$; the first is treated in `Parking.chi_mono`, from which the present statement is derived.

## Proof

By induction on $j$ it suffices to prove one step, $(1+1/i)^{i-1} \le (1+1/(i+1))^{i}$ for $i \ge 1$. The proof of `Parking.chi_mono` contains the inequality $(1+1/i)^{i} \le (1+1/(i+1))^{i+1}$ for $i \ge 1$ (it is its one-step case). Hence

$$\Bigl(1 + \frac{1}{i}\Bigr)^{i-1}\Bigl(1 + \frac{1}{i}\Bigr) = \Bigl(1 + \frac{1}{i}\Bigr)^{i} \le \Bigl(1 + \frac{1}{i+1}\Bigr)^{i+1} = \Bigl(1 + \frac{1}{i+1}\Bigr)^{i}\Bigl(1 + \frac{1}{i+1}\Bigr) \le \Bigl(1 + \frac{1}{i+1}\Bigr)^{i}\Bigl(1 + \frac{1}{i}\Bigr),$$

where the last step uses $1 + 1/(i+1) \le 1 + 1/i$. Dividing by the positive number $1 + 1/i$ gives the step.

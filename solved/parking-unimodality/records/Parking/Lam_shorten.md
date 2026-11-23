---
weight: unit
short: shortening a chain sum by one
---
## Description

With $N = k + r + 1$ and $\mu_-$ the mean number of cuts under the homogeneous law with parameter $(k-1)/(k+r)$ on the compositions of $r$, the chain sums satisfy $\Lambda_{r+1}(k-1;N) \le (1+1/r)^r\,\bigl(1 - \mu_-/(2(k-1))\bigr)\,\Lambda_r(k;N)$.

## Statement

Let $k \ge 2$ and $r \ge 1$ be natural numbers, and put $N = k + r + 1$, $h_- = (k-1)/(k+r)$ and $\mu_- = \mu_r(h_-)$. Then

$$\Lambda_{r+1}(k-1;N) \ \le\ \Bigl(1 + \frac1r\Bigr)^{r}\Bigl(1 - \frac{\mu_-}{2(k-1)}\Bigr)\,\Lambda_r(k;N).$$

Here $\Lambda_m(y;N)$ is the chain sum, the total weight of the compositions of $m$ for the threshold profile $s \mapsto y/(N-s)$ (`Parking.Lam`, `Parking.thr`), and $\mu_r(h)$ is the mean number of cuts of a composition of $r$ under the homogeneous law with parameter $h$ (`Parking.muh`).

## Explanation

The statement bounds the boundary term $B_- = (a_k/k)\,\Lambda_{r+1}(k-1;N)$ of column $k$ in `Parking.dq_frozen` from above by a multiple of the chain sum $\Lambda_r(k;N)$. The boundary term of column $k+1$ is bounded from below by a multiple of the same chain sum in `Parking.Lam_raise`, and `Parking.step_neg_of_Gfun` compares the two multiples.

The bound has two factors. The factor $(1+1/r)^r$, which is less than $e$, is the growth of the total of the homogeneous model from the length $r$ to the length $r + 1$ at $h = 1$. The factor $1 - \mu_-/(2(k-1))$ is the gain that comes from $h_- < 1$. `Parking.tau_succ_le` supplies both factors, the second in the form $1 - \frac{1-h}{2h(r+1)}\,\mu_r(h)$, which equals $1$ at $h = 1$ and is the smaller the larger the mean number of cuts is. The constant $1/(2(k-1))$ is the value of $(1-h)/(2h(r+1))$ at $h = h_-$.

## Proof

Put $h = h_-$; then $0 < h \le 1$. By `Parking.Lam_first_cell`,

$$\Lambda_{r+1}(k-1;N)\,\tau_r(h) \le \tau_{r+1}(h)\,\Lambda_r(k;N),$$

with the totals $\tau_m(h)$ of the homogeneous model (`Parking.tau`). By `Parking.tau_succ_le`,

$$\tau_{r+1}(h) \le \Bigl(1+\frac1r\Bigr)^{r}\Bigl(1 - \frac{1-h}{2h(r+1)}\,\mu_r(h)\Bigr)\tau_r(h).$$

For $h = (k-1)/(k+r)$ we have $1 - h = (r+1)/(k+r)$ and $2h(r+1) = 2(k-1)(r+1)/(k+r)$, so $(1-h)/(2h(r+1)) = 1/(2(k-1))$. Multiplying the second inequality by $\Lambda_r(k;N) > 0$ (`Parking.Lam_thr_pos`) and combining it with the first gives

$$\Lambda_{r+1}(k-1;N)\,\tau_r(h) \le \Bigl(1+\frac1r\Bigr)^{r}\Bigl(1 - \frac{\mu_-}{2(k-1)}\Bigr)\Lambda_r(k;N)\,\tau_r(h),$$

and $\tau_r(h) > 0$ (`Parking.tau_pos`) can be cancelled.

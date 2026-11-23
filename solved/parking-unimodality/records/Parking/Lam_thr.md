---
weight: step
short: the chain sum as a polynomial in the threshold
---
## Description

For the threshold profile the total weight of the compositions of $m$ is a polynomial in the threshold: $\Lambda_m(y;N) = \sum_{q=1}^{m} y^{q-1}\, V_q(m;\lambda^{1,N})$.

## Statement

For all real numbers $y$ and $N$ and every natural number $m$,

$$\Lambda_m(y;N) = \sum_{q=1}^{m} y^{q-1}\, V_q(m;\lambda^{1,N}),$$

where $\Lambda_m(y;N) = \Lambda_m[\lambda^{y,N}]$ is the total weight of the compositions of $m$ (`Parking.Lam`) for the threshold profile $\lambda^{y,N}(s) = y/(N-s)$ (`Parking.thr`), and $V_q(m;f)$ is the weight of the compositions with $q$ parts (`Parking.Vc`).

## Explanation

The chain sum $\Lambda_m(y;N)$ depends on the threshold $y$ only through one factor $y$ for each cut. The statement therefore displays it as a polynomial in $y$ of degree at most $m - 1$ whose coefficients $V_q(m;\lambda^{1,N})$ depend on $m$ and $N$ only and are nonnegative when $m \le N$. Two proofs use this form. In `Parking.curv_ratio` it turns the frozen polynomial into an explicit polynomial in $y$ with nonnegative coefficients. In `Parking.Lam_raise` it shows that passing from the threshold $k$ to $k+2$ multiplies the term of $q$ parts by $(1+2/k)^{q-1}$.

## Proof

By `Parking.Vc_thr`, $V_q(m;\lambda^{y,N}) = y^{q-1} V_q(m;\lambda^{1,N})$ for every $q$; summing over $1 \le q \le m$ gives the statement.

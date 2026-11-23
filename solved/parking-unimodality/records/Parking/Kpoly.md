---
weight: unit
short: frozen polynomial
---
## Description

The frozen polynomial $K_{n,k}(y)$ of the position $(n,k)$: a polynomial in the threshold $y$, defined as a combination of chain sums, whose values at $y = k$ and $y = k+1$ are the normalised numbers of parking functions of length $n \le 2k+1$ with all displacements less than $k$ and less than $k+1$.

## Statement

For natural numbers $k$ and $n$ and a real number $y$, with $N = n + 1$,

$$K_{n,k}(y) = \kappa_k(N) + \sum_{m=1}^{n-k} \frac{\kappa_k(N-m)}{N-m}\; y\; \Lambda_m(y;N).$$

Here $\kappa_k(t) = a_t - \sum_{k<i<t} a_i a_{t-i}$ with $a_j = j^{j-1}/j!$ (`Parking.kap`, `Parking.cay`), and $\Lambda_m(y;N)$ is the chain sum: the total weight of the compositions of $m$ in which a part of size $p$ weighs $a_p$ and a cut at the position $s$ weighs $y/(N-s)$ (`Parking.Lam` for the threshold profile `Parking.thr`). The sum is empty when $n \le k$.

## Explanation

**Where the definition comes from.** Let $z^{(y)}_n = A(n,y-1)/n!$ be the number of parking functions of length $n$ with all displacements less than $y$, divided by $n!$ (`Parking.zr`). The last-car recursion makes $z^{(y)}$ the solution of a quadratic recursion with the weight $\min(t,y)$ (`Parking.zr_isWSol`). For the two thresholds $y = k$ and $y = k+1$ this weight is $t$ for $t \le k$ and $y$ for $t > k$. In the rows $n \le 2k+1$, the single-chain range, the single-chain formula `Parking.IsWSol.fwd` replaces the quadratic recursion by a linear one. Written for $u(M) = z^{(y)}_{M-1}$ in the size coordinate $M = n + 1$ it reads

$$u(M) = \kappa_k(M) + \sum_{k < t < M} a_{M-t}\, \frac{y}{t}\, u(t), \qquad 1 \le M \le 2k+2.$$

This is a Volterra equation, and the threshold occurs in it only as the explicit factor $y$: the term $\kappa_k(M)$ and the kernel $a_{M-t}/t$ depend on $k$ alone. Solving the equation by iteration expresses $u(N)$ as a sum over decreasing chains of sizes $N > t_1 > \dots > t_j > k$,

$$u(N) = \kappa_k(N) + \sum_{j \ge 1}\ \sum_{N > t_1 > \dots > t_j > k} a_{N-t_1}\,\frac{y}{t_1}\; a_{t_1-t_2}\,\frac{y}{t_2} \cdots a_{t_{j-1}-t_j}\,\frac{y}{t_j}\; \kappa_k(t_j).$$

Put $m = N - t_j$ and $s_i = N - t_i$. The jumps $N - t_1, t_1 - t_2, \dots, t_{j-1} - t_j$ are the parts of a composition of $m$, the points $s_1 < \dots < s_{j-1}$ are its cut points, and the size $t_i = N - s_i$ visited at a cut contributes $y/(N - s_i)$, the threshold profile. The last size contributes $(y/t_j)\,\kappa_k(t_j) = y\,\kappa_k(N-m)/(N-m)$. Summing over the chains with a given $m$ gives $y\,\Lambda_m(y;N)\,\kappa_k(N-m)/(N-m)$, and $m$ runs from $1$ to $N - k - 1 = n - k$. This is the definition. That $z^{(k)}_n = K_{n,k}(k)$ and $z^{(k+1)}_n = K_{n,k}(k+1)$ for $n \le 2k+1$ is proved inside `Parking.dq_frozen`.

**Why it is called frozen.** For a fixed column $k$ the right-hand side of the Volterra equation makes sense for every real $y$, and it corresponds to the weight that is $t$ for sizes $t \le k$ and $y$ for sizes $t > k$: the size $k$ at which the weight stops growing is frozen, while the value $y$ at which it stops is left free. The count $z^{(y)}_n$ of a threshold $y$ other than $k$ and $k+1$ belongs to the weight $\min(t,y)$, whose switching point moves with $y$, and it is in general not $K_{n,k}(y)$. The library proves the identification only for $y \in \{k, k+1\}$, which is all it uses; for the neighbouring thresholds $k-1$ and $k+2$ the difference is an explicit boundary term (`Parking.dq_frozen`).

**What is gained.** Two consecutive thresholds are two values of one function of a real variable. That function is a polynomial in $y$ of degree at most $n - k$, because $\Lambda_m(y;N)$ is a polynomial of degree at most $m - 1$ (`Parking.Lam_thr`). For $n \le 2k-1$ its coefficients are nonnegative, because $\kappa_k(t) > 0$ in the range that occurs (`Parking.kap_pos`) and the weights of the compositions are nonnegative. Differences of the counts in the threshold thereby become differences of a polynomial with nonnegative coefficients, to which calculus applies (`Parking.curv_ratio`).

In Lean the definition is `Kpoly k n y`. It carries the same normalisation by $n!$ as `zr`. The upper limit $n - k$ is a natural-number subtraction, so for $n \le k$ the sum is empty and $K_{n,k}(y) = \kappa_k(n+1) = a_{n+1}$.

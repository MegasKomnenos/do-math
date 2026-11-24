---
weight: unit
short: the steps of two consecutive columns as curvature minus boundary
---
## Description

At a first-layer position $n = k + r$, $1 \le r \le k-1$, the normalised steps of the columns $k$ and $k+1$ in the row $n$ are each a second difference of the frozen polynomial $K_{n,k}$ minus a multiple of a chain sum: $d_{n,k}/n! = C_- - B_-$ and $d_{n,k+1}/n! = C_+ - B_+$.

## Statement

Let $k \ge 2$ and $1 \le r \le k - 1$ be natural numbers, and put $n = k + r$, $N = n + 1$ and $K = K_{n,k}$, the frozen polynomial of `Parking.Kpoly`. Let $\delta^{(j)}_n = \bigl(b(n,j) - b(n,j-1)\bigr)/n!$ be the normalised step of column $j$ in the row $n$ (`Parking.dq`), where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$. Then

$$\delta^{(k)}_n = \bigl(K(k+1) - 2K(k) + K(k-1)\bigr) - \frac{a_k}{k}\,\Lambda_{r+1}(k-1;N),$$

$$\delta^{(k+1)}_n = \bigl(K(k+2) - 2K(k+1) + K(k)\bigr) - \frac{a_{k+1}}{k+1}\,\Lambda_{r}(k+2;N).$$

Here $a_j = j^{j-1}/j!$ (`Parking.cay`) and $\Lambda_m(y;N)$ is the chain sum, the total weight of the compositions of $m$ for the threshold profile $s \mapsto y/(N-s)$ (`Parking.Lam`, `Parking.thr`).

## Explanation

We write $C_- = K(k+1) - 2K(k) + K(k-1)$ and $C_+ = K(k+2) - 2K(k+1) + K(k)$ for the two second differences, the curvatures, and $B_- = (a_k/k)\,\Lambda_{r+1}(k-1;N)$ and $B_+ = (a_{k+1}/(k+1))\,\Lambda_r(k+2;N)$ for the boundary terms.

The step of a column is a second difference in the threshold. With $z^{(y)}_n = A(n,y-1)/n!$, the normalised number of parking functions with all displacements less than $y$ (`Parking.zr`), one has $\delta^{(k)}_n = z^{(k+1)}_n - 2 z^{(k)}_n + z^{(k-1)}_n$. If the three counts were the values at $k+1$, $k$, $k-1$ of one polynomial, the step would be a second difference of that polynomial, a discrete curvature. Two of them are: $z^{(k)}_n = K(k)$ and $z^{(k+1)}_n = K(k+1)$. The third is not, because the threshold $k - 1$ belongs to the frozen polynomial of the column $k - 1$, but the two polynomials differ by an explicit multiple of a chain sum, and at $y = k - 1$ that difference is $B_-$. The step of column $k+1$ is treated with the same polynomial $K = K_{n,k}$: the thresholds $k$ and $k+1$ lie on it and the threshold $k+2$ misses it by $B_+$.

The statement is the bridge between the parking functions and the estimates of the steps in the chain range. Both steps are now differences of a curvature and a positive boundary term (`Parking.Lam_thr_pos`), so that the sign of a step is decided by the comparison of its curvature with its boundary term: $\delta^{(k)}_n \le 0$ says $C_- \le B_-$, and $\delta^{(k+1)}_n > 0$ says $C_+ > B_+$. Each of the two equations is used by itself. `Parking.dq_curv_sub_boundary` writes the curvature $C_-$ of the first equation as a sum over the sizes $m \le r$ of the compositions, and in this form `Parking.diagonal_step_curve` compares the step at the position $(k+r,k)$ with the step one row down and one column to the right. `Parking.dq_pos_of_pair` applies the second equation with the column $k-1$ in the place of $k$, bounds the curvature from below (`Parking.curv_ge_pair`), and so obtains a criterion for a positive step.

The range $1 \le r \le k - 1$ is the chain range $k + 1 \le n \le 2k - 1$ of column $k$. The upper end is forced by the threshold $k - 1$: its count is a value of the frozen polynomial of column $k - 1$ only in the rows $n \le 2(k-1) + 1$. In Lean the statement is the conjunction of the two equations, with `dq k (k + r)` and `dq (k + 1) (k + r)` on the left.

## Proof

The proof has three parts: the Volterra equation and its solution, which identify counts with values of frozen polynomials; the knot identity, which compares the frozen polynomials of two consecutive columns; and the assembly.

**The Volterra equation.** Let $j \ge 1$ and $k \le j \le k + 1$, and let $n \le 2k + 1$. By `Parking.zr_isWSol` the sequence $z^{(j)}$ solves the weighted last-car recursion with the weight $\omega(t) = \min(t,j)$. This weight equals $t$ for $t \le k$, so the single-chain formula `Parking.IsWSol.fwd` applies with the parameter $k$ and gives, with $c_m = (m+1)^{m-1}/m! = a_{m+1}$,

$$c_n - z^{(j)}_n = \sum_{t=k+1}^{n} c_{n-t}\Bigl(c_{t-1} - \frac{\omega(t)}{t}\, z^{(j)}_{t-1}\Bigr).$$

For $t \ge k + 1$ we have $\omega(t) = j$. Writing $c_n = a_{n+1}$, $c_{n-t} = a_{n+1-t}$, $c_{t-1} = a_t$ and collecting the terms without $z$ into $\kappa_k(n+1) = a_{n+1} - \sum_{k<t<n+1} a_t a_{n+1-t}$ (`Parking.kap`), this becomes

$$z^{(j)}_n = \kappa_k(n+1) + \sum_{k<t<n+1} a_{n+1-t}\, \frac{j}{t}\, z^{(j)}_{t-1}.$$

In the size coordinate, $u(M) = z^{(j)}_{M-1}$ satisfies $u(M) = \kappa_k(M) + \sum_{k<t<M} a_{M-t}\,(j/t)\,u(t)$ for $1 \le M \le 2k + 2$.

**The chain expansion.** Let $y$ be real and let $u$ satisfy $u(M) = \kappa(M) + \sum_{k<t<M} a_{M-t}\,(y/t)\,u(t)$ for $1 \le M \le B$, for some sequence $\kappa$. Then for $1 \le M \le B$

$$u(M) = \kappa(M) + \sum_{k<\tau<M} \kappa(\tau)\, \frac{y}{\tau}\, \Lambda_{M-\tau}(y;M).$$

This is proved by strong induction on $M$. Insert the expansion of $u(t)$, $t < M$, into the equation for $u(M)$ and exchange the summations over $t$ and $\tau$. The coefficient of $\kappa(\tau)\,y/\tau$ becomes

$$a_{M-\tau} + \sum_{\tau<t<M} a_{M-t}\, \frac{y}{t}\, \Lambda_{t-\tau}(y;t),$$

and this equals $\Lambda_{M-\tau}(y;M)$. Indeed, the first-part recursion `Parking.Lam_first` for the threshold profile with top size $M$ and for the length $M - \tau$ has, for a first part of size $g$, the term $a_g \cdot y/(M-g) \cdot \Lambda_{M-\tau-g}$ of the shifted profile $s \mapsto y/(M-g-s)$, which is the threshold profile with top size $M - g$. With $t = M - g$ this is the displayed sum.

Applying the expansion to $u(M) = z^{(j)}_{M-1}$ with $y = j$, $B = 2k+2$ and $M = n + 1$, and substituting $\tau = n + 1 - m$, gives the definition of `Parking.Kpoly`:

$$z^{(j)}_n = K_{n,k}(j) \qquad \text{for } j \ge 1,\ k \le j \le k+1,\ n \le 2k+1.$$

**The knot identity.** For $1 \le k \le n$ and every real $y$, with $N = n + 1$,

$$K_{n,k-1}(y) - K_{n,k}(y) = (y - k)\,\frac{a_k}{k}\,\Lambda_{N-k}(y;N).$$

To see this, compare the two definitions term by term. From the definition of $\kappa$ one reads off $\kappa_{k-1}(t) = \kappa_k(t) - a_k a_{t-k}$ for $t > k$ and $\kappa_{k-1}(k) = a_k$. The sum of $K_{n,k-1}$ has one term more than that of $K_{n,k}$, the term $m = N - k$, which is $(a_k/k)\,y\,\Lambda_{N-k}(y;N)$. In the constant term and in the terms $1 \le m \le n - k$ the difference of the two $\kappa$ is $-a_k a_{N-m-k}$, so these terms contribute

$$-a_k\Bigl(a_{N-k} + \sum_{m=1}^{n-k} \Lambda_m(y;N)\,\frac{y}{N-m}\,a_{N-k-m}\Bigr) = -a_k\,\Lambda_{N-k}(y;N),$$

by the last-cut recursion `Parking.Lam_last` for the length $N - k$ and the threshold profile, whose value at the cut $m$ is $y/(N-m)$. The sum of the two contributions is $(y-k)(a_k/k)\,\Lambda_{N-k}(y;N)$. The two polynomials agree at $y = k$, the knot.

**Assembly.** Let $k \ge 2$, $1 \le r \le k-1$, $n = k + r$. The identification of the counts gives four values. With the column $k$: $z^{(k)}_n = K_{n,k}(k)$ and $z^{(k+1)}_n = K_{n,k}(k+1)$, since $n \le 2k+1$. With the column $k-1$ and the level $k-1 \ge 1$: $z^{(k-1)}_n = K_{n,k-1}(k-1)$, since $n \le 2k - 1 = 2(k-1)+1$; this is where $r \le k - 1$ is used. With the column $k+1$ and the level $k+2$: $z^{(k+2)}_n = K_{n,k+1}(k+2)$. The knot identity at the column $k$ and $y = k - 1$, where $N - k = r + 1$, gives

$$K_{n,k-1}(k-1) = K_{n,k}(k-1) - \frac{a_k}{k}\,\Lambda_{r+1}(k-1;N),$$

and at the column $k + 1$ (which requires $k + 1 \le n$, that is $r \ge 1$) and $y = k + 2$, where $N - (k+1) = r$,

$$K_{n,k+1}(k+2) = K_{n,k}(k+2) - \frac{a_{k+1}}{k+1}\,\Lambda_{r}(k+2;N).$$

Finally `Parking.bq_eq` gives $b(n,j)/n! = z^{(j+1)}_n - z^{(j)}_n$ for $j \ge 1$, so $\delta^{(k)}_n = z^{(k+1)}_n - 2z^{(k)}_n + z^{(k-1)}_n$ and $\delta^{(k+1)}_n = z^{(k+2)}_n - 2z^{(k+1)}_n + z^{(k)}_n$. Substituting the four values gives the two equations.

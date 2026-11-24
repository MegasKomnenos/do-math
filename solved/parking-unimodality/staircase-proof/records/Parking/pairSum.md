---
weight: unit
short: pair sum
---
## Description

The pair sum of the position $(k+R-1,\,k)$: $\mathcal{P}(k,R) = \sum_{b=1}^{R} \Lambda^{(1)}_b(k;N)\cdot\frac{k}{N-b}\cdot z^{(k)}_{N-b-1}$ with $N = k+R$, where $\Lambda^{(1)}_b(k;N)$ is the weight of the compositions of $b$ with one marked cut point for the cut factors $k/(N-s)$, and $z^{(k)}_n = A(n,k-1)/n!$ is the environment of the threshold $k$.

## Statement

Let $k \ge 1$ and $R$ be natural numbers and put $N = k + R$. Then

$$\mathcal{P}(k,R) \;=\; \sum_{b=1}^{R} \Lambda^{(1)}_b(k;N)\;\cdot\;\frac{k}{N-b}\;\cdot\; z^{(k)}_{N-b-1}.$$

Here $\Lambda^{(1)}_b(k;N) = \Lambda^{(1)}_b[\lambda^{k,N}]$ is the total weight of the compositions of $b$ with one marked cut point (`Parking.Lam1`) for the threshold profile $\lambda^{k,N}(s) = k/(N-s)$ (`Parking.thr`), and $z^{(k)}_n = A(n,k-1)/n!$ is the number of parking functions of length $n$ with all displacements less than $k$, divided by $n!$ (`Parking.zr`). The Lean definition `pairSum k R` is also defined for $k = 0$, where every term contains the factor $0/(N-b)$ and the value is $0$.

## Explanation

**The form with two marked points.** Unfolding the definition of $\Lambda^{(1)}$, and using that the profile $\lambda^{k,N}$ shifted by $a$ is the threshold profile $\lambda^{k,N-a}$, the pair sum is

$$\mathcal{P}(k,R) = \sum_{1 \le a < b \le R} \Lambda_a(k;N)\;\frac{k}{N-a}\;\Lambda_{b-a}(k;N-a)\;\frac{k}{N-b}\; z^{(k)}_{N-b-1},$$

where $\Lambda_m(y;N)$ is the chain sum, the total weight of the compositions of $m$ for the profile $s \mapsto y/(N-s)$ (`Parking.Lam`). It is a sum over pairs $a < b$ of marked points, which is the reason for the name.

**What it counts.** Put $n = k + R - 1$, so that $N = n + 1$ and the position $(n,k)$ has the deficit $n - k = R - 1$. By `Parking.dq_frozen` the normalised step of column $k$ in the row $n$ is a curvature term minus a boundary term, and the curvature term is the second difference at $y = k$ of the frozen polynomial $K_{n,k-1}(y)$ (`Parking.Kpoly`).

As the record of `Parking.Kpoly` explains, the frozen polynomial is a sum over decreasing chains of sizes $N > t_1 > \dots > t_j \ge k$, in which every size that the chain visits contributes one factor $y/t_i$. A chain that visits $j$ sizes therefore contributes to the coefficient of $y^j$. The second difference of $y^j$ at $y = k$, multiplied by $k^2$, is at least $j(j-1)\,k^j$, and $j(j-1)$ is twice the number of pairs of visited sizes. So $k^2$ times the curvature term is at least twice a sum over the chains with two marked visited sizes, each chain taken with its weight at $y = k$. The pair sum is this sum.

In the displayed form the two marked sizes are $N - a > N - b$. The factor $\Lambda_a(k;N)$ sums over the part of the chain above the upper marked size, and $k/(N-a)$ is the factor of that size. The factor $\Lambda_{b-a}(k;N-a)$ sums over the part between the two marked sizes, and $k/(N-b)$ is the factor of the lower marked size. The environment $z^{(k)}_{N-b-1}$ sums over everything below the lower marked size; this rests on the fact that in these rows the environment of the threshold $k$ is the value at $y = k$ of a frozen polynomial of the column $k - 1$, which is part of the proof of `Parking.dq_frozen`.

This reading applies in the range $R \le k - 2$ of `Parking.curv_ge_pair`, in which $R \ge 1$ gives $k \ge 3$ and the rows $k \le n \le 2k - 3$. That statement is the inequality just described, $2\,\mathcal{P}(k,R) \le k^2$ times the curvature term. Its proof contains the identity that expresses the regrouping of the chains, and obtains it from two Volterra equations without expanding into chains.

**Why it has this form.** The pair sum is written so that it can be bounded from below. Each of its factors is a positive sum of products of cut factors $k/t \le 1$, that is, of exponentials $e^{-\log(t/k)}$: the two chain sums, to which `Parking.Lam_jensen` applies, and the environment, to which `Parking.zr_jensen` applies. This gives the lower bound `Parking.pairSum_ge`. Organising the sum by the lower marked point $b$, with one marked point above it collected in $\Lambda^{(1)}$, is also the form in which the pair sum is one side of a duality of two Volterra equations (see the proof of `Parking.curv_ge_pair`).

**Where it is used.** The pair sum is the right side of the pair–impulse criterion `Parking.dq_pos_of_pair`: the step at the position $(k+R-1,k)$ is positive as soon as twice the pair sum exceeds $k\, a_k\, \Lambda_R(k+1;N)$ with $a_k = k^{k-1}/k!$, which is $k^2$ times the boundary term of that step.

**The Lean form.** `pairSum k R` is the sum over `Finset.Icc 1 R` of `Lam1 (thr (k : ℝ) ((k : ℝ) + R)) b * thr (k : ℝ) ((k : ℝ) + R) b * zr k (k + R - b - 1)`. The number $N$ is the real number $k + R$. The index $k + R - b - 1$ of the environment is a subtraction of natural numbers, which is exact for $k \ge 1$ and $b \le R$. The term $b = 1$ vanishes, because a composition of $1$ has no cut point. In the term $b = R$ the cut factor is $k/k = 1$.

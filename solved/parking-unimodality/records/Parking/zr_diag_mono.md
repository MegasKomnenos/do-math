---
weight: unit
short: stochastic monotonicity along the diagonal
---
## Description

Stochastic monotonicity along the diagonal: for $y\ge1$ and every $n$, $z^{(y)}_n/c_n\le z^{(y+1)}_{n+1}/c_{n+1}$; that is, the probability that a uniform parking function of length $n$ has maximum displacement below $y$ does not decrease when $n$ and $y$ are both raised by one.

## Statement

For all natural numbers $y\ge1$ and $n$,
$$\frac{z^{(y)}_n}{c_n}\;\le\;\frac{z^{(y+1)}_{n+1}}{c_{n+1}},$$
where $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`) and $c_n=(n+1)^{n-1}/n!$ (`Parking.cc`).

## Explanation

**What it says.** Write $F^{y}_n=z^{(y)}_n/c_n=A(n,y-1)/(n+1)^{n-1}$. Since $(n+1)^{n-1}$ is the number of parking functions of length $n$ (the classical count; see the record of `Parking.zr` for how it stands in the library), $F^y_n$ is the probability $\Pr(M_n<y)$ that the maximum displacement $M_n$ of a uniformly chosen parking function of length $n$ is smaller than $y$. The statement is $\Pr(M_n<y)\le\Pr(M_{n+1}<y+1)$: one more car can push the maximum displacement up, but allowing one more unit of displacement more than compensates. In the array of the probabilities $F^y_n$ it is a monotonicity along the diagonals $(n,y)\to(n+1,y+1)$. In the free range $n\le y$ both sides are $1$.

**Why it holds.** Divide the recursion of `Parking.zr_isWSol` by $(n+1)c_{n+1}$:
$$F^y_{n+1}=\sum_{j=0}^{n}q_n(j)\,G^y_n(j),\qquad q_n(j)=\frac{(j+1)\,c_j\,c_{n-j}}{(n+1)\,c_{n+1}},\qquad G^y_n(j)=\frac{\min(j+1,y)}{j+1}\,F^y_j\,F^y_{n-j}.$$
The numbers $q_n(0),\dots,q_n(n)$ are positive and sum to $1$ (`Parking.cc_rec`): $q_n$ is the law of the spot $j$ that the last of $n+1$ cars takes in a uniform parking function, and $G^y_n(j)$ is the probability, given that spot, that all displacements are below $y$, a product over the last car, the $j$ cars on its left and the $n-j$ cars on its right. Passing from $n+1$ cars with threshold $y$ to $n+2$ cars with threshold $y+1$ changes both the law and the values. The values compare in two ways: $G^y_n(j)\le G^{y+1}_{n+1}(j)$, where the right part has grown by one car, and $G^y_n(j)\le G^{y+1}_{n+1}(j+1)$, where the left part has grown by one car; in each case the part that has grown is compared by the statement itself for a shorter street, and the other part by the monotonicity in the threshold. The laws compare correspondingly: $q_{n+1}(j)\le q_n(j)$ and $q_{n+1}(j+1)\le q_n(j)$, which means that the mass that $q_n$ puts on $j$ can be divided between the points $j$ and $j+1$ so as to produce $q_{n+1}$. An Abel summation turns these four comparisons into the inequality between the two averages.

**What it is used for.** It is the input from which the diagonal lower bound $\gamma_k\beta^{(k-1)}_{n-1}\le\beta^{(k)}_n$ is derived (`Parking.bq_diag_lower`), it enters the proof of the crossing criterion (`Parking.cross_criterion`), and, multiplied by the powers of the critical tilt, it is used in the weighted arguments of the left half (`Parking.DeltaId_nonneg`, `Parking.weighted_debt`).

**The Lean form.** The statement is written with the two quotients `zr y n / cc n` and `zr (y + 1) (n + 1) / cc (n + 1)`; the denominators are positive (`Parking.cc_pos`).

## Proof

Write $F^y_m=z^{(y)}_m/c_m$, and define $q_n(j)$ and $G^y_n(j)$ for $0\le j\le n$ as in the explanation. All $c_m$ are positive (`Parking.cc_pos`) and all $z^{(y)}_m$ are nonnegative (`Parking.zr_nonneg`), so $F^y_m\ge0$. The proof is a strong induction on $n$, for all $y\ge1$ at once, and it uses the following four facts, which are private lemmas of the module.

**(A) The normalised recursion.** For $y\ge1$ and $n\ge0$, $F^y_{n+1}=\sum_{j=0}^{n}q_n(j)\,G^y_n(j)$. Indeed $q_n(j)\,G^y_n(j)=\min(j+1,y)\,z^{(y)}_j\,z^{(y)}_{n-j}/((n+1)c_{n+1})$, and by `Parking.zr_isWSol` the sum of the numerators over $j$ is $(n+1)\,z^{(y)}_{n+1}$.

**(B) The weights sum to one.** $\sum_{j=0}^{n}q_n(j)=1$, by `Parking.cc_rec`: $(n+1)c_{n+1}=\sum_{j\le n}(j+1)c_jc_{n-j}$.

**(C) The weights interlace.** For $j\le n$: $q_{n+1}(j)\le q_n(j)$ and $q_{n+1}(j+1)\le q_n(j)$.

For the first inequality, after cancelling $(j+1)c_j$ and clearing the positive denominators, it is to be shown that $(n+1)\,c_{n+1-j}\,c_{n+1}\le(n+2)\,c_{n-j}\,c_{n+2}$. This follows from $n+1\le n+2$ and the log-convexity of the Cayley numbers, $c_{n-j+1}\,c_{n+1}\le c_{n-j}\,c_{n+2}$, which is `Parking.cay_logconvex` ($a_{u+1}a_v\le a_ua_{v+1}$ for $1\le u\le v$) with $u=n-j+1$, $v=n+2$ and $c_m=a_{m+1}$.

For the second inequality, after cancelling $c_{n-j}$ and clearing denominators, it is to be shown that
$$(j+2)\,c_{j+1}\cdot(n+1)\,c_{n+1}\;\le\;(j+1)\,c_j\cdot(n+2)\,c_{n+2}.$$
Put $\psi_i=(1+1/i)^{i-1}$ and $\chi_i=(1+1/i)^{i}$ for $i\ge1$. Then $c_i=\psi_i\,c_{i-1}$ (`Parking.cay_ratio`), and $(i+1)\,\psi_i=i\,\chi_i$, because $i(1+1/i)=i+1$. Hence $(j+2)\,c_{j+1}=(j+2)\,\psi_{j+1}\,c_j=(j+1)\,\chi_{j+1}\,c_j$, and
$$(j+1)\chi_{j+1}c_j\cdot(n+1)c_{n+1}\le(j+1)c_j\cdot(n+1)\chi_{n+1}c_{n+1}=(j+1)c_j\cdot(n+2)\psi_{n+1}c_{n+1}\le(j+1)c_j\cdot(n+2)\psi_{n+2}c_{n+1},$$
where the first step is $\chi_{j+1}\le\chi_{n+1}$ (`Parking.chi_mono`, as $j\le n$) and the last is $\psi_{n+1}\le\psi_{n+2}$ (`Parking.psi_mono`). The right-hand side is $(j+1)c_j\cdot(n+2)c_{n+2}$.

**(D) The coupling lemma.** Let $m\ge0$, and let $q(0),\dots,q(m)$, $q'(0),\dots,q'(m-1)$, $G(0),\dots,G(m)$, $G'(0),\dots,G'(m-1)$ be real numbers such that $\sum_{j\le m}q(j)=\sum_{j<m}q'(j)$ and, for every $j<m$,
$$q(j)\le q'(j),\qquad q(j+1)\le q'(j),\qquad G'(j)\le G(j),\qquad G'(j)\le G(j+1).$$
Then $\sum_{j<m}q'(j)\,G'(j)\le\sum_{j\le m}q(j)\,G(j)$.

To prove it, write $Q(t)=\sum_{j<t}q(j)$ and $Q'(t)=\sum_{j<t}q'(j)$. For $t\le m$ we have $Q(t)\le Q'(t)$, by the first comparison term by term, and $Q'(t)\le Q(t+1)$: the second comparison gives $Q'(m)-Q'(t)=\sum_{t\le j<m}q'(j)\ge\sum_{t\le j<m}q(j+1)=Q(m+1)-Q(t+1)$, and $Q'(m)=Q(m+1)$ by the hypothesis on the total masses. So the partial sums interlace, $Q(t)\le Q'(t)\le Q(t+1)$. We show by induction on $t\le m$ that
$$\sum_{j<t}q'(j)\,G'(j)\;\le\;\sum_{j<t}q(j)\,G(j)+\bigl(Q'(t)-Q(t)\bigr)\,G(t).$$
For $t=0$ both sides are $0$. For the step from $t$ to $t+1\le m$, split $q'(t)=\bigl(Q(t+1)-Q'(t)\bigr)+\bigl(Q'(t+1)-Q(t+1)\bigr)$ into two nonnegative parts and use $G'(t)\le G(t)$ on the first and $G'(t)\le G(t+1)$ on the second:
$$q'(t)\,G'(t)\le\bigl(Q(t+1)-Q'(t)\bigr)G(t)+\bigl(Q'(t+1)-Q(t+1)\bigr)G(t+1).$$
Adding the induction hypothesis, the terms with $G(t)$ combine to $\bigl(Q(t+1)-Q(t)\bigr)G(t)=q(t)\,G(t)$, which gives the inequality for $t+1$. For $t=m$ the remainder is $\bigl(Q'(m)-Q(m)\bigr)G(m)=\bigl(Q(m+1)-Q(m)\bigr)G(m)=q(m)\,G(m)$, and the inequality is the claim. No sign condition on the $q$, $q'$, $G$, $G'$ is needed.

**The induction.** For $n=0$: $z^{(y)}_0=c_0$ and $z^{(y+1)}_1=c_1$ by `Parking.zr_eq_cc`, since $0\le y$ and $1\le y+1$; both sides are $1$.

Let $n=N+1$ and suppose that $F^{y'}_m\le F^{y'+1}_{m+1}$ for all $m\le N$ and all $y'\ge1$. By (A), $F^y_{N+1}=\sum_{j\le N}q_N(j)\,G^y_N(j)$ and $F^{y+1}_{N+2}=\sum_{j\le N+1}q_{N+1}(j)\,G^{y+1}_{N+1}(j)$. Apply (D) with $m=N+1$, $q=q_{N+1}$, $q'=q_N$, $G=G^{y+1}_{N+1}$ and $G'=G^y_N$. The total masses are both $1$ by (B), and the two comparisons of the weights are (C). It remains to compare the values, for $j\le N$. Each value is a product of three nonnegative factors, and the factors are compared one by one.

- $G^y_N(j)\le G^{y+1}_{N+1}(j)=\frac{\min(j+1,y+1)}{j+1}F^{y+1}_j\,F^{y+1}_{N+1-j}$: we have $\min(j+1,y)\le\min(j+1,y+1)$; $F^y_j\le F^{y+1}_j$ by `Parking.zr_mono`; and $F^y_{N-j}\le F^{y+1}_{N-j+1}$ by the induction hypothesis at the index $N-j\le N$.
- $G^y_N(j)\le G^{y+1}_{N+1}(j+1)=\frac{\min(j+2,y+1)}{j+2}F^{y+1}_{j+1}\,F^{y+1}_{N-j}$: with $M=\min(j+1,y)\le j+1$ we have $\min(j+2,y+1)=M+1$ and $\frac{M}{j+1}\le\frac{M+1}{j+2}$; $F^y_j\le F^{y+1}_{j+1}$ by the induction hypothesis at the index $j\le N$; and $F^y_{N-j}\le F^{y+1}_{N-j}$ by `Parking.zr_mono`.

So (D) gives $F^y_{N+1}\le F^{y+1}_{N+2}$, which is the statement for $n=N+1$.

---
weight: unit
short: the steps beyond the first layer are positive, except at eleven positions
---
## Description

For every column $k\ge1$ and every row $n\ge2k$: $b(n,k-1)<b(n,k)$, except at the eleven positions $(n,k)=(2k,k)$ with $k\le7$ and $(2k+1,k)$ with $2\le k\le5$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k\ge1$ and $n\ge2k$ be natural numbers, and suppose that neither $n=2k$ and $k\le7$, nor $n=2k+1$ and $2\le k\le5$. Then
$$b(n,k-1)<b(n,k).$$

The positions $(n,k)$ excluded by the supposition are the eleven positions $(2,1),(4,2),(6,3),(8,4),(10,5),(12,6),(14,7)$ and $(5,2),(7,3),(9,4),(11,5)$.

## Explanation

**What the statement says.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The first layer of the column $k$ consists of the rows $k+1\le n\le2k-1$ (also called the chain range of the column), and the rows $n\ge2k$ lie beyond it. The statement gives the sign of every step beyond the first layer with eleven exceptions: it is positive. At ten of the eleven positions, those with $k\ge2$, the step is negative (`Parking.Tab.negative_cells`). The eleventh is $(2,1)$, the one step of the row $2$. There $b(2,0)=2$ and $b(2,1)=1$: of the three parking functions of length $2$, with the preferences $(1,1)$, $(1,2)$, $(2,1)$, only the first displaces a car. The library does not state this sign, and no proof uses it.

**What it is for.** The staircase theorem (`Parking.staircase`) is derived from two rules, the column rule `Parking.column_rule` and the diagonal rule `Parking.diagonal_rule`, and both are settled by the present statement in the region beyond the first layer. The column rule there (`Parking.column_rule_beyond`) has a conclusion that holds without its hypothesis at every position but the eleven, and the diagonal rule there (`Parking.diagonal_rule_beyond`) has a hypothesis that can hold at the eleven positions only. So beyond the first layer the rules are reduced to finitely many signs in the rows up to $15$.

**Why the sign has to be strict.** For unimodality the sign with $\le$ would be enough, but here it does not serve. The staircase theorem asserts that every row increases strictly up to its peak, and the diagonal rule has a step that is not positive as its hypothesis: a single step equal to zero beyond the first layer would satisfy that hypothesis and would have to be followed by a negative step diagonally after it. The content of the statement is therefore that, outside the eleven positions, no step beyond the first layer is zero or negative.

**The three sources.** The proof takes the sign from a different source in each of three groups of columns.

- For $k\ge82$ the sign is `Parking.step_pos_large`, which states the strict inequality for all $n\ge2k$.
- For $2\le k\le81$ the rows below the listed row $n_0(k)$ (`Parking.Tab.n0`) are the cells of the junction table `Parking.Tab.junction_table`, evaluated with $<$, and the rows from $n_0(k)$ on are reached by the strict propagation `Parking.propagate_pos`, which starts from the last cell below $n_0(k)$ and uses the nonnegative sums of the table `Parking.Tab.small_table` at the row $n_0(k)$.
- For $k=1$ the claim is $2A(n,0)<A(n,1)$ for $n\ge3$, where $A(n,l)$ is the number of parking functions of length $n$ with maximum displacement at most $l$; it follows from the last-car recursion by comparing the two levels term by term.

**The Lean form.** The exceptions are a hypothesis, `¬(n = 2 * k ∧ k ≤ 7 ∨ n = 2 * k + 1 ∧ 2 ≤ k ∧ k ≤ 5)`, and the sign is the comparison `b n (k - 1) < b n k` of natural numbers; `k - 1` is exact because $k\ge1$.

## Proof

The proof distinguishes $k=1$, $2\le k\le81$ and $k\ge82$.

**The column $k=1$.** Here $n\ge2$ and $n\ne2$, so $n\ge3$. Let $A(n,l)$ be as above (`Parking.A`). Since $b(n,0)=A(n,0)$ (`Parking.b_zero`) and $b(n,1)+A(n,0)=A(n,1)$ (`Parking.b_succ_add_A`), the claim $b(n,0)<b(n,1)$ is
$$2\,A(n,0)<A(n,1)\qquad(n\ge3).$$
This is proved by induction on $n$.

*The row $3$.* The inequality $2A(3,0)+1\le A(3,1)$ is evaluated by the kernel of the proof assistant: the two numbers are computed as $\operatorname{hd}(0,3)$ and $\operatorname{hd}(1,3)$, by the last-car recursion in natural numbers (`Parking.Tab.hd`), and they are $A(3,0)$ and $A(3,1)$ by `Parking.Tab.hd_eq`. The values are $A(3,0)=6$ and $A(3,1)=13$.

*From $n$ to $n+1$.* The last-car recursion `Parking.A_succ` for the levels $0$ and $1$ reads
$$A(n+1,0)=\sum_{j=0}^{n}\binom nj A(j,0)\,A(n-j,0),\qquad A(n+1,1)=\sum_{j=0}^{n}\min(j+1,2)\binom nj A(j,1)\,A(n-j,1).$$
Compare $2A(n+1,0)$ with $A(n+1,1)$ term by term. For $j\ge1$ the term of the level $1$ carries the factor $\min(j+1,2)=2$, and $A(j,0)\,A(n-j,0)\le A(j,1)\,A(n-j,1)$ by `Parking.A_mono`; so twice the term of the level $0$ is at most the term of the level $1$. For $j=0$ the two terms are $A(n,0)$ and $A(n,1)$, because $A(0,l)=1$ (`Parking.A_zero`), and $2A(n,0)<A(n,1)$ is the induction hypothesis. Adding up gives $2A(n+1,0)<A(n+1,1)$.

**The columns $2\le k\le81$.** Let $n_0=n_0(k)$. By `Parking.Tab.junction_table`, $2k+3\le n_0$, and $b(m,k-1)<b(m,k)$ for every row $2k\le m<n_0$ other than $m=2k$ when $k\le7$ and $m=2k+1$ when $k\le5$.

If $n<n_0$, the row $n$ is one of these rows, since for $k\ge2$ the supposition of the statement excludes exactly the two exceptions, and the claim is the cell.

If $n\ge n_0$, put $m=n_0-1$. Then $m\ge2k+2$, so $m$ is a row of the junction that is not excepted, and $b(m,k-1)<b(m,k)$. In terms of the normalised step $\delta_m=(b(m,k)-b(m,k-1))/m!$ (`Parking.dq`) this is $\delta_m>0$ (`Parking.dq_pos_iff`). Now apply `Parking.propagate_pos` to the column $k$, the row $m\ge k$ and the critical tilt $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`). Its hypotheses hold:

- $0<x_k$ (`Parking.xcrit_pos`), and $x_k<1$, because $0\le k/(k+1)<1$ and the exponent $k-1$ is at least $1$;
- the tilted environment $z^{(k)}_Nx_k^N$, with $z^{(k)}_N=A(N,k-1)/N!$, does not increase in $N$ (`Parking.zrT_anti_crit`);
- the sums $\sum_{t=s}^{n_0}\xi_tx_k^t$ of the tree curvature $\xi$ of the column $k$ (`Parking.xi`) are nonnegative for $k\le s\le n_0$: this is the fourth part of `Parking.Tab.small_table`, and $n_0=m+1$;
- $\delta_m>0$.

The conclusion is $\delta_n>0$ for every $n\ge m$, in particular for the given $n\ge n_0$, and by `Parking.dq_pos_iff` this is $b(n,k-1)<b(n,k)$.

**The columns $k\ge82$.** `Parking.step_pos_large` states $b(n,k-1)<b(n,k)$ for $k\ge82$ and $n\ge2k$.

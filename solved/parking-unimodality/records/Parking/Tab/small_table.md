---
weight: unit
short: the table of the columns 2 to 81
---
## Description

The computed facts about each column $2\le k\le81$ of the numbers $b(n,k)$: a positive step $b(n,k)-b(n,k-1)$ in a row $k+1\le n\le2k-2$ is followed by a positive step in the row $n+1$, the step is nonnegative in the rows $\max(2k,17)\le n<n_0(k)$, and at the row $n_0(k)$ all the sums $\sum_{t=s}^{n_0(k)}\xi_tx_k^t$, $k\le s\le n_0(k)$, are nonnegative.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`) and $A(n,l)$ the number of those with maximum displacement at most $l$ (`Parking.A`). Let $k$ be an integer with $2\le k\le81$, let $n_0=n_0(k)$ be the row listed for the column $k$ (`Parking.Tab.n0`), let $x_k=(k/(k+1))^{k-1}$, and for $t\ge1$ let
$$\xi_t=\frac{1}{t!}\Bigl(\min(t,k+1)\,A(t-1,k)-2\min(t,k)\,A(t-1,k-1)+\min(t,k-1)\,A(t-1,k-2)\Bigr)$$
(`Parking.xi`, for the column $k$). Then:

1. $2k\le n_0$;
2. for every $n$ with $k+1\le n\le2k-2$: if $b(n,k-1)<b(n,k)$, then $b(n+1,k-1)<b(n+1,k)$;
3. for every $n$ with $2k\le n$, $17\le n$ and $n<n_0$: $b(n,k-1)\le b(n,k)$;
4. for every $s$ with $k\le s\le n_0$: $\displaystyle\sum_{t=s}^{n_0}\xi_t\,x_k^{\,t}\ge0$.

## Explanation

**What the four parts are for.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The rows $k+1\le n\le2k-1$ are the chain range of the column $k$. Part 2 is the persistence of the sign in the chain range, `Parking.chain_column`, for the columns $k\le81$: it concerns the rows $n$ for which $n$ and $n+1$ both lie in the chain range; for the columns $k\ge82$ that statement is proved by analysis. Parts 1, 3 and 4 give the left half for the columns $2\le k\le81$ (`Parking.small_columns`): part 3 is the inequality $d_{n,k}\ge0$ in the rows below $n_0$, and part 4 is the hypothesis of the propagation theorem `Parking.propagate` at the critical tilt $x_k$ (`Parking.xcrit`), which, together with the monotonicity of the tilted masses (`Parking.zrT_anti_crit`), gives $d_{n,k}\ge0$ in all the rows $n\ge n_0$. Part 1 is needed there to know that $n_0\ge k$.

**Why a finite table can say something about all rows.** Parts 2 and 3 are finite statements. Part 4 is the device that makes the infinitely many rows $n\ge n_0$ accessible: by `Parking.propagate`, nonnegativity of the suffix sums of the numbers $\xi_tx^t$ at one row is inherited by every later row and implies the sign of the step there. The numbers $\xi_t$ (the tree curvature of the column, `Parking.xi`) involve only the rows $t-1<n_0$ of the three levels $k,k-1,k-2$, and $x_k$ is the rational number $k^{k-1}/(k+1)^{k-1}$, so part 4 is a comparison of integers.

**The row 17.** Part 3 starts at the row $\max(2k,17)$ and not at the row $2k$. The rows $n\le16$ are treated by a table of their own (`Parking.Tab.small_rows`), and for small rows the inequality is false at some positions: for instance $b(5,1)=421>b(5,2)=377$, at the position $(n,k)=(5,2)$ with $n\ge2k$. For $k\le5$ one has $n_0(k)\le15$, so part 3 is empty for these columns. (An exact computation made for this record, outside the library, found that among the positions with $2\le k$ and $2k\le n$ the inequality $b(n,k-1)\le b(n,k)$ fails exactly at $(4,2),(5,2),(6,3),(7,3),(8,4),(9,4),(10,5),(11,5),(12,6),(14,7)$, as far as the rows $n<60$ were examined.)

**The Lean form.** The step is written with natural numbers, `b n (k - 1) < b n k` for $d_{n,k}>0$ and `b n (k - 1) ≤ b n k` for $d_{n,k}\ge0$; `2 * k - 2` and `k - 1` are exact because $k\ge2$. The range of part 3 is written with the two hypotheses `2 * k ≤ n` and `17 ≤ n`. The tilt is written out as `((k : ℝ) / ((k : ℝ) + 1)) ^ (k - 1)`, which is `Parking.xcrit k` unfolded, and the sum of part 4 is a sum of real numbers over `Finset.Icc s (n0 k)`. `Parking.xi k t` is defined through $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`), as $t\,\xi_t=\min(t,k+1)z^{(k+1)}_{t-1}-2\min(t,k)z^{(k)}_{t-1}+\min(t,k-1)z^{(k-1)}_{t-1}$, with $\xi_0=0$; the formula of the statement is this definition with $z^{(y)}_{t-1}=A(t-1,y-1)/(t-1)!$ inserted.

## Proof

The statement is established by an exact computation, which the kernel of the proof assistant performs, and by a proof of what the computation means. Fix a column $k\ge2$, a row $a$, and a row $n_0$.

**What is computed.** For each of the three levels $l=k,k-1,k-2$ the computation builds the list of the numbers $A(n_0-1,l),A(n_0-2,l),\dots,A(0,l)$ by the last-car recursion: it starts from $A(0,l)=1$ and obtains each further row from the rows before it by
$$A(m+1,l)=\sum_{j=0}^{m}\min(j+1,l+1)\binom mjA(j,l)\,A(m-j,l),$$
the binomial coefficients being carried along as a running product with an exact division. That the lists so produced consist of the numbers $A(n,l)$ of `Parking.A` follows from the recursion `Parking.A_succ` and the value `Parking.A_zero`; this is the content of `Parking.Tab.hd_eq`, whose proof establishes it for the whole list. All arithmetic is that of natural numbers of arbitrary size and is exact. (As an indication of the sizes, not a statement of the library: for $k=81$ the Horner values below have more than fourteen thousand decimal digits.)

On the three lists a Boolean value is computed, the conjunction of the comparison $2k\le n_0$ and of three checks. In the checks the step is read from the three levels, by `Parking.d_eq_A`: for $k\ge2$,
$$d_{n,k}=A(n,k)-2A(n,k-1)+A(n,k-2).$$

- *(s1)* For each $n$ with $k+1\le n\le2k-2$: $A(n,k)+A(n,k-2)\le2A(n,k-1)$ or $2A(n+1,k-1)+1\le A(n+1,k)+A(n+1,k-2)$. That is, $d_{n,k}\le0$ or $d_{n+1,k}>0$.
- *(s2)* For each $n$ with $a\le n\le n_0-1$: $2A(n,k-1)\le A(n,k)+A(n,k-2)$. That is, $d_{n,k}\ge0$.
- *(s3)* Put $P=k^{k-1}$, $Q=(k+1)^{k-1}$, and for $1\le t\le n_0$ let $\Xi_t=t!\,\xi_t$, the integer $\min(t,k+1)A(t-1,k)-2\min(t,k)A(t-1,k-1)+\min(t,k-1)A(t-1,k-2)$. With the positive integers $m_{n_0}=1$, $m_{t-1}=m_t\,Q\,t$ (so $m_t=Q^{n_0-t}n_0!/t!$), define $R_{n_0+1}=0$ and $R_t=\Xi_t\,m_t+P\,R_{t+1}$ for $t=n_0,n_0-1,\dots,k$. The check is $R_t\ge0$ for every $t$ with $k\le t\le n_0$. Since $\Xi_t$ can be negative and the computation stays within the natural numbers, $R_t$ is carried as a pair: the part $R_t^{+}$ built from the two terms of $\Xi_t$ with a plus sign and the part $R_t^{-}$ built from the term with the minus sign, each by the same recursion, and the check is $R_t^{-}\le R_t^{+}$.

**What the checks mean.** (s1) and (s2) are, by the identity for $d_{n,k}$, the statements about the steps written next to them; the proof that the Boolean functions test exactly the rows named is an induction along the lists. For (s3), an induction on $t$ downwards from $n_0$ shows
$$R_t\,P^{\,t}=n_0!\,Q^{\,n_0}\sum_{v=t}^{n_0}\xi_v\,x^{v},\qquad x=\frac PQ.$$
Indeed $m_t\,t!=Q^{n_0-t}n_0!$ and $x^tQ^t=P^t$ give $\Xi_t\,m_t\,P^t=\xi_t\,x^t\,n_0!\,Q^{n_0}$, and $P\,R_{t+1}\cdot P^t=R_{t+1}P^{t+1}$ is the sum from $t+1$ on by the induction hypothesis. As $P^t$ and $n_0!\,Q^{n_0}$ are positive, $R_t\ge0$ holds exactly when $\sum_{v=t}^{n_0}\xi_vx^v\ge0$. With $P=k^{k-1}$ and $Q=(k+1)^{k-1}$ the number $x$ is $(k/(k+1))^{k-1}=x_k$.

Together: if the Boolean value computed for $(k,a,n_0)$ is true, then $2k\le n_0$; for the rows $k+1\le n\le2k-2$, $d_{n,k}>0$ implies $d_{n+1,k}>0$; $d_{n,k}\ge0$ for $a\le n<n_0$; and $\sum_{t=s}^{n_0}\xi_tx_k^t\ge0$ for $k\le s\le n_0$.

**The evaluation.** For each column $2\le k\le81$ the Boolean value is formed with $n_0=n_0(k)$ from the list `Parking.Tab.n0tab` and with $a=\max(2k,17)$. The eighty columns are evaluated in nineteen blocks of consecutive columns, $2$–$8$, $9$–$25$, $26$–$35$, $36$–$42$, $43$–$47$, $48$–$51$, $52$–$55$, $56$–$58$, $59$–$61$, $62$–$64$, $65$–$66$, $67$–$68$, $69$–$70$, $71$–$72$, $73$–$74$, $75$–$76$, $77$–$78$, $79$–$80$, $81$; for each block the kernel reduces the conjunction of the values of its columns (`Parking.Tab.allRange`) to true. No compiled code and no external program is involved: the definitions are part of the Lean source, the evaluation is a step of the type checking of that source, and it is repeated whenever the module is compiled. `Parking.Tab.allRange_sound` gives the value true for each column of a block, and `Parking.Tab.glue` joins the nineteen ranges to $2\le k<82$.

**Conclusion.** For $2\le k\le81$ the value computed for $(k,\max(2k,17),n_0(k))$ is true, so the four facts of the previous paragraph hold with $a=\max(2k,17)$. The condition $\max(2k,17)\le n$ is the conjunction of $2k\le n$ and $17\le n$, which gives part 3 in the form stated.

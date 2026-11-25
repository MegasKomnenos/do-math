---
weight: unit
short: persistence of the sign in the first layer
---
## Description

For $k\ge2$ and $k+1\le n\le2k-2$: if $b(n,k-1)<b(n,k)$, then $b(n+1,k-1)<b(n+1,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$. A positive step in a row of the first layer of a column is followed by a positive step in the next row of that layer.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k\ge2$ and $n$ be natural numbers with $k+1\le n\le2k-2$. If $b(n,k-1)<b(n,k)$, then $b(n+1,k-1)<b(n+1,k)$.

## Explanation

**What the statement says.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The rows $k+1\le n\le2k-1$ are the *first layer* of the column $k$ (some records call them the chain range of the column). The statement is $d_{n,k}>0\Rightarrow d_{n+1,k}>0$ for two consecutive rows of the first layer: once the step of a column is positive in a row of its first layer, it is positive in the next row of the layer. The condition $n\le2k-2$ keeps the row $n+1$ inside the layer. The passage from the last row $2k-1$ of the layer to the row $2k$ is not part of this statement; it belongs to `Parking.column_rule_beyond`. The statement starts from a positive step. It says nothing about a step that is zero or negative.

**What it is used for.** It is the column rule `Parking.column_rule` in the case in which the conclusion of that rule lies in the first layer of the column. Applied repeatedly it gives `Parking.step_persists_iter`, which is the form in which the diagonal rule `Parking.diagonal_rule` uses persistence.

**Why it does not follow from the recursion along the column alone.** In the rows of the first layer the normalised step $\delta_n=d_{n,k}/n!$ of the column satisfies the column equation `Parking.dq_col`,
$$\delta_n=\frac{k+1}{n}\,\delta_{n-1}+\frac2n\,\beta^{(k-1)}_{n-1}+\sum_{m=1}^{n-k}\varepsilon_m\,\delta_{n-m},\qquad\beta^{(k-1)}_{n-1}=\frac{b(n-1,k-1)}{(n-1)!},\quad\varepsilon_m=\frac{(m-1)^{m-1}}{m!}.$$
The step of a row is thus the sum of a multiple of the step of the row before, of a source term that is not negative, and of a feedback of all the earlier rows down to the row $k$, with weights that are not negative. When the step of the row before is positive, the first two terms are not negative. The feedback, however, contains the rows above the first row in which the column is positive, beginning with the row $k$, where $\delta_k=-a_k/k<0$ with $a_k=k^{k-1}/k!$ (`Parking.dq_base`). The steps of those rows are not positive, and they stay in the sum in every later row of the layer. So the equation does not by itself pass the positive sign to the next row. The content of the statement is that the positive terms outweigh this feedback throughout the layer.

**The two groups of columns.** For $2\le k\le81$ the statement is one of the facts established by the exact computation of these columns (`Parking.Tab.small_table`). For $k\ge82$ it follows from the single change of sign in the first layer (`Parking.one_sign_change`), which rests on an early positive row of the column (`Parking.positive_row_early`) and on the analytic statement `Parking.persist`. The division at the column $82$ is that of `Parking.persist`: its estimates hold from that column on, as its record explains, and the table covers the columns below it.

**The Lean form.** The statement is `(k n : ℕ) (hk : 2 ≤ k) (hn1 : k + 1 ≤ n) (hn2 : n ≤ 2 * k - 2) (h : b n (k - 1) < b n k) : b (n + 1) (k - 1) < b (n + 1) k`. The sign of a step is written as a comparison of the two natural numbers, so no difference of counts is formed; the proof passes to the real number $\delta_n$ (`Parking.dq`) by `Parking.dq_pos_iff`. The differences `2 * k - 2` and `k - 1` are differences of natural numbers and are the ordinary ones because $k\ge2$.

## Proof

The proof distinguishes the columns $k\le81$ and $k\ge82$.

*The columns $2\le k\le81$.* The second part of `Parking.Tab.small_table` states, for $2\le k\le81$ and every $n$ with $k+1\le n\le2k-2$: if $b(n,k-1)<b(n,k)$, then $b(n+1,k-1)<b(n+1,k)$. This is the claim.

*The columns $k\ge82$.* By `Parking.one_sign_change` there is a row $q$ such that $d_{j,k}\le0$ for every $j$ with $k\le j<q$, and $d_{m,k}>0$ for every $m$ with $q\le m\le2k-1$. By assumption $d_{n,k}>0$, and $n\ge k$. So $n$ is not one of the rows $k\le j<q$, which means $q\le n$. Then $q\le n+1\le2k-1$, and therefore $d_{n+1,k}>0$, which is $b(n+1,k-1)<b(n+1,k)$. The two passages between the sign of $d_{m,k}$ and the comparison of the counts $b(m,k-1)$ and $b(m,k)$, in the rows $m=n$ and $m=n+1$, are `Parking.dq_pos_iff`.

---
weight: unit
short: one change of sign in the first layer of a column k ≥ 82
---
## Description

Every column $k\ge82$ has a row $q$ with $k+1\le q\le k+27k/100$ such that $b(j,k)\le b(j,k-1)$ for $k\le j<q$ and $b(n,k-1)<b(n,k)$ for $q\le n\le2k-1$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`), and let $d_{n,k}=b(n,k)-b(n,k-1)$ be the step of the column $k$ in the row $n$. For every natural number $k\ge82$ there is a natural number $q$ such that

- $k+1\le q$ and $100\,(q-k)\le27\,k$;
- $d_{j,k}\le0$ for every $j$ with $k\le j<q$;
- $d_{n,k}>0$ for every $n$ with $q\le n\le2k-1$.

## Explanation

**What the statement says.** The rows $k+1\le n\le2k-1$ are the *first layer* of the column $k$ (some records call them the chain range of the column), and the row $k$ directly above the layer is the row in which the column begins: there the step is negative, $d_{k,k}=-k^{k-2}$ (`Parking.dq_base`). The second condition of the statement includes this row $j=k$. No parking function of length $k$ has maximum displacement $k$, so $b(k,k)=0$ and $d_{k,k}=-b(k,k-1)$. In this row the statement itself asserts only that the step is not positive, $d_{k,k}\le0$, and none of the values $d_{k,k}=-k^{k-2}$, $b(k,k)=0$ and $d_{k,k}=-b(k,k-1)$. Read down the column from the row $k$ to the row $2k-1$, the step changes its sign exactly once, from not positive to positive, and the change comes within the first $27k/100$ rows of the layer. The row $q$ is the *first positive row* of the column, that is, the first row after the row $k$ in which its step is positive (some records call it the crossing row of the column). The three conditions determine it: the steps in the rows from $k$ to $q-1$ are not positive, and the step in the row $q$ itself is positive, because $q\le k+27k/100\le2k-1$.

**Why it holds.** Two facts are combined. The column has a positive row early in its first layer (`Parking.positive_row_early`), so its first positive row $q$ exists and satisfies $100(q-k)\le27k$. And a column that turns positive in the first third of its first layer does not turn back before the end of the layer. The second fact is `Parking.persist`, the analytic statement on which the present one rests; its record says how it is proved and why it ends at the row $2k-1$, which is the last row in which the column equation `Parking.dq_col` holds. The present statement adds to these two only the choice of $q$ as the first positive row. That choice is what supplies the signs before $q$ that `Parking.persist` asks for as a hypothesis.

**What it is used for.** It is used in two places. `Parking.step_persists` obtains from it the persistence of the sign in the first layer for the columns $k\ge82$: a positive step in a row of the layer lies at the row $q$ or after it, and then so does the step in the next row. `Parking.step_pos_large` starts from it to show that the column is positive in all the rows $n\ge2k$. There the signs in the rows from $k$ to $2k-1$ are the start of an induction on the row, and the bound $100(q-k)\le27k$ is used a second time, in the comparison of the weights that a row $n\ge2k$ gives to the rows before $q$ and to the rows from $q$ on.

**The Lean form.** The statement is `∃ q, k + 1 ≤ q ∧ 100 * (q - k) ≤ 27 * k ∧ (∀ j, k ≤ j → j < q → dq k j ≤ 0) ∧ (∀ n, q ≤ n → n ≤ 2 * k - 1 → 0 < dq k n)`. The signs are written for the real number $\delta^{(k)}_j=d_{j,k}/j!$ (`Parking.dq`), which has the sign of $d_{j,k}$; the comparisons of the counts follow by `Parking.dq_pos_iff`. The differences `q - k` and `2 * k - 1` are differences of natural numbers and are the ordinary ones because $k+1\le q$ and $k\ge82$.

## Proof

By `Parking.positive_row_early` there is a natural number $r\ge1$ with $100\,r\le27\,k$ and $d_{k+r,k}>0$. So the set of the rows $j\ge k+1$ with $d_{j,k}>0$ is not empty; let $q$ be its least element. Then $k+1\le q\le k+r$, hence $100\,(q-k)\le100\,r\le27\,k$, and $d_{q,k}>0$.

*The rows before $q$.* Let $k\le j<q$. If $j=k$, `Parking.dq_base` states $d_{k,k}/k!=-a_k/k$ for $k\ge2$, where $a_k=k^{k-1}/k!$ (`Parking.cay`), and $a_k\ge0$ (`Parking.cay_nonneg`); so $d_{k,k}\le0$. If $k+1\le j<q$, then $d_{j,k}\le0$, because $q$ is the least row $j\ge k+1$ with $d_{j,k}>0$.

*The rows from $q$ on.* Put $r_q=q-k$. Then $r_q\ge1$, and $3\,r_q\le k$, since $100\,r_q\le27\,k$. `Parking.persist` states: if $k\ge82$, $r_q\ge1$ and $3\,r_q\le k$, if $d_{j,k}\le0$ for every $j$ with $k\le j<k+r_q$, and if $d_{k+r_q,k}>0$, then $d_{n,k}>0$ for every $n$ with $k+r_q\le n\le2k-1$. Its hypotheses have just been verified for $k+r_q=q$, and its conclusion is the third condition of the statement.

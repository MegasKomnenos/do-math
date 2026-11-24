---
weight: unit
short: the step bound
---
## Description

For a column $k\ge2$, a tilt $x>0$ at which the tilted environment $z^{(k)}_Nx^N$ does not increase in $N$, and a row $n\ge k$ at which all the sums $\sum_{t=s}^{n}\xi_tx^t$, $k\le s\le n$, of the tree curvature $\xi$ of the column are nonnegative: $(1-x)\,\xi_n\le\delta_n$, where $\delta_n=(b(n,k)-b(n,k-1))/n!$ is the normalised step of the column in the row $n$.

## Statement

Let $A(N,l)$ be the number of parking functions of length $N$ with maximum displacement at most $l$ (`Parking.A`) and $b(n,\ell)$ the number of those of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k\ge2$ and $n\ge k$ be natural numbers and $x>0$ a real number. Write

- $z^{(y)}_N=A(N,y-1)/N!$ for the environment of a threshold $y$ (`Parking.zr`);
- $\delta_n=(b(n,k)-b(n,k-1))/n!$ for the normalised step of the column $k$ in the row $n$ (`Parking.dq`);
- $\xi_t$ for the tree curvature of the column $k$ (`Parking.xi`): $\xi_0=0$ and, for $t\ge1$,
$$t\,\xi_t=\min(t,k+1)\,z^{(k+1)}_{t-1}-2\min(t,k)\,z^{(k)}_{t-1}+\min(t,k-1)\,z^{(k-1)}_{t-1}.$$

Assume

1. $z^{(k)}_{N+1}\,x^{N+1}\le z^{(k)}_N\,x^N$ for every $N\ge0$;
2. $\displaystyle\sum_{t=s}^{n}\xi_t\,x^t\ge0$ for every $s$ with $k\le s\le n$.

Then
$$(1-x)\,\xi_n\le\delta_n .$$

## Explanation

**What the bound adds.** Under the same two hypotheses, the one-tree bound and a summation by parts give $\delta_n\ge0$, and nothing more: a step equal to zero is not excluded. The staircase theorem (`Parking.staircase`), for which the step bound is proved, needs strict signs: both of the rules from which it is derived, `Parking.column_rule` and `Parking.diagonal_rule`, conclude with a strict inequality. The step bound keeps this argument and replaces the lower bound $0$ by $(1-x)\,\xi_n$. Hypothesis 1 at $N=0$ reads $x\le1$, since $z^{(k)}_0=z^{(k)}_1=1$; so the factor $1-x$ is never negative, and the bound gives $\delta_n>0$ as soon as $x<1$ and $\xi_n>0$. The curvature $\xi_n$ is positive when the step of the row before is positive, because $n\,\xi_n=(k+1)\,\delta_{n-1}+2\,b(n-1,k-1)/(n-1)!$ for $n-1\ge k$. A positive step therefore produces a positive step in the next row. This is carried out in `Parking.propagate_pos`, which is the only place where the step bound is used.

**Where the gain comes from.** Multiplied by $x^n$, the one-tree bound `Parking.one_tree_bound` reads
$$\delta_n\,x^n\ \ge\ \sum_{t=k}^{n}\bigl(\xi_t\,x^t\bigr)\,u_{n-t},\qquad u_N=z^{(k)}_N\,x^N .$$
The weights $u_{n-t}$, $t=k,\dots,n$, are nonnegative and, by hypothesis 1, do not decrease in $t$; the last one is $u_0=1$ at $t=n$, and for $n>k$ the one before it is $u_1=x$ at $t=n-1$. Summation by parts shows that a sum $\sum_ta_tw_t$ is nonnegative when all the sums $\sum_{t\ge s}a_t$ are nonnegative and the weights $w_t$ are nonnegative and do not decrease. It asks nothing else of the weights. The last weight can therefore be lowered from $u_0=1$ to $u_1=x$: the weights still do not decrease, since for $n>k$ the last one now equals the one before it and for $n=k$ there is only one weight, and the sum with the lowered weight is still nonnegative. What was taken away from the right-hand side is $\xi_n\,x^n\,(1-x)$, and this amount is the lower bound for $\delta_n\,x^n$. For $n>k$ the value $u_1$ is the smallest that the last weight can take without breaking the monotonicity, so $1-x$ is the factor that this argument yields. Nothing is estimated beyond the summation by parts that gives $\delta_n\ge0$.

**The row $n=k$.** The statement admits $n=k$, but it has no content there: hypothesis 2 for $s=n=k$ reads $\xi_k\ge0$, while $\xi_k=-a_k/k<0$ with $a_k=k^{k-1}/k!$, a value that the record of `Parking.xi` gives. The bound says something from the row $k+1$ on.

**The tilt.** The tilt $x$ is a free parameter, and hypothesis 1 is all that the proof asks of it. In the application the tilt is the critical tilt $x_k=(k/(k+1))^{k-1}$ of the column (`Parking.xcrit`), for which hypothesis 1 is the theorem `Parking.zrT_anti_crit`, and hypothesis 2 is supplied at the row $n_0(k)$ by the table `Parking.Tab.small_table` for the columns $2\le k\le81$ (see `Parking.step_pos_beyond`).

**The Lean form.** The conclusion is `(1 - x) * xi k n ≤ dq k n`. Hypothesis 1 is written with the tilted environment `zrT k x N = zr k N * x ^ N` (`Parking.zrT`), as `∀ N, zrT k x (N + 1) ≤ zrT k x N`. The sums of hypothesis 2 run over `Finset.Icc s n`. The statement is about real numbers; by `Parking.dq_pos_iff`, $\delta_n>0$ is the inequality $b(n,k-1)<b(n,k)$ of natural numbers.

## Proof

Write $u_N=z^{(k)}_Nx^N$ for the tilted environment and $a_t=\xi_tx^t$. The proof has three steps: the one-tree bound in tilted form, a summation by parts with the last weight lowered, and the comparison of the two weighted sums.

**Step 1: the one-tree bound, tilted.** `Parking.one_tree_bound` states, for $k\ge2$ and every $n$, that $\sum_{t=0}^{n}\xi_t\,z^{(k)}_{n-t}\le\delta_n$. Multiply by $x^n>0$ and write $x^n=x^t\,x^{n-t}$ in the term of index $t$. The terms with $t<k$ vanish, because $\xi_t=0$ for $t<k$ (`Parking.xi_eq_zero`). Hence
$$\sum_{t=k}^{n}a_t\,u_{n-t}\ \le\ \delta_n\,x^n .\tag{1}$$

**Step 2: summation by parts with the last weight lowered.** For $k\le t\le n$ put $w_t=u_{\max(n-t,\,1)}$, so that $w_t=u_{n-t}$ for $t<n$ and $w_n=u_1$. These weights are nonnegative, because $x\ge0$ (`Parking.zrT_nonneg`). They do not decrease in $t$: hypothesis 1 says that $u_N$ does not increase in $N$, and $\max(n-s-1,1)\le\max(n-s,1)$, so $w_s\le w_{s+1}$ for $k\le s<n$.

The summation by parts is the following fact about real sequences $a$ and $w$. If $\sum_{t=s}^{n}a_t\ge0$ for every $s$ with $k\le s\le n$, and $w_s\le w_{s+1}$ for every $s$ with $k\le s<n$, then
$$w_s\sum_{t=s}^{n}a_t\ \le\ \sum_{t=s}^{n}a_t\,w_t\qquad\text{for every } s \text{ with } k\le s\le n .$$
It is proved by induction on $n-s$. For $s=n$ both sides are $a_nw_n$. For $s<n$, the induction hypothesis for $s+1$, then $w_s\le w_{s+1}$ together with $\sum_{t=s+1}^{n}a_t\ge0$, give
$$\sum_{t=s}^{n}a_tw_t=a_sw_s+\sum_{t=s+1}^{n}a_tw_t\ \ge\ a_sw_s+w_{s+1}\sum_{t=s+1}^{n}a_t\ \ge\ a_sw_s+w_s\sum_{t=s+1}^{n}a_t=w_s\sum_{t=s}^{n}a_t .$$
Apply this to $a_t=\xi_tx^t$, whose sums are nonnegative by hypothesis 2, and to the weights $w_t$, with $s=k$. Since $w_k\ge0$ and $\sum_{t=k}^{n}a_t\ge0$,
$$\sum_{t=k}^{n}a_t\,w_t\ \ge\ w_k\sum_{t=k}^{n}a_t\ \ge\ 0 .\tag{2}$$

**Step 3: the two sums differ in one term.** For $t<n$ the weights $u_{n-t}$ and $w_t$ are equal. For $t=n$ they are $u_0$ and $u_1$. Here $u_0=1$ (`Parking.zrT_zero`), and $u_1=x$: the index $1\le k$ lies in the free range of the threshold $k$, where the tilted environment is the tilted Cayley mass $c_Nx^N$ (`Parking.zrT_eq_ccT`, `Parking.ccT`), and $c_1=1$, because `Parking.cc_eq` gives $c_N=(N+1)^N/(N+1)!$, which is $2^1/2!$ for $N=1$. Therefore
$$\sum_{t=k}^{n}a_t\,u_{n-t}-\sum_{t=k}^{n}a_t\,w_t=a_n\,(u_0-u_1)=(1-x)\,\xi_n\,x^n .$$
With (1) and (2) this gives $(1-x)\,\xi_n\,x^n\le\delta_n\,x^n$, and division by $x^n>0$ gives the claim.

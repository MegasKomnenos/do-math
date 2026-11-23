---
weight: unit
short: single-chain formula, forward form
---
## Description

Single-chain formula, forward form. If $W$ solves the weighted last-car recursion with a weight that satisfies $\omega(t)=t$ for $1\le t\le k$, then for $n\le 2k+1$: $c_n-W_n=\sum_{t=k+1}^{n}c_{n-t}\bigl(c_{t-1}-\frac{\omega(t)}{t}W_{t-1}\bigr)$.

## Statement

Let $\omega$ and $W$ be real sequences such that $W$ is a solution of the weighted last-car recursion with weight $\omega$ (`Parking.IsWSol`), and let $k$ be a natural number such that $\omega(t)=t$ for every $t$ with $1\le t\le k$. Then for every natural number $n\le 2k+1$,
$$c_n-W_n\;=\;\sum_{t=k+1}^{n}c_{n-t}\Bigl(c_{t-1}-\frac{\omega(t)}{t}\,W_{t-1}\Bigr),$$
where $c_n=(n+1)^{n-1}/n!$ (`Parking.cc`). For $n\le k$ the sum is empty and the statement is $W_n=c_n$.

## Explanation

**What the formula says.** With $P=\sum_nc_nX^n$, $\mathbf W=\sum_nW_nX^n$ and $D=\sum_{t\ge1}\bigl(c_{t-1}-\frac{\omega(t)}tW_{t-1}\bigr)X^t$ as in `Parking.IsWSol.ez`, that record gives $\mathbf W/P\equiv1-D\pmod{X^{2k+2}}$. Multiplying by $P$ gives $P-\mathbf W\equiv P\,D\pmod{X^{2k+2}}$, and the present statement is the coefficient of $X^n$, $n\le2k+1$, of this congruence; the sum starts at $t=k+1$ because $D$ has no terms of degree at most $k$. The reason why the range is $n\le 2k+1$ is explained in `Parking.IsWSol.ez`.

**How it reads.** The difference $c_n-W_n$ measures how far the solution of the weight $\omega$ falls below the solution $c$ of the unrestricted weight $t$. The formula expresses it through the earlier values $W_{t-1}$, $k<t\le n$, with the explicit positive coefficients $c_{n-t}$: a recursion "forward" in $n$, in which $W_n$ does not occur on the right. For the threshold weight $\omega(t)=\min(t,y)$ with $k=y$, multiplied by $n!$, it reads
$$P_n-A(n,y-1)=\sum_{t=y+1}^{n}\binom nt\,P_{n-t}\,\bigl(t\,P_{t-1}-y\,A(t-1,y-1)\bigr),\qquad P_m=(m+1)^{m-1},$$
a recursion for the numbers $P_n-A(n,y-1)$. Since $P_n$ is the number of all parking functions of length $n$ (the classical count; `Parking.A_eq_pow` gives $A(n,k)=P_n$ for $k\ge n-1$, and no displacement exceeds $n-1$), this is the number of those that have some displacement at least $y$.

**What it is for.** It gives the initial value of the step of a column (`Parking.dq_base`); the table of two signs (`Parking.Tab.two_signs`) computes its entries by the integer form just displayed; and the frozen polynomial of the part on the next column (`Parking.dq_frozen`) is obtained from it, where it is applied to the threshold weights $\min(t,j)$, $j\in\{k,k+1\}$, with the same $k$.

**The Lean form.** The sum runs over `Icc (k + 1) n`; `ω t / t` is a division of real numbers with $t\ge k+1\ge1$; the subtractions `n - t` and `t - 1` of natural numbers are exact on the range of summation.

## Proof

Keep the notation $E=1/P$, $V=E\,\mathbf W$, $D=T-G$, $V_i$, $D_i$ of the proof of `Parking.IsWSol.ez`. That proof establishes, under the present hypotheses: $V_0=1$; $V_i=0$ for $1\le i\le k$; $V_i=-D_i$ for $1\le i\le 2k+1$; and $D_t=c_{t-1}-\frac{\omega(t)}{t}W_{t-1}$ for $t\ge1$. (These facts are private lemmas of the module, shared by the two proofs.)

Since $E\,P=1$ (`Parking.TreeSeries.Eser_mul_Pser`), we have $\mathbf W=V\,P$. Take the coefficient of $X^n$, with the term of index $0$ split off (`Parking.TreeSeries.coeff_mul_split`), and use that the coefficients of $P$ are the $c_n$ (`Parking.TreeSeries.coeff_Pser`):
$$W_n=V_0\,c_n+\sum_{t=1}^{n}V_t\,c_{n-t}=c_n+\sum_{t=k+1}^{n}V_t\,c_{n-t},$$
because $V_0=1$ and the terms with $1\le t\le k$ vanish. For $k+1\le t\le n\le 2k+1$ we have $V_t=-D_t=-\bigl(c_{t-1}-\frac{\omega(t)}{t}W_{t-1}\bigr)$. Substituting and rearranging gives the statement.

---
weight: unit
short: weights of the tilted source term
---
## Description

The weights $\pi_j=x^ja_j/j$ of the column $k$, where $x=1/\gamma_k$ is the diagonal tilt of the column and $a_j=j^{j-1}/j!$.

## Statement

For natural numbers $k$ and $j\ge1$,
$$\pi_j=\pi_j(k)=\frac{x^j\,a_j}{j},$$
where $x$ is the diagonal tilt of the column $k$ (`Parking.xk`) and $a_j=j^{j-1}/j!$ (`Parking.cay`). The Lean definition also gives a value for $j=0$, namely $0$.

## Explanation

**Where the weights come from.** Put $c_n=(n+1)^{n-1}/n!=a_{n+1}$ (`Parking.cc`), $z^{(k)}_n=A(n,k-1)/n!$ (`Parking.zr`) and $\beta^{(k-1)}_n=b(n,k-1)/n!$ (`Parking.bq`). The ratios $F_n=z^{(k)}_n/c_n$ and $P_n=\beta^{(k-1)}_n/c_n$ are the proportions, among all parking functions of length $n$, of those with maximum displacement at most $k-1$ and exactly $k-1$. The column equations have source terms that do not involve the unknown sequence: $z^{(k)}_{n-1}/n$ in the equation `Parking.bq_L0` of the column $k-1$, and $(2/n)\beta^{(k-1)}_{n-1}$ in the equation `Parking.dq_col` of the step. After the tilt by $x^n$, and since $a_n=c_{n-1}$, these become
$$\frac{x^n z^{(k)}_{n-1}}{n}=\pi_n\,F_{n-1},\qquad\frac{2x^n\beta^{(k-1)}_{n-1}}{n}=2\,\pi_n\,P_{n-1}.$$
So $\pi_n$ is the weight with which the proportions $F_{n-1}$ and $P_{n-1}$ enter the tilted equations of the row $n$. The first values of the tilted sequences are also weights: $x^k\beta^{(k-1)}_k=\pi_k$ and, by `Parking.dq_base`, $x^k\delta_k=-\pi_k$, where $\delta_n=d_{n,k}/n!$ is the normalised step of the column $k$ (`Parking.dq`).

**How they vary.** By `Parking.CrossCrit.pix_succ`, $\pi_{n+1}=x\gamma_n\,\pi_n$ for $n\ge2$, with $\gamma_n=(1+1/n)^{n-2}$ (`Parking.gam`). Because $x\gamma_k=1$ and $\gamma$ is nondecreasing, $\pi_{k+1}=\pi_k$ and the weights are nondecreasing from the index $k$ on, with ratios $x\gamma_n$ that exceed $1$ only by $O((n-k)/k^2)$. If the ratios were exactly $1$ the weights would be constant and several terms of the crossing criterion would vanish; the quantities `Parking.ecor` and `Parking.ecorSum` measure the effect of their not being constant.

**The Lean form.** `pix k j = xk k ^ j * cay j / j`, with the real division; at $j=0$ both `cay 0` and the division by zero give $0$. The weights are used only for $j\ge k\ge2$.

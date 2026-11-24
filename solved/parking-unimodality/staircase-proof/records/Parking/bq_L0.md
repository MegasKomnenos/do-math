---
weight: unit
short: column equation of a level
---
## Description

The column equation of the level $l\ge1$ on the rows $l+1\le n\le 2l+1$: $\beta^{(l)}_n=\frac1n z^{(l+1)}_{n-1}+\frac ln\beta^{(l)}_{n-1}+\sum_{m=1}^{n-l-1}\varepsilon_m\beta^{(l)}_{n-m}$, where $\beta^{(l)}_n=b(n,l)/n!$.

## Statement

Let $l\ge1$ and $n$ be natural numbers with $l+1\le n\le 2l+1$. Then
$$\beta^{(l)}_n=\frac{z^{(l+1)}_{n-1}}{n}+\frac{l}{n}\,\beta^{(l)}_{n-1}+\sum_{m=1}^{n-l-1}\varepsilon_m\,\beta^{(l)}_{n-m},$$
where $\beta^{(l)}_n=b(n,l)/n!$ (`Parking.bq`), $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`) and $\varepsilon_m=(m-1)^{m-1}/m!$ (`Parking.eps`).

## Explanation

The equation determines the column $l$ row by row, starting from its first nonzero row $n=l+1$: the value in the row $n$ is given by the value in the row $n-1$, by a source term $z^{(l+1)}_{n-1}/n$ that comes from the environment of the threshold $l+1$, and by a feedback sum over the earlier rows with the fixed kernel $\varepsilon$. All three contributions are nonnegative. Multiplied by $n!$ it is an identity between counts,
$$b(n,l)=A(n-1,l)+l\,b(n-1,l)+\sum_{m=1}^{n-l-1}\binom nm(m-1)^{m-1}\,b(n-m,l).$$

It is the single-chain formula `Parking.IsWSol.ez` for the two thresholds $l+1$ and $l$, subtracted. The range $n\le2l+1$ is the single-chain range of the smaller threshold $l$; the sum stops at $m=n-l-1$ because the column vanishes in the rows $n-m\le l$ (`Parking.bq_eq_zero`). The equation is used for the profile of the column $l=k-1$ in the far rows of the chain range (`Parking.caseFar`): it gives the positivity of the profile, and, multiplied by the powers of $e^{-1}$, the inequality $\sum_{i=1}^{\sigma}f_i\,v_{\sigma-i}\le v_\sigma$ between the sequence $v_\sigma=e^{-\sigma}\beta^{(k-1)}_{k+\sigma}$ and the frozen kernel $f$ (`Parking.fker`); the corresponding equation for the difference of two columns is `Parking.dq_col`.

In Lean the upper limit of the sum is `n - l - 1` with the subtraction of natural numbers, exact because $n\ge l+1$; $z^{(l+1)}_{n-1}$ is `zr (l + 1) (n - 1)`.

## Proof

*The single-chain formula for one threshold.* For a threshold $y\ge1$ and $y\le n\le 2y+1$,
$$z^{(y)}_n-\sum_{m=1}^{n}\varepsilon_m\,z^{(y)}_{n-m}=\frac yn\,z^{(y)}_{n-1}-c_{n-1}. \tag{1}$$
(This is a private lemma of the module, used again for `Parking.dq_col`.) By `Parking.zr_isWSol`, $z^{(y)}$ solves the weighted last-car recursion with the weight $\min(t,y)$, which equals $t$ for $t\le y$, so `Parking.IsWSol.ez` applies with $k=y$. For $y<n\le2y+1$ it gives (1), because $\min(n,y)=y$. For $n=y$ it gives that the left-hand side is $0$; the right-hand side is $z^{(y)}_{y-1}-c_{y-1}$, which is $0$ by `Parking.zr_eq_cc`.

*Subtraction.* Apply (1) with $y=l+1$, which is allowed because $l+1\le n\le 2l+3$, and with $y=l$, which is allowed because $l\le n\le 2l+1$, and subtract. By `Parking.bq_eq`, $z^{(l+1)}_i-z^{(l)}_i=\beta^{(l)}_i$ for every $i$. The terms $c_{n-1}$ cancel, and
$$\beta^{(l)}_n-\sum_{m=1}^{n}\varepsilon_m\,\beta^{(l)}_{n-m}=\frac{l+1}{n}z^{(l+1)}_{n-1}-\frac ln z^{(l)}_{n-1}=\frac{z^{(l+1)}_{n-1}}{n}+\frac ln\,\beta^{(l)}_{n-1}.$$

*Truncation.* For $m>n-l-1$ we have $n-m\le l$ and $\beta^{(l)}_{n-m}=0$ by `Parking.bq_eq_zero`, so the sum over $1\le m\le n$ equals the sum over $1\le m\le n-l-1$ (`Parking.sum_Icc_trunc`). Moving the sum to the right gives the statement.
